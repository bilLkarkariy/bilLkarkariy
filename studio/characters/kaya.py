"""Kaya : jeune femme athlétique, 7 têtes de haut.

Queue de cheval haute, frange anguleuse, sweat à capuche, short, baskets.
Le personnage habillé est fait des mêmes ingrédients que le mannequin : des
volumes attachés au squelette (leur contour donne la silhouette sous tout angle)
et des lignes tracées sur ces volumes (yeux, bouche, ourlets).
"""
import numpy as np

from studio.characters.body import O, ears, mannequin, skeleton
from studio.engine.mannequin import Ball, Curve, Model, Part, Tube

PROPORTIONS = dict(
    root=3.95, waist=0.45, neck=1.32, head=0.31,
    skull=dict(center=(0, 0.52, 0.0), radii=(0.40, 0.45, 0.46)),
    jaw=dict(center=(0, 0.22, 0.17), radii=(0.27, 0.27, 0.28)),
    cage=dict(center=(0, 0.70, 0.02), radii=(0.52, 0.64, 0.36)),
    pelvis=dict(center=(0, -0.03, 0.0), radii=(0.52, 0.38, 0.33)),
    shoulder=(0.62, 1.22), hip=(0.30, -0.20),
    upper_arm=1.05, forearm=0.93, hand=0.55, thigh=1.78, shin=1.72,
    arm_r=(0.14, 0.11, 0.08), leg_r=(0.26, 0.18, 0.17, 0.10), neck_r=(0.14, 0.13),
    hand_ball=dict(center=(0, -0.27, 0), radii=(0.07, 0.28, 0.14)),
    foot=(((0, -0.12, -0.05), 0.13), ((0, -0.16, 0.60), 0.09)),
)

# Mèches : (racine, rayon à la racine, pointe), dans le repère de la tête.
TUFTS = [
    ((-0.10, 0.90, 0.28), 0.13, (-0.30, 0.47, 0.47)),      # frange
    ((0.00, 0.92, 0.30), 0.14, (-0.10, 0.43, 0.50)),
    ((0.10, 0.92, 0.30), 0.14, (0.08, 0.40, 0.50)),
    ((0.20, 0.88, 0.26), 0.13, (0.26, 0.46, 0.46)),
    ((0.30, 0.78, 0.10), 0.12, (0.45, 0.30, 0.20)),        # tempes
    ((-0.30, 0.78, 0.10), 0.12, (-0.45, 0.28, 0.20)),
    ((0.34, 0.60, 0.12), 0.09, (0.41, -0.02, 0.20)),       # mèches devant les oreilles
    ((-0.34, 0.60, 0.12), 0.09, (-0.41, -0.02, 0.20)),
    ((0.28, 0.40, -0.30), 0.14, (0.30, -0.04, -0.34)),     # nuque
    ((-0.28, 0.40, -0.30), 0.14, (-0.30, -0.04, -0.34)),
    ((0.0, 0.36, -0.40), 0.15, (0.0, -0.06, -0.40)),
    ((0.05, 0.97, -0.10), 0.05, (0.14, 1.10, -0.18)),      # épi
]
# Queue de cheval : tronçons (début, rayon, fin, rayon).
TAIL = [
    ((0, 0.80, -0.40), 0.13, (0, 0.62, -0.74), 0.17),
    ((0, 0.62, -0.74), 0.17, (0, 0.12, -0.84), 0.12),
    ((0, 0.12, -0.84), 0.12, (0.03, -0.38, -0.72), 0.015),
    ((0, 0.50, -0.78), 0.10, (-0.08, -0.15, -0.90), 0.012),
]


def build():
    return mannequin("kaya", PROPORTIONS)


def _cone(joint, top, end, flat=False):
    """Volume conique le long d'un os ; `flat` le termine par une coupe nette (un ourlet)."""
    (y0, r0), (y1, r1) = top, end
    last = y1 + r1 if flat else y1
    n = max(2, int(abs(last - y0) / 0.09) + 1)
    balls = []
    for y in np.linspace(y0, last, n):
        r = r0 + (r1 - r0) * (y - y0) / (y1 - y0)
        balls.append(Ball(joint, (0, y, 0), (r, r, r)))
    if flat:
        balls.append(Ball(joint, (0, y1, 0), (r1, 0.02, r1)))
    return balls


def _ring(joint, y, rx, rz, drop=0.0, n=33, **kw):
    """Ourlet ou col : un anneau autour d'un os, plus bas devant de `drop`."""
    a = np.radians(np.linspace(0, 360, n))
    pts = np.stack([rx * np.cos(a), y - drop * np.sin(a), rz * np.sin(a)], axis=1)
    nrm = np.stack([np.cos(a), np.zeros(n), np.sin(a)], axis=1)
    return Curve(joint, pts, nrm, **kw)


def _front(joint, xy, z, weight=0.7):
    """Détail cousu sur le devant d'un vêtement, à la profondeur z."""
    pts = np.array([(x, y, z) for x, y in xy], float)
    dense = np.vstack([np.linspace(a, b, 6, endpoint=False) for a, b in zip(pts, pts[1:])]
                      + [pts[-1:]])
    return Curve(joint, dense, np.tile((0, 0, 1.0), (len(dense), 1)), weight=weight)


def _on_face(balls, xy, side=1, **kw):
    """Pose un tracé 2D (vu de face) sur la surface du visage."""
    pts, nrm = [], []
    for x, y in xy:
        x *= side
        best = None
        for b in balls:
            (cx, cy, cz), (rx, ry, rz) = b.center, b.radii
            t = 1 - ((x - cx) / rx) ** 2 - ((y - cy) / ry) ** 2
            if t > 0:
                z = cz + rz * np.sqrt(t)
                if best is None or z > best[0]:
                    n = np.array([(x - cx) / rx ** 2, (y - cy) / ry ** 2, (z - cz) / rz ** 2])
                    best = (z, n / np.linalg.norm(n))
        pts.append(np.array([x, y, best[0]]) + best[1] * 0.004)
        nrm.append(best[1])
    return Curve("head", np.array(pts), np.array(nrm), **kw)


def _face(balls):
    curves = []
    a = np.radians(np.linspace(155, 385, 16))
    iris = np.stack([0.195 + 0.052 * np.cos(a), 0.352 + 0.058 * np.sin(a)], axis=1)
    for s in (1, -1):
        curves += [
            _on_face(balls, [(0.08, 0.355), (0.115, 0.395), (0.19, 0.41), (0.265, 0.40),
                             (0.315, 0.375), (0.335, 0.385)], s, weight=1.25, passes=2),
            _on_face(balls, [(0.10, 0.375), (0.19, 0.396), (0.30, 0.376)], s, weight=1.1),
            _on_face(balls, [(0.14, 0.305), (0.21, 0.298), (0.275, 0.312)], s, weight=0.6),
            _on_face(balls, iris, s, weight=0.85),
            _on_face(balls, [(0.15, 0.386), (0.24, 0.386)], s, weight=0.8),
            _on_face(balls, [(0.065, 0.455), (0.17, 0.49), (0.30, 0.485), (0.335, 0.47)], s,
                     weight=0.9),
        ]
        for x in (0.185, 0.195, 0.205):
            curves.append(_on_face(balls, [(x, 0.335), (x, 0.372)], s, weight=1.2))
    curves.append(Curve("head", np.array([(0, 0.25, 0.47), (0, 0.19, 0.525), (0, 0.165, 0.47)]),
                        np.array([(0, 0, 1.0)] * 3), weight=0.7))
    curves.append(_on_face(balls, [(-0.07, 0.085), (0, 0.078), (0.07, 0.086)], weight=0.7))
    return curves


def design():
    """Le personnage habillé, sur le même squelette que son mannequin."""
    p = PROPORTIONS
    joints, marks = skeleton(p)
    head = [Ball("head", **p["skull"]), Ball("head", **p["jaw"]),
            Ball("head", (0, 0.02, 0.30), (0.09, 0.08, 0.10)),      # menton
            Ball("head", (0, 0.20, 0.47), (0.03, 0.04, 0.05))]      # nez
    parts = [
        Part("visage", head, _face(head[:3]) + ears(weight=0.8)),
        Part("cou", [Tube(("neck", O), 0.14, ("head", (0, 0.10, 0)), 0.13)]),
        Part("calotte", [Ball("head", (0, 0.58, -0.06), (0.47, 0.48, 0.52))]),
    ]
    for i, (root, r, tip) in enumerate(TUFTS):
        parts.append(Part(f"meche_{i}", [Tube(("head", root), r, ("head", tip), 0.012)]))
    for i, (a, ra, b, rb) in enumerate(TAIL):
        parts.append(Part(f"queue_{i}", [Tube(("head", a), ra, ("head", b), rb)]))

    sx, sy = p["shoulder"]
    parts += [
        Part("capuche", [Ball("waist", (0, 1.30, -0.24), (0.36, 0.24, 0.22))]),
        Part("sweat", [Ball("waist", (0, 0.70, 0.02), (0.58, 0.66, 0.42)),
                       Ball("waist", (sx, sy, 0), (0.2, 0.2, 0.2)),
                       Ball("waist", (-sx, sy, 0), (0.2, 0.2, 0.2)),
                       Ball("waist", (0, 0.10, 0.02), (0.54, 0.40, 0.38)),
                       Ball("pelvis", (0, 0.22, 0), (0.56, 0.30, 0.40)),
                       Ball("pelvis", (0, 0.02, 0), (0.60, 0.13, 0.42))],
             [_ring("pelvis", 0.13, 0.585, 0.41, weight=0.7),
              _ring("waist", 1.36, 0.24, 0.22, drop=0.07, weight=0.8,
                    skip=("sweat", "cou", "capuche")),
              # Poche ventrale et cordons de capuche, posés sur le devant.
              _front("waist", [(-0.32, 0.02), (-0.22, 0.36), (0.22, 0.36), (0.32, 0.02)], 0.41),
              _front("waist", [(-0.07, 1.26), (-0.09, 0.98)], 0.36),
              _front("waist", [(0.07, 1.26), (0.10, 0.94)], 0.36)]),
    ]
    for side in "LR":
        sh, el, wr = f"shoulder_{side}", f"elbow_{side}", f"wrist_{side}"
        hip, kn, an = f"hip_{side}", f"knee_{side}", f"ankle_{side}"
        parts += [
            Part(f"manche_{side}", _cone(sh, (0, 0.20), (-1.05, 0.155))),
            Part(f"manche_bas_{side}", _cone(el, (0, 0.155), (-0.70, 0.14))
                 + [Ball(el, (0, -0.86, 0), (0.105, 0.02, 0.105))],
                 [_ring(el, -0.80, 0.125, 0.125, weight=0.7),
                  _ring(el, -0.86, 0.107, 0.107, weight=0.8,
                        skip=(f"manche_bas_{side}", f"main_{side}", f"pouce_{side}"))]),
            Part(f"main_{side}", [Ball(wr, (0, -0.20, 0), (0.06, 0.20, 0.12)),
                                  Ball(wr, (0, -0.40, 0.01), (0.045, 0.16, 0.095))]),
            Part(f"pouce_{side}", [Tube((wr, (0, -0.08, 0.09)), 0.05, (wr, (0, -0.30, 0.19)), 0.03)]),
            Part(f"short_{side}", _cone(hip, (0, 0.29), (-0.78, 0.30), flat=True),
                 [_ring(hip, -0.78, 0.302, 0.302, weight=0.9,
                        skip=(f"short_{side}", f"cuisse_{side}"))]),
            Part(f"cuisse_{side}", [Tube((hip, O), 0.26, (kn, O), 0.18)]),
            Part(f"jambe_{side}", [Tube((kn, O), 0.17, (an, O), 0.10),
                                   Ball(kn, (0, -0.50, -0.05), (0.175, 0.42, 0.19))],
                 [_ring(kn, -1.42, 0.118, 0.118, weight=0.7),
                  Curve(kn, np.array([(-0.10, 0.06, 0.15), (-0.05, 0.0, 0.18), (0.05, 0.0, 0.18),
                                      (0.10, 0.06, 0.15)]), np.tile((0, 0, 1.0), (4, 1)),
                        weight=0.5)]),
            Part(f"chaussure_{side}", [Ball(an, (0, -0.115, -0.04), (0.135, 0.135, 0.16)),
                                       Ball(an, (0, -0.165, 0.58), (0.115, 0.085, 0.14)),
                                       Ball(an, (0, -0.06, 0.12), (0.125, 0.12, 0.20))],
                 [_ring(an, -0.20, 0.12, 0.30, weight=0.6)]),
        ]
    return Model("kaya", (0, p["root"], 0), joints, parts, [], marks,
                 feet=("chaussure_L", "chaussure_R"))
