# V01 AR — repères de finition

Calculés sur `src/data/v01_ar.vo.json` et `public/vo/v01_ar.wav`, à 30 i/s. Temps voix du WAV **assemblé**, pas de la brute. Vidéo = voix + **0,8 s** ; image = `24 + Math.round(voix × 30)`. Fins de fenêtres exclusives. Les fins de mots sont arrondies à l’image la plus proche.

Référence des six remplacements : `../../billkarkariy-en/studio/docs/v01-finition.md`. Méthode reprise de la finition ourdoue : chaque fenêtre suit les mots arabes et les transitions du montage. Aucun insert rendu ou posé ici.

## Intro Pixar

Garder la voix arabe seule jusqu’au fondu, puis recaler les bruitages propres à l’intro. Couper la source française avant le crédit « Wilson et al. », visible vers 13,7 s.

| Repère | Segment | Voix (s) | Temps vidéo | Images vidéo |
|---|---|---:|---:|---:|
| خمس عشرة دقيقة | `s1` | 0.800 → 2.240 | 00:01.600 → 00:03.040 | 48 → 91 |
| وحدك | `s2` | 2.810 → 3.360 | 00:03.610 → 00:04.160 | 108 → 125 |
| لا هاتف | `s3` | 5.220 → 6.120 | 00:06.020 → 00:06.920 | 181 → 208 |
| أنت وأفكارك | `s4` | 8.265 → 9.700 | 00:09.065 → 00:10.500 | 272 → 315 |
| وزرٌّ | `s5` | 10.555 → 11.780 | 00:11.355 → 00:12.580 | 341 → 377 |
| بشحنة كهربائية | `s5` | 12.720 → 14.280 | 00:13.520 → 00:15.080 | 406 → 452 |
| ضغط عليه رجلان من كل ثلاثة | `s6` | 15.880 → 18.945 | 00:16.680 → 00:19.745 | 500 → 592 |

## Six fenêtres à remplacer

| Passage | Voix (s, fenêtre complète) | Temps vidéo | Images [début, fin[ | Calcul |
|---|---:|---:|---:|---|
| Film muet | 188.433 → 199.167 | 03:09.233 → 03:19.967 | **5677 → 5999** | « أن تفكر وحدك » − 9 images → p21 − 4 |
| Nuit au crayon | 312.967 → 320.267 | 05:13.767 → 05:21.067 | **9413 → 9632** | p32 − 6 → p33 − 6 |
| Khalwa VHS | 385.267 → 391.600 | 06:26.067 → 06:32.400 | **11582 → 11772** | p41 − 4 → p42 − 4 |
| Exercice 1 | 538.333 → 563.767 | 08:59.133 → 09:24.567 | **16174 → 16937** | p54 − 6 → p57 − 6 |
| Exercice 2 | 597.600 → 616.200 | 09:58.400 → 10:17.000 | **17952 → 18510** | p59 − 6 → p61 − 6 |
| Veste, fenêtre 6 | 508.300 → 522.033 | 08:29.100 → 08:42.833 | **15273 → 15685** | aroll6 → fondIn, src/montage/p4.tsx |

La fenêtre film commence 9 images avant « أن تفكر وحدك » ; les autres suivent les transitions du montage. Les tableaux suivants donnent les bornes de parole, sans les marges.

### Film muet

| Repère | Segment | Voix (s) | Temps vidéo | Images vidéo |
|---|---|---:|---:|---:|
| Début : أن تفكر وحدك | `s31` | 188.740 → 190.020 | 03:09.540 → 03:10.820 | 5686 → 5725 |
| Décrochage : وما إن يتعب | `s31` | 194.220 → 195.380 | 03:15.020 → 03:16.180 | 5851 → 5885 |
| Fin | `s31` | 195.920 → 198.520 | 03:16.720 → 03:19.320 | 5902 → 5980 |

### Nuit au crayon

| Repère | Segment | Voix (s) | Temps vidéo | Images vidéo |
|---|---|---:|---:|---:|
| Passage entier | `s43` | 313.175 → 319.650 | 05:13.975 → 05:20.450 | 9419 → 9614 |
| تستيقظ | `s43` | 314.940 → 315.660 | 05:15.740 → 05:16.460 | 9472 → 9494 |
| أول ردّ فعل | `s43` | 317.540 → 318.680 | 05:18.340 → 05:19.480 | 9550 → 9584 |
| الشاشة | `s43` | 318.680 → 319.650 | 05:19.480 → 05:20.450 | 9584 → 9614 |

### Khalwa VHS

| Repère | Segment | Voix (s) | Temps vidéo | Images vidéo |
|---|---|---:|---:|---:|
| Passage entier | `s52` | 385.410 → 390.300 | 06:26.210 → 06:31.100 | 11586 → 11733 |
| كلمة تعني | `s52` | 387.500 → 388.600 | 06:28.300 → 06:29.400 | 11649 → 11682 |
| الانفراد | `s52` | 389.240 → 390.300 | 06:30.040 → 06:31.100 | 11701 → 11733 |

### Exercice 1

| Repère | Segment | Voix (s) | Temps vidéo | Images vidéo |
|---|---|---:|---:|---:|
| Invitation, début | `s65` | 538.520 → 546.165 | 08:59.320 → 09:06.965 | 16180 → 16409 |
| أربعين | `s65` | 541.005 → 541.605 | 09:01.805 → 09:02.405 | 16254 → 16272 |
| دقيقتين | `s65` | 543.325 → 544.065 | 09:04.125 → 09:04.865 | 16324 → 16346 |
| واحد | `s66` | 547.510 → 548.340 | 09:08.310 → 09:09.140 | 16449 → 16474 |
| اثنان | `s67` | 558.795 → 559.600 | 09:19.595 → 09:20.400 | 16788 → 16812 |
| Fin : يكفي كرسي | `s67` | 561.960 → 562.980 | 09:22.760 → 09:23.780 | 16883 → 16913 |

### Exercice 2

| Repère | Segment | Voix (s) | Temps vidéo | Images vidéo |
|---|---|---:|---:|---:|
| Étape 5, début | `s70` | 597.810 → 603.640 | 09:58.610 → 10:04.440 | 17958 → 18133 |
| خمسة | `s70` | 597.810 → 598.480 | 09:58.610 → 09:59.280 | 17958 → 17978 |
| Suite et fin | `s71` | 604.800 → 615.400 | 10:05.600 → 10:16.200 | 18168 → 18486 |
| أربعين ثانية | `s71` | 608.420 → 609.560 | 10:09.220 → 10:10.360 | 18277 → 18311 |
| فقط لأعرف الساعة | `s71` | 614.000 → 615.400 | 10:14.800 → 10:16.200 | 18444 → 18486 |

### Veste, fenêtre 6

| Repère | Segment | Voix (s) | Temps vidéo | Images vidéo |
|---|---|---:|---:|---:|
| Début de p53 | `s64` | 508.515 → 512.560 | 08:29.315 → 08:33.360 | 15279 → 15401 |
| Veste | `s64` | 520.020 → 522.160 | 08:40.820 → 08:42.960 | 15625 → 15689 |
| Sortie vers les fondements | `s64` | 522.160 → 524.600 | 08:42.960 → 08:45.400 | 15689 → 15762 |

## Bruitages à couper

Les cinq passages animés, plus `[0, 30]`. La veste reste hors de cette liste. Bornes en images de la vidéo longue.

```json
{"sfxOff":[[0,30],[5677,5999],[9413,9632],[11582,11772],[16174,16937],[17952,18510]]}
```

Propriétés de rendu pour la finition sans visage :

```json
{"clean":true,"no3d":false,"faceless":true,"sfxOff":[[0,30],[5677,5999],[9413,9632],[11582,11772],[16174,16937],[17952,18510]]}
```

## Verset et chuchotements

| Repère | Segment | Voix (s) | Temps vidéo | Images vidéo |
|---|---|---:|---:|---:|
| Introduction et verset récité | `s63` | 501.250 → 507.215 | 08:22.050 → 08:28.015 | 15062 → 15240 |
| Premier أستغفرُ الله chuchoté | `s69` | 593.760 → 595.140 | 09:54.560 → 09:55.940 | 17837 → 17878 |
| Second أستغفرُ الله chuchoté | `s69` | 595.140 → 596.760 | 09:55.940 → 09:57.560 | 17878 → 17927 |

Verset affiché sur les images **15052 → 15270** : dès `at("p52") - 10`, récitation comprise, puis environ une seconde. Uthmani exact, Amiri Quran, fondu seul, rien dessous. Voix audible, musique et bruitages coupés. Aucun silence ajouté (`--verse-hold 0`).

Chuchotements sans gain, échantillons d’origine conservés. Les vérifications numériques et Whisper ne remplacent pas l’écoute humaine du mix final.
