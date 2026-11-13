"""Kaya : jeune femme athlétique, 7 têtes de haut.

Queue de cheval haute, frange anguleuse, sweat à capuche, short, baskets.
Le personnage habillé est fait des mêmes ingrédients que le mannequin : des
volumes attachés au squelette (leur contour donne la silhouette sous tout angle)
et des lignes tracées sur ces volumes (yeux, bouche, ourlets).
"""
import numpy as np

from studio.characters.body import ears, mannequin, skeleton
from studio.engine.mannequin import Ball, Curve, Model, Part, Sweep

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

# Mèches : (points de la courbe, rayon à la racine), dans le repère de la tête.
TUFTS = [
    ([(-0.16, 0.93, 0.22), (-0.26, 0.72, 0.42), (-0.33, 0.44, 0.47)], 0.12),      # frange
    ([(-0.04, 0.95, 0.26), (-0.14, 0.72, 0.46), (-0.12, 0.40, 0.50)], 0.13),
    ([(0.06, 0.95, 0.26), (0.02, 0.70, 0.47), (0.07, 0.36, 0.50)], 0.13),
    ([(0.16, 0.93, 0.22), (0.18, 0.70, 0.44), (0.25, 0.42, 0.46)], 0.12),
    ([(0.24, 0.88, 0.16), (0.33, 0.66, 0.36), (0.36, 0.46, 0.38)], 0.10),
    ([(0.32, 0.80, 0.08), (0.44, 0.55, 0.16), (0.44, 0.22, 0.20)], 0.11),         # tempes
    ([(-0.32, 0.80, 0.08), (-0.45, 0.53, 0.16), (-0.45, 0.18, 0.20)], 0.11),
    ([(0.36, 0.62, 0.10), (0.42, 0.30, 0.20), (0.40, -0.06, 0.22)], 0.075),       # devant les oreilles
    ([(-0.36, 0.62, 0.10), (-0.43, 0.28, 0.20), (-0.41, -0.10, 0.22)], 0.075),
    ([(0.26, 0.42, -0.30), (0.33, 0.15, -0.36), (0.30, -0.06, -0.34)], 0.13),     # nuque
    ([(-0.26, 0.42, -0.30), (-0.33, 0.13, -0.36), (-0.31, -0.08, -0.34)], 0.13),
    ([(0.0, 0.38, -0.40), (0.0, 0.12, -0.44), (0.0, -0.08, -0.40)], 0.14),
    ([(0.05, 0.99, -0.08), (0.12, 1.07, -0.14), (0.20, 1.10, -0.22)], 0.05),      # épis
    ([(-0.10, 0.98, -0.15), (-0.20, 1.04, -0.25), (-0.30, 1.03, -0.36)], 0.06),
]
# Queue de cheval : (points, rayons).
TAIL = [
    ([(0, 0.84, -0.36), (0, 0.80, -0.62), (0, 0.50, -0.86), (0, 0.05, -0.88), (0.04, -0.40, -0.74)],
     (0.11, 0.15, 0.17, 0.13, 0.01)),
    ([(0, 0.74, -0.60), (-0.06, 0.40, -0.90), (-0.10, -0.05, -0.95), (-0.08, -0.30, -0.86)],
     (0.08, 0.11, 0.08, 0.01)),
    ([(0, 0.70, -0.62), (0.10, 0.30, -0.82), (0.14, -0.10, -0.80)], (0.07, 0.08, 0.01)),
]

# Expressions : décalage des sourcils (intérieur, extérieur), ouverture des yeux, bouche.
EXPRESSIONS = {
    "neutre": dict(),
    "joie": dict(eyes="closed", brow=(0.02, 0.025), mouth="rire"),
    "colère": dict(brow=(-0.05, 0.02), lid=-0.014, mouth="serree"),
    "surprise": dict(brow=(0.055, 0.05), wide=1.3, mouth="o"),
    "tristesse": dict(brow=(0.04, -0.03), lid=-0.012, mouth="triste"),
}
MOUTHS = {
    "neutre": [[(-0.07, 0.085), (0, 0.078), (0.07, 0.086)]],
    "rire": [[(-0.11, 0.115), (0, 0.095), (0.11, 0.115)],
             [(-0.11, 0.115), (-0.07, 0.05), (0, 0.025), (0.07, 0.05), (0.11, 0.115)]],
    "serree": [[(-0.08, 0.068), (0, 0.09), (0.08, 0.068)]],
    "triste": [[(-0.07, 0.072), (0, 0.088), (0.07, 0.072)]],
    "o": [[(0.04 * np.cos(t), 0.07 + 0.05 * np.sin(t)) for t in np.linspace(0, 2 * np.pi, 13)]],
}


def build():
    return mannequin("kaya", PROPORTIONS)


def _ring(joint, y, rx, rz, drop=0.0, arc=(0, 360), **kw):
    """Ourlet, col ou pli : un anneau (ou un arc) autour d'un os, plus bas devant de `drop`.
    Les angles partent du côté gauche du personnage ; 90 est devant."""
    a = np.radians(np.linspace(arc[0], arc[1], max(5, int(abs(arc[1] - arc[0]) / 11))))
    pts = np.stack([rx * np.cos(a), y - drop * np.sin(a), rz * np.sin(a)], axis=1)
    nrm = np.stack([np.cos(a), np.zeros(len(a)), np.sin(a)], axis=1)
    return Curve(joint, pts, nrm, **kw)


def _sweep(joint, points, radii, **kw):
    return Sweep([(joint, pt, r) for pt, r in zip(points, radii)], **kw)


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


def _face(balls, expr):
    e = EXPRESSIONS[expr]
    curves = []
    wide, lid = e.get("wide", 1.0), e.get("lid", 0.0)
    inner, outer = e.get("brow", (0, 0))
    a = np.radians(np.linspace(155, 385, 16))
    iris = np.stack([0.195 + 0.052 * np.cos(a), 0.352 + 0.058 * wide * np.sin(a)], axis=1)
    shine = np.stack([0.176 + 0.014 * np.cos(a * 1.6), 0.372 + 0.014 * np.sin(a * 1.6)], axis=1)

    def open_(pts):          # écarte les paupières autour de l'axe de l'œil
        return [(x, 0.355 + (y - 0.355) * wide + lid) for x, y in pts]

    for s in (1, -1):
        brow = [(0.065, 0.455), (0.17, 0.49), (0.30, 0.485), (0.335, 0.47)]
        brow = [(x, y + inner + (outer - inner) * i / 3 + 0.03 * (wide - 1))
                for i, (x, y) in enumerate(brow)]
        curves.append(_on_face(balls, brow, s, weight=0.9))
        if e.get("eyes") == "closed":
            curves.append(_on_face(balls, [(0.08, 0.35), (0.13, 0.385), (0.20, 0.40), (0.27, 0.385),
                                           (0.32, 0.35)], s, weight=1.25, passes=2))
            continue
        curves += [
            _on_face(balls, open_([(0.08, 0.355), (0.115, 0.395), (0.19, 0.41), (0.265, 0.40),
                                   (0.315, 0.375), (0.335, 0.385)]), s, weight=1.25, passes=2),
            _on_face(balls, open_([(0.10, 0.375), (0.19, 0.396), (0.30, 0.376)]), s, weight=1.1),
            _on_face(balls, open_([(0.11, 0.428), (0.20, 0.442), (0.29, 0.425)]), s, weight=0.45),
            _on_face(balls, [(0.14, 0.305 - 0.01 * (wide - 1)), (0.21, 0.298), (0.275, 0.312)], s,
                     weight=0.6),
            _on_face(balls, iris, s, weight=0.85),
            _on_face(balls, shine, s, weight=0.6),
            _on_face(balls, [(0.15, 0.386 + lid), (0.24, 0.386 + lid)], s, weight=0.8),
        ]
        for x in (0.188, 0.197, 0.206):
            curves.append(_on_face(balls, [(x, 0.330), (x, 0.365)], s, weight=1.2))
    curves.append(Curve("head", np.array([(0, 0.25, 0.47), (0, 0.19, 0.525), (0, 0.165, 0.47)]),
                        np.array([(0, 0, 1.0)] * 3), weight=0.7))
    for line in MOUTHS[e.get("mouth", "neutre")]:
        curves.append(_on_face(balls, line, weight=0.75))
    return curves


def _hand(wr, s):
    """Main : paume, quatre doigts légèrement repliés vers la paume, pouce."""
    parts = [Part(f"paume_{wr}", [_sweep(wr, [(0, -0.02, 0), (0, -0.14, 0.005), (0, -0.27, 0)],
                                         [(0.045, 0.085), (0.05, 0.115), (0.045, 0.108)])])]
    for i, (z, length) in enumerate(((0.078, 0.215), (0.028, 0.25), (-0.022, 0.235),
                                     (-0.068, 0.19))):
        pts = [(0, -0.25, z), (-s * 0.012, -0.25 - length * 0.55, z),
               (-s * 0.04, -0.25 - length, z * 0.9)]
        parts.append(Part(f"doigt{i}_{wr}", [_sweep(wr, pts, (0.028, 0.026, 0.02))], weight=0.8))
    parts.append(Part(f"pouce_{wr}", [_sweep(wr, [(0, -0.05, 0.085), (-s * 0.012, -0.17, 0.155),
                                                  (-s * 0.025, -0.27, 0.165)],
                                             (0.036, 0.031, 0.022))], weight=0.8))
    return parts


def design(expr="neutre"):
    """Le personnage habillé, sur le même squelette que son mannequin."""
    p = PROPORTIONS
    joints, marks = skeleton(p)
    head = [Ball("head", **p["skull"]), Ball("head", (0, 0.22, 0.17), (0.25, 0.27, 0.28)),
            Ball("head", (0, 0.02, 0.30), (0.09, 0.08, 0.10)),      # menton
            Ball("head", (0, 0.20, 0.47), (0.03, 0.04, 0.05))]      # nez
    parts = [
        Part("visage", head, _face(head[:3], expr) + ears(weight=0.8)),
        Part("cou", [Sweep([("neck", (0, -0.05, 0), 0.15), ("neck", (0, 0.12, 0), 0.125),
                            ("head", (0, 0.12, 0), 0.12)])]),
        Part("calotte", [Ball("head", (0, 0.58, -0.06), (0.47, 0.48, 0.52))]),
    ]
    for i, (pts, r) in enumerate(TUFTS):
        parts.append(Part(f"meche_{i}", [_sweep("head", pts, (r, r * 0.72, 0.008))]))
    for i, (pts, radii) in enumerate(TAIL):
        parts.append(Part(f"queue_{i}", [_sweep("head", pts, radii)]))

    def on_torso(xy, weight=0.5):
        """Pli ou couture sur le devant du sweat."""
        pts = [(x, y, 0.39 * np.sqrt(max(0.02, 1 - (x / 0.58) ** 2))) for x, y in xy]
        dense = np.vstack([np.linspace(a, b, 5, endpoint=False) for a, b in zip(pts, pts[1:])]
                          + [pts[-1:]])
        nrm = dense * (1 / 0.58 ** 2, 0, 1 / 0.39 ** 2)
        return Curve("waist", dense, nrm / np.linalg.norm(nrm, axis=1, keepdims=True),
                     weight=weight)

    parts += [
        Part("capuche", [Ball("waist", (0, 1.30, -0.24), (0.36, 0.24, 0.22))]),
        Part("sweat", [Sweep([("pelvis", (0, -0.02, 0), (0.56, 0.40)),
                              ("pelvis", (0, 0.10, 0), (0.585, 0.41)),
                              ("waist", (0, 0.05, 0.0), (0.50, 0.36)),
                              ("waist", (0, 0.55, 0.02), (0.56, 0.40)),
                              ("waist", (0, 1.00, 0.02), (0.61, 0.38)),
                              ("waist", (0, 1.25, 0.0), (0.67, 0.30)),
                              ("waist", (0, 1.37, 0.0), (0.27, 0.23))], start="open", end="open")],
             [_ring("pelvis", -0.02, 0.56, 0.40, weight=0.9),
              _ring("pelvis", 0.12, 0.585, 0.41, weight=0.6),
              _ring("waist", 1.36, 0.25, 0.22, drop=0.07, weight=0.8,
                    skip=("sweat", "cou", "capuche")),
              on_torso([(-0.32, 0.02), (-0.22, 0.36), (0.22, 0.36), (0.32, 0.02)], 0.7),
              on_torso([(-0.07, 1.26), (-0.09, 0.98)], 0.7),
              on_torso([(0.07, 1.26), (0.10, 0.94)], 0.7),
              on_torso([(-0.50, 0.98), (-0.42, 0.80), (-0.30, 0.66)]),       # plis sous les bras
              on_torso([(0.50, 0.98), (0.43, 0.82), (0.33, 0.70)]),
              on_torso([(-0.46, 0.30), (-0.34, 0.20), (-0.18, 0.16)]),       # plis de taille
              on_torso([(0.47, 0.34), (0.36, 0.22), (0.22, 0.18)])]),
    ]
    for side, s in (("L", 1), ("R", -1)):
        sh, el, wr = f"shoulder_{side}", f"elbow_{side}", f"wrist_{side}"
        hip, kn, an = f"hip_{side}", f"knee_{side}", f"ankle_{side}"
        parts += [
            Part(f"manche_{side}", [Sweep([(sh, (-s * 0.05, -0.07, 0), 0.14),
                                           (sh, (0, -0.24, 0), 0.185), (sh, (0, -0.45, 0), 0.19),
                                           (sh, (0, -0.80, 0), 0.165), (el, (0, 0, 0), 0.16),
                                           (el, (0, -0.45, 0), 0.155), (el, (0, -0.72, 0), 0.145),
                                           (el, (0, -0.80, 0), 0.11), (el, (0, -0.88, 0), 0.105)],
                                          end="open")],
                 [_ring(el, -0.88, 0.107, 0.107, weight=0.9,
                        skip=(f"manche_{side}", f"paume_{wr}", f"pouce_{wr}")),
                  _ring(el, -0.79, 0.118, 0.118, weight=0.6),
                  _ring(el, 0.07, 0.165, 0.165, drop=0.05, arc=(30, 150), weight=0.5),
                  _ring(el, -0.08, 0.162, 0.162, drop=-0.04, arc=(40, 140), weight=0.5),
                  _ring(sh, -0.38, 0.19, 0.19, drop=0.08, arc=(200, 320) if s > 0 else (220, 340),
                        weight=0.45)]),
            *_hand(wr, s),
            Part(f"short_{side}", [Sweep([(hip, (0, 0.06, 0), 0.30), (hip, (0, -0.40, 0), 0.30),
                                          (hip, (0, -0.80, 0), 0.315)], end="open")],
                 [_ring(hip, -0.80, 0.317, 0.317, weight=0.9,
                        skip=(f"short_{side}", f"jambe_{side}")),
                  _ring(hip, -0.22, 0.30, 0.30, drop=0.10, arc=(35, 145), weight=0.5),
                  _ring(hip, -0.42, 0.302, 0.302, drop=0.06, arc=(50, 130), weight=0.45)]),
            Part(f"jambe_{side}", [Sweep([(hip, (0, -0.60, 0), (0.25, 0.26)),
                                          (hip, (0, -1.30, 0), (0.20, 0.21)),
                                          (kn, (0, 0.0, 0.01), (0.175, 0.185)),
                                          (kn, (0, -0.25, -0.02), (0.165, 0.19)),
                                          (kn, (0, -0.55, -0.04), (0.172, 0.20)),
                                          (kn, (0, -1.00, -0.02), (0.12, 0.135)),
                                          (kn, (0, -1.45, 0), (0.095, 0.105)),
                                          (an, (0, 0, 0), (0.09, 0.10))])],
                 [_ring(kn, -1.38, 0.103, 0.113, weight=0.7),
                  Curve(kn, np.array([(-0.10, 0.07, 0.15), (-0.05, 0.01, 0.185), (0.05, 0.01, 0.185),
                                      (0.10, 0.07, 0.15)]), np.tile((0, 0, 1.0), (4, 1)),
                        weight=0.5)]),
            Part(f"chaussure_{side}", [Ball(an, (0, -0.115, -0.04), (0.135, 0.135, 0.16)),
                                       Ball(an, (0, -0.165, 0.58), (0.115, 0.085, 0.14)),
                                       Ball(an, (0, -0.06, 0.12), (0.125, 0.12, 0.20))],
                 [_ring(an, -0.20, 0.12, 0.30, weight=0.6),
                  _ring(an, 0.02, 0.118, 0.13, weight=0.6, skip=(f"chaussure_{side}",
                                                                 f"jambe_{side}"))]),
        ]
    return Model("kaya", (0, p["root"], 0), joints, parts, [], marks,
                 feet=("chaussure_L", "chaussure_R"))
