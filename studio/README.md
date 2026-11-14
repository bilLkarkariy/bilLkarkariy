# Studio

Simulation du processus de dessin d'un studio d'animation 2D, du croquis à
l'animation, sans aucun appel à un modèle d'image : le dessin est une suite de
gestes (tracé + pression) qu'un moteur pose sur le papier comme un crayon.

## Lancer

```bash
python3 -m studio.steps.s01_crayon
python3 -m studio.steps.s02_mannequin
python3 -m studio.steps.s03_model_sheet
python3 -m studio.steps.s03_expressions
python3 -m studio.steps.s03_tete --video
python3 -m studio.steps.s04_storyboard
python3 -m studio.steps.s05_layout
python3 -m studio.steps.s06_cles
python3 -m studio.steps.s07_intervalles
python3 -m studio.steps.s08_cleanup
```

Les rendus sont écrits dans `studio/out/` (non versionné). Les planches de l'étape 3
sont dessinées en double résolution (`ZOOM = 2`, tête de 300 px) pour un trait fin. Dépendances :
Python 3, `numpy`, `pillow`, et `ffmpeg` pour les vidéos.

## Structure

- `engine/paper.py` : la feuille et son grain.
- `engine/brush.py` : les outils (crayons bleu et rouge, HB, 2B, tranche de la mine).
- `engine/canvas.py` : calques, fusion sur le papier, journal des traits.
- `engine/hand.py` : la main (visée, tremblement, pression) et le dessinateur.
- `engine/timelapse.py`, `engine/video.py` : rejoue le journal en vidéo, écrit les MP4.
- `engine/mannequin.py` : squelette, volumes, poses, caméra, lignes cachées.
- `engine/construction.py` : dessin de structure 2D, commun aux deux modes.
- `engine/libre.py` : mode sans mannequin, figures posées à la main en 2D.
- `engine/poses.py` : poses de base.
- `engine/inbetween.py` : poses entre les clés (courbes lisses, ralentis).
- `engine/scene.py` : décor en boîtes, vu par la même caméra que le personnage.
- `engine/vpath.py`, `engine/formes.py` : ce que le dessinateur sait de la forme (tracés, formes
  posées du fond vers l'avant) pour ne tracer que ce qui est visible. Ces modules ne dessinent rien.
- `characters/` : `body.py` (corps paramétrable), puis un personnage par fichier
  (proportions, volumes des cheveux et des vêtements, traits du visage).
- `shots/` : un plan par fichier (caméra, décor, cadre, poses clés, timing), et `render.py`
  qui dessine un plan image par image.
- `steps/` : une étape du studio par fichier.

## Tête de Kaya (`s03_tete`)

Dessin au crayon uniquement, monté geste après geste : charpente au crayon bleu, esquisse,
trait appuyé, cheveux mèche par mèche de l'épi à la pointe (reflet réservé), ombres hachurées.
`--video` rejoue le dessin en train de se faire. La description de la tête est dans
`characters/kaya_tete.py`. Règles de construction appliquées :

- ligne des yeux à mi-hauteur de la tête, base du nez à mi-chemin yeux-menton, bouche au
  premier tiers nez-menton, oreille entre la ligne des yeux et la base du nez ;
- de trois quarts : ligne médiane décalée et courbe, œil éloigné large de 0,7 fois l'œil proche ;
- cheveux décollés du crâne, dessinés par mèches qui partent de l'épi, de tailles inégales.

Sources : [Clip Studio, visage de profil et de trois quarts](https://www.clipstudio.net/oekaki/archives/176083),
[Clip Studio, repères du visage](https://www.clipstudio.net/oekaki/archives/151365),
[AnimeOutline, visage de trois quarts](https://www.animeoutline.com/?p=4399),
[Clip Studio Tips, cheveux](https://tips.clip-studio.com/en-us/articles/16481),
[canmom, conventions du dessin d'anime](https://canmom.art/animation/anime-girl-1).

## Étapes

| # | Étape | État |
|---|---|---|
| 1 | Crayon et main | fait |
| 2 | Mannequin de construction (squelette, volumes, poses) | fait |
| 3 | Model sheet (turnaround, expressions) | fait |
| 4 | Storyboard rough | fait |
| 5 | Layout (cadre, perspective, caméra) | fait |
| 6 | Poses clés et feuille de timing | fait |
| 7 | Intervalles | fait |
| 8 | Clean-up | fait |
| 9 | Couleur et ombres | à faire |
| 10 | Décors | à faire |
| 11 | Compositing et export | à faire |
