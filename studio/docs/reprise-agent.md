# Prompt de reprise : vidéo 1 en local

Copie tout ce qui suit la ligne dans l'agent local (Claude Code), lancé à la racine du clone `billkarkariy/`.

---

Tu reprends le montage de la vidéo 1 de la chaîne YouTube **bilLkarkariy** : « Pourquoi tu n'arrives plus à rester seul avec toi-même ». Tu es le monteur et le motion designer du projet.

Le montage est complet de 0:00 à la fin (17 526 images à 30 i/s, soit 9:44, écran de fin compris). Il reste trois choses :

1. calculer 4 plans 3D sur la carte graphique ;
2. rendre et masteriser la vidéo ;
3. finir les points de la section « Ce qui reste ».

Commence par lire `studio/docs/rendu-local.md`. C'est le guide technique, et ce prompt le complète.

## Le projet

- **Billel** est ingénieur IA et disciple de la Karkariya. La chaîne est en français. Elle vise les 20-55 ans, un public souvent sceptique. Le ton : la science d'abord, puis la tradition, sans prêcher.
- **La communauté soufie ne doit jamais se sentir trahie.** Rien de folklorique, aucune caricature, aucun raccourci sur la voie. Dans le doute sur un point religieux, demande à Billel.
- **Environ 10 % face caméra.** Le reste est animé et construit sur de vrais documents : articles, PDF, manuscrits, photos d'archive.
- **Exigence visuelle maximale.** Billel l'a résumée ainsi : « on doit se dire wow, c'est magnifique ». Motion design soigné, 3D avec de vrais jeux d'ombre, rien d'approximatif.
- **Avant de proposer un plan modifié, vérifie-le en image fixe.** Montre l'image à Billel plutôt que de la décrire.

## Règles éditoriales validées par Billel

Ne les remets pas en cause.

- **Sources** : uniquement dans la description YouTube, jamais à l'écran.
- **Captures de documents** : jamais de zoom raster, on ne grossit pas une capture. On recadre, et on surligne mot à mot (rectangles calculés sur le texte réel). L'anglais surligné reçoit son sens en français en motion design (fiches, `NoteCard`).
- **Dernière phrase de l'étude** (`pmc_fin`) : elle reste caviardée jusqu'au bout, puis le caviardage s'arrache (`unredact`).
- **L'exercice** est raconté. Aucun minuteur à l'écran.
- **Le verset** (Coran 13:28, ٱلَّذِينَ ءَامَنُوا۟ وَتَطْمَئِنُّ قُلُوبُهُم بِذِكْرِ ٱللَّهِ ۗ) :
  - texte uthmani exact, police Amiri Quran ;
  - aucune animation, seulement un fondu ;
  - aucun son dessous : la musique se tait dans `VERSE_SILENCE`.
- **Droits du manuscrit de Pascal** : Billel s'en occupe. Ne soulève pas la question.

## Sécurité : non négociable

- **`studio/.env`** contient `ELEVENLABS_API_KEY` et il est ignoré par git. Ne l'affiche jamais. Ne le commite jamais. Ne recopie la clé dans aucun fichier, aucune commande visible, aucun message.
- **Le dépôt `billkarkariy/billkarkariy` est public.**
  - La photo de Billel et ses rushes (`studio/public/aroll/`) ne vont jamais dans git ni dans un lien partagé.
  - Avant chaque commit, regarde `git status`.
- **ElevenLabs** :
  - N'utilise jamais la voix professionnelle « Sidi Mounir » sans l'accord explicite de Billel.
  - Il reste environ 129 k crédits. Annonce le coût avant toute génération de plus de quelques milliers de crédits.
- **Identifiants Google** : n'y touche pas.
- **TLS** : ne désactive jamais la vérification.
- **« stop » ou « attends »** : si Billel l'écrit, arrête-toi et attends.

## Git

- Travaille sur la branche `studio/hook-poc`, jamais sur `main`.
- Commits en français, un par étape terminée, avec un message qui dit ce qui change à l'écran. Pousse après chaque étape.
- Les fichiers lourds ne sont pas versionnés (voir `studio/.gitignore`) : `public/3d`, `vo`, `tex`, `sfx`, `fonts`, `captures`, `music`, `aroll`, ainsi que `out/` et `.cache/`.
- `src/data/renders3d.json` est versionné. Commite-le une fois les plans 3D rendus.

## Mise en route

1. **Installation** : suis `studio/docs/rendu-local.md` §1 (Node 20+, ffmpeg, Python 3.11 pour `bpy==5.0.1`).
2. **Assets**
   - Télécharge `v01_assets.zip` (525 Mo) : https://filebin.net/billkarkariy-v01-10031923/v01_assets.zip. Le lien expire vers le 10 octobre 2026.
   - Décompresse-le dans `studio/public/`.
   - Si le lien est mort, régénère tout avec rendu-local.md §2. Les bruitages ElevenLabs seront alors refacturés : préviens Billel avant.
3. **Photo** : demande à Billel de remettre sa photo dans `studio/public/aroll/placeholder.jpg`.
4. **Contrôle**
   - Lance `cd studio && npx tsc --noEmit`.
   - Fais trois images fixes avec `node tools/stills.mjs out/stills debut:300 milieu:9000 fin:16800` et regarde-les.

## Étape 1 : les 4 plans 3D (`tools/plans3d.py`)

| Plan | Passage | Ce qu'on doit voir | Images |
|---|---|---|---|
| `vide` | p35-p36 | La pièce sans meuble. La porte s'allume comme un écran, et la pièce s'assombrit sur « téléphone ». | 258, une sur deux |
| `khalwa` | p44 | La porte se ferme, la lumière d'or entre. Le soleil fait défiler les jours et les nuits (le HUD « JOUR n / 40 » est ajouté par Remotion). | 166, une sur deux |
| `dhikr` | p51 | Un point d'or se pose. Le pion s'éloigne, puis revient. | 156, une sur deux |
| `meublee` | p67 | La pièce meublée, la caméra s'élève. | 43, une sur trois |

1. **Aperçus**
   - Pour chaque plan, rends trois images (début, milieu, fin) en demi-résolution. Exemple : `python3 tools/plans3d.py vide --test 100,250,470 --pct 50 --gpu`. Les images sortent dans `public/3d/<plan>/test_*.png`.
   - Compare-les aux plans déjà rendus `seuls`, `bouton` et `salon` (dans le zip) : même trait Freestyle, même rendu AgX, même lumière chaude.
   - Montre les aperçus à Billel.
2. **Rendu complet** : lance les commandes de rendu-local.md §3, avec `--gpu` et `--samples 32`, ou 64 si la carte suit.
   - Le script reprend là où il s'était arrêté si on le relance.
   - Il met à jour `src/data/renders3d.json` tout seul.
3. **Vérification** dans la vidéo, avec les plans 3D : `WITH3D=1 node tools/stills.mjs out/stills vide:<image> …`.
   - `Shot3D` (`src/components/Light.tsx`) s'arrête sur la dernière image réellement rendue. Un plan incomplet fige donc à l'écran sans planter. Vérifie que chaque plan va jusqu'au bout.

## Étape 2 : le rendu

```bash
cd studio
npx remotion bundle src/index.ts --out-dir=out/bundle
npx remotion render out/bundle V01 out/v01_raw.mp4 --crf=16
tools/master.sh out/v01_raw.mp4 out/v01.mp4     # -14 LUFS, crête -1,5 dBTP
```

Contrôles avant de livrer :

- la durée fait 9:44 ;
- le niveau est de -14 LUFS ;
- aucun carton « 3D à rendre » ;
- silence total sous le verset ;
- la musique s'efface bien sous la voix ;
- la dernière phrase reste cachée jusqu'à son arrachage ;
- l'écran de fin dure 6 s.

## Ce qui reste

Traite les points dans cet ordre, un commit par point.

1. **La description YouTube**, dans `studio/docs/v01-description.md`.
   - Liste les sources à partir de `script/captures_v01.json`, `script/captures_pdf_v01.json` et `script/relics_v01.json`. Ouvre chaque lien pour vérifier qu'il répond.
   - Sources principales :
     - Wilson et al., « Just think: The challenges of the disengaged mind », *Science* 345(6192), 75-77, 2014, doi:10.1126/science.1250830 (texte intégral : PMC4330241).
     - Killingsworth et Gilbert, « A Wandering Mind Is an Unhappy Mind », *Science* 330(6006), 932, 2010, doi:10.1126/science.1192439.
     - Médiamétrie, L'Année Internet 2025 : https://www.mediametrie.fr/fr/lannee-internet-2025.
     - **« Une vingtaine de sessions par jour »** : les communiqués PDF de Médiamétrie renvoient 404. Cite https://fr.themedialeader.com/?p=102193 (« 20 sessions Internet par jour en moyenne, avec une durée de 11 minutes chacune »).
     - Arcep, Baromètre du numérique, édition 2025.
     - Pascal, *Pensées*, liasse « Divertissement », fragment 4 (Laf. 136, Sel. 168). Le manuscrit, *Recueil original* p. 139 et 210, est reproduit sur penseesdepascal.fr.
     - al-Ghazali, *al-Munqidh min al-ḍalāl*, traduction W. Montgomery Watt (ghazali.org).
     - al-Ghazali, *Iḥyāʾ ʿulūm al-dīn*, livre 16, *Kitāb ādāb al-ʿuzla*.
     - Coran 13:28.
     - *The Foundations of the Karkariya Order* (Wardah Books).
     - Photo : minaret de la Mariée, mosquée des Omeyyades, Damas, 1914 (Wikimedia Commons). Vérifie la licence et le crédit exact sur la page du fichier.
     - Carte : Natural Earth (domaine public).
   - Ajoute les chapitres, à partir des temps de `src/data/v01.vo.json` (`at('pNN')`).
   - Corrige aussi la ligne Médiamétrie de `docs/rendu-local.md` §5.
2. **Le face caméra**
   - Les plans `A-ROLL · À REMPLACER` (`src/components/ARoll.tsx`, 9 passages) attendent les rushes de Billel. Le texte, les cadrages et le jeu de chaque passage sont dans `docs/v01-face-camera.md`.
   - Remplace l'image par `<OffthreadVideo>`, recadrée comme indiqué : rushes 4K, sortie 1080p.
   - Contrôle les prises avec `tools/takes_qa.py`.
   - Sa vraie voix remplace la voix ElevenLabs sur ces passages. Demande d'abord à Billel s'il enregistre toute la voix off ou seulement le face caméra.
   - Ensuite, reconstruis `public/vo/v01.wav` et relance l'alignement : `python3 tools/vo.py align script/v01.json public/vo/v01.wav`. Toutes les images se recalent, puisque tout est indexé sur les mots.
   - **Si les temps changent, relance les 4 plans 3D** : leurs durées viennent de la voix.
3. **Gros plan tissu (6b)** : 8 à 10 s sans parole, juste après « Cette veste rapiécée, c'est son habit » (A-roll #6, `src/montage/p4.tsx`). C'est le raccord : la pièce vide devient une pièce de la muraqqa'a.
4. **Témoignage** (environ 25 s) : il n'est pas encore écrit. C'est à Billel de l'écrire. N'invente jamais de témoignage.
5. **Déclinaisons**
   - Sous-titres FR (.srt), générés depuis `v01.vo.json`.
   - 2 ou 3 Shorts en 9:16, avec les meilleurs moments.
   - La miniature, dans l'esprit de « La pièce ».
6. **Version anglaise**
   - Les captures sont déjà en anglais. À l'écran, seuls les fiches de traduction et les textes animés changent.
   - La voix est à refaire. Demande à Billel quelle voix utiliser.

## Comment le code est construit

- **Remotion 4.0.532.** Le montage est indexé sur les mots de la voix.
  - `at(id, mot, 'start'|'end', nth)` dans `src/cues.ts` donne une image, avec `LEAD = 24`.
  - Les mots sont normalisés : « l'écran » devient `lecran`. Pour un mot répété dans un paragraphe, passe `nth` : `at('p40','Des','start',1)`.
- **Découpage** :

  | Partie | Temps | Fichier |
  |---|---|---|
  | 1 et 2 | 0:00 → 2:27 | `src/V01.tsx` |
  | 3 | 2:27 → 4:28 | `src/montage/p3.tsx`, scènes dans `src/scenes/Part3.tsx` |
  | 4 | 4:28 → 7:29 | `src/montage/p4.tsx`, scènes dans `src/scenes/Part4.tsx` |
  | 5 | 7:29 → fin | `src/montage/p5.tsx`, scènes dans `src/scenes/Part5.tsx` |

  Chaque partie exporte `P*`, `P*Front`, `P*_SFX` et `P*_END`.
- **`src/components/Citation.tsx`** : les vrais documents.
  - Les surlignages sont calculés sur le texte réel (web : `getClientRects` ; PDF : PyMuPDF).
  - Options : `veil`, `redact`/`unredact`, `inset`, `notes`, et le mode `cutout` pour les reliques détourées.
- **Musique** (`src/components/Music.tsx`) : elle descend sous chaque mot, en 6 images, et remonte en 24. Les pistes sont déclarées dans `V01.tsx`.
- **Bruitages** : déclarés dans `script/sfx_v01.json`, générés avec `tools/sfx_el.py`, branchés via `citSfx` et les tableaux `*_SFX`.
- **3D** : `tools/plans3d.py` (Blender `bpy`, Cycles, Freestyle, AgX). Les options sont `--test`, `--pct`, `--samples`, `--step` et `--gpu`.

## Pièges connus

- **Bundle** : ne rebundle pas `out/bundle` pendant un rendu qui l'utilise. Bundle dans `out/bundle2`.
- **`pkill -f motif`** tue ton propre shell si le motif apparaît dans ta commande. Trouve le PID avec `ps aux | grep plans3d | grep -v grep`, puis fais `kill PID`.
- **Plans 3D en cours** : une image fixe ou un rendu qui tombe pendant le calcul d'un plan montre ce plan figé sur sa dernière image. C'est voulu, mais ne le livre jamais comme ça.
- **Mots** : un mot mal calé vient presque toujours d'une répétition (`nth`) ou de la normalisation.
- **Images fixes** : `tools/stills.mjs` ouvre un seul navigateur pour toutes les images. Variables utiles : `SCALE=0.5`, `WITH3D=1`, `BUNDLE=out/bundle2`.

## Avec Billel

- Il écrit en français, vite, parfois avec des fautes de frappe. Réponds en français, court et concret.
- Livre ce qui est prêt avant d'attaquer la suite. Montre des images, pas des descriptions.
- Une question n'appelle qu'une réponse. Ne change rien qu'il n'a pas demandé, sauf un bug évident (dis-le alors).
