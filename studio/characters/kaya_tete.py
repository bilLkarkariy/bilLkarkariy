"""Kaya, tête de trois quarts (elle regarde vers la gauche de l'image).

Ce module ne dessine rien : il contient ce que le dessinateur sait du personnage avant de
poser le crayon. Les repères de construction, puis les formes, posées du fond vers l'avant.

Unités : « pixels d'étude ». Sommet du crâne y = 200, menton (482, 927), donc une tête
= 727. Proportions tirées des méthodes de dessin manga (voir studio/README.md) :
ligne des yeux à mi-hauteur, base du nez à mi-chemin yeux-menton, bouche au tiers
nez-menton, œil éloigné large de 0,7 fois l'œil proche, oreille entre ligne des yeux et
base du nez, cheveux décollés du crâne.
"""
import numpy as np

from studio.engine.formes import Sheet
from studio.engine.hand import spline
from studio.engine.vpath import ellipse

BOX = (150, 60, 1150, 1340)

# --- repères de construction (ce qu'on trace d'abord, léger, au crayon bleu) --------------------
GUIDES = {
    "crane": ellipse(585, 470, 272, 272),
    "mediane": "M 470 214 C 436 330 440 520 448 625 C 452 740 466 850 482 927",
    "yeux": "M 296 634 C 420 654 600 652 722 624",
    "sourcils": "M 300 566 C 420 584 600 580 730 550",
    "nez": "M 322 760 C 420 774 560 772 706 746",
    "bouche": "M 372 824 C 430 832 520 830 620 812",
    "machoire": "M 312 560 L 306 700 L 440 902 L 486 927 L 552 894 L 716 740 L 716 600",
    "oreille": "M 712 640 L 792 630 L 786 750 L 716 746",
    "cou": "M 486 930 L 474 1062 M 676 790 L 690 1040 M 474 1062 C 540 1090 630 1076 690 1040",
    "epaules": "M 250 1150 C 420 1050 760 1040 1060 1170",
    "cheveux": "M 300 600 C 262 420 340 210 560 170 C 720 150 850 230 880 420 C 890 560 850 700 780 760",
    "queue": "M 846 300 C 960 220 1070 380 1040 640 C 1020 780 980 880 940 950",
}

RING = (348.0, 0.00105, 560.0, 34.0)      # reflet des cheveux : y = a + b (x - c)², demi-largeur


def _even(points, n=72):
    """Courbe lisse par les points, rééchantillonnée en n points régulièrement espacés."""
    p = spline(np.asarray(points, float), per=24)
    s = np.concatenate([[0.0], np.cumsum(np.hypot(*np.diff(p, axis=0).T))])
    u = np.linspace(0, s[-1], n)
    return np.stack([np.interp(u, s, p[:, 0]), np.interp(u, s, p[:, 1])], axis=1)


def via(notch, tip, bend=(0, 0)):
    """Points de passage d'un bord de mèche : l'encoche, puis le milieu encoche-pointe, cintré."""
    return [notch, ((notch[0] + tip[0]) / 2 + bend[0], (notch[1] + tip[1]) / 2 + bend[1])]


def meche(S, name, left, right, tip, fade=0.2, pen=(True, True), shine=None, tone=1.0, **kw):
    """Une mèche : deux bords qui vont de la racine à la pointe.
    left, right : [racine, points de passage...] ; fade : force du trait à la racine (1 = plein),
    un nombre ou un couple (bord gauche, bord droit)."""
    L, R = _even(list(left) + [tip]), _even(list(right) + [tip])
    pts = np.concatenate([L, R[::-1][1:]])
    n = len(L)
    stroked = np.ones(len(pts), bool)
    stroked[0] = False
    if not pen[0]:
        stroked[:n] = False
    if not pen[1]:
        stroked[n:] = False
    fl, fr = fade if isinstance(fade, tuple) else (fade, fade)
    up = np.clip(np.linspace(0, 1, n) / 0.6, 0, 1) ** 1.3
    weight = np.concatenate([fl + (1 - fl) * up, (fr + (1 - fr) * up)[::-1][1:]])
    kw.setdefault("w", 0.72)
    it = S.shape("cheveux", subs=[dict(pts=pts, pen=stroked, corners=[n - 1], closed=False, weight=weight)],
                 name=name, **kw)
    it.update(lock=(L, R), shine=shine, tone=tone)
    return it


def build():
    S = Sheet()
    grp = {"g": ""}
    add = S._add

    def tagged(kind, d=None, subs=None, **kw):
        it = add(kind, d, subs, **kw)
        it["group"] = grp["g"]
        return it
    S._add = tagged

    # --- queue de cheval (derrière tout) ----------------------------------------------------------
    grp["g"] = "queue"
    tail = dict(shine=("t", 0.24, 0.08))
    meche(S, "P4", [(848, 318), (890, 380), (910, 520), (904, 680)], [(846, 332), (870, 400), (886, 540), (880, 690)],
          (862, 792), fade=0.7, tone=1.3, **tail)
    meche(S, "P3", [(850, 310), (914, 342), (952, 450), (958, 610), (932, 760)],
          [(848, 328), (890, 380), (910, 500), (912, 650), (896, 760)], (884, 838), fade=0.7, tone=1.15, **tail)
    meche(S, "P2", [(852, 300), (940, 290), (1000, 400), (1010, 560), (986, 720)],
          [(850, 322), (912, 344), (950, 450), (956, 600), (940, 740)], (930, 854), fade=0.7, **tail)
    meche(S, "P1", [(852, 290), (930, 222), (1020, 250), (1066, 380), (1060, 540), (1024, 690)],
          [(858, 316), (936, 300), (994, 400), (1004, 540), (990, 680)], (990, 792), fade=0.85, **tail)
    S.line("M 1052 400 C 1082 450 1092 520 1084 590", w=0.45, taper=(0.3, 0.5))
    S.line("M 1010 262 C 1040 300 1056 340 1062 384", w=0.45, taper=(0.3, 0.5))

    # --- buste : épaules, capuche -------------------------------------------------------------------
    grp["g"] = "buste"
    S.shape("sweat",
            "M 232 1340 C 236 1240 246 1160 264 1118 C 290 1072 340 1044 392 1032 X 478 990 X 692 956 X 900 1040 "
            "C 962 1062 1026 1108 1054 1174 C 1072 1228 1082 1290 1084 1340", name="corps")
    S.line("M 968 1088 C 990 1158 994 1250 982 1340", w=0.55, taper=(0.2, 0.5))
    S.line("M 880 1078 C 846 1118 790 1148 734 1164", w=0.55, taper=(0.1, 0.6))
    S.line("M 384 1062 C 402 1098 432 1126 472 1144", w=0.55, taper=(0.1, 0.6))
    S.line("M 310 1210 C 324 1256 330 1300 330 1340", w=0.5, taper=(0.3, 0.5))
    S.line("M 640 1120 C 660 1180 664 1250 656 1320", w=0.45, taper=(0.3, 0.5))
    S.line("M 440 1180 C 456 1230 462 1280 460 1330", w=0.45, taper=(0.3, 0.5))
    S.shape("sweat",
            "M 392 1032 C 378 1002 384 970 404 958 C 430 944 456 964 478 990 X 692 956 "
            "C 704 930 724 908 752 896 C 790 882 842 884 876 906 C 904 926 914 972 908 1018 C 904 1042 888 1060 862 1068 "
            "C 820 1050 780 1040 744 1036 X 560 1078", name="capuche")
    S.line("M 706 962 C 740 934 800 922 850 936 C 872 944 886 958 892 978", w=0.6, taper=(0.05, 0.4))
    S.line("M 760 990 C 790 972 826 968 858 978", w=0.45, taper=(0.2, 0.5))
    S.line("M 744 1036 C 770 1008 812 994 866 1002", w=0.55, taper=(0.1, 0.5))
    S.line("M 420 968 C 408 984 402 1004 406 1022", w=0.5, taper=(0.2, 0.5))
    S.shadow("M 744 1036 C 780 1040 820 1050 862 1068 C 850 1098 820 1118 780 1124 C 764 1088 752 1062 744 1036 Z",
             on="sweat", w=0.0)

    # --- cou ---------------------------------------------------------------------------------------------
    grp["g"] = "cou"
    S.shape("peau", "M 487 918 C 490 950 486 974 478 1000 X 500 1050 X 540 1060 X 700 990 C 684 920 680 860 676 786",
            name="cou")
    S.line("M 650 838 C 634 890 600 950 556 1004", w=0.5, taper=(0.2, 0.5))
    S.shadow("M 470 900 X 700 770 C 696 850 676 900 624 934 C 584 958 524 962 482 986 Z", on="peau", w=0.0)

    # --- col : deux pans de capuche qui se croisent, cordons -------------------------------------------------
    grp["g"] = "buste"
    S.shape("sweat", "M 478 990 C 488 1012 506 1030 530 1040 L 552 1070 C 516 1064 480 1044 462 1014 Z", name="pan_e")
    S.shape("sweat", "M 692 956 C 660 992 600 1030 536 1046 L 528 1078 C 600 1068 670 1028 708 982 Z", name="pan_p")
    S.shadow("M 692 956 C 660 992 600 1030 536 1046 L 534 1056 C 600 1042 664 1004 698 966 Z", on="sweat", w=0.0)
    S.shadow("M 478 990 C 488 1012 506 1030 530 1040 L 536 1048 C 506 1040 484 1022 472 1000 Z", on="sweat", w=0.0)
    S.shape("cordon", "M 512 1070 C 510 1122 506 1172 500 1222 L 513 1224 C 519 1174 523 1124 525 1072 Z", w=0.6)
    S.shape("cordon", "M 572 1072 C 578 1126 582 1178 584 1232 L 597 1230 C 595 1178 591 1126 585 1068 Z", w=0.6)

    # --- cheveux tirés vers l'attache ---------------------------------------------------------------------
    grp["g"] = "calotte"
    meche(S, "cap_cote", [(770, 700), (790, 560), (806, 420)],
          [(778, 748), (804, 716), (838, 640), (870, 500), (868, 380)], (846, 306),
          fade=1.0, pen=(False, True), tone=1.25, shine=("ring",), w=1.0)
    meche(S, "cap_haut", [(612, 166), (700, 166), (792, 216)], [(640, 200), (740, 240), (800, 296)], (846, 306),
          fade=(1.0, 0.2), pen=(True, False), shine=("ring",), w=1.0)
    meche(S, "epi_a", [(588, 180), (584, 140)], [(601, 182), (599, 138)], (538, 98), fade=0.5, w=0.7)
    meche(S, "epi_b", [(606, 180), (622, 150)], [(617, 184), (636, 160)], (670, 128), fade=0.5, w=0.7)
    S.line("M 476 196 C 446 184 414 190 390 208", w=0.45, taper=(0.35, 0.45))
    S.line("M 720 170 C 752 162 782 170 804 190", w=0.45, taper=(0.35, 0.45))
    S.line("M 330 360 C 312 380 300 404 294 432", w=0.45, taper=(0.35, 0.45))
    S.shape("elastique", "M 828 292 C 840 280 860 286 866 302 C 870 318 860 334 846 336 C 832 334 822 312 828 292 Z",
            name="elastique")
    S.line("M 838 290 C 848 300 852 316 848 334", w=0.5)

    # --- oreille, visage -------------------------------------------------------------------------------------
    grp["g"] = "visage"
    S.shape("peau", "M 712 650 C 722 622 760 610 780 634 C 798 660 786 716 754 744 C 742 754 728 754 718 740",
            name="oreille")
    S.line("M 736 654 C 754 646 768 662 763 688 C 759 706 750 716 742 722", w=0.55)
    S.line("M 743 676 C 750 690 746 702 738 708", w=0.55)
    S.shadow("M 730 650 C 754 640 772 660 766 690 C 760 712 748 724 738 730 C 730 700 728 676 730 650 Z",
             on="peau", w=0.0)
    S.shape("peau",
            "M 314 590 C 308 616 305 640 306 662 C 304 690 308 720 320 748 C 340 800 388 858 440 902 "
            "C 456 916 470 927 486 927 C 506 927 528 914 552 894 L 652 806 C 684 778 704 760 716 738 "
            "X 714 650 X 700 470 X 500 380 X 330 440", name="visage")

    # --- yeux -----------------------------------------------------------------------------------------------------
    grp["g"] = "yeux"
    S.shape("oeil", "M 534 660 C 544 648 560 638 580 630 C 602 621 634 617 656 623 C 676 629 690 637 698 644 "
            "C 690 656 676 664 656 667 C 624 672 584 670 560 666 C 548 664 540 662 534 660", w=0.0, name="blanc_p")
    S.shape("iris", ellipse(606, 644, 36, 41), w=0.8, on="oeil", name="iris_p")
    S.shadow("M 560 596 L 650 596 L 650 648 C 626 634 588 634 560 648 Z", on="iris", w=0.0)
    S.ink(ellipse(604, 646, 12, 15), on=["iris", "oeil"], name="pupille")
    S.shape("reflet", ellipse(588, 633, 9.5, 9.5), w=0.0, on=["iris", "encre", "oeil"])
    S.shape("reflet", ellipse(623, 660, 4, 4), w=0.0, on=["iris", "encre", "oeil"])
    S.ink("M 522 658 C 532 640 550 626 572 617 C 598 607 632 602 656 608 C 672 612 684 620 694 632 L 700 642 "
          "C 690 636 676 628 656 622 C 632 616 600 620 578 629 C 558 637 542 648 532 660 Z", name="cils_p")
    S.line("M 688 628 L 706 620", w=0.5, taper=(0.05, 0.7))
    S.line("M 590 670 C 620 673 654 670 682 658", w=0.5, taper=(0.3, 0.25))
    S.line("M 560 606 C 590 594 634 590 668 600", w=0.4, taper=(0.3, 0.3))
    S.shape("oeil", "M 402 664 C 396 652 388 644 376 636 C 360 628 340 624 322 630 C 308 636 298 644 292 650 "
            "C 298 660 310 666 324 669 C 346 673 372 672 388 668 C 394 667 398 666 402 664", w=0.0, name="blanc_e")
    S.shape("iris", ellipse(350, 646, 26, 41), w=0.8, on="oeil", name="iris_e")
    S.shadow("M 318 598 L 384 598 L 384 650 C 366 636 338 636 318 650 Z", on="iris", w=0.0)
    S.ink(ellipse(348, 648, 9.5, 15), on=["iris", "oeil"], name="pupille")
    S.shape("reflet", ellipse(338, 635, 7.5, 7.5), w=0.0, on=["iris", "encre", "oeil"])
    S.shape("reflet", ellipse(361, 662, 3.5, 3.5), w=0.0, on=["iris", "encre", "oeil"])
    S.ink("M 412 662 C 406 646 396 632 382 624 C 364 614 338 610 320 616 C 308 620 300 628 294 638 L 290 648 "
          "C 298 640 308 632 322 628 C 340 622 362 626 378 634 C 390 642 398 652 404 664 Z", name="cils_e")
    S.line("M 298 634 L 284 626", w=0.45, taper=(0.05, 0.7))
    S.line("M 318 669 C 340 674 366 672 386 666", w=0.5, taper=(0.25, 0.3))
    S.line("M 316 606 C 336 596 366 598 388 610", w=0.4, taper=(0.3, 0.3))
    S.ink("M 512 596 C 550 580 596 570 636 568 C 656 568 672 572 686 578 L 684 584 C 670 579 654 577 636 577 "
          "C 598 579 554 589 516 604 Z", name="sourcil_p")
    S.ink("M 416 598 C 394 584 366 576 342 574 C 328 574 316 578 306 584 L 308 590 C 318 584 330 583 342 583 "
          "C 366 585 392 592 412 607 Z", name="sourcil_e")
    grp["g"] = "visage"
    S.line("M 438 716 C 432 730 426 742 421 750", w=0.65, taper=(0.3, 0.1), name="nez")
    S.line("M 426 760 C 433 764 442 764 449 760", w=0.5, taper=(0.3, 0.3))
    S.line("M 436 814 C 452 818 470 818 486 816 C 496 816 506 814 514 811", w=0.7, taper=(0.15, 0.25), name="bouche")
    S.line("M 466 837 C 474 840 484 840 490 837", w=0.4, taper=(0.3, 0.3))

    # --- frange : pointes et encoches -------------------------------------------------------------------------
    grp["g"] = "frange"
    T = {1: (258, 736), 2: (340, 600), 3: (408, 642), 4: (464, 716), 5: (566, 618), 6: (640, 572),
         7: (706, 650), 8: (730, 850)}
    N = {12: (320, 540), 23: (378, 548), 34: (436, 560), 45: (512, 520), 56: (604, 478), 67: (676, 536),
         78: (724, 580)}
    ring = dict(shine=("ring",))
    # mèche qui s'échappe du côté éloigné, derrière les autres
    meche(S, "B1", [(540, 172), (420, 196), (328, 286), (280, 400)], [(556, 182), (440, 228), (360, 320), (306, 440)],
          (230, 578), fade=(1.0, 0.2), **ring)
    # petites mèches intercalaires, dont seule la pointe dépasse dans une encoche
    meche(S, "s1", [(576, 190), (500, 240), (440, 400), (420, 580)], [(586, 192), (516, 244), (460, 400), (438, 580)],
          (430, 680), **ring)
    meche(S, "s2", [(626, 196), (670, 260), (676, 400), (664, 530)], [(636, 198), (690, 260), (696, 400), (684, 530)],
          (678, 612), **ring)
    meche(S, "F1", [(556, 172), (430, 206), (348, 292), (298, 420), (272, 580)],
          [(566, 182), (452, 238), (384, 336), N[12], (290, 640)], T[1], fade=(1.0, 0.2), **ring)
    meche(S, "F2", [(562, 180), (436, 234), (368, 334), N[12]], [(574, 186), (500, 224), (424, 320), N[23]],
          T[2], **ring)
    meche(S, "F3", [(570, 184), (488, 228), (412, 326), N[23], (386, 600)],
          [(584, 188), (540, 230), (484, 320), N[34], (426, 606)], T[3], **ring)
    meche(S, "F8", [(636, 194), (706, 250), (744, 352), N[78], (708, 700)],
          [(660, 202), (750, 248), (800, 340), (800, 470), (784, 640), (760, 760)], T[8], tone=1.1, **ring)
    meche(S, "F7", [(622, 192), (668, 250), (690, 346), N[67]], [(644, 198), (720, 248), (760, 350), N[78]],
          T[7], **ring)
    meche(S, "F6", [(608, 190), (612, 260), (606, 340), N[56]], [(630, 194), (676, 246), (700, 340), N[67]],
          T[6], **ring)
    meche(S, "F5", [(596, 188), (572, 248), (538, 334), N[45]], [(616, 192), (624, 258), (620, 340), N[56]],
          T[5], **ring)
    meche(S, "F4", [(580, 186), (528, 234), (468, 306), N[34], (440, 640)],
          [(604, 190), (580, 248), (548, 330), N[45], (482, 630)], T[4], **ring)
    meche(S, "s3", [(590, 186), (560, 250), (524, 340), (506, 520), (510, 600)],
          [(598, 188), (572, 250), (540, 340), (526, 520), (528, 600)], (522, 656), **ring)
    S.cast(["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "s1", "s2", "s3"], 9, 20, on="peau")
    S._add = add
    return S
