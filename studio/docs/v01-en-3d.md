# V01 EN — préparation 3D sur la voix réelle

Aucun calcul Blender lancé. Images vidéo à 30 i/s, bornes inclusives dans le tableau ; images Blender locales numérotées depuis 1. Estimation indicative : 7 s par image calculée, hors initialisation.

| Plan | Images vidéo EN | Images locales | Pas | PNG à calculer | Temps GPU | Décalage début / fin depuis estimation EN |
|---|---:|---:|---:|---:|---:|---:|
| maquette | 98–231 | 1–134 | 2 | 67 | 7.8 min | +1 / -5 |
| seuls | 2340–2516 | 1–177 | 2 | 89 | 10.4 min | -259 / -283 |
| bouton | 4313–4439 | 1–127 | 2 | 64 | 7.5 min | -424 / -418 |
| salon | 3758–3835 | 1–78 | 2 | 39 | 4.5 min | -381 / -369 |
| vide | 8615–9118 | 1–504 | 2 | 252 | 29.4 min | -864 / -904 |
| khalwa | 10581–10950 | 1–370 | 2 | 185 | 21.6 min | -1077 / -1101 |
| dhikr | 13083–13408 | 1–326 | 2 | 163 | 19.0 min | -1269 / -1335 |
| meublee | 18436–18554 | 1–119 | 3 | 40 | 4.7 min | -1398 / -1400 |

## Repères déplacés (FR → EN, images locales)

- **maquette** (81 PNG FR présents) : ['p1', 'Seul']: 4 → 4; ['p1', 'téléphone']: 76 → 70; ['p1', 'lire']: 114 → 116.
- **seuls** (74 PNG FR présents) : ['p10', 'bouton']: 66 → 62; ['p10', 'remettre']: 104 → 124; ['p10', 'seuls']: 33 → 30.
- **bouton** (42 PNG FR présents) : ['p18', 'bouton', 'end']: 67 → 80.
- **salon** (41 PNG FR présents) : ['p16', 'Un']: 85 → 81; ['p16', 'canapé']: 50 → 42; ['p16', 'chez']: 4 → 4.
- **vide** (515 PNG FR présents) : ['p35', 'chaise']: 91 → 80; ['p35', 'cherches']: 307 → 307; ['p35', 'entres']: 146 → 139; ['p35', 'murs']: 249 → 241; ['p35', 'porte']: 324 → 324; ['p35', 'quoi']: 177 → 167; ['p35', 'table']: 120 → 106; ['p35', 'touches']: 240 → 228; ['p35', 'tournes']: 206 → 198; ['p36', 'pièce']: 418 → 412; ['p36', 'téléphone']: 448 → 445.
- **khalwa** (332 PNG FR présents) : ['p44', 'Exactement']: 219 → 223; ['p44', 'quarante']: 122 → 118; ['p44', 'retire']: 47 → 48; ['p44', 'volontairement']: 59 → 69.
- **dhikr** (312 PNG FR présents) : ['p51', "L'idée"]: 7 → 7; ['p51', 'fixe']: 114 → 119; ['p51', 'meuble']: 58 → 62; ['p51', 'part']: 156 → 168; ['p51', 'ramènes']: 193 → 196; ['p51', 'ramènes', 'start', 1]: 272 → 280; ['p51', 'repart']: 233 → 244.
- **meublee** (43 PNG FR présents) : ['p67', 'meublé']: 11 → 11.

## Réemploi proposé

La maquette initiale est une caméra sans action liée à un mot : réutiliser les images FR et atteindre l’image de vue verticale 138 au nouveau repère de fin. Les annotations téléphone/lecture sont déjà recalées par Remotion. Aucun recalcul nécessaire pour ce plan.
Pour les sept autres plans, une correspondance linéaire par morceaux entre les repères locaux du tableau peut réutiliser les PNG FR : fermer la porte, faire tomber le pion ou poser le point d’or exactement sur les mots EN. Vérifier la monotonie de chaque correspondance, la continuité des vitesses et les fondus. Un étirement global unique ne garantit pas ces actions. Les plans très ralentis risquent une cadence visible ; les changements de vitesse doivent être lissés entre les actions.
Aucun réemploi ni nouveau rendu n’est branché automatiquement : les cartons 3D EN restent actifs jusqu’à inspection des aperçus. Le plan dhikr conserve ensuite son dernier état pendant la traduction parlée, avant le verset silencieux.
Option recalcul intégral des sept plans animés : environ 97.1 min (1.62 h) à 7 s/image. Le rendu GPU réel peut différer.

## Décision : aucune 3D anglaise calculée

Billel refuse tout nouveau rendu 3D pour la version anglaise. Les images FR sont réutilisées et recalées :
`python3 tools/report_3d_en.py` puis `python3 tools/remap3d_en.py` écrivent `src/data/remap3d_en.json`
(repères [image EN, image FR] de chaque plan), lu par `Shot3D` en anglais. Lecture linéaire entre deux repères,
vitesse normale avant le premier et après le dernier, dernière image tenue. Les plans rendus image par image
(vide, khalwa, dhikr) prennent l'image la plus proche, sans fondu, pour ne pas dédoubler le pion.
La maquette suit déjà les repères EN dans `src/scenes/Maquette.tsx`.
