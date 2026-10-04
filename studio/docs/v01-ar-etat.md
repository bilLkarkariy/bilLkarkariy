# V01 AR — état

4 octobre 2026 — branche `studio/v01-ar`. Brief exécuté : `docs/v01-ar-voix-brief.md`.
**Vraie voix assemblée et alignée ; montage et livrables recalés.** V01-AR : **20 503 images à 30 i/s,
soit 11:23.433**, écran de fin compris. Sept commits locaux par étape ; aucun push.

## Voix et alignement

| Livrable | Résultat |
|---|---|
| `public/vo/v01_ar_brut.wav` | Prise originale intacte : 626.286 s, WAVEX, 48 kHz, mono, PCM 24 bits. |
| `public/vo/v01_ar.wav` | **677.506 s** ; même format, 79 segments, 78 jonctions dans le silence, 65,6 s de pauses prescrites, lead 0,8 s et tail 1,5 s. |
| `src/data/v01_ar.assembly.json` | Coupes en échantillons, pauses, empreintes SHA-256, fondus de 8 ms. Copie identique à côté du WAV. **Aucun gain, aucun insert de silence pour le verset.** |
| `script/v01_ar.audio-review.json` | Reprises isolées documentées, liées à l’empreinte de la brute : question, répétition des techniques, deux chuchotements, invitation. La répétition s50/s51 est protégée par le silence mesuré. |
| `src/data/v01_ar.vo.json` | `audio: "vo/v01_ar.wav"`, `language: "ar"`, sans estimation ; **79 segments, 1 211 mots** du texte figé, ordonnés et bornés par les coupes. Aucun trou interne supérieur à 1,2 s. |

Empreintes SHA-256 :

- Brute : `bf6581f9c9e3c323501d75e13c60674b12d28b15a1dc927f1707a21058847e4f`.
- WAV assemblé : `e9b9c194564ebddedc3d49f1e7da99a1aa4be341521459899036e1427c447bb9`.

Les intérieurs des 79 segments sont copiés **bit pour bit**, hors fondus de coupe. Les silences de jonction
mesurent au plus −63,69 dBFS RMS. Aucun mot ni intérieur de segment n’a été rogné. Le WAV et le manifeste
ont été reproduits à l’identique. La révision de l’invitation n’a changé aucun échantillon du WAV.

### Reconnaissance et incertitudes

Whisper **small**, CPU int8, fichiers locaux seulement. La première reconnaissance multibeam a été interrompue
après un ralentissement prolongé ; une forte activité d’échange mémoire était mesurée sur le Mac. La passe arabe
livrée utilise deux threads, `beam_size=1`, `temperature=0`, `condition_on_previous_text=false`. Ces paramètres
sont consignés dans les caches et dans `alignment.decoding`. Les paramètres anglais restent inchangés.

Deux observations du même signal : prise brute et WAV final. Les temps source sont transférés par les coupes
exactes du manifeste ; le choix par segment privilégie le moins d’interpolations, puis de répartitions et de
substitutions. **64 segments** retiennent le WAV final, **15** la source.

- **1 mot interpolé sur 1 211 (0,083 %)** : `عام`, s57, **420.860 → 421.260 s voix**
  (**421.660 → 422.060 s vidéo**, images 12650 → 12662). Whisper entend `عن`,
  y compris lors de la dernière reprise isolée du passage de Bagdad. Le mot figé du script est conservé.
- **24 mots répartis** dans des blocs reconnus dont Whisper change les espaces ou les formes ; leurs bornes sont approximatives.
- Les nombres reconnus en chiffres sont aussi répartis sur leurs mots ; une reconnaissance n’est pas une preuve de précision phonétique absolue.
- **56 substitutions rapprochées** : le texte du script est conservé, pas l’orthographe proposée par Whisper.
- Audit complet dans `alignment.interpolated` et `alignment.segment_recognition`. Le nom historique
  `interpolated` contient aussi les substitutions et répartitions : ses 81 entrées ne sont pas 81 interpolations.

La reprise de l’invitation retrouve `مالذي`, réparti sur `ما الذي`. Les nombres en chiffres, y compris les chiffres
arabes orientaux, sont comparés aux mots du script. Les noms propres restent ceux du texte figé.

### Chuchotements

Les deux `أستغفرُ الله` sont conservés **sans gain**, sans normalisation ni traitement de voix. La reconnaissance
continue en avait omis un ; une reprise isolée sans amplification retrouve les deux. Les mots tronqués aux bords
d’un extrait d’analyse sont exclus de la correction grâce à `replace_range`.

Leurs temps voix et vidéo sont dans `v01-ar-finition.md`. Les extraits de contrôle locaux sont dans
`out/validation/vo-ar/chuchotements-brut.wav` et `chuchotements-final.wav`. Les mesures et la reconnaissance ne
remplacent pas une écoute humaine ; aucune écoute humaine n’a été effectuée dans cette session. Ces extraits
contiennent toute l’étape 4 (s69), pour garder les deux chuchotements complets et leur contexte.

## Montage et livrables

- **Verset** : images **15052 → 15270** (fin exclusive), dès `at('p52') - 10`, pendant l’introduction et la récitation,
  puis une seconde après la dernière parole. Uthmani exact, Amiri Quran, fondu seul, rien dessous. **La voix
  continue ; musique et bruitages coupés.** Le plan dhikr s’arrête dès l’entrée du fondu. Aucun `silent_verse` ;
  assemblage `--verse-hold 0`. Français et anglais inchangés.
- **3D** : `tools/remap3d.py --lang ar`, sept correspondances monotones et bornées dans `src/data/remap3d_ar.json`.
  Réemploi des images françaises, aucun Blender. Dhikr borné à l’entrée du verset. Recalcul anglais identique
  à l’octet. Le repère d’image fixe `meublee` vise désormais le milieu du plan 3D, après le mot « meublé ».
- **Description** : chapitres recalculés dans `docs/v01-ar-description.md` (début du groupe + 0,8 s, seconde inférieure).
- **Sous-titres** : `docs/v01-ar.srt`, **266 entrées**, temps vidéo, chiffres occidentaux et marques RTL ; temps
  croissants, aucun chevauchement, tous dans la composition.
- **Finition** : `docs/v01-ar-finition.md`, intro Pixar, six fenêtres, mots internes, temps voix et images vidéo,
  `sfxOff` prêt à coller pour les cinq passages animés et `[0,30]`.
- **Images fixes** : `docs/v01-ar-images-fixes.md`, **75 vues longues + 11 sans visage + 9 Shorts**, sur le vrai alignement.
- **Shorts** : bouton **3 755** images ; Pascal **2 174** ; exercice **2 803**.

## Vérifications

- Audio : empreintes, format, copie PCM, pauses, lead/tail, absence de gain et mots bornés/ordonnés : réussi.
- Montage : **313 repères**, **1 296 instants AR**, **1 367 sans visage**, textes arabes et direction RTL vérifiés.
- Verset : texte seul et sons de fond à zéro sur chacune de ses **218 images**, voix à volume 1 ; plateau immobile.
  Contrôle ciblé supplémentaire avec la 3D activée. Aucun PNG Remotion n’a été rendu ou inspecté.
- Comparaison `--baseline` : **1 733 instants FR/EN identiques** (durées, HTML, styles, événements audio simulés).
  Référence : `src` du commit de départ **933a712**, copié dans `out/validation/ar-baseline/src`.
- Outils anglais : alignement, WAV et manifeste avant/après identiques à l’octet. Plans 3D anglais identiques.
- `npx tsc --noEmit` : réussi. Avertissement React préexistant sur les clés de `FilmStrip` dans le contrôle HTML.
- Brute, voix FR/EN, script arabe figé et `package.json` : empreintes inchangées.
- Aucun `.env` lu, réseau, appel ElevenLabs, voix régénérée ou calcul Blender. Aucune modification de
  `package.json`, `node_modules/` ou `.venv/`. Dans `public/`, seules écritures dans `public/vo/`. Aucun audio,
  `public/` ou `out/` commité.

Commandes de reproduction, depuis `studio/` :

```bash
HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 .venv/bin/python tools/assemble_vo.py script/v01_ar.json public/vo/v01_ar_brut.wav public/vo/v01_ar.wav --lang ar --verse-hold 0
cp public/vo/v01_ar.assembly.json src/data/v01_ar.assembly.json
HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 .venv/bin/python tools/vo.py align script/v01_ar.json public/vo/v01_ar.wav
HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 .venv/bin/python tools/check_vo_ar.py
node tools/check_v01_ar.mjs --baseline out/validation/ar-baseline/src
HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 python3 tools/remap3d.py --lang ar
HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 python3 tools/srt.py src/data/v01_ar.vo.json docs/v01-ar.srt
HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 .venv/bin/python tools/update_v01_ar_docs.py
npm_config_offline=true npx tsc --noEmit
```

Rapports locaux dans `out/validation/` et `out/validation-ar/`. `update_v01_ar_docs.py` recalcule description,
finition et liste d’images à partir de l’alignement final et du rapport du contrôleur.

## À transmettre à Claude

1. Rendre et regarder les PNG de `v01-ar-images-fixes.md`, notamment les quatre plans 3D, les petites étiquettes,
   les interlignes, les fiches et la colonne de l’exercice. Les vérifications HTML ne prouvent pas le rendu PNG.
2. Écouter les noms propres, les nombres, `عام`, les 24 répartitions et les deux chuchotements. Aucune écoute humaine
   ni inspection du mix vidéo final n’a été effectuée ici.
3. Rendre V01-AR avec les propriétés de `v01-ar-finition.md`, puis poser intro Pixar, cinq passages animés et veste
   selon les repères fournis ; écouter et masteriser le résultat, avec la voix seule sous le verset.
4. Finaliser les Shorts, les miniatures et le paquet. Les autres points éditoriaux restent dans `v01-ar-questions.md` ;
   les décisions voix et verset du présent brief sont appliquées.
5. Claude pourra pousser les sept commits locaux. Rien n’a été poussé ici.
