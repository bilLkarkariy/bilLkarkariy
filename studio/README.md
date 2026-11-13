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
python3 -m studio.steps.s04_storyboard
python3 -m studio.steps.s05_layout
python3 -m studio.steps.s06_cles
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
- `engine/scene.py` : décor en boîtes, vu par la même caméra que le personnage.
- `characters/` : `body.py` (corps paramétrable), puis un personnage par fichier
  (proportions, volumes des cheveux et des vêtements, traits du visage).
- `shots/` : un plan par fichier (caméra, décor, cadre, poses clés, timing).
- `steps/` : une étape du studio par fichier.

## Étapes

| # | Étape | État |
|---|---|---|
| 1 | Crayon et main | fait |
| 2 | Mannequin de construction (squelette, volumes, poses) | fait |
| 3 | Model sheet (turnaround, expressions) | fait |
| 4 | Storyboard rough | fait |
| 5 | Layout (cadre, perspective, caméra) | fait |
| 6 | Poses clés et feuille de timing | fait |
| 7 | Intervalles | à faire |
| 8 | Clean-up | à faire |
| 9 | Couleur et ombres | à faire |
| 10 | Décors | à faire |
| 11 | Compositing et export | à faire |
