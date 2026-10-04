# Test de synchro labiale FR → EN : rapport

**Verdict court : pas publiable tel quel.** La bouche suit le rythme de la voix anglaise. Mais MuseTalk efface
la moustache, lisse la barbe sous la lèvre et rend les lèvres roses et cireuses. Sur le gros plan (clip 2),
ça saute aux yeux. Sur les plans larges (1, 3, 4), c'est moins visible, mais l'écart avec les autres plans
non retouchés de la vidéo se verra (moustache présente / absente d'un plan à l'autre).

## Machine

| | |
|---|---|
| Carte graphique | **aucune** (`nvidia-smi` absent, pas de CUDA) |
| Processeur | Intel Xeon 2,1 GHz, 4 cœurs |
| Mémoire | 15 Go, sans swap |
| Disque | 30 Go libres |

Sans carte graphique, LatentSync 1.6 est exclu, donc **MuseTalk 1.5 sur processeur** (règle du brief).

## Modèle et licences

| Brique | Source officielle | Licence | Usage commercial |
|---|---|---|---|
| MuseTalk 1.5, code | github.com/TMElyralab/MuseTalk, commit `0a89dec` (26/09/2025) | MIT | oui |
| MuseTalk 1.5, poids `musetalkV15/unet.pth` | huggingface.co/TMElyralab/MuseTalk (rév. `2bcb936`) | MIT (README : « available for any purpose, even commercially ») | oui |
| VAE `sd-vae-ft-mse` | huggingface.co/stabilityai | MIT | oui |
| Audio `whisper-tiny` | huggingface.co/openai | Apache 2.0 | oui |
| Repères du visage DWPose | huggingface.co/yzd-v/DWPose | Apache 2.0 | oui |
| Détecteur de visage S3FD | adrianbulat.com (auteur de face-alignment) | code BSD-3 | ⚠ voir plus bas |
| Masque de fusion BiSeNet `79999_iter.pth` | lien Google Drive de l'auteur (zllrunning/face-parsing.PyTorch), donné par MuseTalk | code MIT | ⚠ voir plus bas |

⚠ **Zone grise à connaître.** Le code de ces deux briques est sous licence libre. Mais leurs poids ont été
entraînés sur des jeux de données réservés à la recherche : CelebAMask-HQ pour BiSeNet, WIDER FACE pour S3FD.
Elles ne génèrent aucun pixel : elles servent seulement à trouver le visage et à découper le masque de collage.
Le risque est faible, mais il existe. Si on veut l'éliminer, on peut remplacer le masque BiSeNet par un masque
calculé à partir des repères DWPose (Apache 2.0). Ce n'est pas un avis juridique.

Écartés : Wav2Lip (non commercial), CodeFormer (licence S-Lab, non commerciale).

Tout a tourné en local. Aucune vidéo ni voix n'est partie vers un service en ligne : on a seulement *téléchargé*
les poids depuis les sources ci-dessus.

## Réglages essayés (clip 2, gros plan)

MuseTalk 1.5 génère le bas du visage **en un seul passage, à 256×256 px**. Il n'a donc pas de « nombre
d'étapes », et la taille de génération est fixe. Les réglages possibles portent sur le cadrage et le masque
de collage.

| Essai | Réglages | Résultat |
|---|---|---|
| A, défaut | marge menton 10 px, masque `jaw`, joues 90, bord haut 0,50 | flou, moustache effacée, barbe lissée |
| **B, retenu** | marge 10, masque `jaw`, **joues 60**, **bord haut 0,55**, **cadre lissé sur 5 images** | un peu plus de vraie barbe gardée sur les côtés, cadre plus stable |
| C | masque `raw`, marge 0, cadre lissé | pas mieux que B |

Aucun réglage ne règle le fond du problème : la moustache et la texture de la barbe disparaissent dans tous les
cas. Pour le clip 2, le visage fait 395×520 px : la sortie 256 px y est agrandie environ 2 fois, d'où le flou.

## Temps de calcul (processeur, 4 cœurs)

| Clip | Images | Repères du visage | Synchro labiale | Collage + encodage | **Total** |
|---|---|---|---|---|---|
| 1 quinze | 73 | 350 s | 245 s | 18 s | **10,6 min** |
| 2 presque sûr | 100 | 460 s | 349 s | 28 s | **≈ 14,5 min** |
| 3 tu te dis | 198 | 877 s | 672 s | 52 s | **27 min** |
| 4 quarante jours | 222 | 983 s | 731 s | 58 s | **30 min** |

Cela fait environ 8,5 s de calcul par image, soit **à peu près 4 à 5 min par seconde de vidéo**. Plus de la
moitié de ce temps passe dans la détection des repères (DWPose en 1080p sur processeur). Avec une carte
graphique, le tout prendrait quelques secondes par clip.

## Avis clip par clip (regardé image par image autour de la bouche)

Méthode : j'ai fait des recadrages avant/après à la résolution d'origine et des bandes d'images consécutives.
J'ai aussi placé chaque mot anglais dans le temps (whisper-tiny en local) pour vérifier les formes de bouche
attendues. Je n'ai pas pu *écouter* les aperçus : il faut les regarder avec le son pour juger la synchro.

**Points communs aux 4 clips**
- Moustache **effacée** : peau lisse au-dessus de la lèvre, bien visible quand on compare avec le source.
- Barbe sous la lèvre et au menton **lissée**, sans poils, comme floutée.
- Lèvres uniformément roses, un peu « plastique ». Dents réduites à une bande blanche floue.
- Articulation **molle** : la bouche s'ouvre peu et reste mi-ouverte. Les fermetures attendues sur p/b/m sont
  absentes ou à peine marquées (ex. « **p**retty », « **p**ressed » au clip 2). Le rythme suit la voix, mais ça
  ressemble à quelqu'un qui marmonne.
- Bons points : pas de scintillement d'une image à l'autre, pas de bouche qui glisse, pas de couture visible au
  bord du visage ni contre la capuche. Les yeux et le haut du visage restent intacts.

| Clip | Publiable ? | Détails |
|---|---|---|
| 1 « Fifteen minutes. » | **Non, limite** | La bouche reste bien fermée pendant le blanc de 0,8 s. Clip court, plan large : à taille normale ça passe presque, mais la moustache manquante se voit. |
| 2 « …pressed it too. » (gros plan) | **Non** | Le pire des quatre : flou net sur tout le bas du visage, barbe en bouillie, lèvres cireuses. |
| 3 « You might be thinking… » | **Non, limite** | Mêmes défauts qu'au clip 1. Les lèvres s'arrondissent bien sur « too ». Sur 6,6 s, l'articulation molle finit par se remarquer. |
| 4 « I'm not going to ask you… » | **Non, limite** | Idem. Bord du visage propre. Certains mots arrondis (« Tonight ») donnent une bouche neutre au lieu de lèvres arrondies. |

« Limite » veut dire : acceptable dans un plan bref, en incrustation ou vu sur téléphone, mais pas pour un face
caméra en plein écran à côté de plans d'origine.

**Note clip 4** : la voix anglaise dure 7,48 s pour une vidéo de 7,40 s. L'aperçu coupe donc les 0,08 dernières
secondes (fin de « expect. »).

## Ce qu'il faudrait pour faire mieux

1. **Une carte graphique de 16 Go ou plus et LatentSync 1.6** (ByteDance, génération en 512 px) : c'est le saut
   de qualité le plus net, surtout pour le gros plan. Licence : code Apache 2.0, poids à revérifier au moment
   du test.
2. Avec MuseTalk, garder la vraie moustache : restreindre le masque de collage à la zone des lèvres, calculée
   à partir des repères DWPose, au lieu du masque « mâchoire ». Ça remplacerait aussi BiSeNet (la zone grise
   de licence). Il faut cependant le tester : MuseTalk risque de laisser des décalages entre la bouche
   générée et la barbe d'origine.
3. Ne pas « regonfler » le visage avec un restaurateur (GFPGAN, CodeFormer) : CodeFormer est non commercial,
   et les deux changent les traits du visage.
4. Au montage, privilégier les plans larges ou de courtes coupes. Éviter le gros plan pour les passages doublés.

## Fichiers rendus (`lipsync_test/resultats/`, hors git)

- `clipN_*_lipsync.mp4` : 4 vidéos sans son, 1920×1080, 30 i/s, même nombre d'images et même durée que l'entrée
  (vérifié avec ffprobe : 73 / 100 / 198 / 222 images).
- `clipN_*_apercu.mp4` : les mêmes avec la voix anglaise (AAC 192 kb/s), complétée par du silence ou coupée à
  la durée de la vidéo.
- `planche.png` : pour chaque clip, 3 images (10 %, 50 %, 90 %) avant/après, recadrées sur le visage.
- `clipN_*_stats.json` : réglages exacts et temps mesurés.

Les vidéos d'origine, les voix, l'archive reçue et tous les fichiers de travail ont été effacés de la machine.
Les résultats et la planche (qui montrent le visage) ne sont **pas** dans git : seul ce rapport est versionné.

Script utilisé : `lipsync_test/scripts/run_clip.py`, à lancer depuis un clone de MuseTalk avec les poids. Réglages
retenus : `--smooth 5 --left_cheek_width 60 --right_cheek_width 60 --upper_boundary_ratio 0.55`.
