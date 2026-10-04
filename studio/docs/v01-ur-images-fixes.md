# V01 UR — images fixes sur le vrai alignement

Calculées sur `src/data/v01_ur.vo.json`, voix réelle `vo/v01_ur.wav` : **21072 images**, 30 i/s, **11:42.400**. Vidéo = voix + 0,8 s. Les trois Shorts suivent automatiquement le même alignement.

Le contrôle HTML/styles et audio simulé est décrit dans `docs/v01-ur-etat.md`. Les PNG et le rendu complet restent à inspecter sur le Mac ; les tableaux ci-dessous sont une liste de rendu, pas une preuve d’inspection. La police `public/fonts/NotoNastaliqUrdu-Regular.ttf` est présente.

## Vidéo longue

| Vue | Image | Temps vidéo |
|---|---:|---:|
| p1_debut | 30 | 00:01.000 |
| p1_milieu | 754 | 00:25.133 |
| p1_fin | 1473 | 00:49.100 |
| p2_debut | 1538 | 00:51.267 |
| consigne | 2020 | 01:07.333 |
| p2_milieu | 3514 | 01:57.133 |
| p2_fin | 5485 | 03:02.833 |
| p3_debut | 5550 | 03:05.000 |
| pause_question | 6508 | 03:36.933 |
| p3_milieu | 7719 | 04:17.300 |
| ecrans | 7939 | 04:24.633 |
| pascal | 8561 | 04:45.367 |
| solitude | 8832 | 04:54.400 |
| p3_fin | 9882 | 05:29.400 |
| p4_debut | 9947 | 05:31.567 |
| khalwa | 12422 | 06:54.067 |
| carte | 12982 | 07:12.733 |
| p4_milieu | 13250 | 07:21.667 |
| ghazali | 13369 | 07:25.633 |
| carte_route | 13660 | 07:35.333 |
| dhikr | 15120 | 08:24.000 |
| verset_avant | 15429 | 08:34.300 |
| verset_fondu_entree | 15437 | 08:34.567 |
| traduction_parlee | 15531 | 08:37.700 |
| verset | 15541 | 08:38.033 |
| verset_fondu_sortie | 15645 | 08:41.500 |
| verset_apres | 15652 | 08:41.733 |
| fondements | 16094 | 08:56.467 |
| p4_fin | 16547 | 09:11.567 |
| p5_debut | 16612 | 09:13.733 |
| point | 18145 | 10:04.833 |
| chuchotements | 18406 | 10:13.533 |
| retour | 18562 | 10:18.733 |
| p5_milieu | 18827 | 10:27.567 |
| revelation | 20083 | 11:09.433 |
| fin_voix | 20872 | 11:35.733 |
| ecran_final | 20982 | 11:39.400 |
| p5_fin | 21037 | 11:41.233 |

## Pages sans face caméra

| Vue | Image | Temps vidéo |
|---|---:|---:|
| sans_face_2 | 898 | 00:29.933 |
| sans_face_3 | 3687 | 02:02.900 |
| sans_face_4 | 6507 | 03:36.900 |
| sans_face_5a | 9585 | 05:19.500 |
| sans_face_5b | 9763 | 05:25.433 |
| sans_face_8a | 20375 | 11:19.167 |
| sans_face_8b | 20540 | 11:24.667 |
| sans_face_9 | 20857 | 11:35.233 |

## Shorts

| Short | Durée (images) | Vues |
|---|---:|---|
| short-bouton-ur | 3617 | debut:60 milieu:1809 fin:3587 |
| short-pascal-ur | 2316 | debut:60 milieu:1158 fin:2286 |
| short-exercice-ur | 2864 | debut:60 milieu:1432 fin:2834 |

## Commandes pour Claude

Réemploi des images 3D françaises avec `WITH3D=1`, aucun Blender. `FACELESS=1` est requis pour toutes les vues ourdoues.

```bash
node tools/bundle_local.mjs out/bundle-ur
export CHROME='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
export BUNDLE=out/bundle-ur
FACELESS=1 WITH3D=1 node tools/stills.mjs out/validation/ur-png --composition V01-UR p1_debut:30 p1_milieu:754 p1_fin:1473 p2_debut:1538 consigne:2020 p2_milieu:3514 p2_fin:5485 p3_debut:5550 pause_question:6508 p3_milieu:7719 ecrans:7939 pascal:8561 solitude:8832 p3_fin:9882 p4_debut:9947 khalwa:12422 carte:12982 p4_milieu:13250 ghazali:13369 carte_route:13660 dhikr:15120 verset_avant:15429 verset_fondu_entree:15437 traduction_parlee:15531 verset:15541 verset_fondu_sortie:15645 verset_apres:15652 fondements:16094 p4_fin:16547 p5_debut:16612 point:18145 chuchotements:18406 retour:18562 p5_milieu:18827 revelation:20083 fin_voix:20872 ecran_final:20982 p5_fin:21037
FACELESS=1 WITH3D=1 node tools/stills.mjs out/validation/ur-sans-face-png --composition V01-UR sans_face_2:898 sans_face_3:3687 sans_face_4:6507 sans_face_5a:9585 sans_face_5b:9763 sans_face_8a:20375 sans_face_8b:20540 sans_face_9:20857
FACELESS=1 WITH3D=1 node tools/stills.mjs out/validation/short-bouton-ur-png --composition short-bouton-ur debut:60 milieu:1809 fin:3587
FACELESS=1 WITH3D=1 node tools/stills.mjs out/validation/short-pascal-ur-png --composition short-pascal-ur debut:60 milieu:1158 fin:2286
FACELESS=1 WITH3D=1 node tools/stills.mjs out/validation/short-exercice-ur-png --composition short-exercice-ur debut:60 milieu:1432 fin:2834
```

## Contrôles visuels et sonores

- Nastaliq : hampes et points visibles, aucun débordement coupé dans les fiches, les étapes de l’exercice et les Shorts ; lecture de droite à gauche et nombres de gauche à droite.
- Verset : texte uthmani en Amiri Quran, traduction ourdoue dessous, immobile entre les fondus. La voix continue ; musique et bruitages se taisent.
- Plans 3D : vérifier chaque raccord de vitesse et la continuité des images françaises remappées, surtout khalwa, dhikr et pièce vide.
- Pages sans face caméra : aucun visage ; la veste et l’invitation attendent les inserts de finition.
- Les repères précis des inserts, de l’intro Pixar et des chuchotements figurent dans `v01-ur-finition.md`.
- Comparaison FR/EN : le contrôle `--baseline out/validation/ur-baseline/src` compare HTML, styles et audio simulé. Il ne remplace pas une comparaison de PNG ni une écoute.
