# Vidéo 1 en ourdou : tout préparer pour le rendu (agent cloud)

Tu travailles sur le dépôt GitHub `bilLkarkariy/bilLkarkariy` (public). Le projet vidéo est dans `studio/`.
C'est la vidéo 1 de la chaîne bilLkarkariy : « Pourquoi tu n'arrives plus à rester seul avec toi-même ».
Elle existe en français et en anglais (validées). Tu fais **la version ourdou**.
Un autre agent fait l'arabe en parallèle : ne touche jamais à sa branche.

## Ta mission

Rendre la version ourdou **prête à rendre** : voix calée mot par mot, textes à l'écran en ourdou, écriture de droite
à gauche, 3D recalée, fenêtres des passages animés, Shorts, sous-titres, description.
Tu ne peux pas produire le fichier vidéo final : `public/` (images 3D, sons, polices, voix, photos) n'est pas dans git.
Claude fera le rendu et la finition sur le Mac de Billel à partir de ce que tu livres (voir `studio/docs/v01-finition.md`).

## Branche

- Si `origin/studio/v01-ur` existe déjà (un premier agent a commencé), reprends-la : lis d'abord
  `studio/docs/v01-ur-etat.md` et `studio/docs/v01-ur-questions.md`, ne refais pas ce qui est fait.
- Sinon, crée `studio/v01-ur` à partir de `studio/v01-en`.
- Pousse uniquement `studio/v01-ur`. Ne fusionne rien.

## À lire avant de commencer

`studio/docs/reprise-agent.md`, `studio/docs/v01-langue-brief.md` (la base), `studio/docs/v01-finition.md`,
`studio/docs/v01-en-etat.md`, `studio/docs/v01-en-3d.md`. **Ce prompt l'emporte** là où ils diffèrent.

## Fichier joint par Billel

`bilKarkariy_ep1_urdu.mp3` : la voix ourdou complète (10:41, 44,1 kHz, mono), enregistrée avec son clone ElevenLabs
à partir de `studio/script/v01_texte_playground_balises_ur.txt`. Elle dit exactement ce texte : la traduction du verset
(Kanz ul-Iman), les deux citations d'al-Ghazali, deux « استغفراللہ » chuchotés à l'étape quatre de l'exercice.
**Ne le commite jamais, ni aucun fichier audio tiré de lui** : le dépôt est public. Travaille dans un dossier ignoré
(`studio/out/`). S'il n'est pas joint, fais tout le reste et dis-le clairement à la fin.

## Règles absolues

- Ne lis jamais `.env`. Aucun appel ElevenLabs, aucune voix générée. Jamais la voix « Sidi Mounir ».
- Aucun calcul 3D, jamais. Ne touche pas à `package.json`, n'ajoute aucune dépendance.
- Ne commite jamais `public/`, `out/`, audio, photos. `git status` avant chaque commit. Commits en français, un par étape.
- Respect de la communauté soufie : rien de folklorique. Le verset (Coran 13:28) reste en arabe uthmani exact
  (police Amiri Quran), sans animation, fondu seul. Toute question religieuse va dans les questions, jamais tranchée par toi.
- Les sources ne s'affichent jamais à l'écran, seulement dans la description.
- Version sans face caméra (`faceless`), comme l'anglais.

## Ce qu'il faut livrer

1. **Texte** : `script/v01_ur.json` (mêmes `id`, `pause`, `lead`, `tail` que `script/v01_en.json`), découpé dans le
   texte du fichier playground sans rien y changer, et `src/data/v01_ur.groups.json`.
2. **Voix assemblée** : `tools/assemble_vo.py` (pauses du script, coupes seulement dans le silence entre deux segments,
   jamais à l'intérieur ; fondus de 5 à 10 ms ; **`--verse-hold 0`**). Vérifie que les deux « استغفراللہ » chuchotés
   sont entiers. **Ils sont très bas dans la prise** (vers 565,2 à 567,8 s du mp3 : environ -54 dB de moyenne, contre
   -26 dB pour la parole autour) : remonte seulement ce passage d'environ 12 dB, avec des fondus, pour qu'on les entende
   comme un chuchotement, sans saturer. Note le gain exact dans le manifeste. Commite le manifeste d'assemblage dans `src/data/v01_ur.assembly.json`, avec l'empreinte sha256 du WAV
   produit : Claude reconstruira le même fichier sur le Mac et comparera l'empreinte.
3. **Alignement** : `python3 tools/vo.py align script/v01_ur.json <wav assemblé>` → `src/data/v01_ur.vo.json`
   (Whisper « small », langue `ur`). Contrôle : 79 segments, mots dans l'ordre, aucun trou anormal. Mots que Whisper
   entend mal : امام غزالی، الکرکری، ناظور، میڈیامیٹری، استغفراللہ، خلوت، les nombres écrits en lettres. Aligne le mot du
   script, pas ce que Whisper croit entendre.
4. **Écran en ourdou** : `src/i18n/ur.ts`, `Lang` étendu, tous les textes traduits (Kinetic, fiches, carte, HUD, écran
   de fin, pages sans face caméra, Shorts). Droite à gauche partout. Police Nastaliq : déclare
   `fonts/NotoNastaliqUrdu-Regular.ttf` dans `src/fonts.ts` (Claude posera le fichier sur le Mac), interligne plus grand,
   vérifie que rien ne déborde avec les hauteurs du Nastaliq. Chiffres occidentaux par défaut, question posée.
   Le français et l'anglais ne bougent pas d'un pixel.
5. **Le verset** : arabe uthmani, avec dessous la traduction ourdou dite par la voix (« سن لو، اللہ کی یاد ہی میں دلوں کا
   چین ہے »), même place et même style que la traduction anglaise. Il s'affiche comme en français (dès « قرآن اسے ایک جملے
   میں کہتا ہے », `verseIn = at('p52') - 10`) et reste pendant la phrase, puis environ 1 s. Musique et bruitages coupés
   sous le verset, la voix continue.
6. **3D recalée** : généralise `tools/remap3d_en.py` (`--lang`), produis `src/data/remap3d_ur.json`, et fais lire à
   `Shot3D` la table de la langue. Plans à pas 1 : image la plus proche, jamais de fondu (sinon le pion se dédouble).
7. **Ouverture** : `V01-UR` ouvre sur la maquette dès l'image 0, comme l'anglais. L'intro Pixar sera posée sur le Mac.
8. **Repères de finition** dans `docs/v01-ur-finition.md`, tous en temps voix ET en images vidéo (vidéo = voix + 0,8 s) :
   - intro Pixar : « پندرہ منٹ », « اکیلے », « نہ فون », « بس آپ اور آپ کے خیالات », « ایک بٹن », « بجلی کا جھٹکا »,
     « تین میں سے دو مردوں » (début et fin de la phrase) ;
   - les 6 passages de `docs/v01-finition.md` : début et fin, et les mots repères dedans : film muet (« جیسے ہی لکھاری
     تھکتا ہے ») ; nuit (« آنکھ کھلتی ہے », « پہلا ردِعمل », « اسکرین ») ; khalwa VHS (« لفظی مطلب », « تنہائی ») ;
     exercice 1 (« چالیس », « دو منٹ », « ایک », « دو ») ; exercice 2 (« پانچ », « چالیس سیکنڈ », « بس وقت دیکھنے
     کے لیے ») ; veste (fenêtre 6, `aroll6`) ;
   - la liste `sfxOff` prête à coller (les 5 passages animés, plus `[0, 30]`).
9. **Shorts** : `short-bouton-ur`, `short-pascal-ur`, `short-exercice-ur` dans `src/Root.tsx`, sous-titres ourdou de
   droite à gauche, carton final traduit.
10. **Sous-titres** : `tools/srt.py` adapté à l'ourdou ; commite le résultat dans `docs/v01-ur.srt`.
11. **Description** : `docs/v01-ur-description.md` : titre, description, chapitres calculés sur le vrai alignement,
    sources (titres d'origine : al-Munqidh min al-ḍalāl, Iḥyāʾ ʿulūm al-dīn, Kitāb ādāb al-ʿuzla ; traduction du verset :
    Kanz ul-Iman, Ahmed Raza Khan), trois textes courts pour les miniatures.

## Contrôles

- `npx tsc --noEmit` passe. Ton script de repères (sur le modèle de `tools/check_v01_en.mjs`) passe sur le vrai alignement.
- `docs/v01-ur-images-fixes.md` : les images que Claude doit regarder (début, milieu, fin de chaque partie, toutes les
  pages de texte, la carte, le verset, l'écran de fin, chaque Short).

## À la fin

- `docs/v01-ur-questions.md` et `docs/v01-ur-etat.md` à jour (fait, pas fait, ce que Claude doit lancer sur le Mac).
- Pousse `studio/v01-ur`.
- Résumé court en français : ce qui est fait, ce que tu n'as pas pu faire et pourquoi, les questions pour Billel.
