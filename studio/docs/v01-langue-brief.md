# Vidéo 1 en ourdou (`ur`) et en arabe (`ar`) : brief pour un agent cloud

Tu prépares **une** version de « Pourquoi tu n'arrives plus à rester seul avec toi-même » (chaîne bilLkarkariy) :
l'ourdou **ou** l'arabe, selon ce qu'on t'a demandé. Un autre agent fait l'autre langue en parallèle.
La version anglaise est le modèle à suivre : elle est finie et validée sur la branche `studio/v01-en`.

## Branche

- Pars de `studio/v01-en` (pas de `studio/hook-poc`). Crée `studio/v01-ur` ou `studio/v01-ar`.
- Pousse uniquement sur ta branche. Ne fusionne rien, ne touche à aucune autre branche.

Lis d'abord `docs/reprise-agent.md` (règles, sécurité, architecture), `docs/v01-en-brief.md` (comment la version
anglaise a été faite), `docs/v01-en-etat.md` et `docs/v01-en-3d.md`.

## Règles absolues

- Ne lis jamais `.env`, n'affiche aucune clé. **Aucun appel ElevenLabs, aucune voix générée.** Jamais la voix « Sidi Mounir ».
- `public/` n'est pas dans git (images 3D, sons, polices, voix, photos de Billel) : tu ne l'as pas, c'est normal.
  N'essaie pas de le recréer, ne commite jamais `public/` ni `out/`. Regarde `git status` avant chaque commit.
- Ne touche pas à `package.json`, n'ajoute aucune dépendance.
- **Aucun calcul 3D, jamais.** Les versions étrangères réutilisent les images 3D françaises, recalées dans le temps
  (`tools/remap3d_en.py`, `src/data/remap3d_en.json`, `Shot3D` dans `src/components/Light.tsx`).
- Commits en français, un par étape, message qui dit ce qui change à l'écran.
- Le respect de la communauté soufie est non négociable : rien de folklorique, aucun raccourci sur la voie.
  Le verset (Coran 13:28) reste en arabe uthmani exact (police Amiri Quran), sans animation, avec seulement un fondu,
  aucun son dessous. Toute question religieuse va dans `docs/v01-<langue>-questions.md`, jamais tranchée par toi.
- Les sources ne s'affichent jamais à l'écran, seulement dans la description.
- Version **sans face caméra** (comme l'anglais : `faceless`), avec les textes sur papier traduits.

## La voix

Billel enregistre lui-même la voix avec son clone ElevenLabs, à partir de
`script/v01_texte_playground_balises_ur.txt` ou `script/v01_texte_playground_balises_ar.txt`.
**Ce texte est figé : la voix dira exactement ces mots.** N'y change rien. S'il te semble faux, écris-le dans les questions.

## Ce qu'il faut produire

1. **`script/v01_<langue>.json`** : même structure que `script/v01_en.json` (mêmes `id` de segments, mêmes `pause`,
   `lead`, `tail`), avec le texte du fichier playground découpé segment par segment, balises comprises.
   Ajoute `src/data/v01_<langue>.groups.json` (correspondance des segments `p…`) sur le modèle anglais.
2. **La langue dans le code** : `Lang` passe à `'fr' | 'en' | 'ur' | 'ar'` (`src/i18n/index.tsx`), avec
   `src/i18n/ur.ts` ou `src/i18n/ar.ts`. Tous les textes à l'écran traduits : Kinetic, fiches, titres, étiquettes, carte,
   HUD, écran de fin, Shorts, pages sans face caméra (`src/montage/faceless.tsx`). Le français et l'anglais ne doivent
   pas bouger d'un pixel.
3. **Écriture de droite à gauche.** Arabe et ourdou se lisent de droite à gauche : sens du texte, alignement, ordre des
   mots barrés ou colorés, soulignés, compteurs, puces. Polices : arabe en Amiri (déjà dans `src/fonts.ts`) ;
   ourdou en Nastaliq (Noto Nastaliq Urdu, interligne plus grand). Déclare la police dans `src/fonts.ts` avec le
   chemin `fonts/NotoNastaliqUrdu-Regular.ttf` : Claude posera le fichier sur le Mac. Chiffres : chiffres occidentaux
   par défaut, et pose la question (chiffres arabes orientaux ou non) dans les questions.
4. **Le verset** : en arabe, rien sous le texte uthmani (la voix dit le verset lui-même). En ourdou, la traduction du
   fichier playground (« سن لو، اللہ کی یاد ہی میں دلوں کا چین ہے », Kanz ul-Iman) sous l'arabe, même place et même style
   que la traduction anglaise.
5. **Repères** : `src/data/v01_<langue>.anchors.json` sur le modèle de `src/data/v01_en.anchors.json` (clé = le mot
   français, valeur = la phrase dans ta langue). Adapte `tools/check_v01_en.mjs` pour ta langue : tous les repères
   doivent se résoudre.
6. **Alignement provisoire** : `src/data/v01_<langue>.vo.json` estimé avec `tools/vo_estime.py` (adapte-le à
   l'écriture arabe : syllabes approchées par les voyelles longues et les mots), `audio: null`. Il sera remplacé par le
   vrai alignement sur le Mac quand la voix existera.
7. **Compositions** : `V01-UR` ou `V01-AR`, et les trois Shorts (`short-*-ur` ou `short-*-ar`) dans `src/Root.tsx`.
8. **Recalage 3D** : généralise `tools/remap3d_en.py` à toutes les langues (`--lang`), sans rien recalculer. Il tournera
   sur le Mac avec le vrai alignement.
9. **Description YouTube** : `docs/v01-<langue>-description.md`, mêmes sources que la version anglaise, titres d'œuvres
   dans leur langue d'origine quand ils existent (al-Munqidh min al-ḍalāl, Iḥyāʾ ʿulūm al-dīn). Chapitres provisoires.
   Propose aussi un titre de vidéo et trois textes courts de miniature (sur le modèle « YOU WOULD HAVE PRESSED IT. »,
   « 15 MIN. ALONE. », « RATHER THE SHOCK? »).
10. **Sous-titres** : adapte `tools/srt.py` à ta langue (chiffres à l'écran, ponctuation de droite à gauche).

## Contrôles

- `npx tsc --noEmit` passe. Le script de repères passe.
- Tu ne peux pas rendre d'images (pas de `public/`) : écris dans `docs/v01-<langue>-images-fixes.md` la liste des images
  à regarder (début, milieu, fin de chaque partie, toutes les pages de texte, la carte, le verset, l'écran de fin,
  les Shorts). Claude les rendra sur le Mac.

## À la fin

- `docs/v01-<langue>-questions.md` : questions pour Billel (chiffres, termes religieux, choix de traduction à l'écran,
  titre, miniatures).
- `docs/v01-<langue>-etat.md` : ce qui est fait, ce qui reste (voix, vrai alignement, recalage 3D, rendu sur le Mac).
- Pousse ta branche.
