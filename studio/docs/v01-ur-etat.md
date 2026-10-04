# V01 UR — état

4 octobre 2026 — branche `studio/v01-ur`. Brief exécuté : `docs/v01-ur-voix-brief.md`. **Vraie voix assemblée et alignée ; montage et livrables recalés.** Durée de V01-UR : **21 072 images à 30 i/s, soit 11:42.400**, écran de fin compris. Sept commits locaux par étape ; aucun push.

## Voix et alignement

| Livrable | Résultat |
|---|---|
| `public/vo/v01_ur_brut.wav` | Prise originale intacte, 640,914 s ; WAVEX, 48 kHz, mono, PCM 24 bits. |
| `public/vo/v01_ur.wav` | **696,455 s**, même format. 79 segments conservés ; 78 jonctions dans le silence ; 65,6 s de pauses prescrites, lead 0,8 s et tail 1,5 s. Fondus de coupe de 8 ms. |
| `src/data/v01_ur.assembly.json` | Coupes en échantillons, pauses, gains, empreintes SHA-256. Copie locale identique dans `public/vo/v01_ur.assembly.json`. Aucun audio dans git. |
| `script/v01_ur.audio-review.json` | Reconnaissances isolées des deux chuchotements, protection de la coupe après s69, bornes mesurées et gain exact. Lié à l’empreinte de la prise. |
| `src/data/v01_ur.vo.json` | `audio: "vo/v01_ur.wav"`, `language: "ur"`, **79 segments, 1 836 mots** du script figé, tous ordonnés, durées positives et bornées par les coupes. Aucun trou interne de plus de 1,2 s. |
| Outils | `assemble_vo.py --lang ur`, `vo_alignment_en.py`, `vo_alignment_ur.py`, `vo.py align`, `check_vo_ur.py`. Whisper small, CPU int8, fichiers locaux seulement. Le chemin anglais reste compatible et identique. |

Empreintes SHA-256 :

- Prise brute : `7dc530f0c308557ee6dfcdd8d7ecffc6106c0bba95e4105e801cd40f73a9589d`.
- WAV assemblé : `c509a8bfc53a26f5726f15e7259088f2f92687fd09df22c78dbc11a740f492dc`.

### Les deux chuchotements

**+12 dB exactement**, seulement sur les deux occurrences chuchotées de « استغفراللہ », avec rampes de gain de 30 ms. Pas de normalisation globale. Les autres échantillons de parole restent identiques bit pour bit hors fondus de coupe.

| Occurrence | Gain dans la brute (s) | Gain dans le WAV final (s) | Niveau moyen avant → après | Crête après |
|---|---:|---:|---:|---:|
| 1 | 565.180 → 566.450 | 611.390 → 612.660 | -53.03 → -41.06 dBFS | -18.27 dBFS |
| 2 | 566.490 → 567.830 | 612.700 → 614.040 | -55.98 → -43.98 dBFS | -21.81 dBFS |

Les deux mots ont été reconnus séparément après **+24 dB d’analyse uniquement**. Ce gain d’analyse n’a pas été appliqué au WAV livré. Aucune saturation ; aucun rognage de l’intérieur de s69. Les extraits comparatifs sont dans `out/validation/vo-ur/chuchotements-{brut,final}.wav`.

### Incertitudes de l’alignement

La reconnaissance du WAV final est comparée, segment par segment, à celle de la prise brute, dont les temps sont transférés par les coupes exactes. 56 segments retiennent la reconnaissance finale, 23 celle de la source. Le choix privilégie le moins de mots interpolés, puis le moins de répartitions et de substitutions. Les variantes homophones sont comparées seulement après fixation des coupes.

- **24 mots interpolés** entre des voisins reconnus, sur 1 836 (1,31 %).
- **28 mots répartis dans un bloc reconnu** dont Whisper change la séparation des mots ; ces temps restent approximatifs.
- **111 substitutions rapprochées** : orthographe ou prononciation reconnue différente ; le mot du script est conservé.
- **3 bornes revues par enveloppe** : les deux chuchotements et le début de « پانچ ». Un écart de 10 ms entre reconnaissances a été borné au mot suivant.
- Audit complet dans `alignment.interpolated` et `alignment.segment_recognition` du JSON ; ce nom historique contient aussi les substitutions et répartitions, pas seulement les 24 interpolations.

Mots encore interpolés, à écouter en priorité :

| Segment | Mot(s) | Temps voix (s) |
|---|---|---:|
| s12 | مشق | 46.100 → 46.500 |
| s18 | سیدھی | 63.340 → 63.697 |
| s18 | سی | 63.697 → 63.840 |
| s18 | سوئیں | 65.500 → 65.760 |
| s26 | دس | 127.600 → 128.100 |
| s26 | نو | 128.460 → 128.760 |
| s32 | آگے | 200.360 → 200.680 |
| s32 | طے | 202.220 → 202.400 |
| s42 | ساڑھے | 297.475 → 297.960 |
| s43 | دوڑ | 311.175 → 311.435 |
| s46 | ڈھونڈنے | 342.650 → 343.010 |
| s51 | صدیاں | 380.920 → 381.520 |
| s57 | کیریئر | 434.490 → 434.970 |
| s59 | چڑھ | 460.710 → 460.950 |
| s60 | عظیم | 469.660 → 470.080 |
| s60 | وقف | 473.040 → 473.360 |
| s60 | الگ | 475.700 → 475.980 |
| s60 | بڑھ | 480.040 → 480.340 |
| s66 | دیں | 565.090 → 565.130 |
| s69 | لفظ | 598.970 → 599.330 |
| s69 | لفظ | 603.690 → 604.130 |
| s72 | مشق | 634.640 → 635.060 |
| s72 | مشق | 636.840 → 637.280 |
| s72 | چاہیں | 643.400 → 643.840 |

## Montage et livrables

- **Verset** : images **15430 → 15652** (fin exclusive), dès `at("p52") - 10`, pendant l’introduction et la traduction, puis une seconde après la dernière parole. Arabe uthmani exact, Amiri Quran, fondu seul. **La voix continue ; musique et bruitages coupés.** Aucun insert `silent_verse`, assemblage `--verse-hold 0`. Français et anglais inchangés.
- **Sans face caméra** : rendre avec `faceless: true` ; ouverture sur la maquette. L’intro Pixar sera posée par Claude après le rendu. Les fenêtres veste et invitation restent destinées aux inserts de finition.
- **3D** : `report_3d_en.py --lang ur` puis `remap3d_en.py --lang ur` exécutés. `src/data/remap3d_ur.json` définitif pour cet alignement ; 7 correspondances monotones et bornées. Dhikr arrêté à l’entrée du verset. Images FR réutilisées, aucun Blender. Rapport : `docs/v01-ur-3d.md`.
- **Chapitres** recalculés dans `docs/v01-ur-description.md`, par la même méthode que l’anglais.
- **Sous-titres** : `docs/v01-ur.srt`, **306 entrées**, temps vidéo (voix + 0,8 s), chiffres occidentaux, ponctuation ourdoue et marque RTL. Temps croissants, aucun chevauchement.
- **Finition** : `docs/v01-ur-finition.md`, repères intro Pixar, six remplacements, mots internes, bornes voix/vidéo et `sfxOff` prêt à coller.
- **Images fixes** : `docs/v01-ur-images-fixes.md`, 38 vues longues, 8 pages sans face caméra et 9 vues des Shorts recalculées. Police Noto Nastaliq Urdu présente sur le Mac.
- **Shorts** : `short-bouton-ur` 3 617 images ; `short-pascal-ur` 2 316 ; `short-exercice-ur` 2 864.

## Vérifications exécutées

```bash
HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 .venv/bin/python tools/assemble_vo.py script/v01_ur.json public/vo/v01_ur_brut.wav public/vo/v01_ur.wav --lang ur --verse-hold 0
HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 .venv/bin/python tools/vo.py align script/v01_ur.json public/vo/v01_ur.wav
HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 .venv/bin/python tools/check_vo_ur.py
node tools/check_v01_en.mjs --lang ur --baseline out/validation/ur-baseline/src
node tools/check_v01_en.mjs
HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 python3 tools/report_3d_en.py --lang ur
HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 python3 tools/remap3d_en.py --lang ur
HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 python3 tools/srt.py src/data/v01_ur.vo.json docs/v01-ur.srt
npx tsc --noEmit
```

- Contrôle audio : format conservé, empreintes, copie PCM, 79 pauses, lead/tail, deux gains, aucun écrêtage et mots bornés/ordonnés : réussi. Le WAV a été reproduit à l’identique.
- Contrôle montage : **302 repères**, **1 311 instants UR**, mode faceless sans image de visage, verset immobile et sources de fond muettes sur chaque image de sa fenêtre : réussi.
- Comparaison `--baseline` : **1 733 instants FR/EN identiques** (durées, HTML, styles et événements audio simulés). La référence est le `src` du commit de départ `27a19b7`.
- Régression des outils anglais : assemblage exécuté avec les outils avant/après ; **WAV et manifeste identiques octet pour octet**, alignement des mots identique. Plans 3D FR/EN identiques. Voix FR/EN, prise UR et `package.json` gardent leurs empreintes.
- TypeScript : réussi. SRT : 306 intervalles croissants, dans la composition, aucun chevauchement.
- Rapports locaux dans `out/validation/` ; aucun de ces fichiers lourds ni aucun audio commité. Avertissement React préexistant sur les clés de `FilmStrip` ; les contrôles terminent avec le code 0.
- `.env` jamais lu ; aucun réseau, appel ElevenLabs, génération vocale ou calcul Blender. Aucun changement dans `package.json`, `node_modules/`, `.venv/` ; seules écritures dans `public/vo/` pour les assets.

## Entendu / vu et reste pour Claude

**Pas d’écoute humaine effectuée.** La reconnaissance Whisper et les mesures du signal ne prouvent pas seules la qualité perceptive ou une précision phonétique absolue. Écouter en priorité les 24 interpolations, les 28 répartitions, les noms propres et les deux chuchotements.

**Pas de PNG Remotion ni de rendu vidéo inspecté dans cette session.** Les contrôles visuels sont des comparaisons HTML/styles ; ils ne remplacent pas l’inspection de la police, des raccords 3D et du rendu réel.

1. Rendre et regarder les PNG de `docs/v01-ur-images-fixes.md`, avec `FACELESS=1 WITH3D=1`.
2. Rendre V01-UR avec les propriétés de `docs/v01-ur-finition.md`, puis poser intro Pixar, cinq passages animés et veste selon les repères fournis.
3. Écouter et masteriser la vidéo finale, contrôler en particulier la voix seule sous le verset et le niveau des chuchotements.
4. Finaliser les trois Shorts à partir de la vidéo validée, les miniatures et le paquet. Les questions éditoriales restantes sont dans `docs/v01-ur-questions.md` ; les décisions voix/verset du présent brief sont appliquées.
5. Claude pourra pousser les commits locaux. Rien n’a été poussé ici.
