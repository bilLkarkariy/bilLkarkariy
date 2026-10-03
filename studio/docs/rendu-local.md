# Rendu en local : vidéo 1

Le montage est complet de 0:00 à la fin (9:44 avec l'écran de fin). Il manque 4 plans 3D à calculer. Ils sont trop lents pour le serveur (4 cœurs, environ 45 s par image), mais rapides sur une carte graphique.

## 1. Le code

```bash
git clone https://github.com/billkarkariy/billkarkariy.git
cd billkarkariy && git checkout studio/hook-poc
cd studio && npm install
```

Il faut aussi :

- Node 20 ou plus ;
- ffmpeg ;
- Python **3.11** (le module `bpy` 5.0.1 ne s'installe qu'avec cette version) :

```bash
pip install numpy scipy pillow soundfile pymupdf bpy==5.0.1
```

## 2. Les fichiers qui ne sont pas dans git

Les fichiers lourds ne sont pas versionnés : voix, captures, bruitages, musiques, textures, polices, plans 3D déjà rendus. Le dépôt est public.

Décompresse **le zip d'assets** (lien donné dans la conversation) dans `studio/public/`. Il contient `vo/`, `captures/`, `sfx/`, `music/`, `tex/`, `fonts/` et `3d/`, avec les plans maquette, seuls, bouton et salon.

`public/aroll/placeholder.jpg` (ta photo) n'est pas dans le zip. Remets-la toi-même.

Pour tout régénérer à la place, sans le zip :

```bash
tools/setup.sh                                          # polices, textures, sons de base
python3 tools/capture.py script/captures_v01.json      # pages web
python3 tools/pdfcap.py script/captures_pdf_v01.json   # Harvard 2010 (PDF)
python3 tools/relics.py script/relics_v01.json         # manuscrit de Pascal, photo de Damas
python3 tools/sfx_el.py sfx script/sfx_v01.json        # bruitages ElevenLabs
```

`tools/sfx_el.py` a besoin de `ELEVENLABS_API_KEY` dans `studio/.env`. Les fichiers déjà générés sont en cache dans `.cache/`, et ce dossier n'est pas dans le zip.

## 3. Les 4 plans 3D

| Plan | Passage | Images (une sur deux) |
|---|---|---|
| `vide` | p35-p36 : la pièce sans meuble, la porte qui s'allume comme un écran | 258 |
| `khalwa` | p44 : la porte se ferme, la lumière d'or, les jours et les nuits | 166 |
| `dhikr` | p51 : le point d'or se pose, le pion s'éloigne et revient | 156 |
| `meublee` | p67 : la pièce meublée, la caméra s'élève (une image sur trois) | 43 |

D'abord un aperçu rapide, pour vérifier qu'on a la même image. Il sort en quelques secondes, dans `public/3d/<plan>/test_*.png` :

```bash
python3 tools/plans3d.py vide --test 100,250,470 --pct 50 --gpu
```

Ensuite le rendu complet :

```bash
python3 tools/plans3d.py vide    --step 2 --samples 32 --gpu
python3 tools/plans3d.py khalwa  --step 2 --samples 32 --gpu
python3 tools/plans3d.py dhikr   --step 2 --samples 32 --gpu
python3 tools/plans3d.py meublee --step 3 --samples 32 --gpu
```

- `--gpu` prend la carte graphique (OptiX, CUDA, Metal, HIP ou oneAPI). Sans carte utilisable, le script le dit et calcule sur le processeur.
- Sur GPU, on peut monter à `--samples 64`.
- Si le rendu est interrompu, relance la même commande : il reprend où il s'était arrêté, sans écraser les images déjà faites.
- Les temps des plans sont calculés depuis la voix (`src/data/v01.vo.json`). Si la voix change, il faut relancer les plans.

## 4. La vidéo

```bash
npx remotion bundle src/index.ts --out-dir=out/bundle
npx remotion render out/bundle V01 out/v01_raw.mp4 --crf=16
tools/master.sh out/v01_raw.mp4 out/v01.mp4      # -14 LUFS, crête -1,5 dBTP
```

- **Avant que tous les plans 3D soient prêts** : `--props='{"no3d":["vide","khalwa"]}'` met un carton à la place des plans listés. `--props='{"no3d":true}'` en met à la place de tous les plans 3D.
- **Un passage seulement** : `--frames=4418-8124`. Pour trouver une image, `at('p20')` dans `src/cues.ts` vaut 24 + secondes × 30.
- **Vérifier une image précise** : `node tools/stills.mjs out/stills nom:4584 autre:6217`. Un seul navigateur sert à toutes les images.
- **Éditer en direct** : `npm run studio`.

## 5. Ce qui reste à remplacer

- **Face caméra** : les plans `A-ROLL · À REMPLACER` (`src/components/ARoll.tsx`) attendent tes rushes. Le texte et les cadrages sont dans `docs/v01-face-camera.md`. Une fois ta vraie voix enregistrée, on relance l'alignement mot à mot et toutes les images se recalent.
- **Gros plan tissu (6b)** : à poser après « Cette veste rapiécée, c'est son habit ».
- **Médiamétrie, « une vingtaine de sessions »** : les communiqués PDF de Médiamétrie renvoient 404. À l'écran, il n'y a que la fiche. Dans la description, cite https://fr.themedialeader.com/?p=102193 (« 20 sessions Internet par jour en moyenne, avec une durée de 11 minutes chacune »).
- **Agent local** : le prompt de reprise est dans `docs/reprise-agent.md`.

## Où est quoi

| Partie | Temps | Fichier |
|---|---|---|
| Hook + L'expérience | 0:00 → 2:27 | `src/V01.tsx` |
| Le scénariste, Harvard, les écrans, Pascal | 2:27 → 4:28 | `src/montage/p3.tsx` (scènes : `src/scenes/Part3.tsx`) |
| La pièce vide, khalwa, al-Ghazali, dhikr, verset | 4:28 → 7:29 | `src/montage/p4.tsx` (`src/scenes/Part4.tsx`) |
| L'exercice, le bouton, la dernière phrase, la fin | 7:29 → fin | `src/montage/p5.tsx` (`src/scenes/Part5.tsx`) |
| Musique (atténuée sous la voix, coupée sous le verset) | toute la vidéo | `src/components/Music.tsx`, pistes dans `V01.tsx` |
