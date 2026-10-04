# V01 AR — images fixes sur le vrai alignement

Liste recalculée sur `src/data/v01_ar.vo.json` et `vo/v01_ar.wav` : **20503 images**, 30 i/s, **11:23.433**. Vidéo = voix + 0,8 s.

Le contrôle HTML/styles et audio simulé est décrit dans `v01-ar-etat.md`. Les PNG et le rendu complet restent à inspecter ; cette liste ne constitue pas une preuve d’inspection visuelle.

## Vidéo longue : 75 vues (+ 11 sans visage)

| Vue | Image | Temps vidéo |
|---|---:|---:|
| p1_debut | 30 | 00:01.000 |
| p1_milieu | 792 | 00:26.400 |
| p1_fin | 1548 | 00:51.600 |
| p2_debut | 1613 | 00:53.767 |
| p2_milieu | 3601 | 02:00.033 |
| p2_fin | 5584 | 03:06.133 |
| p3_debut | 5649 | 03:08.300 |
| p3_milieu | 7835 | 04:21.167 |
| p3_fin | 10015 | 05:33.833 |
| p4_debut | 10080 | 05:36.000 |
| p4_milieu | 13112 | 07:17.067 |
| p4_fin | 16139 | 08:57.967 |
| p5_debut | 16204 | 09:00.133 |
| p5_milieu | 18339 | 10:11.300 |
| p5_fin | 20468 | 11:22.267 |
| plan | 292 | 00:09.733 |
| points | 598 | 00:19.933 |
| revue | 1090 | 00:36.333 |
| derniere_phrase | 1314 | 00:43.800 |
| consigne | 2215 | 01:13.833 |
| decharge | 2542 | 01:24.733 |
| groupes | 3122 | 01:44.067 |
| resultats | 3534 | 01:57.800 |
| page_labo | 3823 | 02:07.433 |
| vagabondage | 4093 | 02:16.433 |
| domicile | 4694 | 02:36.467 |
| etude9 | 4933 | 02:44.433 |
| preparation | 5440 | 03:01.333 |
| scenariste | 5663 | 03:08.767 |
| pellicule | 5980 | 03:19.333 |
| boulangerie | 6256 | 03:28.533 |
| page_question | 6635 | 03:41.167 |
| harvard | 6902 | 03:50.067 |
| resultats_kg | 7196 | 03:59.867 |
| titre_kg | 7516 | 04:10.533 |
| ascenseur | 7653 | 04:15.100 |
| mediametrie | 8111 | 04:30.367 |
| annees | 8611 | 04:47.033 |
| pascal | 8762 | 04:52.067 |
| solitude | 9022 | 05:00.733 |
| poche | 9263 | 05:08.767 |
| nuit | 9517 | 05:17.233 |
| page_cause | 9899 | 05:29.967 |
| vide | 10211 | 05:40.367 |
| muscle | 10691 | 05:56.367 |
| techniques | 11061 | 06:08.700 |
| siecles | 11382 | 06:19.400 |
| mot_solitude | 11733 | 06:31.100 |
| khalwa_mot | 11984 | 06:39.467 |
| khalwa_3d | 12241 | 06:48.033 |
| carte_bagdad | 12768 | 07:05.600 |
| langue | 13151 | 07:18.367 |
| carte_damas | 13464 | 07:28.800 |
| minaret | 13697 | 07:36.567 |
| ihya | 13994 | 07:46.467 |
| dhikr_mot | 14490 | 08:03.000 |
| chapelet | 14550 | 08:05.000 |
| dhikr_3d | 15038 | 08:21.267 |
| verset | 15161 | 08:25.367 |
| verset_fondu_entree | 15059 | 08:21.967 |
| verset_fondu_sortie | 15263 | 08:28.767 |
| fondements | 16085 | 08:56.167 |
| exercice_1 | 16603 | 09:13.433 |
| exercice_2 | 16851 | 09:21.700 |
| exercice_3 | 17155 | 09:31.833 |
| exercice_4 | 17897 | 09:56.567 |
| exercice_5 | 18046 | 10:01.533 |
| envie | 18476 | 10:15.867 |
| retours | 18874 | 10:29.133 |
| bouton_poche | 19313 | 10:43.767 |
| revelation | 19544 | 10:51.467 |
| page_entraine | 19727 | 10:57.567 |
| meublee | 20024 | 11:07.467 |
| page_suite | 20293 | 11:16.433 |
| ecran_final | 20413 | 11:20.433 |

Version sans visage : p1_debut, consigne, page_labo, page_question, page_cause, retours, revelation, page_entraine, meublee, page_suite, ecran_final.

## Shorts : 9 vues

| Short | Durée (images) | Vues |
|---|---:|---|
| short-bouton-ar | 3755 | debut:60 milieu:1878 fin:3725 |
| short-pascal-ar | 2174 | debut:60 milieu:1087 fin:2144 |
| short-exercice-ar | 2803 | debut:60 milieu:1402 fin:2773 |

## Commandes pour Claude

Réemploi des images 3D françaises, aucun Blender.

```bash
node tools/bundle_local.mjs out/bundle-ar
export CHROME='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
export BUNDLE=out/bundle-ar
FACELESS=1 CLEAN=1 WITH3D=1 node tools/stills.mjs out/validation-ar/ar-png --composition V01-AR p1_debut:30 p1_milieu:792 p1_fin:1548 p2_debut:1613 p2_milieu:3601 p2_fin:5584 p3_debut:5649 p3_milieu:7835 p3_fin:10015 p4_debut:10080 p4_milieu:13112 p4_fin:16139 p5_debut:16204 p5_milieu:18339 p5_fin:20468 plan:292 points:598 revue:1090 derniere_phrase:1314 consigne:2215 decharge:2542 groupes:3122 resultats:3534 page_labo:3823 vagabondage:4093 domicile:4694 etude9:4933 preparation:5440 scenariste:5663 pellicule:5980 boulangerie:6256 page_question:6635 harvard:6902 resultats_kg:7196 titre_kg:7516 ascenseur:7653 mediametrie:8111 annees:8611 pascal:8762 solitude:9022 poche:9263 nuit:9517 page_cause:9899 vide:10211 muscle:10691 techniques:11061 siecles:11382 mot_solitude:11733 khalwa_mot:11984 khalwa_3d:12241 carte_bagdad:12768 langue:13151 carte_damas:13464 minaret:13697 ihya:13994 dhikr_mot:14490 chapelet:14550 dhikr_3d:15038 verset:15161 verset_fondu_entree:15059 verset_fondu_sortie:15263 fondements:16085 exercice_1:16603 exercice_2:16851 exercice_3:17155 exercice_4:17897 exercice_5:18046 envie:18476 retours:18874 bouton_poche:19313 revelation:19544 page_entraine:19727 meublee:20024 page_suite:20293 ecran_final:20413
FACELESS=1 CLEAN=1 WITH3D=1 node tools/stills.mjs out/validation-ar/ar-sans-visage-png --composition V01-AR p1_debut:30 consigne:2215 page_labo:3823 page_question:6635 page_cause:9899 retours:18874 revelation:19544 page_entraine:19727 meublee:20024 page_suite:20293 ecran_final:20413
FACELESS=1 CLEAN=1 WITH3D=1 node tools/stills.mjs out/validation-ar/short-bouton-ar-png --composition short-bouton-ar debut:60 milieu:1878 fin:3725
FACELESS=1 CLEAN=1 WITH3D=1 node tools/stills.mjs out/validation-ar/short-pascal-ar-png --composition short-pascal-ar debut:60 milieu:1087 fin:2144
FACELESS=1 CLEAN=1 WITH3D=1 node tools/stills.mjs out/validation-ar/short-exercice-ar-png --composition short-exercice-ar debut:60 milieu:1402 fin:2773
```

## Points à regarder

- Arabe en Amiri : droite à gauche, chiffres dans l’ordre, petites étiquettes lisibles, interlignes, fiches empilées et colonne de l’exercice sans débordement.
- Verset : uthmani exact, Amiri Quran, fondu seul, rien dessous ; voix seule pendant toute sa fenêtre.
- Plans 3D : vide, khalwa, dhikr, meublee ; raccords de vitesse et continuité des images françaises remappées.
- Repères d’intro, inserts, veste et bruitages : `v01-ar-finition.md`.
- La comparaison FR/EN `--baseline out/validation/ar-baseline/src` vérifie HTML, styles et audio simulé ; elle ne remplace pas une écoute ni le contrôle du rendu vidéo.
