# Vidéo 1 AR : caler la vraie voix arabe (brief pour Codex)

Billel a enregistré la voix arabe avec son clone ElevenLabs, en une seule prise, à partir de
`script/v01_texte_playground_balises_ar.txt`. Ta mission : que le texte, la voix et le montage `V01-AR` tombent juste,
mot par mot. Tu travailles sur la branche `studio/v01-ar`, dans ce dossier (`billkarkariy-ar/studio`).

Relis `docs/v01-ar-etat.md` (ce que l'agent précédent a fait), `docs/reprise-agent.md` (règles) et, pour la méthode,
la version ourdoue qui vient d'être calée de la même façon : `../../billkarkariy-ur/studio/docs/v01-ur-voix-brief.md`,
`../../billkarkariy-ur/studio/docs/v01-ur-etat.md` et ses outils (`tools/assemble_vo.py --lang`). Reprends ce qui marche
déjà en ourdou plutôt que de le réécrire.

## Règles absolues

- Ne lis jamais `.env`. Aucun appel ElevenLabs, aucune voix régénérée. Jamais la voix « Sidi Mounir ».
- Tu peux écrire dans `public/vo/` (et seulement là, dans `public/`). Rien d'autre dans `public/`, `node_modules/`, `.venv/`.
- Pas de réseau : lance Python avec `HF_HUB_OFFLINE=1` (Whisper « small » est en cache sur ce Mac).
- Ne touche pas à `package.json`. Ne commite jamais `public/`, `out/`, audio. `git status` avant chaque commit.
  Commits en français, un par étape. Ne pousse pas : Claude poussera.
- Le verset (Coran 13:28) reste en arabe uthmani exact (Amiri Quran), fondu seul, aucun son dessous (ni musique ni
  bruitage). Aucun calcul 3D (Blender), jamais. Le français et l'anglais ne doivent pas bouger (`--baseline`).

## La matière

- `public/vo/v01_ar_brut.wav` : la prise brute, 48 kHz, mono, 24 bits, 626,3 s. Convertie sans retouche depuis
  `~/Downloads/bilKarkariy_ep1_ar.mp3`. Ne la modifie pas.
- `../../billkarkariy/studio/out/voix_ar_ur/transcription_ar.txt` : transcription Whisper « small » de la prise
  (repère seulement). La voix est complète : verset vers 470 s, « فكان لساني لا ينطق بكلمة واحدة » vers 405 s,
  « هذا أمر نزل بالقلب » vers 412 s, les deux « أستغفر الله » chuchotés vers 554 à 558 s (bien audibles, pas de gain).

## Le verset

La voix récite le verset. Il s'affiche comme en français : dès « والقرآن يقولها في جملة واحدة »
(`verseIn = at('p52') - 10`), il reste pendant la récitation, puis environ 1 s. **Pas de silence ajouté** :
`--verse-hold 0`. Arabe uthmani seul, rien dessous. Musique et bruitages coupés sous le verset ; la voix continue.

## Étapes

1. **Assembler** : `tools/assemble_vo.py --lang ar` (pauses du script, coupes seulement dans le silence entre deux
   segments, jamais dans un mot ni à l'intérieur d'un segment, fondus de 5 à 10 ms). Écris `public/vo/v01_ar.wav` et
   le manifeste `src/data/v01_ar.assembly.json` (coupes, pauses, empreinte sha256 du WAV).
2. **Aligner** : `HF_HUB_OFFLINE=1 .venv/bin/python tools/vo.py align script/v01_ar.json public/vo/v01_ar.wav`.
   Contrôle `src/data/v01_ar.vo.json` : `audio` renseigné, 79 segments, mots dans l'ordre, aucun trou anormal, nombre
   de mots interpolés le plus bas possible (note-le). Mots que Whisper entend mal : الكركري، الناظور، ميدياميتري،
   الغزالي، les nombres écrits en lettres. Aligne le mot du script.
3. **Montage** : `node tools/check_v01_ar.mjs` passe sur le vrai alignement, verset muet (musique et bruitages),
   français et anglais inchangés. `npx tsc --noEmit` passe.
4. **3D** : `python3 tools/remap3d.py --lang ar` (aucun Blender), commite `src/data/remap3d_ar.json`.
5. **Paquet** : chapitres de `docs/v01-ar-description.md` recalculés ; sous-titres
   `python3 tools/srt.py src/data/v01_ar.vo.json docs/v01-ar.srt` (commités).
6. **Repères de finition** (`docs/v01-ar-finition.md`), en temps voix ET en images vidéo (vidéo = voix + 0,8 s) :
   - intro Pixar : « خمس عشرة دقيقة », « وحدك », « لا هاتف », « أنت وأفكارك », « وزرٌّ », « بشحنة كهربائية »,
     « ضغط عليه رجلان من كل ثلاثة » (début et fin de la phrase) ;
   - les 6 passages de `../../billkarkariy-en/studio/docs/v01-finition.md` : début et fin, et les mots repères dedans :
     film muet (« وما إن يتعب ») ; nuit (« تستيقظ », « أول ردّ فعل », « الشاشة ») ; khalwa VHS (« كلمة تعني »,
     « الانفراد ») ; exercice 1 (« أربعين », « دقيقتين », « واحد », « اثنان ») ; exercice 2 (« خمسة », « أربعين ثانية »,
     « فقط لأعرف الساعة ») ; veste (fenêtre 6, `aroll6`) ;
   - la liste `sfxOff` prête à coller (les 5 passages animés, plus `[0, 30]`).

## À la fin

Mets à jour `docs/v01-ar-etat.md` et `docs/v01-ar-images-fixes.md` (sur le vrai alignement). Commits séparés :
outils ; voix assemblée et manifeste ; alignement ; verset ; recalage 3D ; description, sous-titres, finition ; état.
