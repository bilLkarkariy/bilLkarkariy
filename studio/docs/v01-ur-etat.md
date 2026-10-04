# V01 UR — état

4 octobre 2026 — branche `studio/v01-ur`, partie de `studio/v01-en`. Rien n'est fusionné.

La version ourdoue est montée **sur une voix estimée** : tous les textes, le sens de droite à gauche, le verset, les
Shorts et les pages sans face caméra sont prêts. La vraie voix, le vrai alignement, le recalage 3D définitif et le
rendu restent à faire sur le Mac. Aucune voix générée, aucun appel ElevenLabs, aucun calcul 3D, `.env` jamais lu,
`package.json` inchangé, rien de `public/` ni de `out/` dans git.

## Fait

| Livrable | État |
|---|---|
| `script/v01_ur.json` | Texte figé découpé en **79 segments**, balises comprises ; mêmes `id`, `pause`, `lead`, `tail` que l'anglais. Mis bout à bout, il redonne mot pour mot `script/v01_texte_playground_balises_ur.txt`. `tts.voice_id` vide : aucune génération possible par accident. |
| `src/data/v01_ur.groups.json` | Mêmes groupes `p…` → `s…` que l'anglais. |
| `tools/vo_estime.py` | Écriture arabe : mots, voyelles longues, lettres muettes (ھ, ں). Sortie anglaise inchangée. |
| `src/data/v01_ur.vo.json` | **Estimé**, `audio: null`, 1 836 mots, 669 s de voix, silence du verset de 6 s après `s63`. |
| `src/data/v01_ur.anchors.json` | **302 repères**, mêmes clés que l'anglais, tous résolus. Quand l'ourdou inverse l'ordre (verbe en fin de phrase), le premier mot français prend le premier mot ourdou de la tournure, pour qu'aucune animation ne recule. |
| `src/i18n/ur.ts`, `src/i18n/rtl.tsx` | Tous les textes à l'écran en ourdou. Cadre de droite à gauche autour des versions RTL seulement : le français et l'anglais ne passent jamais par là. |
| `src/fonts.ts` | Noto Nastaliq Urdu déclarée (`fonts/NotoNastaliqUrdu-Regular.ttf`), interligne réglé ; si le fichier manque, le rendu n'attend pas. |
| Montage | Kinetic, fiches, titres, étiquettes, carte, compteur de la khalwa, étapes de l'exercice, écran de fin, pages sans face caméra : en ourdou, de droite à gauche. Mots barrés de droite à gauche, nombres composés (« 16 / 40 ») lus de gauche à droite. Chiffres occidentaux. |
| Verset | Arabe uthmani exact en Amiri Quran, traduction Kanz ul-Iman dessous (même place et style que l'anglais), fondu seul, aucun son. |
| `src/Root.tsx` | `V01-UR` (**20 255 images, 11:15**) et `short-bouton-ur` (3 519 images, 1:57), `short-pascal-ur` (2 122, 1:11), `short-exercice-ur` (2 712, 1:30). |
| 3D | `tools/report_3d_en.py` et `tools/remap3d_en.py` prennent `--lang`. `src/data/remap3d_ur.json` **provisoire** (voix estimée), branché dans `Shot3D`. Images 3D françaises réutilisées, aucune recalculée. |
| `tools/srt.py` | Ourdou : chiffres, ponctuation ourdoue, marque de droite à gauche en tête de ligne. 306 sous-titres sur la voix estimée. |
| `tools/vo.py align` | Sait découper et comparer les mots ourdous ; garde la langue et le silence du verset. |
| `tools/check_v01_en.mjs --lang ur` | Texte figé, repères, verset immobile et muet, sens de droite à gauche, Shorts, textes restés en latin. |
| Docs | `v01-ur-description.md`, `v01-ur-images-fixes.md`, `v01-ur-questions.md`, ce fichier. |

## Vérifications faites ici

- `npx tsc --noEmit` : réussi.
- `node tools/check_v01_en.mjs --lang ur --baseline out/validation/baseline-src` : 79 segments, 302 repères,
  1 284 instants ourdous, les trois Shorts ; **1 733 instants FR et EN identiques** avant/après (HTML et styles,
  pas des pixels). Seuls textes encore en lettres latines : « OTHER TECHNIQUES » (citation de l'article, voir les
  questions) et « BILLKARKARIY ».
- `node tools/check_v01_en.mjs` (anglais) : réussi, inchangé.
- `tools/srt.py`, `tools/report_3d_en.py`, `tools/remap3d_en.py` : sorties françaises et anglaises identiques
  octet pour octet avant/après.
- Planche HTML regardée dans le navigateur (polices du Mac, nastaliq du système) : début de vidéo, consigne,
  fiches, compteur, carte, verset, étapes, écran de fin, pages sans face caméra, Short. Pas de PNG Remotion.

## Reste à faire sur le Mac

1. **Police :** poser `public/fonts/NotoNastaliqUrdu-Regular.ttf` (Noto Nastaliq Urdu, OFL).
2. **Voix :** Billel enregistre avec son clone, à partir de `script/v01_texte_playground_balises_ur.txt`, sans rien
   changer au texte. Jamais la voix « Sidi Mounir ».
3. **Vrai alignement :** `tools/assemble_vo.py` et `tools/vo_alignment_en.py` sont réglés pour l'anglais (Whisper en
   anglais, nombres anglais). Deux chemins :
   - les adapter à l'ourdou (Whisper `language='ur'`, mots ourdous et comparaison `tokens(text, 'ur')` /
     `norm_arabic` de `tools/vo.py`), puis assembler avec `--verse-hold 6` comme l'anglais ;
   - ou, plus simple : `python3 tools/vo.py align script/v01_ur.json public/vo/v01_ur.wav`. Il lit l'ourdou, mais
     n'ajoute pas le silence du verset tout seul (il le reprend d'un manifeste `v01_ur.assembly.json` s'il existe).
   Whisper small en ourdou est moins sûr qu'en anglais : contrôler le nombre de mots interpolés.
4. **Contrôle :** `node tools/check_v01_en.mjs --lang ur --baseline <src de référence>` ; tous les repères doivent
   encore se résoudre (le texte est figé, ils le devraient).
5. **Recalage 3D :** `python3 tools/report_3d_en.py --lang ur` puis `python3 tools/remap3d_en.py --lang ur`, sans
   Blender ; commiter `src/data/remap3d_ur.json`. Regarder les plans avec `WITH3D=1`.
6. **Paquet :** recalculer les chapitres de `docs/v01-ur-description.md` (même méthode que l'anglais) ;
   `python3 tools/srt.py src/data/v01_ur.vo.json out/package_ur/v01.ur.srt` ; miniatures depuis les brouillons
   français, avec les textes proposés.
7. **Images fixes :** rendre et regarder la liste de `docs/v01-ur-images-fixes.md` (à recalculer après l'alignement).
8. **Rendu :** `npx remotion bundle src/index.ts --out-dir=out/bundle` puis
   `npx remotion render out/bundle V01-UR out/v01_ur_raw.mp4 --crf=16 --props='{"faceless":true}'`, et les trois
   `short-*-ur`, puis `tools/master.sh`.
9. **Questions :** les réponses de Billel à `docs/v01-ur-questions.md` (chiffres, verset, termes religieux, citations,
   titre, miniatures) peuvent changer des textes de `src/i18n/ur.ts`.

## Points d'attention

- Les chapitres, sous-titres, Shorts et images listées suivent la voix **estimée** : tout bouge avec la vraie voix.
- `src/data/remap3d_ur.json` vient de la voix estimée : le refaire (étape 5), sinon les plans 3D seront décalés.
- La police nastaliq est haute : regarder en priorité les fiches noires, les étapes de l'exercice et les Shorts.
- L'avertissement React sur les clés de `FilmStrip` existe aussi en français et en anglais.

## Prompt plus récent sur `studio/v01-en`

Après le départ de cette branche, `studio/v01-en` a reçu `docs/prompts/v01-ur-agent-cloud.md` et
`docs/v01-finition.md` (pas sur cette branche). Ce travail suit `docs/v01-langue-brief.md`. Écarts à reprendre par
l'agent suivant, si ce prompt est confirmé :

- **Verset :** le prompt demande `--verse-hold 0` et le verset affiché dès « قرآن اسے ایک جملے میں کہتا ہے »
  (`at('p52') - 10`), pendant la voix, musique et bruitages coupés. Ici : silence de 6 s après `s63`, comme l'anglais
  (`src/montage/p4.tsx`, `src/V01.tsx`, `tools/check_v01_en.mjs`).
- **Voix jointe** (`bilKarkariy_ep1_urdu.mp3`) : pas reçue ici. Assemblage, gain des deux « استغفراللہ » chuchotés,
  manifeste `src/data/v01_ur.assembly.json`, vrai alignement : à faire.
- **À livrer en plus :** `docs/v01-ur-finition.md` (repères de finition et `sfxOff`), `docs/v01-ur.srt`, chapitres sur
  le vrai alignement.
- Déjà conforme : ouverture sur la maquette dès l'image 0, `remap3d_ur.json` lu par `Shot3D` (image la plus proche à
  pas 1), Shorts, police et chiffres.
