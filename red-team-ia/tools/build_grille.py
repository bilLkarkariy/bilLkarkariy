#!/usr/bin/env python3
"""Génère la grille d'audit « état des lieux » (Excel + Markdown) depuis data/*.yaml.

    python3 red-team-ia/tools/build_grille.py

Sources : data/grille.yaml (points de contrôle), data/referentiels.yaml (libellés
officiels NIST / OWASP / MITRE ATLAS) et data/cas.yaml (cas d'école sourcés).
Dépendances : PyYAML et openpyxl. Le classeur contient des formules qu'Excel ou
LibreOffice calculent à l'ouverture.
"""
from __future__ import annotations

import math
from pathlib import Path

import yaml
from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.worksheet.datavalidation import DataValidation

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
XLSX = ROOT / "03-grille-audit-etat-des-lieux.xlsx"
MD = ROOT / "03-grille-audit-etat-des-lieux.md"

FONT = "Arial"
INK, MUTED, WHITE = "1F2328", "57606A", "FFFFFF"
NAVY, BAND, INPUT, GRID = "1F2A44", "E8EDF5", "FFF2CC", "C9D1DC"
SERIES = "2A78D6"  # teinte unique du graphique (une seule série)
# Teintes de fond dérivées de la palette de statut ; le libellé texte porte toujours le sens.
TINTS = {"Critique": "F6D5D5", "Fragile": "FBE1D6", "Intermédiaire": "FEEFCB", "Robuste": "D3EFD3"}

FAMILLES = [
    ("nist_ai_rmf", "NIST AI RMF 1.0"),
    ("nist_csf", "NIST CSF 2.0"),
    ("owasp_llm", "OWASP LLM 2025"),
    ("owasp_asi", "OWASP Agentic 2026"),
    ("atlas", "MITRE ATLAS"),
]

# (titre, largeur) ; l'ordre fixe les lettres de colonnes utilisées dans les formules.
COLS = [
    ("ID", 8), ("Domaine", 9), ("Point de contrôle", 62), ("Preuves attendues", 44),
    ("Méthode", 22), ("Criticité\n(1-3)", 9), ("Flash", 7), ("Maturité\n(0-4 ou N/A)", 12),
    ("Score\npondéré", 9), ("Score\nmax", 8), ("Constat", 40), ("Recommandation", 40),
    ("Priorité", 9), ("NIST AI RMF 1.0", 20), ("NIST CSF 2.0", 16), ("OWASP LLM 2025", 26),
    ("OWASP Agentic 2026", 28), ("MITRE ATLAS v2026.10", 36), ("Cas d'école", 28),
]
C_ID, C_DOM, C_Q, C_PRE, C_MET, C_CRIT, C_FLASH, C_MAT, C_SC, C_MAX, C_CONST, C_RECO, C_PRIO = range(1, 14)
C_REF0 = 14  # première colonne de référentiels (ordre = FAMILLES), puis C_CAS
C_CAS = C_REF0 + len(FAMILLES)
FIRST_ROW = 5
LAST_ROW_A, LAST_ROW_B = 80, 140  # bornes des plages de formules (marge pour ajouts)

thin = Side(style="thin", color=GRID)
BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)


# ---------------------------------------------------------------- chargement
def load():
    g = yaml.safe_load((DATA / "grille.yaml").read_text(encoding="utf-8"))
    r = yaml.safe_load((DATA / "referentiels.yaml").read_text(encoding="utf-8"))
    c = yaml.safe_load((DATA / "cas.yaml").read_text(encoding="utf-8"))["cas"]
    return g, r, c


def controls(g):
    for s in g["surfaces"]:
        for d in s["domaines"]:
            for ctl in d["controles"]:
                yield s, d, ctl


def validate(g, r, c):
    errors, ids, flash = [], set(), 0
    for s, d, ctl in controls(g):
        cid = ctl["id"]
        if cid in ids:
            errors.append(f"ID en double : {cid}")
        ids.add(cid)
        if not (d["id"].startswith(s["id"]) and cid.startswith(d["id"] + ".")):
            errors.append(f"{cid} : identifiant incohérent avec {d['id']}")
        if ctl.get("criticite") not in (1, 2, 3):
            errors.append(f"{cid} : criticité hors 1-3")
        for k in ("question", "preuves", "methode"):
            if not ctl.get(k):
                errors.append(f"{cid} : champ « {k} » vide")
        if ctl.get("flash"):
            flash += 1
            if not ctl.get("question_flash"):
                errors.append(f"{cid} : question_flash manquante")
        for fam, vals in (ctl.get("refs") or {}).items():
            if fam not in r:
                errors.append(f"{cid} : famille de référentiel inconnue {fam}")
                continue
            errors += [f"{cid} : {fam} {v} absent de referentiels.yaml" for v in vals if v not in r[fam]]
        errors += [f"{cid} : cas {t} absent de cas.yaml" for t in ctl.get("cas") or [] if t not in c]
    n_a = sum(1 for s, _, _ in controls(g) if s["id"] == "A")
    n_b = sum(1 for s, _, _ in controls(g) if s["id"] == "B")
    if FIRST_ROW + n_a + 20 > LAST_ROW_A or FIRST_ROW + n_b + 20 > LAST_ROW_B:
        errors.append("Plages de formules trop courtes : augmenter LAST_ROW_A / LAST_ROW_B")
    if errors:
        raise SystemExit("Grille invalide :\n- " + "\n- ".join(errors))
    return flash


# ---------------------------------------------------------------- libellés
def ref_label(fam, i, r):
    if fam in ("owasp_llm", "owasp_asi"):
        return f"{i} {r[fam][i]}"
    if fam == "atlas":
        return f"{i} {r['atlas'][i]['nom']}"
    return i


def ref_cell(ctl, fam, r):
    return "\n".join(ref_label(fam, i, r) for i in (ctl.get("refs") or {}).get(fam, []))


def cas_label(tag, c):
    e = c[tag]
    suffix = {"verifie": "", "partiel": " (sources partielles)"}.get(e.get("statut"), " (à vérifier)")
    return e["court"] + suffix


def used_by(g):
    """Index inverse référence -> contrôles et cas -> contrôles."""
    refs, cas = {}, {}
    for _, _, ctl in controls(g):
        for fam, vals in (ctl.get("refs") or {}).items():
            for v in vals:
                refs.setdefault((fam, v), []).append(ctl["id"])
        for t in ctl.get("cas") or []:
            cas.setdefault(t, []).append(ctl["id"])
    return refs, cas


# ---------------------------------------------------------------- styles
def put(ws, row, col, value=None, *, bold=False, size=10, color=INK, bg=None, wrap=True,
        h="left", v="top", border=True, italic=False, fmt=None):
    cell = ws.cell(row=row, column=col, value=value)
    cell.font = Font(name=FONT, size=size, bold=bold, color=color, italic=italic)
    cell.alignment = Alignment(wrap_text=wrap, horizontal=h, vertical=v)
    if bg:
        cell.fill = PatternFill("solid", start_color=bg, end_color=bg)
    if border:
        cell.border = BORDER
    if fmt:
        cell.number_format = fmt
    return cell


def n_lines(text, width):
    if not text:
        return 1
    per = max(1, int(width * 1.2))
    return sum(max(1, math.ceil(len(part) / per)) for part in str(text).split("\n"))


def fit(ws, row, pairs, minimum=1):
    ws.row_dimensions[row].height = 13 * max([minimum] + [n_lines(t, w) for t, w in pairs]) + 5


def title_block(ws, title, subtitle, last_col, legend=None):
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=last_col)
    put(ws, 1, 1, title, bold=True, size=14, color=NAVY, border=False, wrap=False)
    ws.row_dimensions[1].height = 24
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=last_col)
    put(ws, 2, 1, subtitle, color=MUTED, border=False)
    ws.row_dimensions[2].height = 30
    if legend:
        ws.merge_cells(start_row=3, start_column=2, end_row=3, end_column=last_col)
        put(ws, 3, 1, "", bg=INPUT)
        put(ws, 3, 2, legend, italic=True, color=MUTED, border=False)


def header(ws, row, labels):
    for col, label in enumerate(labels, start=1):
        put(ws, row, col, label, bold=True, color=WHITE, bg=NAVY, v="center")
    ws.row_dimensions[row].height = 30


def print_setup(ws, paper="A4"):
    """Paysage, ajusté à la largeur de la page."""
    ws.page_setup.orientation = "landscape"
    ws.page_setup.paperSize = ws.PAPERSIZE_A3 if paper == "A3" else ws.PAPERSIZE_A4
    ws.page_setup.fitToWidth, ws.page_setup.fitToHeight = 1, 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True


def list_validation(ws, values, prompt):
    dv = DataValidation(type="list", formula1='"' + ",".join(values) + '"', allow_blank=True,
                        showErrorMessage=True, errorTitle="Valeur non prévue", error=prompt)
    ws.add_data_validation(dv)
    return dv


# ---------------------------------------------------------------- feuilles
def sheet_guide(wb, g, flash_count):
    ws = wb.active
    ws.title = "Mode d'emploi"
    ws.sheet_view.showGridLines = False
    for col, w in zip("ABCD", (24, 18, 70, 30)):
        ws.column_dimensions[col].width = w
    meta = g["meta"]
    title_block(ws, meta["titre"], f"Version {meta['version']} du {meta['date']} — généré depuis data/grille.yaml", 4)
    row = 4

    def section(text):
        nonlocal row
        row += 1
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=4)
        put(ws, row, 1, text, bold=True, size=11, color=NAVY, border=False)
        row += 1

    def para(text, height=None):
        nonlocal row
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=4)
        put(ws, row, 1, text, border=False)
        ws.row_dimensions[row].height = height or 13 * n_lines(text, 135) + 5
        row += 1

    section("À quoi sert cette grille")
    para("Établir l'état des lieux d'une organisation sur les deux surfaces révélées par Black October : "
         "la surface classique, désormais attaquée à vitesse machine (surface A), et la surface agentique : "
         "les agents d'IA de l'organisation et ceux de tiers (surface B). Chaque point de contrôle est relié "
         "aux référentiels NIST AI RMF, NIST CSF 2.0, OWASP (LLM 2025 et Agentic 2026) et MITRE ATLAS.")
    section("Comment l'utiliser")
    for step in [
        "1. Fiche mission : renseigner le contexte, le périmètre et la référence de l'autorisation d'audit.",
        f"2. Diagnostic Flash (avant-vente, environ 45 min) : {flash_count} questions posées à un décideur ; score indicatif immédiat.",
        "3. Surface A et Surface B : pour chaque point de contrôle, collecter les preuves puis saisir la maturité (0 à 4, ou N/A), "
        "le constat, la recommandation et la priorité (P1 à P3).",
        "4. Synthèse : scores par domaine et par surface, alertes sur les contrôles critiques et graphique, calculés automatiquement.",
        "5. Plan d'action : saisir l'ID d'un contrôle ; constat, recommandation et priorité sont repris de la grille.",
        "6. Cas d'école et Référentiels : sources des incidents cités et libellés officiels des référentiels.",
    ]:
        para(step)
    section("Cellules à renseigner")
    put(ws, row, 1, "", bg=INPUT)
    ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=4)
    put(ws, row, 2, "Les cellules jaunes sont les seules à saisir. Les autres sont calculées ou issues du référentiel : ne pas les modifier.", border=False)
    row += 1
    section("Échelle de maturité")
    for e in meta["echelle_maturite"]:
        put(ws, row, 1, e["niveau"], bold=True, h="center")
        put(ws, row, 2, e["libelle"], bold=True)
        ws.merge_cells(start_row=row, start_column=3, end_row=row, end_column=4)
        put(ws, row, 3, e["definition"])
        row += 1
    put(ws, row, 1, "N/A", bold=True, h="center")
    put(ws, row, 2, "Non applicable", bold=True)
    ws.merge_cells(start_row=row, start_column=3, end_row=row, end_column=4)
    put(ws, row, 3, "Contrôle sans objet dans le périmètre. Justifier dans la colonne Constat. Exclu du score.")
    row += 1
    section("Criticité (poids du contrôle dans le score)")
    for e in meta["criticite"]:
        put(ws, row, 1, e["poids"], bold=True, h="center")
        put(ws, row, 2, e["libelle"], bold=True)
        ws.merge_cells(start_row=row, start_column=3, end_row=row, end_column=4)
        put(ws, row, 3, e["definition"])
        row += 1
    section("Calcul des scores")
    para("Score d'un domaine = somme (maturité × criticité) ÷ somme (4 × criticité), sur les seuls contrôles évalués "
         "(cellules vides et N/A exclues). Les seuils de niveau (Critique, Fragile, Intermédiaire, Robuste) sont des "
         "paramètres modifiables dans la feuille Synthèse.")
    section("Exemple de ligne renseignée (format attendu)")
    example = [
        ("Contrôle", "A2.1 — délais maximaux de correction par criticité, mesurés et respectés"),
        ("Maturité", "2 (Défini : politique écrite, application non mesurée)"),
        ("Constat", "Politique : correctif critique sous 15 jours. Délais réels non mesurés. PHP2Shell corrigé en 9 jours sur 3 serveurs exposés."),
        ("Recommandation", "Fixer 72 h pour les failles critiques exposées sur Internet, mesurer le délai réel chaque mois, présenter l'indicateur en comité."),
        ("Priorité", "P1"),
    ]
    for k, v in example:
        put(ws, row, 1, k, bold=True)
        ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=4)
        put(ws, row, 2, v, bg=INPUT)
        fit(ws, row, [(v, 115)])
        row += 1
    section("Confidentialité")
    para("Une fois remplie, cette grille décrit les faiblesses du client : la classer en diffusion restreinte, la chiffrer "
         "au repos et ne jamais y copier de secret, de mot de passe ni de donnée personnelle.")


def sheet_mission(wb):
    ws = wb.create_sheet("Fiche mission")
    ws.sheet_view.showGridLines = False
    ws.column_dimensions["A"].width = 38
    ws.column_dimensions["B"].width = 80
    title_block(ws, "Fiche mission", "Contexte de l'audit. Toutes les cellules jaunes sont à renseigner.", 2)
    fields = [
        "Client (raison sociale)", "Entités et périmètre audités", "Secteur d'activité",
        "Réglementations applicables (NIS2, DORA, AI Act, RGPD, LPM…)", "Référence de la lettre de mission",
        "Référence des règles d'engagement signées", "Dates de l'audit", "Auditeurs (nom, rôle)",
        "Interlocuteurs côté client (nom, rôle)", "Agents d'IA de l'équipe d'audit utilisés (version, rôle)",
        "Environnements autorisés pour les tests techniques", "Version de la grille", "Classification du document",
    ]
    header(ws, 4, ["Champ", "Valeur"])
    for i, f in enumerate(fields, start=5):
        put(ws, i, 1, f, bold=True)
        put(ws, i, 2, "Diffusion restreinte" if f.startswith("Classification") else None, bg=INPUT)
        ws.row_dimensions[i].height = 22


def sheet_flash(wb, g, c):
    ws = wb.create_sheet("Diagnostic Flash")
    ws.sheet_view.showGridLines = False
    widths = [6, 9, 70, 14, 9, 40, 11, 30]
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w
    title_block(ws, "Diagnostic Flash — 20 questions pour un premier état des lieux",
                "Entretien d'environ 45 minutes avec un décideur (DSI, RSSI, direction). Score indicatif : il ne remplace pas "
                "l'audit, il en fixe les priorités.", 8,
                legend="Colonnes Réponse et Commentaire à renseigner. Chaque « Ne sait pas » est en soi un constat : un manque de visibilité.")
    header(ws, 4, ["N°", "Surface", "Question", "Réponse", "Points", "Commentaire", "Contrôle", "Cas d'école"])
    dv = list_validation(ws, [e["reponse"] for e in g["meta"]["reponses_flash"]], "Choisir Oui, Partiel, Non ou Ne sait pas.")
    row = 5
    for s, _, ctl in controls(g):
        if not ctl.get("flash"):
            continue
        cas = "\n".join(cas_label(t, c) for t in ctl.get("cas") or [])
        put(ws, row, 1, row - 4, h="center")
        put(ws, row, 2, s["id"], h="center")
        put(ws, row, 3, ctl["question_flash"])
        put(ws, row, 4, None, bg=INPUT, h="center")
        put(ws, row, 5, f'=IF(D{row}="Oui",2,IF(D{row}="Partiel",1,IF(OR(D{row}="Non",D{row}="Ne sait pas"),0,"")))', h="center")
        put(ws, row, 6, None, bg=INPUT)
        put(ws, row, 7, ctl["id"], h="center")
        put(ws, row, 8, cas, size=9, color=MUTED)
        dv.add(f"D{row}")
        fit(ws, row, [(ctl["question_flash"], widths[2]), (cas, widths[7])], minimum=2)
        row += 1
    last = row - 1
    row += 1
    summary = [
        ("Questions renseignées", f"=COUNTA(D5:D{last})", "0"),
        ("Score Flash global", f'=IFERROR(SUM(E5:E{last})/(2*COUNTA(D5:D{last})),"")', "0%"),
        ("Niveau", f'=IF(D{row + 1}="","Non évalué",IF(D{row + 1}<Synthèse!$M$5,"Critique",IF(D{row + 1}<Synthèse!$M$6,"Fragile",IF(D{row + 1}<Synthèse!$M$7,"Intermédiaire","Robuste"))))', None),
        ("Score Flash — surface A", f'=IFERROR(SUMIFS(E5:E{last},B5:B{last},"A")/(2*COUNTIFS(B5:B{last},"A",D5:D{last},"<>")),"")', "0%"),
        ("Score Flash — surface B", f'=IFERROR(SUMIFS(E5:E{last},B5:B{last},"B")/(2*COUNTIFS(B5:B{last},"B",D5:D{last},"<>")),"")', "0%"),
        ("Réponses « Ne sait pas »", f'=COUNTIF(D5:D{last},"Ne sait pas")', "0"),
    ]
    for label, formula, fmt in summary:
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=3)
        put(ws, row, 1, label, bold=True, h="right")
        put(ws, row, 4, formula, bold=True, h="center", fmt=fmt)
        row += 1
    level_cell = f"D{last + 4}"
    add_level_formatting(ws, level_cell, f"D{last + 3}")
    ws.freeze_panes = "A5"
    return last


def add_level_formatting(ws, label_range, score_ref):
    """Colore une plage de libellés de niveau (le texte du libellé reste la seule clé de lecture)."""
    first = label_range.split(":")[0]
    for level, tint in TINTS.items():
        ws.conditional_formatting.add(label_range, FormulaRule(
            formula=[f'{first}="{level}"'], fill=PatternFill("solid", start_color=tint, end_color=tint)))
    del score_ref  # le libellé suffit ; conservé pour lisibilité de l'appel


def sheet_surface(wb, s, r, c):
    ws = wb.create_sheet(f"Surface {s['id']}")
    ws.sheet_view.showGridLines = False
    for i, (_, w) in enumerate(COLS, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w
    last_col = len(COLS)
    title_block(ws, s["titre"], s["resume"], last_col,
                legend="Cellules jaunes à renseigner : Maturité (0-4 ou N/A), Constat, Recommandation, Priorité. "
                       "Score pondéré = maturité × criticité. Les colonnes de droite relient chaque contrôle aux référentiels.")
    header(ws, 4, [t for t, _ in COLS])
    dv_mat = list_validation(ws, ["0", "1", "2", "3", "4", "N/A"], "Saisir un niveau de 0 à 4, ou N/A.")
    dv_prio = list_validation(ws, ["P1", "P2", "P3"], "Choisir P1, P2 ou P3.")
    row = FIRST_ROW
    first_ctl = None
    for d in s["domaines"]:
        put(ws, row, C_ID, d["id"], bold=True, color=NAVY, bg=BAND)
        ws.merge_cells(start_row=row, start_column=C_DOM, end_row=row, end_column=last_col)
        put(ws, row, C_DOM, f"{d['titre']} — {d['objectif']}", bold=True, color=NAVY, bg=BAND, wrap=False)
        ws.row_dimensions[row].height = 20
        row += 1
        for ctl in d["controles"]:
            first_ctl = first_ctl or row
            put(ws, row, C_ID, ctl["id"], bold=True)
            put(ws, row, C_DOM, d["id"], h="center")
            put(ws, row, C_Q, ctl["question"])
            put(ws, row, C_PRE, ctl["preuves"])
            put(ws, row, C_MET, ctl["methode"], size=9)
            put(ws, row, C_CRIT, ctl["criticite"], h="center")
            put(ws, row, C_FLASH, "★" if ctl.get("flash") else "", h="center", color=SERIES)
            put(ws, row, C_MAT, None, bg=INPUT, h="center")
            put(ws, row, C_SC, f'=IF(ISNUMBER(H{row}),H{row}*F{row},"")', h="center")
            put(ws, row, C_MAX, f'=IF(ISNUMBER(H{row}),4*F{row},"")', h="center")
            put(ws, row, C_CONST, None, bg=INPUT)
            put(ws, row, C_RECO, None, bg=INPUT)
            put(ws, row, C_PRIO, None, bg=INPUT, h="center")
            texts = [(ctl["question"], COLS[C_Q - 1][1]), (ctl["preuves"], COLS[C_PRE - 1][1])]
            for k, (fam, _) in enumerate(FAMILLES):
                txt = ref_cell(ctl, fam, r)
                put(ws, row, C_REF0 + k, txt, size=9, color=MUTED)
                texts.append((txt, COLS[C_REF0 + k - 1][1] * 1.1))
            cas = "\n".join(cas_label(t, c) for t in ctl.get("cas") or [])
            put(ws, row, C_CAS, cas, size=9, color=MUTED)
            texts.append((cas, COLS[C_CAS - 1][1] * 1.1))
            dv_mat.add(f"H{row}")
            dv_prio.add(f"M{row}")
            fit(ws, row, texts, minimum=2)
            row += 1
    last = row - 1
    rng = f"H{first_ctl}:H{last}"
    rules = [(f"AND(ISNUMBER(H{first_ctl}),H{first_ctl}<=1)", TINTS["Critique"]),
             (f"AND(ISNUMBER(H{first_ctl}),H{first_ctl}=2)", TINTS["Intermédiaire"]),
             (f"AND(ISNUMBER(H{first_ctl}),H{first_ctl}>=3)", TINTS["Robuste"])]
    for formula, tint in rules:
        ws.conditional_formatting.add(rng, FormulaRule(formula=[formula], fill=PatternFill("solid", start_color=tint, end_color=tint)))
    ws.freeze_panes = f"{get_column_letter(C_Q)}{FIRST_ROW}"
    ws.auto_filter.ref = f"A4:{get_column_letter(last_col)}{last}"
    ws.print_title_rows = "4:4"
    print_setup(ws, "A3")
    return last


def sheet_synthese(wb, g):
    ws = wb.create_sheet("Synthèse")
    ws.sheet_view.showGridLines = False
    widths = [9, 9, 64, 11, 10, 7, 10, 15, 13, 10, 3, 30, 10]
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w
    title_block(ws, "Synthèse de l'état des lieux",
                "Calculée automatiquement depuis les feuilles Surface A et Surface B. Score = somme (maturité × criticité) "
                "÷ somme (4 × criticité) sur les contrôles évalués.", 13)
    header(ws, 4, ["Surface", "Domaine", "Intitulé", "Contrôles", "Évalués", "N/A", "Score", "Niveau",
                   "Critiques\nmaturité ≤ 1", "Actions P1"])
    # Paramètres (seuils) : cellules nommées par leur libellé, référencées par toutes les formules de niveau.
    put(ws, 4, 12, "Paramètres", bold=True, color=WHITE, bg=NAVY)
    put(ws, 4, 13, "Seuil", bold=True, color=WHITE, bg=NAVY, h="center")
    for i, seuil in enumerate(g["meta"]["seuils"][1:], start=5):
        put(ws, i, 12, f"Niveau « {seuil['libelle']} » à partir de")
        put(ws, i, 13, seuil["min"], bg=INPUT, h="center", fmt="0%")
    put(ws, 8, 12, "Sous le premier seuil : « Critique ».", italic=True, color=MUTED, border=False)

    def level(ref):
        return (f'=IF({ref}="","Non évalué",IF({ref}<$M$5,"Critique",IF({ref}<$M$6,"Fragile",'
                f'IF({ref}<$M$7,"Intermédiaire","Robuste"))))')

    row = 5
    for s in g["surfaces"]:
        sh = f"'Surface {s['id']}'"
        end = LAST_ROW_A if s["id"] == "A" else LAST_ROW_B
        B = f"{sh}!$B${FIRST_ROW}:$B${end}"
        F = f"{sh}!$F${FIRST_ROW}:$F${end}"
        H = f"{sh}!$H${FIRST_ROW}:$H${end}"
        I = f"{sh}!$I${FIRST_ROW}:$I${end}"
        J = f"{sh}!$J${FIRST_ROW}:$J${end}"
        M = f"{sh}!$M${FIRST_ROW}:$M${end}"
        for d in s["domaines"]:
            put(ws, row, 1, s["id"], h="center")
            put(ws, row, 2, d["id"], bold=True, h="center")
            put(ws, row, 3, f"{d['id']} · {d['titre']}")
            put(ws, row, 4, f'=COUNTIF({B},B{row})', h="center")
            put(ws, row, 5, f'=SUMPRODUCT(({B}=B{row})*ISNUMBER({H}))', h="center")
            put(ws, row, 6, f'=COUNTIFS({B},B{row},{H},"N/A")', h="center")
            put(ws, row, 7, f'=IFERROR(SUMIFS({I},{B},B{row})/SUMIFS({J},{B},B{row}),"")', h="center", fmt="0%")
            put(ws, row, 8, level(f"G{row}"), h="center")
            put(ws, row, 9, f'=SUMPRODUCT(({B}=B{row})*({F}=3)*ISNUMBER({H})*({H}<=1))', h="center")
            put(ws, row, 10, f'=COUNTIFS({B},B{row},{M},"P1")', h="center")
            ws.row_dimensions[row].height = 18
            row += 1
    last_dom = row - 1
    add_level_formatting(ws, f"H5:H{last_dom}", None)

    row += 1
    header_row = row
    for col, label in enumerate(["Surface", "", "Intitulé", "Contrôles", "Évalués", "N/A", "Score", "Niveau",
                                 "Critiques\nmaturité ≤ 1", "Actions P1"], start=1):
        put(ws, row, col, label, bold=True, color=WHITE, bg=NAVY, v="center")
    ws.row_dimensions[row].height = 30
    row += 1
    first_sum = row
    for s in g["surfaces"]:
        sh = f"'Surface {s['id']}'"
        end = LAST_ROW_A if s["id"] == "A" else LAST_ROW_B
        put(ws, row, 1, s["id"], bold=True, h="center")
        put(ws, row, 2, "")
        put(ws, row, 3, s["titre"])
        put(ws, row, 4, f'=SUMIFS($D$5:$D${last_dom},$A$5:$A${last_dom},A{row})', h="center")
        put(ws, row, 5, f'=SUMIFS($E$5:$E${last_dom},$A$5:$A${last_dom},A{row})', h="center")
        put(ws, row, 6, f'=SUMIFS($F$5:$F${last_dom},$A$5:$A${last_dom},A{row})', h="center")
        put(ws, row, 7, f'=IFERROR(SUM({sh}!$I${FIRST_ROW}:$I${end})/SUM({sh}!$J${FIRST_ROW}:$J${end}),"")', h="center", fmt="0%")
        put(ws, row, 8, level(f"G{row}"), h="center")
        put(ws, row, 9, f'=SUMIFS($I$5:$I${last_dom},$A$5:$A${last_dom},A{row})', h="center")
        put(ws, row, 10, f'=SUMIFS($J$5:$J${last_dom},$A$5:$A${last_dom},A{row})', h="center")
        ws.row_dimensions[row].height = 18
        row += 1
    put(ws, row, 1, "Global", bold=True, h="center")
    put(ws, row, 2, "")
    put(ws, row, 3, "Les deux surfaces", bold=True)
    for col, letter in ((4, "D"), (5, "E"), (6, "F"), (9, "I"), (10, "J")):
        put(ws, row, col, f"=SUM({letter}{first_sum}:{letter}{row - 1})", bold=True, h="center")
    put(ws, row, 7, "=IFERROR((SUM('Surface A'!$I$5:$I$%d)+SUM('Surface B'!$I$5:$I$%d))/(SUM('Surface A'!$J$5:$J$%d)+SUM('Surface B'!$J$5:$J$%d)),\"\")"
        % (LAST_ROW_A, LAST_ROW_B, LAST_ROW_A, LAST_ROW_B), bold=True, h="center", fmt="0%")
    put(ws, row, 8, level(f"G{row}"), bold=True, h="center")
    add_level_formatting(ws, f"H{first_sum}:H{row}", None)
    del header_row

    chart = BarChart()
    chart.type = "bar"
    chart.title = "Maturité par domaine (score pondéré)"
    chart.style = 2
    chart.legend = None
    chart.y_axis.scaling.min = 0
    chart.y_axis.scaling.max = 1
    chart.y_axis.majorUnit = 0.25
    chart.y_axis.number_format = "0%"
    chart.y_axis.title = None
    chart.x_axis.scaling.orientation = "maxMin"  # A1 en haut, dans l'ordre du tableau
    chart.x_axis.delete = False
    chart.y_axis.delete = False
    data = Reference(ws, min_col=7, min_row=4, max_row=last_dom)
    cats = Reference(ws, min_col=3, min_row=5, max_row=last_dom)
    chart.add_data(data, titles_from_data=True)
    chart.set_categories(cats)
    chart.gapWidth = 60
    series = chart.series[0]
    series.graphicalProperties.solidFill = SERIES
    series.graphicalProperties.line.solidFill = SERIES
    chart.width, chart.height = 22, 13
    ws.add_chart(chart, "L11")
    ws.freeze_panes = "A5"


def sheet_plan(wb):
    ws = wb.create_sheet("Plan d'action")
    ws.sheet_view.showGridLines = False
    labels = ["N°", "ID contrôle", "Point de contrôle", "Constat", "Recommandation", "Priorité",
              "Action détaillée", "Responsable", "Échéance", "Statut", "Preuve de clôture"]
    widths = [6, 11, 50, 36, 36, 9, 36, 18, 12, 14, 28]
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w
    title_block(ws, "Plan d'action", "Saisir l'ID d'un contrôle (liste déroulante) : point de contrôle, constat, "
                "recommandation et priorité sont repris automatiquement de la grille.", len(labels),
                legend="Cellules jaunes à renseigner. Échéance au format JJ/MM/AAAA.")
    header(ws, 4, labels)
    dv_id = DataValidation(type="list", formula1="=IDs_Controles", allow_blank=True, showErrorMessage=True,
                           errorTitle="ID inconnu", error="Choisir un ID de contrôle de la grille (ex. A2.1).")
    dv_status = list_validation(ws, ["À faire", "En cours", "Terminé", "Risque accepté"], "Choisir un statut de la liste.")
    ws.add_data_validation(dv_id)

    def lookup(col, row):
        a = f"INDEX('Surface A'!${col}${FIRST_ROW}:${col}${LAST_ROW_A},MATCH($B{row},'Surface A'!$A${FIRST_ROW}:$A${LAST_ROW_A},0))"
        b = f"INDEX('Surface B'!${col}${FIRST_ROW}:${col}${LAST_ROW_B},MATCH($B{row},'Surface B'!$A${FIRST_ROW}:$A${LAST_ROW_B},0))"
        return f'=IF($B{row}="","",IFERROR(T({a}),IFERROR(T({b}),"ID inconnu")))'

    for row in range(5, 55):
        put(ws, row, 1, row - 4, h="center")
        put(ws, row, 2, None, bg=INPUT, h="center")
        put(ws, row, 3, lookup("C", row), size=9)
        put(ws, row, 4, lookup("K", row), size=9)
        put(ws, row, 5, lookup("L", row), size=9)
        put(ws, row, 6, lookup("M", row), h="center")
        for col in (7, 8, 10, 11):
            put(ws, row, col, None, bg=INPUT)
        put(ws, row, 9, None, bg=INPUT, fmt="DD/MM/YYYY", h="center")
        dv_id.add(f"B{row}")
        dv_status.add(f"J{row}")
        ws.row_dimensions[row].height = 42
    ws.freeze_panes = "C5"


def sheet_cas(wb, g, c):
    ws = wb.create_sheet("Cas d'école")
    ws.sheet_view.showGridLines = False
    widths = [22, 34, 14, 70, 60, 12, 22]
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w
    title_block(ws, "Cas d'école cités dans la grille",
                "Incidents réels utilisés pour illustrer les contrôles, avec leurs sources. Voir aussi la timeline "
                "Black October et SOURCES.md.", 7)
    header(ws, 4, ["Code", "Cas", "Date", "Résumé", "Sources", "Vérification", "Contrôles liés"])
    _, cas_idx = used_by(g)
    row = 5
    for tag, e in c.items():
        if tag not in cas_idx:
            continue
        sources = "\n".join(f"{s.get('editeur', '')} — {s.get('titre', '')} ({s.get('date', '')}) : {s.get('url', '')}"
                            for s in e.get("sources") or [])
        statut = {"verifie": "Vérifié", "partiel": "Partiel"}.get(e.get("statut"), "À vérifier")
        values = [tag, e.get("titre") or e["court"], str(e.get("date", "")), e.get("resume", ""), sources, statut,
                  ", ".join(cas_idx[tag])]
        for col, v in enumerate(values, start=1):
            put(ws, row, col, v, size=9 if col in (5, 7) else 10, bold=(col == 1))
        fit(ws, row, [(values[3], widths[3]), (sources, widths[4] * 0.9), (values[1], widths[1])], minimum=2)
        row += 1
    ws.freeze_panes = "B5"


def sheet_refs(wb, g, r):
    ws = wb.create_sheet("Référentiels")
    ws.sheet_view.showGridLines = False
    widths = [20, 16, 90, 40]
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w
    title_block(ws, "Référentiels — libellés officiels et couverture",
                f"Relevés le {r['sources']['releve_le']} dans les publications d'origine (voir data/referentiels.yaml). "
                "Colonne « Contrôles » générée depuis data/grille.yaml.", 4)
    header(ws, 4, ["Référentiel", "ID", "Libellé officiel", "Contrôles de la grille"])
    refs_idx, _ = used_by(g)
    row = 5
    for fam, name in FAMILLES:
        src = r["sources"][fam]
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=4)
        put(ws, row, 1, f"{name} — {src['titre']} — {src['url']}", bold=True, color=NAVY, bg=BAND)
        ws.row_dimensions[row].height = 20
        row += 1
        for i, label in r[fam].items():
            label = label["nom"] if isinstance(label, dict) else label
            ctl = ", ".join(refs_idx.get((fam, i), [])) or "—"
            for col, v in enumerate([name, i, label, ctl], start=1):
                put(ws, row, col, v, size=9 if col == 4 else 10)
            fit(ws, row, [(label, widths[2]), (ctl, widths[3])])
            row += 1
    ws.freeze_panes = "A5"


def sheet_lists(wb, g):
    ws = wb.create_sheet("Listes")
    ids = [ctl["id"] for _, _, ctl in controls(g)]
    for i, cid in enumerate(ids, start=1):
        ws.cell(row=i, column=1, value=cid)
    wb.defined_names["IDs_Controles"] = DefinedName("IDs_Controles", attr_text=f"Listes!$A$1:$A${len(ids)}")
    ws.sheet_state = "hidden"


def build_xlsx(g, r, c, flash_count):
    wb = Workbook()
    sheet_guide(wb, g, flash_count)
    sheet_mission(wb)
    sheet_flash(wb, g, c)
    for s in g["surfaces"]:
        sheet_surface(wb, s, r, c)
    sheet_synthese(wb, g)
    sheet_plan(wb)
    sheet_cas(wb, g, c)
    sheet_refs(wb, g, r)
    sheet_lists(wb, g)
    for ws in wb.worksheets:
        if not ws.title.startswith("Surface") and ws.sheet_state == "visible":
            print_setup(ws)
    wb.properties.title = g["meta"]["titre"]
    wb.properties.creator = "red-team-ia/tools/build_grille.py"
    wb.save(XLSX)


# ---------------------------------------------------------------- Markdown
def pct(x):
    return f"{x * 100:.0f}\u00a0%"


def md_escape(text):
    return str(text).replace("|", "\\|").replace("\n", "<br>")


def build_md(g, r, c, flash_count):
    meta = g["meta"]
    refs_idx, cas_idx = used_by(g)
    n_ctl = sum(1 for _ in controls(g))
    out = [
        f"# {meta['titre']}",
        "",
        f"> Version {meta['version']} du {meta['date']} · {n_ctl} points de contrôle · {flash_count} questions Flash. "
        "Fichier généré par `tools/build_grille.py` depuis `data/grille.yaml` : modifier le YAML, pas ce fichier.",
        "",
        "Version de travail : **[03-grille-audit-etat-des-lieux.xlsx](03-grille-audit-etat-des-lieux.xlsx)**, avec saisie "
        "guidée, scores calculés, synthèse, graphique et plan d'action. Cette page sert à la lecture, à la revue et au diff.",
        "",
        "## Mode d'emploi",
        "",
        "1. **Diagnostic Flash** (avant-vente, environ 45 min) : 20 questions posées à un décideur, réponses Oui / Partiel / Non / Ne sait pas.",
        "2. **Audit** : pour chaque point de contrôle, collecter les preuves attendues puis noter la maturité de 0 à 4 (ou N/A).",
        "3. **Score d'un domaine** = somme (maturité × criticité) ÷ somme (4 × criticité), sur les contrôles évalués.",
        "",
        "| Maturité | Libellé | Définition |",
        "|---|---|---|",
    ]
    out += [f"| {e['niveau']} | {e['libelle']} | {e['definition']} |" for e in meta["echelle_maturite"]]
    out += ["", "| Criticité | Libellé | Définition |", "|---|---|---|"]
    out += [f"| {e['poids']} | {e['libelle']} | {e['definition']} |" for e in meta["criticite"]]
    seuils = meta["seuils"]
    out += ["", "Niveaux : " + " · ".join(
        f"**{s['libelle']}** {'< ' + pct(seuils[i + 1]['min']) if i + 1 < len(seuils) else '≥ ' + pct(s['min'])}"
        for i, s in enumerate(seuils)) + ".", ""]

    out += ["## Diagnostic Flash", "", "| N° | Surface | Question | Contrôle |", "|---|---|---|---|"]
    n = 0
    for s, _, ctl in controls(g):
        if ctl.get("flash"):
            n += 1
            out.append(f"| {n} | {s['id']} | {md_escape(ctl['question_flash'])} | [{ctl['id']}](#{ctl['id'].replace('.', '').lower()}) |")
    out.append("")

    short = {"nist_ai_rmf": "AI RMF", "nist_csf": "CSF", "owasp_llm": "OWASP", "owasp_asi": "OWASP", "atlas": "ATLAS"}
    for s in g["surfaces"]:
        out += [f"## {s['titre']}", "", s["resume"], ""]
        for d in s["domaines"]:
            out += [f"### {d['id']} · {d['titre']}", "", f"*{d['objectif']}*", "",
                    "| ID | Point de contrôle | Preuves attendues · méthode | Crit. | Référentiels | Cas d'école |",
                    "|---|---|---|---|---|---|"]
            for ctl in d["controles"]:
                refs = ctl.get("refs") or {}
                parts = []
                for fam in ("nist_ai_rmf", "nist_csf"):
                    if refs.get(fam):
                        parts.append(f"{short[fam]} : " + ", ".join(refs[fam]))
                owasp = refs.get("owasp_llm", []) + refs.get("owasp_asi", [])
                if owasp:
                    parts.append("OWASP : " + ", ".join(owasp))
                if refs.get("atlas"):
                    parts.append("ATLAS : " + ", ".join(refs["atlas"]))
                cas = ", ".join(cas_label(t, c) for t in ctl.get("cas") or []) or "—"
                star = " ★" if ctl.get("flash") else ""
                anchor = f'<a id="{ctl["id"].replace(".", "").lower()}"></a>'
                out.append(f"| {anchor}**{ctl['id']}**{star} | {md_escape(ctl['question'])} | {md_escape(ctl['preuves'])}"
                           f"<br>*{md_escape(ctl['methode'])}* | {ctl['criticite']} | {md_escape('<br>'.join(parts))} | {md_escape(cas)} |")
            out.append("")

    out += ["## Couverture des référentiels OWASP", "",
            "Chaque risque des deux Top 10 OWASP est couvert par au moins un point de contrôle.", "",
            "| ID | Risque (libellé officiel) | Contrôles |", "|---|---|---|"]
    for fam in ("owasp_llm", "owasp_asi"):
        for i, label in r[fam].items():
            out.append(f"| {i} | {label} | {', '.join(refs_idx.get((fam, i), [])) or '—'} |")
    out += ["", "Libellés NIST AI RMF, NIST CSF 2.0 et MITRE ATLAS : feuille « Référentiels » du classeur et "
            "[`data/referentiels.yaml`](data/referentiels.yaml).", ""]

    out += ["## Cas d'école", "", "| Code | Cas | Contrôles | Vérification |", "|---|---|---|---|"]
    for tag, e in c.items():
        if tag in cas_idx:
            statut = {"verifie": "Vérifié", "partiel": "Partiel"}.get(e.get("statut"), "À vérifier")
            out.append(f"| {tag} | {md_escape(e.get('titre') or e['court'])} | {', '.join(cas_idx[tag])} | {statut} |")
    out += ["", "Sources détaillées : feuille « Cas d'école » du classeur, [`SOURCES.md`](SOURCES.md) et "
            "[timeline Black October](02-timeline-black-october.md).", "",
            "★ = question reprise dans le Diagnostic Flash.", ""]
    MD.write_text("\n".join(out), encoding="utf-8")


def main():
    g, r, c = load()
    flash_count = validate(g, r, c)
    build_xlsx(g, r, c, flash_count)
    build_md(g, r, c, flash_count)
    n = sum(1 for _ in controls(g))
    print(f"OK : {n} contrôles, {flash_count} questions Flash -> {XLSX.name}, {MD.name}")


if __name__ == "__main__":
    main()
