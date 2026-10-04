# Vidéo 1 en arabe : tout préparer pour le rendu (agent cloud)

Tu travailles sur le dépôt GitHub `bilLkarkariy/bilLkarkariy` (public). Le projet vidéo est dans `studio/`.
C'est la vidéo 1 de la chaîne bilLkarkariy : « Pourquoi tu n'arrives plus à rester seul avec toi-même ».
Elle existe en français et en anglais (validées). Tu fais **la version arabe** (arabe standard moderne).
Un autre agent fait l'ourdou en parallèle : ne touche jamais à sa branche.

## Ta mission

Rendre la version arabe **prête à rendre** : voix calée mot par mot, textes à l'écran en arabe, écriture de droite
à gauche, 3D recalée, fenêtres des passages animés, Shorts, sous-titres, description.
Tu ne peux pas produire le fichier vidéo final : `public/` (images 3D, sons, polices, voix, photos) n'est pas dans git.
Claude fera le rendu et la finition sur le Mac de Billel à partir de ce que tu livres (voir `studio/docs/v01-finition.md`).

## Branche

- Si `origin/studio/v01-ar` existe déjà (un premier agent a commencé), reprends-la : lis d'abord
  `studio/docs/v01-ar-etat.md` et `studio/docs/v01-ar-questions.md`, ne refais pas ce qui est fait.
- Sinon, crée `studio/v01-ar` à partir de `studio/v01-en`.
- Pousse uniquement `studio/v01-ar`. Ne fusionne rien.

## À lire avant de commencer

`studio/docs/reprise-agent.md`, `studio/docs/v01-langue-brief.md` (la base), `studio/docs/v01-finition.md`,
`studio/docs/v01-en-etat.md`, `studio/docs/v01-en-3d.md`. **Ce prompt l'emporte** là où ils diffèrent.

## Fichier joint par Billel

`bilKarkariy_ep1_ar.mp3` : la voix arabe complète (10:26, 44,1 kHz, mono), enregistrée avec son clone ElevenLabs
à partir de `studio/script/v01_texte_playground_balises_ar.txt`. Elle dit exactement ce texte : verset, deux citations
d'al-Ghazali, deux « أستغفر الله » chuchotés vers 550 à 558 s.
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

1. **Texte** : `script/v01_ar.json` (mêmes `id`, `pause`, `lead`, `tail` que `script/v01_en.json`), découpé dans le
   texte du fichier playground sans rien y changer, et `src/data/v01_ar.groups.json`.
2. **Voix assemblée** : `tools/assemble_vo.py` (pauses du script, coupes seulement dans le silence entre deux segments,
   jamais à l'intérieur ; fondus de 5 à 10 ms ; **`--verse-hold 0`**). Vérifie que les deux « أستغفر الله » chuchotés
   sont entiers. Commite le manifeste d'assemblage dans `src/data/v01_ar.assembly.json`, avec l'empreinte sha256 du WAV
   produit : Claude reconstruira le même fichier sur le Mac et comparera l'empreinte.
3. **Alignement** : `python3 tools/vo.py align script/v01_ar.json <wav assemblé>` → `src/data/v01_ar.vo.json`
   (Whisper « small », langue `ar`). Contrôle : 79 segments, mots dans l'ordre, aucun trou anormal. Mots que Whisper
   entend mal : الكركري، الناظور، ميدياميتري، الغزالي، les nombres écrits en lettres. Aligne le mot du script, pas ce
   que Whisper croit entendre.
4. **Écran en arabe** : `src/i18n/ar.ts`, `Lang` étendu, tous les textes traduits (Kinetic, fiches, carte, HUD, écran
   de fin, pages sans face caméra, Shorts). Droite à gauche partout. Police Amiri. Chiffres occidentaux par défaut,
   question posée. Le français et l'anglais ne bougent pas d'un pixel.
5. **Le verset** : la voix arabe **récite** le verset. Il s'affiche comme en français (dès « والقرآن يقولها في جملة
   واحدة », `verseIn = at('p52') - 10`) et reste pendant la récitation, puis environ 1 s. Arabe uthmani seul, aucune
   traduction dessous. Musique et bruitages coupés sous le verset, la voix continue.
6. **3D recalée** : généralise `tools/remap3d_en.py` (`--lang`), produis `src/data/remap3d_ar.json`, et fais lire à
   `Shot3D` la table de la langue. Plans à pas 1 : image la plus proche, jamais de fondu (sinon le pion se dédouble).
7. **Ouverture** : `V01-AR` ouvre sur la maquette dès l'image 0, comme l'anglais. L'intro Pixar sera posée sur le Mac.
8. **Repères de finition** dans `docs/v01-ar-finition.md`, tous en temps voix ET en images vidéo (vidéo = voix + 0,8 s) :
   - intro Pixar : « خمس عشرة دقيقة », « وحدك », « لا هاتف », « أنت وأفكارك », « وزرٌّ », « بشحنة كهربائية »,
     « ضغط عليه رجلان من كل ثلاثة » (début et fin de la phrase) ;
   - les 6 passages de `docs/v01-finition.md` : début et fin, et les mots repères dedans : film muet (« وما إن يتعب ») ;
     nuit (« تستيقظ », « أول ردّ فعل », « الشاشة ») ; khalwa VHS (« كلمة تعني », « الانفراد ») ;
     exercice 1 (« أربعين », « دقيقتين », « واحد », « اثنان ») ; exercice 2 (« خمسة », « أربعين ثانية »,
     « فقط لأعرف الساعة ») ; veste (fenêtre 6, `aroll6`) ;
   - la liste `sfxOff` prête à coller (les 5 passages animés, plus `[0, 30]`).
9. **Shorts** : `short-bouton-ar`, `short-pascal-ar`, `short-exercice-ar` dans `src/Root.tsx`, sous-titres arabes de
   droite à gauche, carton final traduit.
10. **Sous-titres** : `tools/srt.py` adapté à l'arabe ; commite le résultat dans `docs/v01-ar.srt`.
11. **Description** : `docs/v01-ar-description.md` : titre, description, chapitres calculés sur le vrai alignement,
    sources (titres arabes d'origine : المنقذ من الضلال، إحياء علوم الدين، كتاب آداب العزلة), trois textes courts pour
    les miniatures.

## Contrôles

- `npx tsc --noEmit` passe. Ton script de repères (sur le modèle de `tools/check_v01_en.mjs`) passe sur le vrai alignement.
- `docs/v01-ar-images-fixes.md` : les images que Claude doit regarder (début, milieu, fin de chaque partie, toutes les
  pages de texte, la carte, le verset, l'écran de fin, chaque Short).

## À la fin

- `docs/v01-ar-questions.md` et `docs/v01-ar-etat.md` à jour (fait, pas fait, ce que Claude doit lancer sur le Mac).
- Pousse `studio/v01-ar`.
- Résumé court en français : ce qui est fait, ce que tu n'as pas pu faire et pourquoi, les questions pour Billel.
