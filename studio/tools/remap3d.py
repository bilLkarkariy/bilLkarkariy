"""Versions étrangères : aucune 3D recalculée. Chaque plan réutilise les images françaises, recalées dans le temps.

  python3 tools/remap3d.py --lang ar        (ou en, ur… : toute langue qui a ses fichiers v01_<langue>)

Entrées, toutes dans le dépôt :
  src/data/v01.vo.json et src/data/v01_<langue>.vo.json   les deux alignements (FR, et la langue) ;
  src/data/v01_<langue>.groups.json / .anchors.json       paragraphes et repères (clé = le mot français) ;
  tools/plans3d.py                                         les mots qui pilotent chaque plan (fermer la porte…) ;
  src/data/renders3d.json                                  les images FR réellement rendues.
Sortie : src/data/remap3d_<langue>.json, {plan: [[image langue, image FR], ...]}, lu par Shot3D
(src/components/Light.tsx). Un fichier vide ({}) garde les cartons « plan 3D en cours ».

Entre deux repères, la lecture est linéaire. Avant le premier et après le dernier, elle reste à vitesse normale :
on tient la première image si le mot arrive plus tard, on tient la dernière une fois le plan FR fini.

Ne recalcule rien, ne lit pas public/. Refuse un alignement estimé (vo_estime.py) : le recalage se fait sur la
vraie voix, sur le Mac (--provisoire pour essayer quand même, sans le commiter).
Anglais : mêmes repères 3D en plus que tools/report_3d_en.py ; résultat identique à tools/remap3d_en.py.
"""
import argparse
import ast
import json
import math
import os
import re
import sys
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEAD = 24
FPS = 30


def load(rel):
    return json.load(open(os.path.join(ROOT, rel), encoding="utf-8"))


def norm(s):
    """Même normalisation que src/cues.ts (latin : accents et signes tombent ; arabe : harakat, hamza et tatweel
    tombent, ٱ ة ى deviennent ا ه ي)."""
    s = unicodedata.normalize("NFD", s)
    s = re.sub("[̀-ًͯ-ٰٟـ]", "", s).lower()
    s = s.replace("ٱ", "ا").replace("ة", "ه").replace("ى", "ي")
    return re.sub("[^a-z0-9ء-غف-ي]", "", s)


def cues(lang):
    """at(paragraphe, mot français, bord, n) en image vidéo, comme createCues(lang) dans src/cues.ts."""
    vo = load("src/data/v01.vo.json" if lang == "fr" else f"src/data/v01_{lang}.vo.json")
    segments = {s["id"]: s for s in vo["segments"]}
    groups = {} if lang == "fr" else load(f"src/data/v01_{lang}.groups.json")
    anchors = {} if lang == "fr" else load(f"src/data/v01_{lang}.anchors.json")
    if lang == "en":  # les repères anglais réservés à la 3D sont dans tools/report_3d_en.py
        sys.path.insert(0, os.path.join(ROOT, "tools"))
        from report_3d_en import EXTRA

        for pid, items in EXTRA.items():
            anchors.setdefault(pid, {}).update(items)

    def at(pid, w=None, edge="start", nth=0):
        parts = [segments[pid]] if pid in segments else [segments[s] for s in groups[pid]]
        if w is None:
            t = parts[0]["start"] if edge == "start" else parts[-1]["end"]
        else:
            words = [x for s in parts for x in s["words"]]
            if lang == "fr":
                phrase, occurrence = w, nth
            else:
                target = anchors[pid][f"{w}|{nth}"]
                phrase = target if isinstance(target, str) else target["phrase"]
                occurrence = 0 if isinstance(target, str) else target["nth"]
            ns = [norm(t) for t in phrase.split()]
            hits = [i for i in range(len(words)) if [norm(x["w"]) for x in words[i:i + len(ns)]] == ns]
            if len(hits) <= occurrence:
                sys.exit(f"Repère {lang.upper()} introuvable : {pid} « {w} » #{nth}")
            i = hits[occurrence]
            t = words[i if edge == "start" else i + len(ns) - 1][edge]
        return LEAD + math.floor(t * FPS + 0.5)

    return at, vo


def specs(at, lang='fr'):
    # Mêmes bornes que les séquences Remotion et tools/plans3d.py (début, fin exclue, pas).
    return {
        "maquette": (at("p1", "Seul") - 3, at("p2") - 10, 2),
        "seuls": (at("p10") - 4, at("p11") - 4 + 2, 2),
        "bouton": (at("p18") - 4, at("p19") - 1 + 2, 2),
        "salon": (at("p16", "chez") - 3, at("p16", "Un") - 4 + 2, 2),
        "vide": (at("p35") - 4, at("p36", None, "end") + 24, 2),
        "khalwa": (at("p44") - 6, at("p44", None, "end") + 24, 2),
        "dhikr": (at("p51", "L'idée") - 6, at("p52") - 10 if lang == 'ar' else at("p51", None, "end") + 30, 2),
        "meublee": (at("p67", "meublé") - 10, at("p68") + 30, 3),
    }


def word_calls():
    """Pour chaque plan, les appels at(p, mot…) / F(p, mot…) de tools/plans3d.py : les actions posées sur un mot."""
    tree = ast.parse(open(os.path.join(ROOT, "tools/plans3d.py"), encoding="utf-8").read())
    out = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.If) or not isinstance(node.test, ast.Compare):
            continue
        if not isinstance(node.test.left, ast.Name) or node.test.left.id != "SHOT":
            continue
        shot = ast.literal_eval(node.test.comparators[0])
        calls = set()
        for statement in node.body:
            for call in ast.walk(statement):
                if isinstance(call, ast.Call) and isinstance(call.func, ast.Name) and call.func.id in ("at", "F"):
                    try:
                        args = tuple(ast.literal_eval(a) for a in call.args)
                    except ValueError:
                        continue
                    if len(args) > 1 and args[1] is not None:
                        calls.add(args)
        out[shot] = sorted(calls, key=str)
    out["maquette"] = [("p1", "Seul"), ("p1", "téléphone"), ("p1", "lire")]
    return out


def knots_for(pairs, n_lang, n_fr):
    knots = []
    for e, f in sorted(pairs):  # une correspondance strictement croissante, sinon l'image reculerait
        if not knots or (e > knots[-1][0] and f > knots[-1][1]):
            knots.append([e, f])
    if not knots:
        knots = [[1, 1]]
    e1, f1 = knots[0]
    head = [[1, f1 - (e1 - 1)]] if f1 - (e1 - 1) >= 1 else [[1, 1], [e1 - f1 + 1, 1]]
    ek, fk = knots[-1]
    tail = [[ek + (n_fr - fk), n_fr], [n_lang, n_fr]] if ek + (n_fr - fk) <= n_lang else [[n_lang, fk + (n_lang - ek)]]
    clean = []
    for e, f in head + knots + tail:
        if clean and e <= clean[-1][0]:
            continue
        clean.append([e, f])
    return clean


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--lang", required=True, help="code de la langue : en, ar, ur…")
    ap.add_argument("--provisoire", action="store_true", help="accepte un alignement estimé (essai, ne pas commiter)")
    ap.add_argument("--out", help="fichier de sortie (défaut : src/data/remap3d_<langue>.json)")
    a = ap.parse_args()
    if a.lang == "fr":
        sys.exit("Le français est la référence : rien à recaler.")
    lang_at, vo = cues(a.lang)
    if vo.get("estimated") and not a.provisoire:
        sys.exit(f"src/data/v01_{a.lang}.vo.json est un alignement estimé : recaler sur la vraie voix "
                 f"(tools/vo.py align …), ou relancer avec --provisoire pour un essai.")
    fr_at, _ = cues("fr")
    done = load("src/data/renders3d.json")
    calls = word_calls()
    lang_specs, fr_specs = specs(lang_at, a.lang), specs(fr_at)
    out = {}
    for shot, (a0, b0, _step) in lang_specs.items():
        if shot not in done:  # la maquette suit déjà les repères de la langue (src/scenes/Maquette.tsx)
            continue
        fa = fr_specs[shot][0]
        n_lang, n_fr = b0 - a0, done[shot]["frames"]
        pairs = []
        for args in calls[shot]:
            e, f = lang_at(*args) - a0 + 1, fr_at(*args) - fa + 1
            if 1 <= e <= n_lang and 1 <= f <= n_fr:
                pairs.append((e, f))
        out[shot] = knots_for(pairs, n_lang, n_fr)
        print(f"{shot:8s} {a.lang.upper()} {n_lang:4d} images ← FR {n_fr:4d} : {out[shot]}")
    dest = a.out or os.path.join(ROOT, f"src/data/remap3d_{a.lang}.json")
    json.dump(out, open(dest, "w"), indent=1)
    print(f"→ {os.path.relpath(dest, ROOT)}")


if __name__ == "__main__":
    main()
