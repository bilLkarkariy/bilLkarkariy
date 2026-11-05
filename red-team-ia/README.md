# Red Team IA

Les fondations d'une offre d'audit et de red teaming centrée sur les agents d'IA, construite après la vague d'incidents d'octobre 2026 (« Black October »). Tous les faits cités ont été vérifiés le 5 novembre 2026.

| Livrable | Usage | Fichiers |
|---|---|---|
| **1. Document de cadrage de l'offre** | Périmètre des deux surfaces, quatre formules, méthodologie en sept phases, architecture de la team d'agents et de ses garde-fous, correspondance NIST, OWASP et MITRE ATLAS, cadre juridique, feuille de route | [01-cadrage-offre-red-team-ia.md](01-cadrage-offre-red-team-ia.md) |
| **2. Timeline Black October** | Une page A4 sourcée pour le pitch commercial | [PDF](02-timeline-black-october.pdf) · [Markdown](02-timeline-black-october.md) · [page HTML](02-timeline-black-october.html) |
| **3. Grille d'audit « état des lieux »** | 86 points de contrôle sur les deux surfaces, Diagnostic Flash de 20 questions, scores automatiques, synthèse, plan d'action | [Excel](03-grille-audit-etat-des-lieux.xlsx) · [Markdown](03-grille-audit-etat-des-lieux.md) |
| Vérification des faits | Verdict et sources pour chaque affirmation de la recherche initiale ; formulations à éviter dans un pitch | [SOURCES.md](SOURCES.md) |

## Organisation

```
red-team-ia/
├── data/
│   ├── grille.yaml          # source unique des points de contrôle (lisible par les futurs agents)
│   ├── referentiels.yaml    # libellés officiels NIST AI RMF, NIST CSF 2.0, OWASP, MITRE ATLAS v2026.10
│   └── cas.yaml             # cas d'école sourcés reliés aux contrôles
└── tools/
    ├── build_grille.py      # génère l'Excel et le Markdown de la grille
    └── render_timeline.mjs  # génère le PDF A4 de la timeline
```

## Régénérer les fichiers

Grille (Python 3 avec PyYAML et openpyxl) :

```bash
python3 red-team-ia/tools/build_grille.py
```

Le script vérifie que chaque référence et chaque cas cité existe, puis écrit les deux fichiers. Pour modifier la grille, éditer `data/grille.yaml` et relancer : l'Excel et le Markdown ne se modifient pas à la main.

Timeline (Node.js avec Playwright et un accès à Google Fonts) :

```bash
node red-team-ia/tools/render_timeline.mjs
```

## Points d'attention

- **Dépôt public.** Ce dossier ne contient que de la méthodologie. Une grille remplie chez un client décrit ses faiblesses : elle ne doit jamais être déposée ici.
- **Faits datés.** La timeline et le cadrage reflètent l'état des sources au 5 novembre 2026. Revérifier avant toute diffusion ultérieure ; les chiffres présentés comme estimations doivent le rester.
- **Prochaine étape.** Le fichier `data/grille.yaml` est prévu pour être chargé par l'agent Gouvernance et conformité décrit dans le cadrage (section 6), première brique de la team d'agents.
