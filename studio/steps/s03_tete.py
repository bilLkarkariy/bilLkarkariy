"""Settei de Kaya — la tête de trois quarts, dessinée au crayon.

Un dessin d'animateur sur papier, monté par passes successives comme à la table :
construction au crayon bleu, croquis de recherche, mise en place au graphite,
puis ombres indiquées au crayon bleu et hachurées. Aucun aplat, aucune forme
remplie : seulement des traits.

    python3 -m studio.steps.s03_tete
"""
from pathlib import Path

import numpy as np

from studio.engine.brush import B2, BLEU, HB
from studio.engine.canvas import Document
from studio.engine.hand import Draftsman, ellipse, spline, TAU
from studio.engine.timelapse import timelapse

OUT = Path(__file__).resolve().parent.parent / "out"
W, H, S = 2200, 2400, 1150            # feuille ; S = pixels pour une hauteur de tête
O = np.array([1000.0, 1560.0])        # la pointe du menton (x à droite, y vers le haut)


def px(pts):
    return O + np.asarray(pts, float) * (S, -S)


def curve(pts):
    return px(spline(np.asarray(pts, float), per=20))


# ---------- le dessin, en hauteurs de tête. Kaya regarde vers la gauche de l'image. ----------

FACE_FAR = [(-0.33, 0.86), (-0.395, 0.72), (-0.41, 0.60), (-0.385, 0.51), (-0.40, 0.40),
            (-0.375, 0.28), (-0.31, 0.14), (-0.22, 0.04), (-0.15, 0.0)]
JAW = [(-0.15, 0.0), (-0.09, 0.005), (0.02, 0.05), (0.14, 0.13), (0.215, 0.21), (0.258, 0.285)]
EAR = [(0.318, 0.565), (0.345, 0.565), (0.366, 0.535), (0.372, 0.47), (0.356, 0.40), (0.325, 0.345)]
EAR_IN = [[(0.305, 0.525), (0.34, 0.515), (0.348, 0.46), (0.328, 0.40)], [(0.31, 0.47), (0.325, 0.44)]]
NECK_FRONT = [(0.0, 0.045), (-0.01, -0.07), (-0.02, -0.165)]
NECK_BACK = [(0.33, 0.27), (0.33, 0.12), (0.335, 0.03)]
NECK_MUSCLE = [(0.29, 0.30), (0.17, 0.06), (0.07, -0.16)]

# Frange : (bord gauche, bord droit) de chaque mèche, de la racine à la pointe. Les mèches
# partent de haut, sont de largeurs et de longueurs inégales, et laissent voir le front
# entre elles : deux longues encadrent le visage, une tombe entre les yeux.
BANGS = [
    ([(-0.385, 0.86), (-0.445, 0.68), (-0.44, 0.50), (-0.40, 0.33)], [(-0.33, 0.78), (-0.36, 0.66), (-0.395, 0.50), (-0.40, 0.33)]),
    ([(-0.33, 0.78), (-0.335, 0.66), (-0.295, 0.53)], [(-0.235, 0.80), (-0.26, 0.64), (-0.295, 0.53)]),
    ([(-0.235, 0.80), (-0.24, 0.62), (-0.215, 0.50), (-0.175, 0.415)], [(-0.07, 0.86), (-0.10, 0.70), (-0.15, 0.55), (-0.175, 0.415)]),
    ([(-0.07, 0.86), (-0.085, 0.70), (-0.06, 0.58), (-0.02, 0.50)], [(0.075, 0.83), (0.055, 0.74), (0.01, 0.62), (-0.02, 0.50)]),
    ([(0.075, 0.83), (0.07, 0.70), (0.095, 0.60), (0.125, 0.545)], [(0.17, 0.76), (0.15, 0.64), (0.125, 0.545)]),
    ([(0.17, 0.76), (0.165, 0.62), (0.185, 0.48), (0.225, 0.36)], [(0.27, 0.78), (0.262, 0.68), (0.245, 0.52), (0.225, 0.36)]),
]
SIDE_LOCK = ([(0.262, 0.60), (0.25, 0.42), (0.262, 0.24), (0.285, 0.10)],
             [(0.30, 0.72), (0.315, 0.52), (0.31, 0.30), (0.285, 0.10)])
HAIR_TOP = [(-0.375, 0.90), (-0.33, 0.975), (-0.24, 1.02), (-0.08, 1.055), (0.12, 1.05), (0.30, 0.985)]
TUFTS = [[(-0.34, 0.965), (-0.385, 1.0), (-0.41, 1.035)], [(-0.41, 1.035), (-0.355, 1.01), (-0.30, 0.995)],
         [(0.16, 1.045), (0.21, 1.075), (0.265, 1.085)], [(0.265, 1.085), (0.245, 1.045), (0.255, 1.01)]]
HAIR_BACK = [(0.38, 0.92), (0.485, 0.75), (0.50, 0.58), (0.455, 0.42), (0.36, 0.30)]
TAIL_OUT = [(0.31, 0.975), (0.40, 1.06), (0.54, 1.085), (0.68, 0.98), (0.76, 0.78), (0.775, 0.52),
            (0.73, 0.28), (0.70, 0.08)]
TAIL_IN = [(0.36, 0.90), (0.44, 0.88), (0.55, 0.80), (0.62, 0.62), (0.645, 0.40), (0.63, 0.15)]
TAIL_TIPS = [[(0.70, 0.08), (0.685, 0.17), (0.672, 0.24)], [(0.672, 0.24), (0.665, 0.12), (0.648, 0.04)],
             [(0.648, 0.04), (0.642, 0.14), (0.63, 0.15)]]
TIE = [[(0.30, 0.985), (0.335, 0.955), (0.36, 0.90)], [(0.325, 1.0), (0.365, 0.965), (0.385, 0.915)]]
COWLICK = [[(-0.10, 1.045), (-0.075, 1.12), (0.005, 1.145)], [(0.005, 1.145), (-0.04, 1.105), (-0.05, 1.052)]]
# Mèches intérieures : elles suivent le sens des cheveux, tirés vers l'attache de la queue.
STRANDS = [
    [(-0.10, 1.03), (-0.26, 0.95), (-0.33, 0.80)], [(-0.07, 1.035), (-0.19, 0.93), (-0.235, 0.82)],
    [(-0.04, 1.04), (-0.06, 0.95), (-0.07, 0.87)], [(-0.01, 1.045), (0.05, 0.94), (0.075, 0.85)],
    [(0.02, 1.05), (0.12, 0.92), (0.17, 0.78)], [(-0.20, 0.74), (-0.205, 0.60), (-0.185, 0.48)],
    [(-0.035, 0.80), (-0.045, 0.66), (-0.025, 0.55)], [(-0.40, 0.74), (-0.42, 0.58), (-0.41, 0.42)],
    [(0.21, 0.70), (0.205, 0.56), (0.22, 0.42)], [(0.04, 1.05), (0.17, 1.02), (0.29, 0.965)],
    [(0.10, 0.96), (0.22, 0.965), (0.31, 0.945)], [(0.25, 0.76), (0.31, 0.85), (0.335, 0.93)],
    [(0.40, 0.66), (0.385, 0.80), (0.35, 0.92)], [(0.47, 0.56), (0.445, 0.74), (0.375, 0.91)],
    [(0.43, 0.44), (0.47, 0.60), (0.44, 0.78)], [(0.285, 0.60), (0.283, 0.42), (0.288, 0.24)],
    [(0.52, 1.04), (0.66, 0.90), (0.715, 0.66)], [(0.47, 0.95), (0.60, 0.80), (0.67, 0.56)],
    [(0.715, 0.60), (0.705, 0.40), (0.68, 0.22)], [(0.66, 0.50), (0.665, 0.34), (0.655, 0.20)],
    [(0.37, 0.31), (0.39, 0.25), (0.40, 0.20)], [(0.345, 0.29), (0.352, 0.23), (0.35, 0.18)],
]

HOOD = [(0.335, 0.03), (0.42, 0.085), (0.52, 0.05), (0.585, -0.06), (0.565, -0.20), (0.62, -0.28)]
HOOD_FOLD = [(0.345, -0.03), (0.40, -0.10), (0.47, -0.22)]
COLLAR = [(-0.15, -0.13), (-0.05, -0.235), (0.08, -0.25), (0.25, -0.16), (0.345, -0.03), (0.335, 0.03)]
SHOULDER_FAR = [(-0.15, -0.13), (-0.30, -0.20), (-0.44, -0.31), (-0.50, -0.46), (-0.52, -0.72)]
SHOULDER_NEAR = [(0.62, -0.28), (0.80, -0.36), (0.90, -0.52), (0.93, -0.72)]
CORDS = [[(-0.075, -0.222), (-0.085, -0.42), (-0.10, -0.62)], [(-0.052, -0.236), (-0.062, -0.42), (-0.076, -0.62)],
         [(0.095, -0.248), (0.10, -0.44), (0.105, -0.64)], [(0.12, -0.24), (0.125, -0.44), (0.13, -0.64)]]
FOLDS = [[(0.40, -0.14), (0.55, -0.30), (0.62, -0.48)], [(-0.22, -0.20), (-0.33, -0.36), (-0.36, -0.52)],
         [(0.70, -0.42), (0.74, -0.58), (0.76, -0.72)]]

# Yeux : l'œil proche (à droite de l'axe du visage) et l'œil éloigné, plus étroit. Ouverture
# étroite, iris large coupé par les deux paupières : un regard posé, pas un regard rond.
EYES = [
    dict(top=[(-0.105, 0.408), (-0.07, 0.44), (-0.01, 0.456), (0.06, 0.452), (0.115, 0.435), (0.158, 0.445)],
         under=[(-0.088, 0.408), (-0.03, 0.436), (0.05, 0.432), (0.12, 0.418)],
         tick=[(0.12, 0.418), (0.135, 0.398)],
         lid=[(-0.07, 0.392), (0.0, 0.384), (0.07, 0.389), (0.118, 0.405)],
         crease=[(-0.085, 0.476), (-0.02, 0.49), (0.08, 0.478)],
         iris=((0.012, 0.418), 0.046, 0.058), pupil=((0.010, 0.414), 0.02, 0.027)),
    dict(top=[(-0.362, 0.418), (-0.335, 0.446), (-0.295, 0.455), (-0.255, 0.44), (-0.232, 0.42)],
         under=[(-0.35, 0.416), (-0.30, 0.437), (-0.245, 0.418)],
         tick=[(-0.362, 0.418), (-0.37, 0.402)],
         lid=[(-0.345, 0.394), (-0.30, 0.386), (-0.255, 0.397)],
         crease=[(-0.35, 0.476), (-0.30, 0.487), (-0.25, 0.474)],
         iris=((-0.298, 0.418), 0.029, 0.055), pupil=((-0.299, 0.414), 0.013, 0.026)),
]
BROWS = [[(-0.115, 0.495), (-0.02, 0.523), (0.09, 0.532), (0.155, 0.512)],
         [(-0.372, 0.498), (-0.33, 0.523), (-0.275, 0.523), (-0.238, 0.498)]]
NOSE = [[(-0.268, 0.312), (-0.289, 0.272), (-0.265, 0.256)], [(-0.252, 0.253), (-0.238, 0.259)]]
MOUTH = [[(-0.268, 0.150), (-0.235, 0.144), (-0.20, 0.147), (-0.158, 0.156)], [(-0.232, 0.118), (-0.20, 0.114)]]

# Ombres : contour au crayon bleu, puis hachures. La lumière vient du haut à gauche.
BANG_TIPS = [(-0.40, 0.33), (-0.33, 0.78), (-0.295, 0.53), (-0.235, 0.80), (-0.175, 0.415),
             (-0.07, 0.86), (-0.02, 0.50), (0.075, 0.83), (0.125, 0.545), (0.17, 0.76), (0.225, 0.36)]
SHADOWS = [
    [(0.0, 0.045), (0.14, 0.125), (0.215, 0.21), (0.30, 0.27), (0.325, 0.12), (0.24, 0.0),
     (0.10, -0.07), (-0.005, -0.05)],                                                # sous la mâchoire
    [(0.262, 0.58), (0.25, 0.42), (0.262, 0.26), (0.236, 0.27), (0.226, 0.42), (0.236, 0.56)],  # joue
    [(-0.266, 0.31), (-0.288, 0.272), (-0.264, 0.256), (-0.248, 0.29)],              # nez
    [(0.44, 0.88), (0.55, 0.80), (0.62, 0.62), (0.645, 0.40), (0.63, 0.16), (0.685, 0.28),
     (0.70, 0.55), (0.655, 0.78), (0.55, 0.93)],                                     # queue de cheval
    [(0.455, 0.42), (0.36, 0.30), (0.335, 0.42), (0.40, 0.56)],                      # nuque
    [(0.345, -0.03), (0.42, 0.075), (0.52, 0.04), (0.50, -0.10), (0.47, -0.22), (0.40, -0.10)],  # capuche
]


def construction(d):
    """Passe 1 : la charpente, au crayon bleu léger."""
    k = dict(pressure=0.36)
    lay = "construction"
    d.stroke(px(ellipse((0.03, 0.56), 0.44, 0.44, 0, 2.0, TAU * 1.12)), BLEU, lay, passes=2, **k)
    d.stroke(curve([(-0.06, 0.99), (-0.17, 0.85), (-0.225, 0.60), (-0.24, 0.35), (-0.20, 0.12),
                    (-0.15, 0.0)]), BLEU, lay, **k)                                  # axe du visage
    for line in ([(-0.41, 0.545), (-0.2, 0.515), (0.05, 0.525), (0.30, 0.57)],       # sourcils
                 [(-0.40, 0.445), (-0.2, 0.42), (0.05, 0.43), (0.29, 0.47)],         # yeux
                 [(-0.385, 0.29), (-0.25, 0.262), (0.0, 0.28), (0.25, 0.335)],       # nez
                 [(-0.33, 0.165), (-0.20, 0.145), (0.0, 0.17), (0.16, 0.21)]):       # bouche
        d.stroke(curve(line), BLEU, lay, overshoot=10, **k)
    d.stroke(curve(FACE_FAR), BLEU, lay, passes=2, **k)
    d.stroke(curve(JAW + [(0.275, 0.50)]), BLEU, lay, passes=2, **k)
    d.stroke(px(ellipse((0.33, 0.455), 0.05, 0.115, -0.1, 0.5, TAU * 1.1)), BLEU, lay, **k)      # oreille
    d.stroke(px(ellipse((0.16, -0.12), 0.20, 0.06, -0.12, 0, TAU * 1.1)), BLEU, lay, **k)        # cou
    d.stroke(curve([(-0.02, 0.06), (-0.03, -0.2)]), BLEU, lay, **k)
    d.stroke(curve([(0.33, 0.27), (0.35, -0.05)]), BLEU, lay, **k)
    d.stroke(curve([(-0.52, -0.36), (0.2, -0.22), (0.9, -0.42)]), BLEU, lay, overshoot=20, **k)   # épaules
    d.stroke(curve([(0.32, 0.96), (0.56, 1.06), (0.74, 0.80), (0.73, 0.40), (0.67, 0.10)]), BLEU, lay, **k)
    for e in EYES:
        (c, rx, ry) = e["iris"]
        d.stroke(px(ellipse((c[0], c[1] + 0.012), rx * 2.6, ry * 0.95, 0.05, 0.3, TAU * 1.1)), BLEU, lay, **k)


def rough(d):
    """Passe 2 : le croquis. On cherche les formes, traits repris et lâchés."""
    k = dict(pressure=0.34, passes=2, reach=260, taper=(0.2, 0.3))
    lay = "rough"
    for c in (FACE_FAR[2:], JAW, EAR, NECK_FRONT, NECK_BACK, HAIR_TOP, HAIR_BACK, TAIL_OUT, TAIL_IN,
              HOOD, COLLAR, SHOULDER_FAR, SHOULDER_NEAR, SIDE_LOCK[0], SIDE_LOCK[1]):
        d.stroke(curve(c), HB, lay, **k)
    for left, right in BANGS:
        d.stroke(curve(left), HB, lay, **k)
        d.stroke(curve(right), HB, lay, **k)
    for e in EYES:
        d.stroke(curve(e["top"]), HB, lay, **k)
        d.stroke(curve(e["lid"]), HB, lay, **k)
    for c in BROWS + NOSE[:1] + MOUTH[:1]:
        d.stroke(curve(c), HB, lay, **k)


def tie_down(d):
    """Passe 3 : la mise en place au graphite. Traits décidés, plus appuyés sur les contours."""
    lay = "net"

    def line(pts, w=1.0, taper=(0.12, 0.22), tip=0.25, **kw):
        d.stroke(curve(pts), B2, lay, pressure=0.62 * w, taper=taper, tip=tip, **kw)

    def flick(pts, w=1.0):
        """Mèche : on part appuyé de la racine et on lâche vers la pointe."""
        d.stroke(curve(pts), B2, lay, pressure=0.6 * w, taper=(0.08, 0.6), tip=0.04)

    # Visage.
    line(FACE_FAR[3:], 1.3, taper=(0.15, 0.1))
    line(JAW, 1.3, taper=(0.1, 0.25))
    line(EAR, 0.95)
    for c in EAR_IN:
        line(c, 0.55, taper=(0.3, 0.3), tip=0.1)
    line(NECK_FRONT, 0.95)
    line(NECK_BACK, 0.95)
    line(NECK_MUSCLE, 0.4, taper=(0.3, 0.5), tip=0.05)
    for e in EYES:
        top, under = curve(e["top"]), curve(e["under"])
        d.stroke(top, B2, lay, passes=2, pressure=0.85, taper=(0.12, 0.12), tip=0.3)
        d.stroke(under, B2, lay, pressure=0.7, taper=(0.15, 0.15))
        d.hatch(np.vstack([top, under[::-1]]), B2, lay, 0.35, 2.3, pressure=0.85, taper=(0.1, 0.1))  # cils
        line(e["tick"], 0.9, taper=(0.1, 0.5), tip=0.05)
        line(e["lid"], 0.55, taper=(0.3, 0.25), tip=0.08)
        line(e["crease"], 0.4, taper=(0.3, 0.3), tip=0.05)
        (c, rx, ry), (pc, prx, pry) = e["iris"], e["pupil"]
        low, high = min(y for _, y in e["lid"]) + 0.004, max(y for _, y in e["under"]) - 0.002
        for start in (np.radians(100), np.radians(-80)):                       # les deux flancs de l'iris
            arc = ellipse(c, rx, ry, 0, start, np.radians(160))
            arc = arc[(arc[:, 1] > low) & (arc[:, 1] < high)]
            if len(arc) > 2:
                d.stroke(px(arc), B2, lay, pressure=0.62, taper=(0.1, 0.1))
        d.hatch(px(ellipse(pc, prx, pry)), B2, lay, -1.0, 2.2, pressure=0.9, taper=(0.1, 0.1))    # pupille
        shade = ellipse((c[0], high - ry * 0.16), rx * 0.86, ry * 0.2)        # haut de l'iris, dans l'ombre
        d.hatch(px(shade), HB, lay, -1.0, 3.2, pressure=0.6)
    for c in BROWS:
        line(c, 0.9, taper=(0.15, 0.35), tip=0.1)
        d.stroke(curve([(x, y - 0.009) for x, y in c[:-1]]), B2, lay, pressure=0.5, taper=(0.2, 0.5), tip=0.05)
    line(NOSE[0], 0.7, taper=(0.3, 0.15), tip=0.08)
    line(NOSE[1], 0.5, taper=(0.3, 0.3), tip=0.1)
    line(MOUTH[0], 0.8, taper=(0.25, 0.3), tip=0.08)
    line(MOUTH[1], 0.4, taper=(0.3, 0.3), tip=0.1)

    # Cheveux : contour, mèches en coups de crayon de la racine à la pointe, attache.
    line(HAIR_TOP, 1.25, reach=420)
    line(HAIR_BACK, 1.25)
    for c in TUFTS:
        flick(c, 0.9)
    line(TAIL_OUT, 1.3, reach=480, taper=(0.1, 0.4), tip=0.08)
    line(TAIL_IN, 0.95, taper=(0.15, 0.5), tip=0.06)
    for c in TAIL_TIPS + COWLICK:
        flick(c, 0.95)
    for c in TIE:
        line(c, 0.9)
    for left, right in BANGS:
        flick(left, 1.05)
        flick(right, 1.0)
    flick(SIDE_LOCK[0], 1.05)
    flick(SIDE_LOCK[1], 1.0)
    for c in STRANDS:
        flick(c, 0.5)

    # Sweat.
    line(HOOD, 1.2, reach=380)
    line(HOOD_FOLD, 0.6, taper=(0.2, 0.4), tip=0.08)
    line(COLLAR, 1.0)
    line([(x + 0.012, y + 0.038) for x, y in COLLAR[:-2]], 0.6, taper=(0.2, 0.3))
    line(SHOULDER_FAR, 1.25, taper=(0.1, 0.1))
    line(SHOULDER_NEAR, 1.25, taper=(0.1, 0.1))
    for c in CORDS:
        line(c, 0.6, taper=(0.1, 0.1))
    for c in FOLDS:
        line(c, 0.5, taper=(0.2, 0.5), tip=0.05)


def shadows(d):
    """Passe 4 : les ombres, cernées au crayon bleu et hachurées, comme sur une feuille d'animation."""
    lay = "ombres"
    shift = np.array([0.018, -0.04])
    tips = np.asarray(BANG_TIPS, float)
    forms = [np.vstack([tips, (tips + shift)[::-1]])] + [np.asarray(s, float) for s in SHADOWS]
    for i, form in enumerate(forms):
        edge = px(tips + shift) if i == 0 else px(spline(np.vstack([form, form[:1]]), per=10))
        d.stroke(edge, BLEU, lay, pressure=0.5, reach=300)
        d.hatch(px(form) if i == 0 else px(spline(form, per=8)), BLEU, lay, -0.95, 15, pressure=0.34)


def drawing(seed=93):
    doc = Document(W, H, seed)
    for name in ("construction", "rough", "ombres", "net"):
        doc.layer(name)
    construction(Draftsman(doc, seed, tremor=0.9, aim=2.0))
    rough(Draftsman(doc, seed + 1, tremor=1.1, aim=2.8, turn=0.012, scale=0.012))
    tie_down(Draftsman(doc, seed + 2, tremor=0.4, aim=0.7, turn=0.004, scale=0.004))
    shadows(Draftsman(doc, seed + 3, tremor=0.6, aim=1.2))
    return doc


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    doc = drawing()
    doc.save(OUT / "s03_tete.png")
    frames = timelapse(doc, OUT / "s03_tete.mp4", seconds=22, scale=0.5)
    print(f"{len(doc.journal)} traits, {frames} images -> {OUT}")
