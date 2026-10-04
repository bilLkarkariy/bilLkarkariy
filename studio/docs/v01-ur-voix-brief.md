# Vidéo 1 UR : caler la vraie voix ourdoue (brief pour Codex)

Billel a enregistré la voix ourdoue avec son clone ElevenLabs, en une seule prise, à partir de
`script/v01_texte_playground_balises_ur.txt`. Ta mission : que le texte, la voix et le montage `V01-UR` tombent juste,
mot par mot. Tu travailles sur la branche `studio/v01-ur`, dans ce dossier (`billkarkariy-ur/studio`).

Relis `docs/v01-ur-etat.md` (ce qui est déjà fait par l'agent précédent), `docs/reprise-agent.md` (règles) et
`docs/v01-en-voix-brief.md` (comment la voix anglaise a été calée : même méthode).

## Règles absolues

- Ne lis jamais `.env`. Aucun appel ElevenLabs, aucune voix régénérée. Jamais la voix « Sidi Mounir ».
- Tu peux écrire dans `public/vo/` (et seulement là, dans `public/`). Rien d'autre dans `public/`, `node_modules/`, `.venv/`.
- Pas de réseau : lance Python avec `HF_HUB_OFFLINE=1` (Whisper « small » est en cache sur ce Mac).
- Ne touche pas à `package.json`. Ne commite jamais `public/`, `out/`, audio. `git status` avant chaque commit.
  Commits en français, un par étape. Ne pousse pas : Claude poussera.
- Le verset (Coran 13:28) reste en arabe uthmani exact (Amiri Quran), fondu seul, aucun son dessous (ni musique ni
  bruitage ; la voix, elle, continue).
- Aucun calcul 3D (Blender), jamais.
- Le français et l'anglais ne doivent pas bouger : vérifie-le comme l'agent précédent (`--baseline`).

## La matière

- `public/vo/v01_ur_brut.wav` : la prise brute, 48 kHz, mono, 24 bits, 640,9 s. Convertie sans retouche depuis
  `~/Downloads/bilKarkariy_ep1_urdu.mp3`. Ne la modifie pas.
- `out/voix_ar_ur/transcription_ur.txt` dans le dépôt français (`../../billkarkariy/studio/out/voix_ar_ur/`) :
  transcription Whisper « small » de cette prise, repère seulement. La voix est complète, du premier au dernier mot.
- **Les deux « استغفراللہ » chuchotés** (étape quatre de l'exercice) sont dans la prise vers **565,2 à 567,8 s**, mais très
  bas : environ -54 dB de moyenne, contre -26 dB pour la parole autour. Whisper ne les entend qu'après +24 dB.

## Décisions de Billel (elles changent ce qu'a fait l'agent précédent)

- **Le verset s'affiche pendant que la voix le dit, comme en français** : dès « قرآن اسے ایک جملے میں کہتا ہے »
  (`verseIn = at('p52') - 10`, comme la version française), il reste pendant la phrase « سن لو، اللہ کی یاد ہی میں دلوں
  کا چین ہے », puis environ 1 s. **Pas de silence ajouté** : `--verse-hold 0`. Retire le silence de 6 s de l'agent précédent
  (`src/montage/p4.tsx`, `src/V01.tsx`, `tools/check_v01_en.mjs`), pour l'ourdou seulement : l'anglais ne change pas.
- La voix ourdoue n'a pas de face caméra (`faceless`) ; l'intro Pixar sera posée par Claude après le rendu.

## Étape 1 : assembler la voix sur les pauses du script

1. Adapte `tools/assemble_vo.py` (et ce qu'il utilise, dont `tools/vo_alignment_en.py`) à l'ourdou par une option
   `--lang ur` : Whisper `language='ur'`, comparaison des mots avec `tokens(text, 'ur')` / `norm_arabic` de `tools/vo.py`.
   Rien ne doit changer pour l'anglais (sortie identique octet pour octet).
2. Coupe uniquement dans le silence entre deux segments, jamais dans un mot ni à l'intérieur d'un segment.
   Chaque segment tel quel, puis un silence égal à sa `pause` dans `script/v01_ur.json` (avec `lead` et `tail`).
   Fondus de 5 à 10 ms à chaque coupe.
3. **Remonte seulement les deux chuchotements** d'environ 12 dB (fondus de 20 à 50 ms autour), pour qu'on les entende
   comme un chuchotement, sans saturer. Écris le gain exact dans le manifeste.
4. Écris `public/vo/v01_ur.wav` (même format que la brute) et le manifeste `src/data/v01_ur.assembly.json` (coupes,
   pauses, gain des chuchotements, empreinte sha256 du WAV produit).

## Étape 2 : aligner

```bash
HF_HUB_OFFLINE=1 .venv/bin/python tools/vo.py align script/v01_ur.json public/vo/v01_ur.wav
```

Contrôle `src/data/v01_ur.vo.json` : `audio` renseigné, 79 segments, mots dans l'ordre, aucun trou anormal, nombre de
mots interpolés le plus bas possible (note-le). Mots que Whisper entend mal : امام غزالی، الکرکری، ناظور، میڈیامیٹری،
استغفراللہ، خلوت، les nombres écrits en lettres. Aligne le mot du script, pas ce que Whisper croit entendre.

## Étape 3 : le montage suit la voix

- `node tools/check_v01_en.mjs --lang ur --baseline …` : tous les repères se résolvent sur le vrai alignement ;
  verset muet (musique et bruitages) pendant sa fenêtre ; français et anglais inchangés.
- `python3 tools/report_3d_en.py --lang ur` puis `python3 tools/remap3d_en.py --lang ur` (aucun Blender), commite
  `src/data/remap3d_ur.json`.
- Chapitres de `docs/v01-ur-description.md` recalculés (même méthode que l'anglais).
- Sous-titres : `python3 tools/srt.py src/data/v01_ur.vo.json docs/v01-ur.srt` (commité) .
- `npx tsc --noEmit` passe.

## Étape 4 : les repères de finition (`docs/v01-ur-finition.md`)

Tous en temps voix ET en images vidéo (vidéo = voix + 0,8 s), sur le vrai alignement :
- intro Pixar : « پندرہ منٹ », « اکیلے », « نہ فون », « بس آپ اور آپ کے خیالات », « ایک بٹن », « بجلی کا جھٹکا »,
  « تین میں سے دو مردوں » (début et fin de la phrase) ;
- les 6 passages de `docs/v01-finition.md` (sur la branche `studio/v01-en`, ou dans `../../billkarkariy-en/studio/docs/`) :
  début et fin, et les mots repères dedans : film muet (« جیسے ہی لکھاری تھکتا ہے ») ; nuit (« آنکھ کھلتی ہے »,
  « پہلا ردِعمل », « اسکرین ») ; khalwa VHS (« لفظی مطلب », « تنہائی ») ; exercice 1 (« چالیس », « دو منٹ », « ایک », « دو ») ;
  exercice 2 (« پانچ », « چالیس سیکنڈ », « بس وقت دیکھنے کے لیے ») ; veste (fenêtre 6, `aroll6`) ;
- la liste `sfxOff` prête à coller (les 5 passages animés, plus `[0, 30]`).

## À la fin

Mets à jour `docs/v01-ur-etat.md` (fait, entendu ou pas, ce qui reste) et `docs/v01-ur-images-fixes.md` (recalculé sur
le vrai alignement). Commits séparés : outils d'assemblage ; voix assemblée et manifeste ; alignement ; verset ;
recalage 3D ; description, sous-titres, finition ; état.
