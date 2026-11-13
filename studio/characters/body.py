"""Le corps : squelette et mannequin de construction, pilotés par des proportions.

Toutes les mesures sont en têtes. Un personnage fournit son jeu de proportions.
"""
import numpy as np

from studio.engine.mannequin import Ball, Curve, Model, Part, Tube

O = (0, 0, 0)


def meridian(joint, ball, start, end, sign=1, n=14, **kw):
    """Ligne médiane d'un ellipsoïde : devant (sign = 1) ou derrière (sign = -1)."""
    a = np.radians(np.linspace(start, end, n))
    (_, cy, cz), (_, ry, rz) = ball["center"], ball["radii"]
    zero = np.zeros(n)
    pts = np.stack([zero, cy + ry * np.cos(a), cz + sign * rz * np.sin(a)], axis=1)
    nrm = np.stack([zero, np.cos(a) / ry, sign * np.sin(a) / rz], axis=1)
    return Curve(joint, pts, nrm / np.linalg.norm(nrm, axis=1, keepdims=True), **kw)


def ears(x=0.40, y=0.36, **kw):
    t = np.radians(np.linspace(0, 360, 17))
    out = []
    for side in (1, -1):
        lean = np.array([side * 0.45, 0, -0.9]) / np.hypot(0.45, 0.9)
        pts = (np.array([side * x, y, -0.04]) + np.outer(np.cos(t), (0, 0.13, 0))
               + np.outer(np.sin(t), lean * 0.07))
        out.append(Curve("head", pts, skip=(), **kw))
    return out


def skeleton(p):
    """Articulations et repères de mesure."""
    joints = {"pelvis": (None, O), "waist": ("pelvis", (0, p["waist"], 0)),
              "neck": ("waist", (0, p["neck"], 0)), "head": ("neck", (0, p["head"], 0.02))}
    marks = {"top": ("head", (0, 0.97, 0)), "chin": ("head", (0, -0.07, 0.2)),
             "neck": ("neck", O), "waist": ("waist", O), "pelvis": ("pelvis", O),
             "crotch": ("pelvis", (0, -p["pelvis"]["radii"][1] - 0.03, 0))}
    for side, s in (("L", 1), ("R", -1)):
        joints[f"shoulder_{side}"] = ("waist", (s * p["shoulder"][0], p["shoulder"][1], 0))
        joints[f"elbow_{side}"] = (f"shoulder_{side}", (0, -p["upper_arm"], 0))
        joints[f"wrist_{side}"] = (f"elbow_{side}", (0, -p["forearm"], 0))
        joints[f"hip_{side}"] = ("pelvis", (s * p["hip"][0], p["hip"][1], 0))
        joints[f"knee_{side}"] = (f"hip_{side}", (0, -p["thigh"], 0))
        joints[f"ankle_{side}"] = (f"knee_{side}", (0, -p["shin"], 0))
        for name in ("shoulder", "elbow", "wrist", "hip", "knee", "ankle"):
            marks[f"{name}_{side}"] = (f"{name}_{side}", O)
        marks[f"hand_{side}"] = (f"wrist_{side}", (0, -p["hand"], 0))
        marks[f"toe_{side}"] = (f"ankle_{side}", (0, -0.16, 0.7))
    return joints, marks


def foot(p, side):
    an = f"ankle_{side}"
    (heel, rh), (toe, rt) = p["foot"]
    return Part(f"pied_{side}", [Tube((an, heel), rh, (an, toe), rt)])


def mannequin(name, p):
    """Le mannequin de construction : volumes simples et lignes d'axe."""
    joints, marks = skeleton(p)
    skull, cage, pelvis = p["skull"], p["cage"], p["pelvis"]
    front = meridian("head", skull, 6, 92)
    chin = meridian("head", p["jaw"], 80, 172, n=10)
    a = np.radians(np.linspace(0, 360, 49))
    zero = np.zeros(len(a))
    brow = np.stack([skull["radii"][0] * np.cos(a), zero + skull["center"][1],
                     skull["radii"][2] * np.sin(a)], axis=1)
    brow_n = np.stack([np.cos(a) / skull["radii"][0], zero, np.sin(a) / skull["radii"][2]], axis=1)
    brow_n /= np.linalg.norm(brow_n, axis=1, keepdims=True)
    head_curves = [
        Curve("head", np.vstack([front.points, chin.points]),
              np.vstack([front.normals, chin.normals])),
        meridian("head", skull, 6, 150, sign=-1), Curve("head", brow, brow_n),
        Curve("head", np.array([(0, 0.40, 0.455), (0, 0.27, 0.56), (0, 0.22, 0.46)]),
              np.array([(0, 0, 1.0)] * 3)),
    ] + ears()
    parts = [
        Part("tete", [Ball("head", **skull), Ball("head", **p["jaw"])], head_curves, passes=2),
        Part("cou", [Tube(("neck", O), p["neck_r"][0], ("head", (0, 0.08, 0)), p["neck_r"][1])]),
        Part("cage", [Ball("waist", **cage)],
             [meridian("waist", cage, 8, 172), meridian("waist", cage, 8, 172, sign=-1)], passes=2),
        Part("bassin", [Ball("pelvis", **pelvis)],
             [meridian("pelvis", pelvis, 15, 165), meridian("pelvis", pelvis, 15, 165, sign=-1)],
             passes=2),
    ]
    sx, sy = p["shoulder"]
    a1, a2, a3 = p["arm_r"]
    l1, l2, l3, l4 = p["leg_r"]
    for side, s in (("L", 1), ("R", -1)):
        sh, el, wr = f"shoulder_{side}", f"elbow_{side}", f"wrist_{side}"
        hip, kn, an = f"hip_{side}", f"knee_{side}", f"ankle_{side}"
        clav = np.linspace((0, sy + 0.06, 0.10), (s * sx, sy, 0), 6)
        parts[2].curves.append(Curve("waist", clav, skip=("cage", "cou", f"bras_{side}")))
        parts += [
            Part(f"bras_{side}", [Tube((sh, O), a1, (el, O), a2)]),
            Part(f"avant_bras_{side}", [Tube((el, O), a2, (wr, O), a3)]),
            Part(f"main_{side}", [Ball(wr, **p["hand_ball"])]),
            Part(f"cuisse_{side}", [Tube((hip, O), l1, (kn, O), l2)]),
            Part(f"jambe_{side}", [Tube((kn, O), l3, (an, O), l4)]),
            foot(p, side),
        ]
    return Model(name, (0, p["root"], 0), joints, parts, [("cage", "bassin")], marks)
