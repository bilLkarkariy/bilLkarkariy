# V01 EN — état de livraison

4 octobre 2026 — branche `studio/v01-en`. Travail enregistré par étapes, **aucun push**.

La préparation anglaise est livrée. **Le contrôle visuel du montage n'est pas terminé** : le bac à sable empêche Chromium de démarrer et l'outil Computer Use a refusé l'accès à Chrome. Les contrôles structurels et les miniatures sont vérifiés ; les planches HTML du film n'ont pas pu être regardées. Aucun export vidéo final n'est livré.

## Livrables

| Élément | État |
|---|---|
| `script/v01_en.json` | 79 segments, mêmes IDs `s1…s79`, pauses, lead/tail et balise `[serious]` que le script FR. Anglais parlé, citations originales, verset en attente explicite. |
| `src/i18n/fr.ts`, `en.ts`, `index.tsx` | Dictionnaires pour textes animés, notes, étiquettes, carte, HUD, placeholders, écran final et Shorts. Prop `lang`, français par défaut. |
| `tools/vo_estime.py` | Estimateur hors ligne, sans dépendance audio : syllabes, ponctuation et pauses du script FR. Reproductible. |
| `src/data/v01_en.vo.json` | Alignement **estimé**, `audio: null`, durée 670,765 s. Ce n'est pas une voix enregistrée. |
| `src/data/v01_en.groups.json`, `v01_en.anchors.json` | Correspondance des 79 segments du script avec les 68 groupes historiques du montage ; 278 repères de mots/expressions EN vérifiés. Aucun étirement global de la timeline FR. |
| `V01-EN` | 20 297 images à 30 i/s, soit **11:16,57**, écran de fin de six secondes inclus. Durée provisoire. |
| `short-bouton-en` | 3 442 images, environ 1:54,73. |
| `short-pascal-en` | 2 219 images, environ 1:13,97. |
| `short-exercice-en` | 2 857 images, environ 1:35,23. |
| `docs/v01-en-description.md` | Description anglaise, mêmes sources et chapitres estimés. Limites de revérification des liens consignées. |
| `out/package_en/miniatures/v01_en_{1,2,3}.png` | Trois PNG 1280×720, générés à partir des bruts FR et **ouverts visuellement**. Textes lisibles, sans débordement observé. Images privées, non versionnées. Reproductibles avec `tools/miniatures_en.py`. |
| `docs/v01-en-questions.md` | Voix, deux traductions du verset, formulations religieuses, choix de fiches et point sur les sessions Internet. Aucun choix religieux nouveau tranché. |

Les textes anglais des documents restent dans les vrais documents. Les quelques captures françaises sont traitées séparément : statistiques en fiches anglaises, Pascal en citations anglaises publiées. Détail dans le fichier de questions. Les textes arabes ne sont pas traduits ni réécrits.

## Vérifications effectuées

- `npx tsc --noEmit` : réussi.
- `node tools/bundle_local.mjs out/bundle-en-final` : réussi. Le cache Webpack est désactivé pour ne pas écrire dans le `node_modules` partagé.
- `node tools/check_v01_en.mjs --baseline out/validation/baseline-src` : réussi. 79 IDs et pauses conformes, balises conformes, mots ordonnés, 278 repères EN résolus. 1 284 instants du montage EN rendus en React, plus les trois Shorts échantillonnés toutes les secondes.
- Comparaison FR avant/après : **835 instants identiques en structure HTML et styles**, vidéo longue et trois Shorts compris. Référence : sources FR du commit `6c502ea`, copiées dans `out/validation/baseline-src` avant les modifications du montage. La durée FR reste 17 526 images. **Ce contrôle n'est pas une comparaison de pixels.**
- Deux instants du plateau du verset EN produisent exactement le même rendu React. Uthmani et Amiri Quran vérifiés. La lumière mobile et le grain variable sont retirés pendant cette seule séquence EN ; voix, musique et bruitages y sont coupés dans le code. L'écoute finale reste à faire avec le vrai son.
- 33 fichiers image utilisés par le montage EN retrouvés localement. Aucun asset partagé modifié.
- Régénération de l'estimation dans `out/validation/v01_en.estime-check.json` : identique octet pour octet au JSON versionné.
- `git diff --check` : réussi.
- Avertissement React préexistant : clés manquantes dans une liste de `FilmStrip`, également présent dans la référence FR. Il n'empêche pas ces contrôles.

Rapport local : `out/validation/v01-en-report.json`. Inventaire des textes rendus : `out/validation/rendered-text.txt`.

## Images fixes : ce qui reste bloqué

Les essais PNG avec `tools/stills.mjs` ont échoué avant la première image :

- Chrome et Chromium headless shell ne peuvent pas démarrer dans le bac à sable macOS ; diagnostic explicite : `bootstrap_check_in … MachPortRendezvousServer … Permission denied (1100)`.
- L'outil Computer Use a répondu : `Computer Use was not approved to use Google Chrome`. Aucune autorisation n'a été contournée.

Le mode de secours `--html` de `tools/stills.mjs` produit les mêmes scènes React à des images fixes, avec les polices et assets locaux ; il omet l'audio et remplace `Img` par une image HTML. **Il ne remplace pas le renderer PNG ni une inspection visuelle.**

Les sorties préparées dans `out/validation/` :

- `en/index.html` : 28 vues, dont début/milieu/fin de chacune des cinq parties et 13 points sensibles (consigne, écrans, Pascal, khalwa, carte, al-Ghazali, dhikr, verset, fondements, exercice, révélation).
- `short-bouton-en/`, `short-pascal-en/`, `short-exercice-en/` : neuf vues au total, début/milieu/fin.
- `fr-before/` et `fr-after/` : sept vues FR avant/après en HTML ; les contrôles finaux de comparaison sont dans `compare-before/` et `check/`.
- `render-en-stills.txt` : commande PNG complète avec les 28 images calculées.

**À faire sur une session locale autorisant Chromium :** exécuter les commandes ci-dessous, ouvrir tous les PNG EN, contrôler les marges, la lisibilité, les fiches, les graphies anglaises et les transitions aux points sensibles ; comparer également les PNG FR avant/après. Aucun constat « zéro débordement » n'est encore validé pour le film ou les Shorts.

```bash
npx tsc --noEmit
node tools/bundle_local.mjs out/bundle-en
# CHROME doit désigner un navigateur installé et autorisé à démarrer.
# BUNDLE est un dossier de bundle, jamais le dépôt public partagé.
CHROME='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' BUNDLE=out/bundle-en \
  node tools/stills.mjs out/validation/en-png --composition V01-EN p1:300 p3:9000 fin:20180
# Remplacer ces trois exemples par la liste complète : out/validation/render-en-stills.txt.
CHROME='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' BUNDLE=out/bundle-en \
  node tools/stills.mjs out/validation/short-bouton-en-png --composition short-bouton-en debut:60 milieu:1721 fin:3412
CHROME='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' BUNDLE=out/bundle-en \
  node tools/stills.mjs out/validation/short-pascal-en-png --composition short-pascal-en debut:60 milieu:1110 fin:2189
CHROME='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' BUNDLE=out/bundle-en \
  node tools/stills.mjs out/validation/short-exercice-en-png --composition short-exercice-en debut:60 milieu:1429 fin:2827
```

Ces frames sont provisoires. Relancer `node tools/check_v01_en.mjs` après tout changement d'alignement pour régénérer la liste.

## Suite de production

1. Réponses de Billel dans le fichier de questions : voix, traduction de Coran 13:28, relecture religieuse, éventuel témoignage et prises face caméra.
2. Compléter `s63`, enlever `_pending`, mettre la traduction choisie dans le dictionnaire EN et créditer le traducteur dans la description. Aucune traduction ne doit être implicite.
3. Enregistrer/provisionner la voix anglaise. Aucun TTS n'a été généré dans cette tâche. Garder `public/` partagé en lecture seule dans ce worktree : la préparation audio et le dépôt du WAV doivent être faits dans le pipeline autorisé, ou après séparation explicite des assets.
4. Remplacer l'estimation avec la commande prévue par le brief, lorsque le WAV existe et le texte est validé :

   ```bash
   python3 tools/vo.py align script/v01_en.json public/vo/v01_en.wav
   ```

   `tools/vo.py` utilise désormais `language: "en"` et l'expansion des nombres anglaise pour ce script ; le français garde son comportement antérieur. Le résultat garde les IDs `s…`, reconnus directement par la nouvelle couche de repères. La voix EN n'est jouée que lorsque le JSON contient un chemin audio.

5. Refaire TypeScript, les contrôles de repères et les images fixes ; recaler chapitres et Shorts. L'alignement Whisper réel reste à écouter et à corriger si nécessaire.
6. **3D anglaise : aucun calcul lancé.** Tous les plans EN restent volontairement en attente, y compris la maquette initiale, même avec `WITH3D=1`. Le script `plans3d.py` actuel est encore calé sur le FR et écrit dans `public/3d/` : ne pas le lancer tel quel ici. Préparer ensuite un calcul EN sur le vrai alignement, vers des assets séparés dans `out/`, et brancher ces rendus sans écraser les fichiers ni le manifeste FR.
7. Intégrer les rushes EN, le gros plan tissu et tout témoignage validé. Ne rien inventer. Refaire les alignements/3D si leurs durées changent.
8. Rendu vidéo, écoute (notamment le silence du verset), masterisation, derniers contrôles visuels. À faire seulement après remplacement des éléments provisoires. Aucun fichier final prêt à publier n'est prétendu.

## Commits et périmètre

Commits en français, par étape : récit ; rythme et repères ; montage/Shorts ; miniatures ; description ; vérifications ; documents de reprise. Consulter `git log --oneline` pour les identifiants exacts.

`package.json` est inchangé. Aucun fichier `public/`, `out/`, photo ou rush n'est commité. Aucun fichier `.env` lu, aucun identifiant affiché, aucun son ElevenLabs produit, aucun plan 3D recalculé, aucun push effectué.
