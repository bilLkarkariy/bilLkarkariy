# V01 EN — état de livraison après calage de la voix

4 octobre 2026 — branche `studio/v01-en`. Aucun push. **Les commits n’ont pas pu être créés** : le bac à sable interdit l’écriture dans le Git commun du worktree (`index.lock: Operation not permitted`). Cinq patches par étape et les commandes de commit sont préparés dans `out/validation/vo-en/commits/`.

La voix enregistrée est assemblée, alignée et branchée dans `V01-EN`. Les contrôles audio numériques, les repères, TypeScript et le bundle passent. **Pas de rendu vidéo final, de contrôle PNG ni d’écoute humaine effectués ici.** Les plans 3D, rushes et derniers contrôles restent à Claude et Billel.

## Résultat

| Livrable | État |
|---|---|
| `script/v01_en.json` | 79 segments, pauses/lead/tail et balise identiques au FR. `s63` contient Pickthall, `_pending` supprimé. Aucune génération autorisée. |
| `public/vo/v01_en_brut.wav` | Intact, 584,594 s, 48 kHz, mono, PCM 24 bits / WAVEX. |
| `public/vo/v01_en.wav` | **623,9242917 s**, même format. 79 intérieurs copiés exactement, fondus de 8 ms aux bords, pauses du script restaurées. |
| `public/vo/v01_en.assembly.json` | Manifeste des coupes, échantillons source/destination, pauses, empreintes et insert du verset. Non versionné. |
| `script/v01_en.audio-review.json` | Corrections liées à l’empreinte de la brute : reprise Whisper de Pascal et protection des chuchotements. |
| `tools/assemble_vo.py`, `tools/vo_alignment_en.py` | Assemblage reproductible et alignement EN hors ligne ; aucune normalisation ni retouche interne. La branche FR de `vo.py align` reste inchangée. |
| `src/data/v01_en.vo.json` | Alignement réel : **1 529 mots, 79 segments**, `audio: "vo/v01_en.wav"`. Une interpolation et deux corrections de durée des chuchotements sont signalées. |
| `V01-EN` | **18 885 images à 30 i/s : 10:29,50**, écran de fin de 6 s inclus. |
| `short-bouton-en` | Source `[24, 3077[`, 3 128 images avec carton final : **1:44,27**. |
| `short-pascal-en` | Source `[7161, 9119[`, 2 033 images : **1:07,77**. |
| `short-exercice-en` | Source `[14644, 17393[`, 2 824 images : **1:34,13**. |
| `docs/v01-en-description.md` | Crédit Pickthall (1930) et neuf chapitres recalés sur la vraie voix. |
| `out/package_en/v01.en.srt` | **318 sous-titres**, ponctuation du script, nombres anglais en chiffres, aucun chevauchement. Non versionné. |
| `docs/v01-en-3d.md` | Huit plans recensés, plages et mots déplacés, coûts GPU, proposition de réemploi et commandes séparées pour Claude. |
| `docs/v01-en-images-fixes.md` | **37 vues longues + 9 vues Shorts**, frames définitives et commandes PNG prêtes. |
| `out/bundle-en-voix/` | Bundle produit sans cache dans `node_modules`. Le WAV du bundle a la même empreinte que le WAV livré. |

Les trois miniatures EN préparées précédemment restent dans `out/package_en/miniatures/` ; elles ne sont pas modifiées ici. Aucun fichier privé, audio ou contenu de `out/` ne doit être commité.

## Audio et points sensibles

Empreinte SHA-256 de la brute : `f05932f6023e24d170c1802216eccb7306b0660eb4357f1abfa2256fbd667957`.

Empreinte du WAV final : `f621eca79abd80c2838485f0bbd8663f1b235ac341082aab606cf02a764fa12d`.

- Les 79 intérieurs sont identiques échantillon par échantillon entre les fondus. Les 79 pauses sont faites de zéros, avec le lead de 0,8 s et le tail de 1,5 s du script. Les pauses de 2 s après `s33` et 2,5 s après `s64` sont vérifiées.
- **Chuchotements :** le second était sous-estimé par Whisper et une première proposition de coupe traversait sa fin. Cette proposition a été corrigée avant livraison. `s69` conserve désormais la brute de 496,725 à 516,555 s, d’un seul tenant. Enveloppes protégées : **513,05–514,65 s (1,60 s)** et **515,04–516,50 s (1,46 s)**, copiées exactement dans le WAV final à **544,205–545,805 s** et **546,195–547,655 s**. Ces temps viennent de la reconnaissance et de l’enveloppe du signal, pas d’une écoute humaine. Ajouter 0,8 s pour les temps vidéo.
- **Dhikr :** Whisper small reconnaît `dhikr` dans la brute à 405,64–406,42 s, puis `remembrance` à 406,70–407,18 s. La passe sur le WAV final reconnaît également le mot. Il n’est pas déclaré avalé ou absent. L’écoute humaine reste à faire, sans régénérer de voix.
- **Pascal :** une reprise isolée de 230 à 241 s, sans prompt, retrouve les treize mots omis par la première transcription continue. La passe finale par segments retrouve la citation entière.
- Les graphies `khalwa`, `Médiamétrie`, `Mohamed`, `Faouzi`, `al-Karkari`, `Nador`, `Karkariya`, `dhikr`, `Astaghfirullah` suivent le script. Les variantes reconnues (`chalwa`, `Mediammetry`, `Mohammed`, `Fawzi`) servent au rapprochement des horaires. La reconnaissance des nombres gère les dates orales, les traits d’union et `2` + `,250`.
- Une seule interpolation reste : **s7, `shock`, 20,580–20,820 s** dans le WAV final ; Whisper écrit `shot` à cet endroit, dans la même plage. Le texte du script est conservé et cette limite est explicite dans le JSON.
- Les nombres demandés sont présents en chiffres dans le SRT : 15, 2014, 12/18, 6/24, 190, 42, 2010, 2,250, 80%, 20, 350, 1095, 300, 2007, 40 et 18–77. Aucun mot du script ne manque au JSON ; tous les horaires sont strictement positifs et ordonnés. Aucun trou interne supérieur à 1,2 s.

Extraits pour l’écoute : `out/validation/vo-en/dhikr-brut.wav`, `chuchotements-brut.wav`, `chuchotements-final.wav` et `pascal-brut.wav`. Le compte rendu ne prétend pas les avoir entendus.

## Verset : parole puis silence

Billel a choisi : “Verily in the remembrance of Allah do hearts find rest!” — Marmaduke Pickthall, *The Meaning of the Glorious Koran* (1930).

L’ancien montage coupait toute la voix de `s63`. La traduction enregistrée est maintenant audible avant l’affichage de l’arabe. La pause du script de 1,3 s est conservée ; **un insert silencieux supplémentaire de 6 s a été retenu provisoirement**, proposé pendant le travail sans réponse reçue, pour permettre la lecture du verset sans couper la parole. Il est déclaré dans le manifeste et le JSON, et réversible avec `--verse-hold 0` suivi des recalages. Le choix est consigné dans `docs/v01-en-questions.md`.

Le verset s’affiche aux images **13652 à 13825 incluses** (7:35,067–7:40,867), soit 5,8 s avec les fondus. Les deux lignes uthmani et Amiri Quran sont conservées exactement. Pickthall occupe le même emplacement et style que la traduction FR. Aucun crédit bibliographique n’est affiché en EN. Le grain et la lumière mobile sont retirés pendant cette fenêtre. Les gains voix, musique et bruitages sont nuls sur ses 174 images ; aucun mot aligné ne la traverse. Pendant la traduction parlée, la dernière position du plan dhikr est maintenue.

## Vérifications effectuées

- `npx tsc --noEmit` : réussi.
- `node tools/bundle_local.mjs out/bundle-en-voix` : réussi ; audio copié intégralement, empreinte vérifiée.
- `node tools/check_v01_en.mjs --baseline out/validation/baseline-src` : **79 segments, 278 repères, 1 246 instants EN**, plus les trois Shorts échantillonnés chaque seconde. Texte complet, ordre, fondu/immobilité du verset et gains audio contrôlés.
- Comparaison FR : **835 instants identiques en HTML/styles**, vidéo et trois Shorts ; durée FR inchangée à 17 526 images. Référence locale : commit `6c502ea`, sources dans `out/validation/baseline-src`. Ce n’est pas une comparaison de pixels.
- `tools/check_vo_en.py` : copie PCM, intégrité brute, 79 pauses, lead/tail, insert nul, 1 529 mots et préservation intégrale des chuchotements vérifiés.
- Assemblage et alignement relancés avec les caches validés par empreinte : même WAV et mêmes temps, sans nouvelle transcription nécessaire.
- SRT EN : 318 entrées, toutes ordonnées, durée positive, texte ≤ 42 caractères, durée ≤ 4,75 s (4,5 s de parole + marge de lecture), aucun chevauchement, nombres demandés présents. Génération FR comparée avant/après : identique octet pour octet.
- `tools/report_3d_en.py` : rapport et 11 repères propres à Blender supplémentaires préparés ; aucun import `bpy` ni rendu dans ce contrôle.
- `git diff --check` : réussi.

Rapports : `out/validation/v01-en-report.json`, `out/validation/vo-en/audio-qa.json`, `out/validation/vo-en/alignment-audit.json`, `out/validation/3d-en-plan.json`. L’avertissement React préexistant sur les clés de `FilmStrip` reste présent dans les deux versions.

## Reproduire hors ligne

Le Python système n’a pas les dépendances audio. La `.venv` partagée contient Whisper et SoundFile ; elle est uniquement lue. L’alignement EN ne dépend plus de `num2words` (absent de cette venv). Ne jamais lancer la commande TTS.

```bash
HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 .venv/bin/python tools/assemble_vo.py script/v01_en.json public/vo/v01_en_brut.wav public/vo/v01_en.wav --verse-hold 6
HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PATH="$PWD/.venv/bin:$PATH" python3 tools/vo.py align script/v01_en.json public/vo/v01_en.wav
HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 .venv/bin/python tools/check_vo_en.py
HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 python3 tools/srt.py src/data/v01_en.vo.json out/package_en/v01.en.srt
HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 python3 tools/report_3d_en.py
node tools/check_v01_en.mjs --baseline out/validation/baseline-src
npx tsc --noEmit
```

## Suite de production

1. Écoute humaine des extraits et de la voix complète, particulièrement dhikr, les chuchotements et les noms propres ; confirmer le plateau de lecture de 6 s. Aucun mot n’est déclaré manquant sans preuve.
2. Claude : rendre et ouvrir les **37 PNG EN + 9 PNG Shorts** de `docs/v01-en-images-fixes.md`, vérifier lisibilité, marges, transitions et maintien du FR. Les planches HTML locales sont préparées ; Chromium n’a pas été relancé dans ce bac à sable.
3. **3D : aucun calcul lancé.** Voir `docs/v01-en-3d.md`. Les sept plans animés demanderaient environ **97,1 min** à 7 s par image et aux pas indiqués. La maquette initiale peut réutiliser sa caméra FR ; les autres plans peuvent être recalés par morceaux sur leurs actions, après inspection. Les commandes écrivent dans `out/3d-en/`, sans écraser les assets ni le registre FR. Les cartons EN restent actifs jusqu’au branchement de rendus validés.
4. Intégrer les rushes EN, le gros plan tissu et un éventuel témoignage uniquement s’ils sont fournis et validés. Les emplacements actuels sont conservés. Tout nouvel insert exige un nouveau recalage.
5. Rendre la vidéo complète, écouter le mix final (dont le silence du verset), masteriser et contrôler le master. Aucun fichier prêt à publier n’est livré ici.
6. Dans une session autorisant Git, créer les cinq commits français depuis les patches préparés. Aucun push : Claude s’en charge.

`package.json` est inchangé. Aucun `.env` lu, aucun appel ElevenLabs, aucune voix régénérée, aucun réseau demandé, aucune écriture dans `public/` hors `public/vo/`, aucune modification de `node_modules/` ni de `.venv/`, aucun calcul Blender ni lancement Chromium, aucun asset privé versionné, aucun push.
