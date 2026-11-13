"""Étape 1 — le crayon et la main.

Planche d'essai : avant de dessiner un personnage, on vérifie que l'outil
(le crayon sur le papier) et le geste (la main) sont crédibles.

    python3 -m studio.steps.s01_crayon
"""
from pathlib import Path

import numpy as np

from studio.engine.brush import BLEU, ROUGE, HB, B2, ESTOMPE, VECTEUR
from studio.engine.canvas import Document
from studio.engine.hand import Draftsman, ellipse, line, spline, TAU
from studio.engine.timelapse import timelapse

OUT = Path(__file__).resolve().parent.parent / "out"
W, H = 1920, 1240


def rect(x, y, w, h):
    return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]


def pressure_tests(doc, d):
    doc.label((70, 108), "A · Pression : de l'effleurement à l'appui", weight="SemiBold")
    for i, brush in enumerate((BLEU, ROUGE, HB, B2)):
        y = 172 + i * 44
        doc.label((70, y - 11), brush.name.upper(), size=14)
        d.stroke(line((160, y), (560, y)), brush, "essais", taper=(0, 0), tip=1,
                 pressure=lambda t: 0.04 + 0.96 * t)
        for k, p in enumerate((0.25, 0.55, 0.9)):
            x = 610 + k * 105
            d.stroke(spline([(x, y + 7), (x + 40, y - 7), (x + 80, y + 4)]), brush, "essais",
                     pressure=p)
    y = 172 + 4 * 44 + 12
    doc.label((70, y - 11), "TRANCHE", size=14)
    d.stroke(line((160, y), (560, y)), ESTOMPE, "essais", taper=(0, 0), tip=1,
             pressure=lambda t: 0.08 + 0.92 * t)
    for k, p in enumerate((0.25, 0.55, 0.9)):
        x = 610 + k * 105
        d.stroke(line((x, y), (x + 80, y)), ESTOMPE, "essais", pressure=p, taper=(0.2, 0.2))


def value_tests(doc, d):
    doc.label((70, 418), "B · Valeurs : hachures et tranche de la mine", weight="SemiBold")
    for i, gap in enumerate((13, 9, 6, 4.2)):
        d.hatch(rect(70 + i * 150, 458, 120, 120), HB, "essais", -0.9, gap, pressure=0.55)
    box = rect(70 + 4 * 150, 458, 120, 120)
    d.hatch(box, HB, "essais", -0.9, 5, pressure=0.6)
    d.hatch(box, HB, "essais", 0.6, 5.5, pressure=0.55)
    for i in range(5):
        box = rect(70 + i * 150, 606, 120, 84)
        for _ in range(1 + i // 2):
            d.hatch(box, ESTOMPE, "essais", -0.5, 8, pressure=0.22 + 0.17 * i, taper=(0.1, 0.1))


def hand_tests(doc, d):
    doc.label((70, 738), "C · La main : droites, ellipses, volumes", weight="SemiBold")
    for i in range(5):
        y = 792 + i * 26
        d.stroke(line((75, y + 6), (345, y - 8)), HB, "essais", pressure=0.6)
    for i, ry in enumerate((48, 34, 19, 8)):
        c = (455 + i * 118, 845)
        start = d.hand.rng.uniform(0, TAU)
        d.stroke(ellipse(c, 48, ry, -0.12, start, TAU * 1.12), BLEU, "essais", passes=2,
                 pressure=0.5, taper=(0.1, 0.3))

    # Cube : construction bleue qui dépasse aux angles, puis arêtes au graphite.
    a, b, c = (95, 1100), (200, 1146), (292, 1086)
    a2, b2, c2, back = (95, 992), (200, 1034), (292, 980), (190, 946)
    edges = [(a, b), (b, c), (a, a2), (b, b2), (c, c2), (a2, b2), (b2, c2), (a2, back), (back, c2)]
    for p, q in edges:
        d.stroke(line(p, q), BLEU, "construction", pressure=0.42, overshoot=16)
    for p, q in edges:
        d.stroke(line(p, q), HB, "net", pressure=0.7, care=1.6)
    d.hatch([b, c, c2, b2], HB, "net", -1.2, 6, pressure=0.45)

    # Cylindre.
    top, bot = (420, 985), (420, 1122)
    d.stroke(line((420, 950), (420, 1160)), BLEU, "construction", pressure=0.35)
    for centre, ry in ((top, 19), (bot, 22)):
        d.stroke(ellipse(centre, 56, ry, 0, 2.0, TAU * 1.1), BLEU, "construction", passes=2,
                 pressure=0.42)
    d.stroke(ellipse(top, 56, 19, 0, 3.3, TAU * 1.03), HB, "net", pressure=0.7, care=1.6)
    d.stroke(ellipse(bot, 56, 22, 0, np.pi, -np.pi), HB, "net", pressure=0.7, care=1.6)
    for x in (364, 476):
        d.stroke(line((x, 985), (x, 1122)), HB, "net", pressure=0.7, care=1.6)
    d.hatch([(446, 1003), (476, 990), (476, 1122), (446, 1141)], HB, "net", -1.2, 6, pressure=0.45)

    # Sphère : contours de volume, puis ombre propre en croissant.
    c, r = np.array((650.0, 1065.0)), 78
    d.stroke(ellipse(c, r, r, 0, 1.0, TAU * 1.15), BLEU, "construction", passes=2, pressure=0.42)
    d.stroke(ellipse(c, r, 22, -0.25, 0, np.pi), BLEU, "construction", pressure=0.4)
    d.stroke(ellipse(c, 26, r, -0.25, -np.pi / 2, -np.pi), BLEU, "construction", pressure=0.4)
    d.stroke(ellipse(c, r, r, 0, 4.0, TAU * 1.04), HB, "net", pressure=0.7, care=1.6)
    th = np.linspace(-0.75, 2.3, 40)
    rim = c + r * np.stack([np.cos(th), np.sin(th)], axis=1)
    depth = 1 - 0.55 * np.sin(np.pi * (th - th[0]) / (th[-1] - th[0]))
    inner = c + (r * depth)[:, None] * np.stack([np.cos(th), np.sin(th)], axis=1)
    d.hatch(np.vstack([rim, inner[::-1]]), HB, "net", -0.75, 5.5, pressure=0.5)


def head(d, cx, cy, r, clean):
    """Tête de trois quarts : volumes d'abord (bleu), traits définitifs ensuite."""
    def px(pts):
        return np.asarray(pts, float) * r + (cx, cy)

    def c(x, y):
        return (cx + x * r, cy + y * r)

    k = dict(pressure=0.40 if clean else 0.5)
    lay = "construction"
    d.stroke(ellipse(c(0, 0), r, r, 0, 2.2, TAU * 1.15), BLEU, lay, passes=2, **k)
    d.stroke(ellipse(c(0.52, 0.02), 0.40 * r, 0.66 * r, -0.08, 0.5, TAU * 1.1), BLEU, lay, **k)
    d.stroke(ellipse(c(0, 0), r, 0.16 * r, 0, np.pi, -(np.pi - 1.0)), BLEU, lay, **k)
    d.stroke(line(c(0.13, 0.12), c(0.91, -0.02)), BLEU, lay, **k)
    d.stroke(line(c(0.50, -0.64), c(0.54, 0.68)), BLEU, lay, **k)
    centre = [(-0.10, -0.99), (-0.40, -0.78), (-0.58, -0.38), (-0.62, 0.0), (-0.63, 0.5),
              (-0.60, 1.0), (-0.55, 1.42)]
    d.stroke(spline(px(centre)), BLEU, lay, reach=1.3 * r, **k)
    d.stroke(ellipse(c(0, -0.52), 0.86 * r, 0.14 * r, 0, np.pi, -1.9), BLEU, lay, **k)
    d.stroke(spline(px([(-0.87, 0.66), (-0.62, 0.74), (-0.1, 0.72), (0.3, 0.62)])), BLEU, lay, **k)
    d.stroke(spline(px([(-0.99, 0.12), (-0.93, 0.6), (-0.82, 1.05), (-0.66, 1.38),
                        (-0.52, 1.47)])), BLEU, lay, passes=2, reach=1.1 * r, **k)
    d.stroke(spline(px([(0.42, 0.62), (0.36, 0.95), (0.26, 1.08), (-0.15, 1.34),
                        (-0.52, 1.47)])), BLEU, lay, passes=2, reach=1.1 * r, **k)
    d.stroke(ellipse(c(0.61, 0.36), 0.13 * r, 0.27 * r, -0.15, 1.0, TAU * 1.1), BLEU, lay, **k)
    d.stroke(spline(px([(0.88, 0.46), (0.72, 0.80), (0.66, 1.25), (0.72, 1.80)])), BLEU, lay, **k)
    d.stroke(spline(px([(-0.02, 1.30), (0.02, 1.55), (-0.04, 1.85)])), BLEU, lay, **k)
    if not clean:
        return

    lay = "net"
    def ink(pts, brush=HB, pressure=0.72, **kw):
        d.stroke(spline(px(pts)), brush, lay, pressure=pressure, care=1.8, **kw)

    # Crâne, visage, mâchoire.
    d.stroke(ellipse(c(0, 0), r, r, 0, 3.55, 3.20), HB, lay, pressure=0.6, care=1.8,
             taper=(0.2, 0.2))
    ink([(-0.93, -0.36), (-0.985, -0.12), (-0.975, 0.10), (-0.925, 0.28), (-0.915, 0.52),
         (-0.86, 0.86), (-0.74, 1.24), (-0.60, 1.43), (-0.47, 1.48)], B2)
    ink([(-0.47, 1.48), (-0.30, 1.42), (-0.02, 1.28), (0.22, 1.09), (0.36, 0.86), (0.42, 0.62)], B2)
    # Oreille, nuque, cou.
    ink([(0.52, 0.16), (0.66, 0.08), (0.75, 0.24), (0.70, 0.50), (0.58, 0.64), (0.50, 0.56)])
    ink([(0.58, 0.24), (0.66, 0.26), (0.65, 0.44)], pressure=0.5)
    ink([(0.90, 0.42), (0.74, 0.74), (0.66, 1.20), (0.72, 1.80)])
    ink([(-0.02, 1.30), (0.02, 1.56), (-0.05, 1.84)])
    # Sourcils.
    ink([(-0.48, 0.10), (-0.26, -0.03), (0.06, 0.06)], B2, 0.8)
    ink([(-0.955, 0.07), (-0.85, -0.02), (-0.72, 0.09)], B2, 0.8)
    # Paupières, iris, pupilles.
    ink([(-0.49, 0.42), (-0.38, 0.26), (-0.14, 0.23), (0.04, 0.38)], B2, 0.95)
    ink([(-0.945, 0.38), (-0.85, 0.25), (-0.71, 0.31)], B2, 0.95)
    for (ex, ey), (ax, ay) in (((-0.22, 0.43), (0.115, 0.185)), ((-0.835, 0.43), (0.062, 0.17))):
        d.stroke(ellipse(c(ex, ey), ax * r, ay * r, 0, -0.75, np.pi + 1.5), B2, lay,
                 pressure=0.6, care=2.5)
        d.hatch(ellipse(c(ex, ey), ax * r * 0.42, ay * r * 0.42), B2, lay, -1.0, 1.7,
                pressure=0.9, care=3, taper=(0.1, 0.1))
        d.hatch(ellipse(c(ex, ey - ay * 0.55), ax * r * 0.8, ay * r * 0.32), HB, lay, -1.0, 2.6,
                pressure=0.5, care=3)
    ink([(-0.40, 0.64), (-0.24, 0.67), (-0.08, 0.61)], pressure=0.45)
    # Nez, bouche, menton.
    ink([(-0.67, 0.74), (-0.75, 0.85), (-0.67, 0.89)], pressure=0.65)
    ink([(-0.77, 1.11), (-0.61, 1.15), (-0.42, 1.11)], pressure=0.7)
    ink([(-0.63, 1.26), (-0.55, 1.28)], pressure=0.4)


def construction_demo(doc, d):
    doc.label((980, 108), "D · Construire, puis mettre au net", weight="SemiBold")
    doc.label((1045, 150), "1. Volumes au crayon bleu", size=14)
    doc.label((1480, 150), "2. Trait définitif au graphite, par-dessus", size=14)
    head(d, 1195, 370, 150, clean=False)
    head(d, 1630, 370, 150, clean=True)


def line_quality(doc, d):
    doc.label((980, 738), "E · Le même tracé, trois façons", weight="SemiBold")
    names = ("Tracé d'ordinateur", "Un seul geste", "Recherche puis mise au net")
    for i, name in enumerate(names):
        x = 1010 + i * 290
        doc.label((x, 778), name, size=14)
        curve = spline([(x + 20, 1150), (x + 60, 1000), (x + 150, 960), (x + 110, 880),
                        (x + 190, 820)])
        if i == 0:
            d.stroke(curve, VECTEUR, "essais", pressure=1, taper=(0, 0), tip=1, care=1e6)
        elif i == 1:
            d.stroke(curve, B2, "essais", pressure=0.8, taper=(0.25, 0.4), tip=0.1)
        else:
            d.stroke(curve, BLEU, "construction", passes=4, reach=150, pressure=0.5,
                     overshoot=10, care=0.4)
            d.stroke(curve, B2, "net", pressure=0.85, taper=(0.25, 0.4), tip=0.1, care=1.8)


def build(seed=7):
    doc = Document(W, H, seed)
    for name in ("construction", "essais", "net"):
        doc.layer(name)
    d = Draftsman(doc, seed)
    doc.label((70, 48), "ÉTAPE 1 · LE CRAYON ET LA MAIN", size=22, weight="SemiBold",
              color=(0.30, 0.31, 0.36))
    pressure_tests(doc, d)
    value_tests(doc, d)
    hand_tests(doc, d)
    construction_demo(doc, d)
    line_quality(doc, d)
    return doc


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    doc = build()
    doc.save(OUT / "s01_crayon.png")
    frames = timelapse(doc, OUT / "s01_crayon.mp4", seconds=14, scale=0.667)
    print(f"{len(doc.journal)} traits, {frames} images -> {OUT}")
