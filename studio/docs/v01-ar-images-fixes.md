# V01 AR — images fixes à rendre et regarder

Liste calculée sur l'**alignement estimé** (pas encore de voix arabe) : 22 542 images, 30 i/s. Les numéros d'image
bougeront avec la vraie voix : après `tools/vo.py align`, relancer `node tools/check_v01_ar.mjs`, qui réécrit la
commande à jour dans `out/validation-ar/render-ar-stills.txt`.

Aucun PNG Remotion n'a été rendu. Les planches HTML (`out/validation-ar/…/index.html`, mêmes React et mêmes images) ont
été regardées dans un navigateur local pour une trentaine de vues, avec les polices du Mac : l'arabe s'affiche en
Amiri, de droite à gauche, guillemets « » tournés vers l'extérieur, chiffres dans le bon ordre. Ce n'est pas une preuve
PNG : le contrôle final reste celui du renderer.

## Vidéo longue : 75 vues (+ 11 en version sans visage)

| Vue | Image | Temps vidéo |
|---|---:|---:|
| p1_debut | 30 | 00:01.000 |
| p1_milieu | 846 | 00:28.200 |
| p1_fin | 1657 | 00:55.233 |
| p2_debut | 1722 | 00:57.400 |
| p2_milieu | 3873 | 02:09.100 |
| p2_fin | 6018 | 03:20.600 |
| p3_debut | 6083 | 03:22.767 |
| p3_milieu | 8530 | 04:44.333 |
| p3_fin | 10972 | 06:05.733 |
| p4_debut | 11037 | 06:07.900 |
| p4_milieu | 14398 | 07:59.933 |
| p4_fin | 17754 | 09:51.800 |
| p5_debut | 17819 | 09:53.967 |
| p5_milieu | 20166 | 11:12.200 |
| p5_fin | 22507 | 12:30.233 |
| plan | 302 | 00:10.067 |
| points | 576 | 00:19.200 |
| revue | 1108 | 00:36.933 |
| derniere_phrase | 1374 | 00:45.800 |
| consigne | 2359 | 01:18.633 |
| decharge | 2691 | 01:29.700 |
| groupes | 3280 | 01:49.333 |
| resultats | 3697 | 02:03.233 |
| page_labo | 4023 | 02:14.100 |
| vagabondage | 4334 | 02:24.467 |
| domicile | 5009 | 02:46.967 |
| etude9 | 5303 | 02:56.767 |
| preparation | 5870 | 03:15.667 |
| scenariste | 6097 | 03:23.233 |
| pellicule | 6445 | 03:34.833 |
| boulangerie | 6758 | 03:45.267 |
| page_question | 7159 | 03:58.633 |
| harvard | 7463 | 04:08.767 |
| resultats_kg | 7800 | 04:20.000 |
| titre_kg | 8146 | 04:31.533 |
| ascenseur | 8304 | 04:36.800 |
| mediametrie | 8856 | 04:55.200 |
| annees | 9455 | 05:15.167 |
| pascal | 9615 | 05:20.500 |
| solitude | 9892 | 05:29.733 |
| poche | 10136 | 05:37.867 |
| nuit | 10406 | 05:46.867 |
| page_cause | 10841 | 06:01.367 |
| vide | 11176 | 06:12.533 |
| muscle | 11711 | 06:30.367 |
| techniques | 12142 | 06:44.733 |
| siecles | 12496 | 06:56.533 |
| mot_solitude | 12852 | 07:08.400 |
| khalwa_mot | 13135 | 07:17.833 |
| khalwa_3d | 13438 | 07:27.933 |
| carte_bagdad | 14052 | 07:48.400 |
| langue | 14468 | 08:02.267 |
| carte_damas | 14802 | 08:13.400 |
| minaret | 15083 | 08:22.767 |
| ihya | 15437 | 08:34.567 |
| dhikr_mot | 15988 | 08:52.933 |
| chapelet | 16048 | 08:54.933 |
| dhikr_3d | 16527 | 09:10.900 |
| verset | 16653 | 09:15.100 |
| verset_fondu_entree | 16553 | 09:11.767 |
| verset_fondu_sortie | 16753 | 09:18.433 |
| fondements | 17695 | 09:49.833 |
| exercice_1 | 18258 | 10:08.600 |
| exercice_2 | 18499 | 10:16.633 |
| exercice_3 | 18819 | 10:27.300 |
| exercice_4 | 19558 | 10:51.933 |
| exercice_5 | 19703 | 10:56.767 |
| envie | 20213 | 11:13.767 |
| retours | 20667 | 11:28.900 |
| bouton_poche | 21209 | 11:46.967 |
| revelation | 21474 | 11:55.800 |
| page_entraine | 21663 | 12:02.100 |
| meublee | 21897 | 12:09.900 |
| page_suite | 22332 | 12:24.400 |
| ecran_final | 22452 | 12:28.400 |

Version livrée **sans visage** (`FACELESS=1 CLEAN=1`) : p1_debut, consigne, page_labo, page_question, page_cause,
retours, revelation, page_entraine, meublee, page_suite, ecran_final (mêmes images que ci-dessus).

## Shorts : 9 vues

| Short | debut | milieu | fin |
|---|---:|---:|---:|
| short-bouton-ar | 60 | 1967 | 3904 |
| short-pascal-ar | 60 | 1174 | 2318 |
| short-exercice-ar | 60 | 1491 | 2951 |

## Commandes pour Claude (sur le Mac)

```bash
node tools/bundle_local.mjs out/bundle-ar
export CHROME='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
export BUNDLE=out/bundle-ar
node tools/stills.mjs out/validation-ar/png --composition V01-AR p1_debut:30 p1_milieu:846 p1_fin:1657 p2_debut:1722 p2_milieu:3873 p2_fin:6018 p3_debut:6083 p3_milieu:8530 p3_fin:10972 p4_debut:11037 p4_milieu:14398 p4_fin:17754 p5_debut:17819 p5_milieu:20166 p5_fin:22507 plan:302 points:576 revue:1108 derniere_phrase:1374 consigne:2359 decharge:2691 groupes:3280 resultats:3697 page_labo:4023 vagabondage:4334 domicile:5009 etude9:5303 preparation:5870 scenariste:6097 pellicule:6445 boulangerie:6758 page_question:7159 harvard:7463 resultats_kg:7800 titre_kg:8146 ascenseur:8304 mediametrie:8856 annees:9455 pascal:9615 solitude:9892 poche:10136 nuit:10406 page_cause:10841 vide:11176 muscle:11711 techniques:12142 siecles:12496 mot_solitude:12852 khalwa_mot:13135 khalwa_3d:13438 carte_bagdad:14052 langue:14468 carte_damas:14802 minaret:15083 ihya:15437 dhikr_mot:15988 chapelet:16048 dhikr_3d:16527 verset:16653 verset_fondu_entree:16553 verset_fondu_sortie:16753 fondements:17695 exercice_1:18258 exercice_2:18499 exercice_3:18819 exercice_4:19558 exercice_5:19703 envie:20213 retours:20667 bouton_poche:21209 revelation:21474 page_entraine:21663 meublee:21897 page_suite:22332 ecran_final:22452
FACELESS=1 CLEAN=1 node tools/stills.mjs out/validation-ar/png-sans-visage --composition V01-AR p1_debut:30 consigne:2359 page_labo:4023 page_question:7159 page_cause:10841 retours:20667 revelation:21474 page_entraine:21663 meublee:21897 page_suite:22332 ecran_final:22452
node tools/stills.mjs out/validation-ar/short-bouton-ar-png --composition short-bouton-ar debut:60 milieu:1967 fin:3904
node tools/stills.mjs out/validation-ar/short-pascal-ar-png --composition short-pascal-ar debut:60 milieu:1174 fin:2318
node tools/stills.mjs out/validation-ar/short-exercice-ar-png --composition short-exercice-ar debut:60 milieu:1491 fin:2951
```

## Ce qu'il faut regarder

- **Taille de l'arabe.** Les lettres arabes écrites en Garamond ou en Plex Mono passent en Amiri, agrandies de 10 %
  (texte) et de 30 % (petites étiquettes). Les étiquettes de 15 à 20 px (kickers des fiches, « التمرين · 1 / 5 »,
  « المختبر · جامعة فيرجينيا », légendes du plan) restent petites : à agrandir si elles ne se lisent pas sur un
  téléphone (`ARABIC_METRICS` dans `src/fonts.ts`).
- **Interlignes.** Fiches noires (1,35), consigne (1,6), titres des Shorts (1,35 à 1,4) : vérifier que les points et
  les harakat ne touchent pas la ligne voisine, et que les fiches empilées ne se chevauchent pas (`ihya`,
  `resultats`, `harvard`).
- **Sens de lecture.** Mots qui sortent depuis la droite (Kinetic, `muscle`, `siecles`, `page_*`), trait rouge qui barre
  depuis la droite (`page_cause`, `muscle`), fiche noire qui pivote depuis la droite avec sa barre de couleur à droite,
  colonne des étapes alignée à droite contre le dessin (`exercice_1` à `exercice_5`).
- **Chiffres.** « 12 / 18 », « 1 / 5 », « اليوم 01 / 40 », « 0:04 / 0:20 », « 57.5% », « 51% », « ≈ 19 » : dans le bon
  ordre, sans espace avant %.
- **Pascal** (`pascal`, `solitude`) : la feuille arabe à droite du manuscrit, surlignage or, rien qui déborde.
- **Le verset** (`verset`, fondus) : texte uthmani seul, Amiri Quran, rien dessous ; pas de grain ni de lumière
  de fenêtre pendant l'affichage ; la voix arabe le récite (musique et bruitages à zéro).
- **Carte** (`carte_bagdad`, `carte_damas`) : noms arabes à côté des points, pas sur eux.
- **Plans 3D** : cartons « لقطة ثلاثية الأبعاد · قيد التجهيز » tant que `src/data/remap3d_ar.json` est vide ; après
  `python3 tools/remap3d.py --lang ar` sur la vraie voix, `WITH3D=1` pour vérifier `khalwa_3d`, `dhikr_3d`, `vide`,
  `meublee`.
- **Écran de fin des Shorts** : le titre arabe passe sur deux lignes équilibrées.
