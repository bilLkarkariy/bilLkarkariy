# Script de montage : POC 1 min (hook + début de « L'expérience »)

Voix : **ton clone ElevenLabs** (« Billel », modèle `eleven_v4`, balises de ton dans `script/hook.json`). Les temps du tableau viennent d'une version antérieure de la voix ; ils sont indicatifs. Si tu enregistres une vraie prise, tout se recale automatiquement : chaque événement est accroché à un mot, pas à un timecode (`src/Hook.tsx`).

Son : **aucune ambiance ajoutée**, la voix passe par l'isolateur vocal ElevenLabs (le clone avait appris le bruit de ses échantillons). Pas de balises « douces » ([softly], [warmly], [lowers voice]) : elles rendaient la voix soufflée.

Direction artistique : « La pièce ». Papier froid quadrillé (le carnet de labo), encre, et une seule couleur à l'image : le **rouge = la fuite** (bouton, décharge, ceux qui appuient). L'or (le centre) n'apparaît pas avant la partie sur la voie.

| # | Temps (indicatif) | Voix | Image | Son |
|---|---|---|---|---|
| 1 | 0:00–0:03 | *(silence)* « Quinze minutes. » | **A-ROLL** plan serré : tu retournes ton téléphone sur le bureau, sans un mot, puis tu dis la phrase. | Téléphone posé face contre le bois. Ambiance de pièce. |
| 2 | 0:03–0:08 | « Seul dans une pièce vide. Pas de téléphone, rien à lire. » | **Maquette 3D** en carton blanc, coupée à 1,1 m, en axonométrie. La caméra pivote lentement jusqu'à la vue de dessus. Un seul point rouge : le bouton sur la table. Cartouche d'architecte « SEUL · SANS RIEN · 15:00 ». Étiquettes TÉLÉPHONE puis LECTURE, barrées sur le mot. | Ambiance seule. |
| 3 | 0:08–0:10 | « Juste toi, tes pensées… » | La maquette, vue de dessus, devient le **plan 2D** au même endroit (murs en contour, puis remplis). Sur « toi », un point d'encre sur la chaise. Sur « pensées », un trait de crayon part et erre dans la pièce. | Crayon, petit tic. |
| 4 | 0:10–0:13 | « et un bouton qui t'envoie une décharge électrique. » | Le bouton rouge apparaît sur « bouton ». Sur « décharge », un arc rouge relie le bouton au point, avec un flash. | Tic, décharge (×2). |
| 5 | 0:13–0:14 | *(silence 1,6 s)* | Poussée lente vers le bouton. Cercle de détail pointillé, légende « 1 PRESSION = 1 DÉCHARGE ». Le trait de l'esprit s'efface. | Ambiance seule. |
| 6 | 0:14–0:17 | « Deux hommes sur trois ont appuyé. » | Trois points. Sur « appuyé », deux deviennent rouges, l'un après l'autre (onde). Puis **67 % des hommes**. | Deux clics de bouton, impact grave. |
| 7 | 0:17–0:22 | « Des gens qui, juste avant, avaient dit qu'ils paieraient pour ne plus jamais la sentir. » | Accolade au-dessus des trois : JUSTE AVANT, *prêts à payer pour ne plus jamais la sentir*. Les deux rouges restent rouges : la contradiction se voit. | Ambiance. |
| 8 | 0:22–0:27 | « Et je suis presque sûr que toi aussi, tu aurais appuyé. » | **A-ROLL** regard caméra. | Ambiance. |
| 9 | 0:27–0:30 | « C'est une étude publiée dans Science en 2014. » | **Fiche recomposée** de l'article qui glisse sur le papier : SCIENCE, 4 juillet 2014, vol. 345, titre et auteurs exacts. Le corps du texte est abstrait (barres). | Feuille qui glisse. |
| 10 | 0:30–0:33 | « Sa dernière phrase, presque personne ne la cite. » | La caméra descend au bas de la colonne 2. Les deux dernières lignes foncent, crochet DERNIÈRE PHRASE. | Tic. |
| 11 | 0:33–0:37 | « Pourtant, elle change complètement le sens de ce bouton. » | Sur « bouton », le petit bouton rouge se relie à la phrase en pointillés. | — |
| 12 | 0:37–0:41 | « Tu l'auras à la fin, avec deux minutes d'exercice pour ce soir. » | Sur « Tu l'auras », la phrase est **caviardée** au feutre noir (la boucle A devient visible). → À LA FIN · + 2 MIN D'EXERCICE. | Feutre. |
| 13 | 0:41–0:44 | « Université de Virginie. » | Coupe sur le **même plan de pièce**, vu de plus haut, avec le couloir devant la porte. Chapitre « 01 · L'EXPÉRIENCE », lieu en dessous. | Crayon. |
| 14 | 0:44–0:47 | « Des étudiants entrent dans une pièce presque vide. » | Des points en file dans le couloir ; l'un d'eux avance. | Tics. |
| 15 | 0:47–0:52 | « On leur fait déposer leurs affaires à l'entrée. Le téléphone, mais aussi les stylos. » | Il s'arrête au casier AFFAIRES. Sur « téléphone », le téléphone (pastille rouge) y tombe ; sur « stylos », le stylo. | Tics. |
| 16 | 0:52–0:54 | « Rien pour écrire. » | Il entre, va à la chaise. La porte se referme derrière lui. | Porte. |
| 17 | 0:54–0:59 | « La consigne tient en une ligne : reste assis, ne t'endors pas, et occupe-toi avec tes pensées. » | Le plan s'efface ; une fiche CONSIGNE glisse. Chaque mot s'écrit au moment où il est dit. | Feuille. |
| 18 | 0:59–1:02 | « Quinze minutes. » | La fiche remonte, **15:00** apparaît puis décompte : 14:59, 14:58. Coupe sèche au noir. | Tic d'horloge. |

Sources (description uniquement) : Wilson et al., *Science* 345(6192), 2014 (R1, R6, R7).

## Remplacer les emplacements A-ROLL par tes rushes

1. Place tes fichiers dans `public/aroll/` (par exemple `hook_01.mp4`).
2. Dans `src/components/ARoll.tsx`, remplace l'`<Img>` par `<OffthreadVideo src={staticFile('aroll/hook_01.mp4')} startFrom={...} />`.
3. Utilise l'audio de ta prise comme voix : `python3 tools/vo.py align script/hook.json public/vo/ta_prise.wav`, puis relance le rendu. Tous les repères se recalent sur ta diction.

## Changer la voix ou le ton

Dans `script/hook.json` : `tts.voice_id`, `tts.model`, et les balises en tête de segment (`[calm]`, `[softly]`, `[serious]`…). Puis `python3 tools/vo.py tts script/hook.json` : génère, met en cache, aligne.

## Rendu

```bash
npx remotion render src/index.ts Hook out/hook_raw.mp4
tools/master.sh out/hook_raw.mp4 out/hook.mp4   # -14 LUFS pour YouTube
```
