# V01 UR — images fixes à rendre et regarder

Liste calculée sur la **voix estimée** (`src/data/v01_ur.vo.json`, `audio: null`) : 20 255 images, 30 i/s, 11:15. Toutes les
images bougeront avec la vraie voix : après l'alignement, relancer `node tools/check_v01_en.mjs --lang ur` (il réécrit
`out/validation/render-ur-stills.txt`) et refaire cette liste.

Aucun PNG Remotion n'a été rendu ici (pas de `public/`). Une planche HTML a été regardée dans le navigateur, avec les
polices du Mac et la police nastaliq du système : sens de lecture, mots barrés et colorés, compteurs, carte, verset,
pages sans face caméra et Shorts sont à leur place. Ce n'est pas une preuve visuelle : les PNG restent à faire.

## Vidéo longue : 38 vues

| Vue | Image | Temps vidéo |
|---|---:|---:|
| p1_debut | 30 | 00:01.000 |
| p1_milieu | 735 | 00:24.500 |
| p1_fin | 1434 | 00:47.800 |
| p2_debut | 1499 | 00:49.967 |
| p2_milieu | 3424 | 01:54.133 |
| p2_fin | 5343 | 02:58.100 |
| p3_debut | 5408 | 03:00.267 |
| p3_milieu | 7404 | 04:06.800 |
| p3_fin | 9395 | 05:13.167 |
| p4_debut | 9460 | 05:15.333 |
| p4_milieu | 12667 | 07:02.233 |
| p4_fin | 15868 | 08:48.933 |
| p5_debut | 15933 | 08:51.100 |
| p5_milieu | 18079 | 10:02.633 |
| p5_fin | 20220 | 11:14.000 |
| consigne | 1976 | 01:05.867 |
| ecrans | 7617 | 04:13.900 |
| pascal | 8200 | 04:33.333 |
| solitude | 8422 | 04:40.733 |
| khalwa | 11829 | 06:34.300 |
| carte | 12376 | 06:52.533 |
| carte_route | 13150 | 07:18.333 |
| ghazali | 12736 | 07:04.533 |
| dhikr | 14417 | 08:00.567 |
| verset | 14996 | 08:19.867 |
| fondements | 15459 | 08:35.300 |
| point | 17416 | 09:40.533 |
| retour | 17783 | 09:52.767 |
| revelation | 19271 | 10:42.367 |
| verset_fondu_entree | 14916 | 08:17.200 |
| verset_fondu_sortie | 15076 | 08:22.533 |
| verset_avant | 14908 | 08:16.933 |
| verset_apres | 15083 | 08:22.767 |
| traduction_parlee | 14789 | 08:12.967 |
| pause_question | 6291 | 03:29.700 |
| chuchotements | 17644 | 09:48.133 |
| fin_voix | 20055 | 11:08.500 |
| ecran_final | 20165 | 11:12.167 |

## Pages sans face caméra (`FACELESS=1`) : 8 vues

| Vue | Image | Temps vidéo |
|---|---:|---:|
| sans_face_2 | 884 | 00:29.467 |
| sans_face_3 | 3665 | 02:02.167 |
| sans_face_4 | 6285 | 03:29.500 |
| sans_face_5a | 9077 | 05:02.567 |
| sans_face_5b | 9345 | 05:11.500 |
| sans_face_8a | 19534 | 10:51.133 |
| sans_face_8b | 19651 | 10:55.033 |
| sans_face_9 | 20017 | 11:07.233 |

## Shorts : 9 vues

| Short | Images | Vues |
|---|---:|---|
| short-bouton-ur | 3 519 | debut:60 milieu:1760 fin:3489 |
| short-pascal-ur | 2 122 | debut:60 milieu:1061 fin:2092 |
| short-exercice-ur | 2 712 | debut:60 milieu:1356 fin:2682 |

## Commandes pour Claude (sur le Mac)

Poser d'abord la police : `public/fonts/NotoNastaliqUrdu-Regular.ttf` (Noto Nastaliq Urdu, Google Fonts, licence OFL).
Sans ce fichier, Remotion n'attend pas : il prend la police système du même nom si elle existe, sinon une autre.

```bash
node tools/bundle_local.mjs out/bundle-ur
export CHROME='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
export BUNDLE=out/bundle-ur
node tools/stills.mjs out/validation/ur-png --composition V01-UR p1_debut:30 p1_milieu:735 p1_fin:1434 p2_debut:1499 p2_milieu:3424 p2_fin:5343 p3_debut:5408 p3_milieu:7404 p3_fin:9395 p4_debut:9460 p4_milieu:12667 p4_fin:15868 p5_debut:15933 p5_milieu:18079 p5_fin:20220 consigne:1976 ecrans:7617 pascal:8200 solitude:8422 khalwa:11829 carte:12376 carte_route:13150 ghazali:12736 dhikr:14417 verset:14996 fondements:15459 point:17416 retour:17783 revelation:19271 verset_fondu_entree:14916 verset_fondu_sortie:15076 verset_avant:14908 verset_apres:15083 traduction_parlee:14789 pause_question:6291 chuchotements:17644 fin_voix:20055 ecran_final:20165
FACELESS=1 node tools/stills.mjs out/validation/ur-sans-face-png --composition V01-UR sans_face_2:884 sans_face_3:3665 sans_face_4:6285 sans_face_5a:9077 sans_face_5b:9345 sans_face_8a:19534 sans_face_8b:19651 sans_face_9:20017
node tools/stills.mjs out/validation/short-bouton-ur-png --composition short-bouton-ur debut:60 milieu:1760 fin:3489
node tools/stills.mjs out/validation/short-pascal-ur-png --composition short-pascal-ur debut:60 milieu:1061 fin:2092
node tools/stills.mjs out/validation/short-exercice-ur-png --composition short-exercice-ur debut:60 milieu:1356 fin:2682
```

Pour les plans 3D, ajouter `WITH3D=1` (les images 3D françaises recalées sur l'ourdou, `src/data/remap3d_ur.json`).

## Ce qu'il faut regarder

- **Sens de lecture :** chaque ligne part de la droite ; les mots barrés le sont de droite à gauche ; les mots en or ou
  en rouge sont les bons ; « 16 / 40 », « 4 / 5 », « 0:07 / 0:20 », « 12 / 18 » se lisent de gauche à droite.
- **Nastaliq :** aucune hampe ni point coupé en haut ou en bas des lignes, des fiches et des Shorts ; interligne
  suffisant sur les étapes de l'exercice (`point`), la consigne (`consigne`) et les fiches noires.
- **Fiches noires :** la citation de Ghazali (`ghazali`) passe sur deux lignes, avec un seul mot sur la seconde :
  à resserrer si c'est gênant.
- **Carte :** noms de villes, de mer, de fleuve et de désert lisibles ; « بغداد » touche le bord droit comme
  « BAGDAD » en français.
- **Verset :** arabe uthmani en Amiri Quran, traduction ourdoue dessous, même place que l'anglais ; immobile entre les
  fondus (`verset_fondu_entree`, `verset`, `verset_fondu_sortie`) ; aucun son.
- **Guillemets :** “ ” ne se retournent pas en écriture de droite à gauche ; vérifier qu'ils s'ouvrent du bon côté.
- **HUD et étiquettes de coin :** restés à leur place française (le compteur de la khalwa en haut à gauche) ;
  dire s'il faut les passer à droite.
- **Français et anglais :** les 1 733 comparaisons HTML FR et EN, avant et après, sont identiques. Comparer aussi
  quelques PNG FR et EN avant/après si une preuve visuelle est voulue.

Le montage ourdou garde ses emplacements face caméra et, sans `WITH3D`, ses cartons 3D. Ce ne sont pas des images
prêtes à publier.
