# V01 UR — repères de finition

Calculés sur `src/data/v01_ur.vo.json` et le WAV assemblé `public/vo/v01_ur.wav`, à 30 i/s. Les temps voix sont ceux du WAV **final**, pas de la prise brute. Vidéo = voix + **0,8 s** ; image = `24 + Math.round(voix × 30)`. Les fins des fenêtres de montage sont exclusives. Les fins de mots sont les bornes de l’alignement, arrondies à l’image la plus proche.

Référence des six remplacements : `docs/v01-finition.md` sur `studio/v01-en`. Les bornes ci-dessous sont recalculées sur les mots ourdous et les transitions du montage ; les images anglaises ne sont pas transposées proportionnellement. Aucun de ces inserts n’a été rendu ou posé ici.

## Intro Pixar

Claude posera les images de l’intro après Remotion. Garder la voix ourdoue seule jusqu’au fondu ; recaler les bruitages propres à l’intro. Couper la source visuelle avant son crédit « Wilson et al. », visible vers 13,7 s dans l’intro française.

| Repère | Segment | Voix (s) | Temps vidéo | Images vidéo |
|---|---|---:|---:|---:|
| پندرہ منٹ | `s1` | 0.800 → 1.580 | 00:01.600 → 00:02.380 | 48 → 71 |
| اکیلے | `s2` | 3.685 → 4.555 | 00:04.485 → 00:05.355 | 135 → 161 |
| نہ فون | `s3` | 4.905 → 5.780 | 00:05.705 → 00:06.580 | 171 → 197 |
| بس آپ اور آپ کے خیالات | `s4` | 7.770 → 9.570 | 00:08.570 → 00:10.370 | 257 → 311 |
| ایک بٹن | `s5` | 10.730 → 11.290 | 00:11.530 → 00:12.090 | 346 → 363 |
| بجلی کا جھٹکا | `s5` | 12.030 → 13.070 | 00:12.830 → 00:13.870 | 385 → 416 |
| تین میں سے دو مردوں | `s6` | 15.840 → 17.185 | 00:16.640 → 00:17.985 | 499 → 540 |
| Phrase entière : تین میں سے دو مردوں نے اسے دبا دیا | `s6` | 15.840 → 18.175 | 00:16.640 → 00:18.975 | 499 → 569 |

## Six fenêtres à remplacer

| Passage | Voix (s, fenêtre complète) | Temps vidéo | Images [début, fin[ | Calcul |
|---|---:|---:|---:|---|
| Film muet | 186.033 → 196.333 | 03:06.833 → 03:17.133 | **5605 → 5914** | « اکیلے سوچنا » − 9 images → p21 − 4 |
| Nuit au crayon | 306.833 → 314.600 | 05:07.633 → 05:15.400 | **9229 → 9462** | p32 − 6 → p33 − 6 |
| Khalwa VHS | 388.300 → 396.033 | 06:29.100 → 06:36.833 | **11673 → 11905** | p41 − 4 → p42 − 4 |
| Exercice 1 | 551.933 → 577.667 | 09:12.733 → 09:38.467 | **16582 → 17354** | p54 − 6 → p57 − 6 |
| Exercice 2 | 614.800 → 631.667 | 10:15.600 → 10:32.467 | **18468 → 18974** | p59 − 6 → p61 − 6 |
| Veste, fenêtre 6 | 521.567 → 537.067 | 08:42.367 → 08:57.867 | **15671 → 16136** | aroll6 → fondIn, src/montage/p4.tsx |

La fenêtre du film commence 9 images avant « اکیلے سوچنا » et finit à l’entrée de p21. Les cinq autres fenêtres suivent les transitions du montage. Les tableaux suivants donnent séparément les bornes de la parole, sans ces marges.

### Film muet

| Repère | Segment | Voix (s) | Temps vidéo | Images vidéo |
|---|---|---:|---:|---:|
| Début : اکیلے سوچنا | `s31` | 186.340 → 187.260 | 03:07.140 → 03:08.060 | 5614 → 5642 |
| Décrochage : جیسے ہی لکھاری تھکتا ہے | `s31` | 191.960 → 193.500 | 03:12.760 → 03:14.300 | 5783 → 5829 |
| Fin : فلم ہر طرف بکھر جاتی ہے | `s31` | 193.500 → 195.700 | 03:14.300 → 03:16.500 | 5829 → 5895 |

### Nuit au crayon

| Repère | Segment | Voix (s) | Temps vidéo | Images vidéo |
|---|---|---:|---:|---:|
| Passage entier | `s43` | 307.035 → 314.005 | 05:07.835 → 05:14.805 | 9235 → 9444 |
| آنکھ کھلتی ہے | `s43` | 308.855 → 309.695 | 05:09.655 → 05:10.495 | 9290 → 9315 |
| پہلا ردِعمل | `s43` | 312.115 → 313.315 | 05:12.915 → 05:14.115 | 9387 → 9423 |
| اسکرین | `s43` | 313.315 → 314.005 | 05:14.115 → 05:14.805 | 9423 → 9444 |

### Khalwa VHS

| Repère | Segment | Voix (s) | Temps vidéo | Images vidéo |
|---|---|---:|---:|---:|
| Passage entier | `s52` | 388.420 → 394.800 | 06:29.220 → 06:35.600 | 11677 → 11868 |
| لفظی مطلب | `s52` | 393.000 → 393.760 | 06:33.800 → 06:34.560 | 11814 → 11837 |
| تنہائی | `s52` | 393.980 → 394.800 | 06:34.780 → 06:35.600 | 11843 → 11868 |

### Exercice 1

| Repère | Segment | Voix (s) | Temps vidéo | Images vidéo |
|---|---|---:|---:|---:|
| Invitation, début du passage | `s65` | 552.120 → 560.640 | 09:12.920 → 09:21.440 | 16588 → 16843 |
| چالیس | `s65` | 554.100 → 554.760 | 09:14.900 → 09:15.560 | 16647 → 16667 |
| دو منٹ | `s65` | 557.100 → 557.760 | 09:17.900 → 09:18.560 | 16737 → 16757 |
| ایک, étape 1 | `s66` | 561.970 → 562.430 | 09:22.770 → 09:23.230 | 16883 → 16897 |
| دو, étape 2 | `s67` | 572.910 → 573.350 | 09:33.710 → 09:34.150 | 17211 → 17225 |
| Fin : ایک کرسی کافی ہے | `s67` | 575.430 → 576.870 | 09:36.230 → 09:37.670 | 17287 → 17330 |

### Exercice 2

| Repère | Segment | Voix (s) | Temps vidéo | Images vidéo |
|---|---|---:|---:|---:|
| Étape 5, début du passage | `s70` | 615.010 → 620.840 | 10:15.810 → 10:21.640 | 18474 → 18649 |
| پانچ | `s70` | 615.010 → 615.460 | 10:15.810 → 10:16.260 | 18474 → 18488 |
| Suite et fin | `s71` | 622.015 → 631.075 | 10:22.815 → 10:31.875 | 18684 → 18956 |
| چالیس سیکنڈ | `s71` | 624.585 → 625.325 | 10:25.385 → 10:26.125 | 18762 → 18784 |
| بس وقت دیکھنے کے لیے | `s71` | 629.525 → 631.075 | 10:30.325 → 10:31.875 | 18910 → 18956 |

### Veste, fenêtre 6

| Repère | Segment | Voix (s) | Temps vidéo | Images vidéo |
|---|---|---:|---:|---:|
| Début de p53 | `s64` | 521.770 → 523.790 | 08:42.570 → 08:44.590 | 15677 → 15738 |
| Veste : یہ پیوند لگا خرقہ اس کا لباس ہے | `s64` | 534.570 → 537.190 | 08:55.370 → 08:57.990 | 16061 → 16140 |
| Sortie vers les fondements | `s64` | 537.190 → 539.730 | 08:57.990 → 09:00.530 | 16140 → 16216 |

## Bruitages à couper

Les cinq passages animés, plus `[0, 30]`. La veste n’est pas un passage animé et n’entre pas dans cette liste. Les bornes sont en images de la vidéo longue.

```json
{"sfxOff":[[0,30],[5605,5914],[9229,9462],[11673,11905],[16582,17354],[18468,18974]]}
```

Propriétés complètes à transmettre au rendu :

```json
{"clean":true,"no3d":false,"faceless":true,"sfxOff":[[0,30],[5605,5914],[9229,9462],[11673,11905],[16582,17354],[18468,18974]]}
```

Le mode `faceless` est obligatoire pour V01-UR ; les fenêtres 6 (veste) et 7 (invitation) seront complétées par les inserts de Claude.

## Verset et chuchotements

| Repère | Segment | Voix (s) | Temps vidéo | Images vidéo |
|---|---|---:|---:|---:|
| Verset parlé : قرآن اسے ایک جملے میں کہتا ہے… | `s63` | 513.850 → 519.930 | 08:34.650 → 08:40.730 | 15440 → 15622 |
| Premier استغفراللہ chuchoté | `s69` | 611.410 → 612.630 | 10:12.210 → 10:13.430 | 18366 → 18403 |
| Second استغفراللہ chuchoté | `s69` | 612.730 → 614.010 | 10:13.530 → 10:14.810 | 18406 → 18444 |

Verset affiché sur les images **15430 → 15652** : arabe uthmani exact, Amiri Quran, fondu seul. La voix continue ; musique et bruitages sont coupés sur toute la fenêtre. Aucun silence ajouté au WAV pour le verset.

Les chuchotements ont reçu +12 dB, avec des fondus de 30 ms, sans saturation. Contrôle numérique et reconnaissance Whisper uniquement ; écoute humaine et contrôle de la vidéo finale restent à faire.
