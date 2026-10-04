# Version anglaise de la vidéo 1 : brief pour Codex

Tu prépares la version anglaise de « Pourquoi tu n'arrives plus à rester seul avec toi-même »
(chaîne bilLkarkariy). La version française est terminée sur la branche `studio/hook-poc`.
Tu travailles sur la branche `studio/v01-en`, dans ce dossier (`billkarkariy-en/studio`).

Lis d'abord `docs/reprise-agent.md` (règles du projet, sécurité, architecture) et `docs/rendu-local.md`.

## Règles absolues

- Ne lis jamais `.env`, n'affiche aucune clé. Ne génère AUCUN son ElevenLabs : la voix anglaise n'est pas encore
  choisie (Billel décidera). N'utilise jamais la voix « Sidi Mounir ».
- `public/`, `node_modules/` et `.venv/` sont des liens vers le dépôt français : n'y écris rien, n'y supprime rien.
  Tes fichiers générés vont dans `out/` (ignoré par git).
- Ne touche pas à `package.json`. Ne commite jamais `public/`, `out/`, photos ou rushes. Regarde `git status` avant chaque commit.
- Commits en français, un par étape, message qui dit ce qui change à l'écran. Ne pousse pas (pas de réseau dans ton bac à sable) : Claude poussera.
- Le respect de la communauté soufie est non négociable : rien de folklorique, aucun raccourci sur la voie.
  Le verset (Coran 13:28) reste en arabe uthmani exact (Amiri Quran), sans animation, avec seulement un fondu.
  Pour sa traduction anglaise, propose Sahih International ET une autre traduction reconnue dans `docs/v01-en-questions.md` :
  c'est Billel qui choisira. Toute autre question religieuse va aussi dans ce fichier, jamais tranchée par toi.
- Les sources ne s'affichent jamais à l'écran (seulement dans la description).

## Ce qu'il faut produire

1. **Le texte anglais** : `script/v01_en.json`, même structure que `script/v01.json` (mêmes `id` de segments,
   mêmes balises d'intonation ElevenLabs entre crochets, adaptées). Anglais parlé, naturel, sobre, pour un public
   20-55 ans plutôt sceptique : pas une traduction mot à mot. Garde les citations exactes quand elles existent en
   anglais (Wilson et al. 2014, Killingsworth & Gilbert 2010, Watt pour al-Ghazali, une traduction anglaise publiée
   de Pascal : indique laquelle). « Astaghfirullah » reste tel quel, avec sa traduction (« I ask God's forgiveness »).
2. **Les textes à l'écran** : tous les textes français affichés (Kinetic, fiches `NoteCard`, titres, étiquettes,
   carte, HUD « JOUR n / 40 », écran de fin, Shorts) passent par un dictionnaire `src/i18n/fr.ts` et `src/i18n/en.ts`,
   choisi par une prop `lang` (`'fr'` par défaut, rien ne doit changer en français : vérifie-le avec des images fixes
   avant/après). Les captures de documents sont déjà en anglais : en version anglaise, les fiches qui traduisaient
   l'anglais vers le français deviennent inutiles. Remplace-les par une fiche courte qui reformule l'idée, ou
   supprime-les si le surlignage suffit (décide au cas par cas, note tes choix).
3. **La composition `V01-EN`** et les Shorts anglais (`short-*-en`) dans `src/Root.tsx`, indexées sur
   `src/data/v01_en.vo.json`. Comme la voix n'existe pas encore, fabrique un alignement provisoire
   (`tools/vo_estime.py`) : durée de chaque mot estimée à partir du nombre de syllabes, avec les mêmes respirations
   que la version française, pour pouvoir prévisualiser le montage. Il sera remplacé par le vrai alignement
   (`python3 tools/vo.py align script/v01_en.json public/vo/v01_en.wav`) quand la voix sera enregistrée.
   Les plans 3D anglais seront à recalculer sur la vraie voix : ne les lance pas.
4. **La description YouTube anglaise** (`docs/v01-en-description.md`) : mêmes sources (en anglais), chapitres
   provisoires (à recaler sur la vraie voix).
5. **Les miniatures anglaises** : reprends `out/package/miniatures/brouillons/titres_v3.py` du dépôt français
   (`../../billkarkariy/studio/out/package/miniatures/brouillons/`) et les images brutes `v3_brut_*.png`, avec ces textes :
   « YOU WOULD HAVE PRESSED IT. », « 15 MIN. ALONE. », « RATHER THE SHOCK? » (ajuste si tu trouves mieux, en restant court).
   Sortie : `out/package_en/miniatures/`.
6. **Contrôle** : `npx tsc --noEmit`, puis des images fixes de la version anglaise (début, milieu, fin de chaque partie)
   avec `tools/stills.mjs` (adapte-le pour choisir la composition). Regarde-les. Rien ne doit déborder ni rester en français.

## À la fin

Écris `docs/v01-en-questions.md` (questions pour Billel : voix anglaise, traduction du verset, tout point religieux,
tes choix de fiches) et `docs/v01-en-etat.md` (ce qui est fait, ce qui reste : voix, alignement, 3D, rendu).
