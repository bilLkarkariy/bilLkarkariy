# Vidéo 1 : la finition sur le Mac (après Remotion)

Ce qui se fait sur le Mac de Billel, parce que les fichiers lourds ou privés n'existent que là
(`public/` n'est pas dans git : images 3D, sons, polices, voix, photos). Les agents cloud préparent tout ce qui
permet ces étapes ; Claude les exécute sur le Mac. Référence : la version anglaise (`studio/v01-en`), validée.

## 1. Rendu Remotion de la version longue

```bash
npx remotion render out/bundle-<langue> V01-<LANGUE> out/<langue>/base.mp4 --config=out/remotion.local.ts \
  --props='{"clean":true,"no3d":false,"faceless":true,"sfxOff":[[de, à], …]}'
```

- `faceless` : aucune face caméra, les pages de texte sur papier les remplacent.
- `sfxOff` : bruitages coupés pendant les passages animés posés ensuite (ils ont leurs propres bruitages),
  plus `[0, 30]` au tout début.
- 3D : aucune image calculée ; `Shot3D` recale les images françaises avec `src/data/remap3d_<langue>.json`.

## 2. Passages posés par-dessus (ffmpeg, sans recalcul)

| Passage | Style | Où, en anglais (images) | Repère |
|---|---|---|---|
| Film muet | noir et blanc, rond | 4805 → 5078 | « Penser seul… le film part dans tous les sens » (décrochage sur « Dès que ») |
| Nuit au crayon | crayon | 8074 → 8264 | « Trois heures du matin… l'écran » |
| Khalwa VHS | caméscope | 10094 → 10297 | « Un mot qui veut dire… solitude » |
| Exercice 1 | crayon | 14644 → 15376 | « Je ne vais pas te demander… » jusqu'à « Deux… une chaise suffit » |
| Exercice 2 | crayon | 16465 → 16975 | « Cinq… » jusqu'à « juste pour l'heure » |
| La veste (mouraqqa) | prise de vue réelle | fenêtre 6 de `faceless` (`aroll6`), 13826 → 14193 | « Cette veste rapiécée, c'est son habit » |

Les passages animés sont refaits pour chaque langue par l'agent des styles (mêmes dessins, recalés sur la voix ;
textes dessinés traduits : « 40 JOURS », « 2 MIN »). Il lui faut, par langue, les temps voix de début et de fin de
chaque passage et les mots repères à l'intérieur.

## 3. Intro Pixar

`final_overlay.mp4` (14,3 s, voix française) : seules ses images servent, recalées sur la voix de la langue.
Plans : « 15:00 » (0 → 3,79 s), pièce et icônes (→ 6,29), visage et pensées (→ 8,875), bouton (→ 10,5),
bouton électrisé (→ 12,17), « 2/3 » (→ 14,33 ; la source « Wilson et al. » apparaît à 13,7 : couper avant).
En anglais : premier plan tenu jusqu'au premier mot, plans décalés pour tomber sur « No phone », « Just you »,
« button », « electric shock », « 2/3 » posé sur « Two out of three », fondu vers la vidéo juste après « pressed it ».
Son : la voix de la langue seule jusqu'au fondu, plus les 15 bruitages de l'intro française, recalés.

## 4. Mastering

`tools/master.sh` : -14 LUFS, crête -1,5 dBTP. Contrôles : durée, volume, silence sous le verset, images fixes
de chaque passage posé.

## 5. Shorts

Le cadre (titre, sous-titres, carton final) vient de Remotion (`short-*-<langue>`) ; la bande vidéo et le son sont
pris dans la vidéo finale validée, posés exactement sur la bande (1080 x 608 à y = 620), puis mastering.

## 6. Paquet

`out/package_<langue>/` : vidéo, `.srt`, `description.md`, 3 miniatures, 3 Shorts. Rien d'autre.
