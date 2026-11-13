# Studio

Simulation du processus de dessin d'un studio d'animation 2D, du croquis à
l'animation, sans aucun appel à un modèle d'image : le dessin est une suite de
gestes (tracé + pression) qu'un moteur pose sur le papier comme un crayon.

## Lancer

```bash
python3 -m studio.steps.s01_crayon
python3 -m studio.steps.s02_mannequin
```

Les rendus sont écrits dans `studio/out/` (non versionné). Dépendances :
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
- `characters/` : un personnage par fichier (proportions et volumes).
- `steps/` : une étape du studio par fichier.

## Étapes

| # | Étape | État |
|---|---|---|
| 1 | Crayon et main | fait |
| 2 | Mannequin de construction (squelette, volumes, poses) | fait |
| 3 | Model sheet (turnaround, expressions) | à faire |
| 4 | Storyboard rough | à faire |
| 5 | Layout (cadre, perspective, caméra) | à faire |
| 6 | Poses clés et feuille de timing | à faire |
| 7 | Intervalles | à faire |
| 8 | Clean-up | à faire |
| 9 | Couleur et ombres | à faire |
| 10 | Décors | à faire |
| 11 | Compositing et export | à faire |
