# V01 AR — état

4 octobre 2026 — branche `studio/v01-ar`, partie de `studio/v01-en` (e688b56). Arabe standard moderne.
Texte de la voix : `script/v01_texte_playground_balises_ar.txt`, **figé, inchangé**.

Pas de voix arabe, pas de rendu vidéo, pas de PNG Remotion, pas de 3D : tout ce qui suit est prêt pour le Mac.
Aucun `.env` lu, aucun appel ElevenLabs, aucun calcul 3D, `package.json` inchangé, rien de `public/` ni de `out/`
dans git.

## Ce qui est fait (un commit par étape)

| Étape | Fichiers | État |
|---|---|---|
| Script | `script/v01_ar.json`, `src/data/v01_ar.groups.json` | 79 segments, mêmes `id`, `pause`, `lead`, `tail` que l'anglais, balises comprises ; le découpage redonne le texte figé caractère pour caractère. `tts.voice_id` vide. |
| Alignement provisoire | `src/data/v01_ar.vo.json`, `tools/vo_estime.py`, `tools/vo.py` | Estimé (`estimated: true`, `audio: null`) : 1 211 mots, 12:26 de voix. Syllabes arabes approchées par les lettres et les voyelles longues ; ponctuation arabe comprise. Sortie anglaise de `vo_estime.py` identique à l'octet. |
| Repères | `src/data/v01_ar.anchors.json` | 313 repères (les 302 de l'anglais + 11 repères réservés à la 3D), tous trouvés. |
| Langue dans le code | `src/i18n/ar.ts`, `src/i18n/index.tsx`, `src/cues.ts`, `src/Root.tsx`… | `Lang = 'fr' \| 'en' \| 'ar'`. Composition `V01-AR` et Shorts `short-bouton-ar`, `short-pascal-ar`, `short-exercice-ar`. Tous les textes à l'écran en arabe (Kinetic, fiches, titres, étiquettes, carte, HUD, écran de fin, Shorts, pages sans visage). |
| Droite à gauche | `src/fonts.ts`, `src/components/*`, `src/scenes/*`, `src/montage/p4.tsx`, `src/Short.tsx` | Tout texte arabe dans un bloc `direction: rtl` ; mots qui sortent depuis la droite, barré et fiches en miroir, chiffres dans l'ordre (« 1 / 5 »), arabe en Amiri sans faux italique ni interlettrage. Pascal : feuille arabe à côté du manuscrit (`ArabicEvidence.tsx`). |
| Verset | `src/scenes/Part4.tsx`, `src/V01.tsx` | Uthmani exact, Amiri Quran, fondu seul, **rien dessous** ; la voix arabe le récite, musique et bruitages à zéro. Voir la question 1.1. |
| Recalage 3D | `tools/remap3d.py`, `tools/remap3d_en.py`, `src/data/remap3d_ar.json` | `--lang` pour toutes les langues, sans rien recalculer ; refuse un alignement estimé. Anglais : même fichier à l'octet. Arabe : `{}` pour l'instant (cartons « en cours »). |
| Sous-titres | `tools/srt.py` | Ponctuation arabe, nombres en chiffres comme à l'écran, repère invisible de droite à gauche en tête de ligne. FR et EN identiques à l'octet. |
| Description | `docs/v01-ar-description.md` | Mêmes sources que l'anglais, titres d'œuvres en arabe, chapitres provisoires, titre et trois miniatures. |
| Contrôles | `tools/check_v01_ar.mjs`, `tools/stills_html.mjs` | Voir ci-dessous. |
| Suivi | `docs/v01-ar-images-fixes.md`, `docs/v01-ar-questions.md`, ce fichier | |

## Contrôles passés

- `npx tsc --noEmit` : passe.
- `node tools/check_v01_ar.mjs --baseline <src de studio/v01-en>` : passe.
  - texte figé, segments, groupes, ordre des mots, 313 repères ;
  - `V01-AR` : 22 542 images (12:31 provisoires), 1 359 images vérifiées, plus 1 503 en version sans visage ;
    aucun texte latin oublié (hors « Science » et « «OTHER TECHNIQUES» ») ; tout l'arabe dans un bloc de droite à gauche ;
  - verset immobile entre ses fondus (images 16 546 à 16 760), Amiri Quran, texte exact, rien dessous, aucun son
    autre que la voix ;
  - Shorts arabes : 3 934, 2 348 et 2 981 images ;
  - **français et anglais inchangés** : 1 733 images de `V01`, `V01-EN` et des six Shorts, même HTML et même son.
- `node tools/check_v01_en.mjs` : passe toujours.
- Planches HTML regardées dans un navigateur local (une trentaine de vues) : voir `v01-ar-images-fixes.md`.

## Ce qui reste à faire sur le Mac

1. **Réponses de Billel** (`v01-ar-questions.md`), d'abord la 1.1 (qui récite le verset) et le choix de la voix
   arabe du clone (jamais « Sidi Mounir »).
2. **Voix.** Billel enregistre avec son clone ElevenLabs, à partir du texte figé, et dépose
   `public/vo/v01_ar.wav` (48 kHz). Écoute humaine : harakat du verset, noms propres (الغزالي، الكركري، الناظور،
   ميدياميتري), chiffres.
3. **Vrai alignement.**
   ```bash
   python3 tools/vo.py align script/v01_ar.json public/vo/v01_ar.wav   # Whisper, langue « ar »
   node tools/check_v01_ar.mjs --baseline <src de studio/v01-en>
   ```
   Le fichier `src/data/v01_ar.vo.json` remplace l'estimation (`audio: "vo/v01_ar.wav"`). Regarder le nombre de mots
   interpolés ; si Whisper small comprend mal l'arabe, essayer le modèle medium dans `tools/vo.py`. Les durées et les
   chapitres bougent : refaire `docs/v01-ar-description.md` (chapitres) et la liste d'images (le contrôle la réécrit
   dans `out/validation-ar/render-ar-stills.txt`).
4. **Recalage 3D** (aucun calcul) :
   ```bash
   python3 tools/remap3d.py --lang ar     # écrit src/data/remap3d_ar.json
   ```
   puis regarder `khalwa_3d`, `dhikr_3d`, `vide`, `meublee` avec `WITH3D=1` (commandes dans `v01-ar-images-fixes.md`).
5. **Images fixes PNG** : 75 vues + 11 sans visage + 9 Shorts, commandes dans `v01-ar-images-fixes.md`. Points à
   regarder en priorité : taille des petites étiquettes arabes, interlignes, fiches empilées, colonne de l'exercice.
6. **Rendu et master** :
   ```bash
   node tools/bundle_local.mjs out/bundle-ar
   npx remotion render out/bundle-ar V01-AR out/v01_ar_raw.mp4 --crf=16 --props='{"faceless":true,"clean":true}'
   tools/master.sh out/v01_ar_raw.mp4 out/v01_ar.mp4
   npx remotion render out/bundle-ar short-bouton-ar out/short-bouton-ar.mp4 --props='{"clean":true}'   # idem pascal, exercice
   python3 tools/srt.py src/data/v01_ar.vo.json out/package_ar/v01.ar.srt
   ```
   Écouter le mix final, dont le verset (voix seule, sans musique).

## À savoir

- L'avertissement React sur les clés de `FilmStrip` existait déjà ; il reste dans toutes les langues.
- `src/data/remap3d_ar.json` vide est voulu : un recalage sur l'estimation mettrait les actions 3D à côté des mots.
  `python3 tools/remap3d.py --lang ar --provisoire --out /tmp/essai.json` permet un essai sans le commiter.
- Les questions éditoriales de l'anglais (mantras, Karkariya, vingt sessions) valent aussi pour l'arabe : le texte
  arabe suit le même récit.
