# V01 EN — images fixes à rendre et regarder

Liste calculée sur la vraie voix : 18 885 images, 30 i/s. Aucun PNG du montage n’a été rendu ou inspecté dans cette session. Les planches HTML sont des contrôles structurels, pas des preuves visuelles.

## Vidéo longue : 37 vues

| Vue | Image | Temps vidéo |
|---|---:|---:|
| p1_debut | 30 | 00:01.000 |
| p1_milieu | 616 | 00:20.533 |
| p1_fin | 1197 | 00:39.900 |
| p2_debut | 1262 | 00:42.067 |
| p2_milieu | 2988 | 01:39.600 |
| p2_fin | 4708 | 02:36.933 |
| p3_debut | 4773 | 02:39.100 |
| p3_milieu | 6679 | 03:42.633 |
| p3_fin | 8580 | 04:46.000 |
| p4_debut | 8645 | 04:48.167 |
| p4_milieu | 11630 | 06:27.667 |
| p4_fin | 14609 | 08:06.967 |
| p5_debut | 14674 | 08:09.133 |
| p5_milieu | 16765 | 09:18.833 |
| p5_fin | 18850 | 10:28.333 |
| consigne | 1701 | 00:56.700 |
| ecrans | 6886 | 03:49.533 |
| pascal | 7417 | 04:07.233 |
| solitude | 7694 | 04:16.467 |
| khalwa | 10757 | 05:58.567 |
| carte | 11278 | 06:15.933 |
| ghazali | 11613 | 06:27.100 |
| dhikr | 13119 | 07:17.300 |
| verset | 13739 | 07:37.967 |
| fondements | 14199 | 07:53.300 |
| point | 16157 | 08:58.567 |
| retour | 16564 | 09:12.133 |
| revelation | 18063 | 10:02.100 |
| verset_fondu_entree | 13659 | 07:35.300 |
| verset_fondu_sortie | 13819 | 07:40.633 |
| verset_avant | 13651 | 07:35.033 |
| verset_apres | 13826 | 07:40.867 |
| traduction_parlee | 13508 | 07:30.267 |
| pause_question | 5643 | 03:08.100 |
| chuchotements | 16410 | 09:07.000 |
| fin_voix | 18685 | 10:22.833 |
| ecran_final | 18795 | 10:26.500 |

## Commandes pour Claude

```bash
node tools/bundle_local.mjs out/bundle-en-voix
export CHROME='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
export BUNDLE=out/bundle-en-voix
node tools/stills.mjs out/validation/en-png --composition V01-EN p1_debut:30 p1_milieu:616 p1_fin:1197 p2_debut:1262 p2_milieu:2988 p2_fin:4708 p3_debut:4773 p3_milieu:6679 p3_fin:8580 p4_debut:8645 p4_milieu:11630 p4_fin:14609 p5_debut:14674 p5_milieu:16765 p5_fin:18850 consigne:1701 ecrans:6886 pascal:7417 solitude:7694 khalwa:10757 carte:11278 ghazali:11613 dhikr:13119 verset:13739 fondements:14199 point:16157 retour:16564 revelation:18063 verset_fondu_entree:13659 verset_fondu_sortie:13819 verset_avant:13651 verset_apres:13826 traduction_parlee:13508 pause_question:5643 chuchotements:16410 fin_voix:18685 ecran_final:18795
node tools/stills.mjs out/validation/short-bouton-en-png --composition short-bouton-en debut:60 milieu:1564 fin:3098
node tools/stills.mjs out/validation/short-pascal-en-png --composition short-pascal-en debut:60 milieu:1017 fin:2003
node tools/stills.mjs out/validation/short-exercice-en-png --composition short-exercice-en debut:60 milieu:1412 fin:2794
```

Contrôler début/milieu/fin des cinq parties, la lisibilité des documents et de la traduction Pickthall, les marges des trois Shorts, les transitions du verset, les deux chuchotements et la révélation finale. Les 835 comparaisons FR sans différence portent sur HTML/styles : comparer aussi les PNG FR avant/après si une validation visuelle du maintien est nécessaire.

Le montage anglais garde ses cartons 3D et ses emplacements face caméra tant que les images/rushes ne sont pas branchés. Ne pas considérer ces images fixes comme un master prêt à publier. Après une modification audio, relancer `node tools/check_v01_en.mjs` et régénérer cette liste.
