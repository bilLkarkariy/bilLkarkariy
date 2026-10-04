# Vidéo 1 EN : caler la vraie voix anglaise (brief pour Codex)

Billel a enregistré la voix anglaise avec son clone ElevenLabs, en une seule prise, à partir de
`script/v01_texte_playground_balises_en.txt`. Ta mission : que le texte, la voix et le montage `V01-EN`
tombent juste, mot par mot. Tu travailles sur la branche `studio/v01-en`, dans ce dossier.

Relis `docs/v01-en-etat.md` (ce que tu as déjà fait) et `docs/reprise-agent.md` (règles).

## Règles absolues (inchangées)

- Ne lis jamais `.env`. Aucun appel ElevenLabs, aucune voix régénérée. Jamais la voix « Sidi Mounir ».
- Tu peux écrire dans `public/vo/` (et seulement là, dans `public/`) : c'est le dossier de la voix. Rien d'autre
  dans `public/`, `node_modules/`, `.venv/`.
- Pas de réseau dans ton bac à sable : lance Python avec `HF_HUB_OFFLINE=1` (le modèle Whisper « small » est déjà
  en cache sur ce Mac).
- Ne touche pas à `package.json`. Ne commite jamais `public/`, `out/`, photos, rushes. `git status` avant chaque commit.
  Commits en français, un par étape. Ne pousse pas : Claude poussera.
- Le verset (Coran 13:28) reste en arabe uthmani exact (Amiri Quran), sans animation, fondu seul, aucun son dessous.
  Les sources ne s'affichent jamais à l'écran.
- Ne lance aucun calcul 3D (Blender). Tu peux préparer les commandes, c'est Claude qui les lancera.

## La matière

- `public/vo/v01_en_brut.wav` : la prise brute, 48 kHz, mono, 24 bits, 584,6 s. Convertie sans retouche depuis
  `~/Downloads/ElevenLabs_2026-10-04T08_30_48__s50_v4.mp3`. Ne la modifie pas.
- `out/v01_en_brut_transcription.txt` : transcription Whisper « small » de cette prise (repère, pas une vérité).
- Le texte collé sur la plateforme est celui de `script/v01_texte_playground_balises_en.txt` (sans les lignes
  d'en-tête ni les séparateurs ═══). Il suit mot pour mot `script/v01_en.json`, sauf deux points ci-dessous.

## Décision de Billel : le verset

Il a choisi **Pickthall** : “Verily in the remembrance of Allah do hearts find rest!” (on l'entend vers 427–435 s).
- Complète `s63` avec cette phrase, retire `_pending`.
- À l'écran, montre cette traduction comme la version FR montre la sienne sous l'arabe (même place, même style).
- Crédite la traduction dans `docs/v01-en-description.md` (Marmaduke Pickthall, *The Meaning of the Glorious Koran*, 1930).
- Mets à jour `docs/v01-en-questions.md` (question tranchée).

## Étape 1 : rythmer la prise sur les pauses du script

La prise est continue : les respirations entre segments sont celles d'ElevenLabs, pas les `pause` du script.
Le montage a besoin des pauses du script. Exemples critiques : le silence du plateau du verset (aucune voix pendant
que l'arabe est à l'écran), les 2 s de silence après « When was it? », les 2,5 s après `s64`.

1. Aligne les mots de la prise brute (même moteur que `tools/vo.py align`).
2. Trouve la fin de chaque segment `s1…s79` dans l'audio. Coupe uniquement dans le silence entre deux segments,
   jamais dans un mot.
3. Reconstruis `public/vo/v01_en.wav` (même format que la brute) : chaque segment tel quel, puis un silence égal à sa
   `pause` dans `script/v01_en.json` (avec `lead` au début et `tail` à la fin). Fondus de 5 à 10 ms à chaque coupe,
   pour éviter les clics.
4. **Piège connu :** en français, l'assemblage a coupé les « Astaghfiroullah » chuchotés, parce que le découpage par
   énergie a pris le chuchotement pour du silence. Ne rogne jamais l'intérieur d'un segment. Vérifie que les deux
   « Astaghfirullah… » chuchotés (vers 512–519 s dans la brute) sont bien présents dans le WAV final, avec leur durée.
5. Écris le script de cet assemblage dans `tools/` (réutilisable), en commentant en français comme le reste du dépôt.

## Étape 2 : aligner

```bash
HF_HUB_OFFLINE=1 python3 tools/vo.py align script/v01_en.json public/vo/v01_en.wav
```

Contrôle `src/data/v01_en.vo.json` :
- les 79 segments, mots dans l'ordre, aucun mot manquant, pas de trou anormal ;
- les mots que Whisper entend mal : « khalwa » (il entend « chalwa »), « dhikr », « Astaghfirullah »,
  « Médiamétrie », « Faouzi », « al-Karkari », « Nador », « Karkariya » ;
- les nombres (15, 2014, 12 sur 18, 6 sur 24, 190, 42, 2010, 2,250, 80 %, 20, 350, 1095, 300, 2007, 40, 18 à 77).

**À vérifier à l'oreille, et à signaler à Billel si c'est le cas :** la transcription donne « In Sufism, you practice
the remembrance. » là où le script dit « In Sufism, you practise dhikr. Remembrance. » Ça peut être une erreur de
Whisper, ou le clone a pu avaler « dhikr ». Écoute le passage (vers 400–410 s dans la brute) par mesure d'énergie et par
la durée des mots. N'invente rien : si le mot manque, note-le dans `docs/v01-en-questions.md`.

## Étape 3 : le montage suit la voix

- Relance `node tools/check_v01_en.mjs` : les 278 repères EN doivent se résoudre sur le vrai alignement.
- La voix EN est jouée dès que le JSON contient un chemin audio : vérifie que `V01-EN` la joue bien et que la durée de
  la composition suit la nouvelle voix.
- Musique, bruitages et silences : même logique que le FR (pas de son sous le verset).
- Recale les trois Shorts EN, les chapitres de `docs/v01-en-description.md` et génère les sous-titres anglais
  (`tools/srt.py`, à adapter à l'anglais si besoin : nombres en chiffres, ponctuation) vers `out/package_en/v01.en.srt`.
- 3D : liste les plans dont les mots de calage ont bougé, avec pour chacun la plage d'images à recalculer et une
  estimation du temps (le FR prend environ 7 s par image sur le GPU). Si tu vois une façon de réutiliser les images
  FR en les recalant dans le temps au lieu de tout recalculer, propose-la. Ne lance rien.
- `npx tsc --noEmit` doit passer. Ton bac à sable ne peut pas lancer Chromium : prépare la liste des images fixes à
  regarder (début, milieu, fin de chaque partie et tous les points sensibles), Claude les rendra.

## À la fin

Mets à jour `docs/v01-en-etat.md` : ce qui est fait, ce que tu as entendu ou pas, ce qui reste (3D, images fixes,
rendu). Commits séparés : verset ; assemblage de la voix ; alignement ; montage, Shorts, description, sous-titres ; état.
