"""Milo : jeune adulte, 7 têtes de haut. Toutes les mesures sont en têtes."""
import numpy as np

from studio.engine.mannequin import Ball, Curve, Model, Part, Tube

SKULL = dict(center=(0, 0.52, 0.0), radii=(0.40, 0.45, 0.46))
JAW = dict(center=(0, 0.20, 0.20), radii=(0.30, 0.27, 0.27))
CAGE = dict(center=(0, 0.72, 0.02), radii=(0.60, 0.66, 0.40))
PELVIS = dict(center=(0, -0.03, 0.0), radii=(0.52, 0.38, 0.34))

UPPER_ARM, FOREARM, HAND = 1.08, 0.95, 0.62
THIGH, SHIN = 1.75, 1.70


def _meridian(joint, ball, start, end, sign=1, n=14, **kw):
    """Ligne médiane d'un ellipsoïde : devant (sign = 1) ou derrière (sign = -1)."""
    a = np.radians(np.linspace(start, end, n))
    (_, cy, cz), (_, ry, rz) = ball["center"], ball["radii"]
    zero = np.zeros(n)
    pts = np.stack([zero, cy + ry * np.cos(a), cz + sign * rz * np.sin(a)], axis=1)
    nrm = np.stack([zero, np.cos(a) / ry, sign * np.sin(a) / rz], axis=1)
    return Curve(joint, pts, nrm / np.linalg.norm(nrm, axis=1, keepdims=True), **kw)


def _head_curves():
    front = _meridian("head", SKULL, 6, 92)
    chin = _meridian("head", JAW, 80, 172, n=10)
    face = Curve("head", np.vstack([front.points, chin.points]),
                 np.vstack([front.normals, chin.normals]))
    back = _meridian("head", SKULL, 6, 150, sign=-1)
    a = np.radians(np.linspace(0, 360, 49))
    rx_, _, rz_ = SKULL["radii"]
    zero = np.zeros(len(a))
    brow = np.stack([rx_ * np.cos(a), zero + SKULL["center"][1], rz_ * np.sin(a)], axis=1)
    brow_n = np.stack([np.cos(a) / rx_, zero, np.sin(a) / rz_], axis=1)
    brow_n /= np.linalg.norm(brow_n, axis=1, keepdims=True)
    nose = Curve("head", np.array([(0, 0.40, 0.455), (0, 0.27, 0.56), (0, 0.22, 0.46)]),
                 np.array([(0, 0, 1.0)] * 3))
    curves = [face, back, Curve("head", brow, brow_n), nose]
    t = np.radians(np.linspace(0, 360, 17))
    for side in (1, -1):
        out = np.array([side * 0.45, 0, -0.9]) / np.hypot(0.45, 0.9)
        ear = (np.array([side * 0.40, 0.36, -0.04]) + np.outer(np.cos(t), (0, 0.13, 0))
               + np.outer(np.sin(t), out * 0.07))
        curves.append(Curve("head", ear, skip=()))
    return curves


def _limbs(side, s):
    sh, el, wr = f"shoulder_{side}", f"elbow_{side}", f"wrist_{side}"
    hip, kn, an = f"hip_{side}", f"knee_{side}", f"ankle_{side}"
    o = (0, 0, 0)
    return [
        Part(f"bras_{side}", [Tube((sh, o), 0.17, (el, o), 0.13)]),
        Part(f"avant_bras_{side}", [Tube((el, o), 0.13, (wr, o), 0.095)]),
        Part(f"main_{side}", [Ball(wr, (0, -0.31, 0), (0.08, 0.32, 0.16))]),
        Part(f"cuisse_{side}", [Tube((hip, o), 0.27, (kn, o), 0.19)]),
        Part(f"jambe_{side}", [Tube((kn, o), 0.185, (an, o), 0.11)]),
        Part(f"pied_{side}", [Tube((an, (0, -0.12, -0.05)), 0.13, (an, (0, -0.16, 0.62)), 0.09)]),
    ]


def build():
    joints = {"pelvis": (None, (0, 0, 0)), "waist": ("pelvis", (0, 0.45, 0)),
              "neck": ("waist", (0, 1.35, 0)), "head": ("neck", (0, 0.33, 0.02))}
    marks = {"top": ("head", (0, 0.97, 0)), "chin": ("head", (0, -0.07, 0.2)),
             "crane": ("head", (0, 0.5, 0)), "neck": ("neck", (0, 0, 0)),
             "waist": ("waist", (0, 0, 0)), "pelvis": ("pelvis", (0, 0, 0)),
             "crotch": ("pelvis", (0, -0.41, 0))}
    parts = [
        Part("tete", [Ball("head", **SKULL), Ball("head", **JAW)], _head_curves(), passes=2),
        Part("cou", [Tube(("neck", (0, 0, 0)), 0.17, ("head", (0, 0.08, 0)), 0.16)]),
        Part("cage", [Ball("waist", **CAGE)],
             [_meridian("waist", CAGE, 8, 172), _meridian("waist", CAGE, 8, 172, sign=-1)],
             passes=2),
        Part("bassin", [Ball("pelvis", **PELVIS)],
             [_meridian("pelvis", PELVIS, 15, 165), _meridian("pelvis", PELVIS, 15, 165, sign=-1)],
             passes=2),
    ]
    for side, s in (("L", 1), ("R", -1)):
        joints[f"shoulder_{side}"] = ("waist", (s * 0.72, 1.24, 0))
        joints[f"elbow_{side}"] = (f"shoulder_{side}", (0, -UPPER_ARM, 0))
        joints[f"wrist_{side}"] = (f"elbow_{side}", (0, -FOREARM, 0))
        joints[f"hip_{side}"] = ("pelvis", (s * 0.30, -0.20, 0))
        joints[f"knee_{side}"] = (f"hip_{side}", (0, -THIGH, 0))
        joints[f"ankle_{side}"] = (f"knee_{side}", (0, -SHIN, 0))
        for name in ("shoulder", "elbow", "wrist", "hip", "knee", "ankle"):
            marks[f"{name}_{side}"] = (f"{name}_{side}", (0, 0, 0))
        marks[f"hand_{side}"] = (f"wrist_{side}", (0, -HAND, 0))
        marks[f"toe_{side}"] = (f"ankle_{side}", (0, -0.16, 0.7))
        clav = np.linspace((0, 1.30, 0.10), (s * 0.72, 1.24, 0), 6)
        parts[2].curves.append(Curve("waist", clav, skip=("cage", "cou", f"bras_{side}")))
        parts += _limbs(side, s)
    return Model("milo", (0, 3.90, 0), joints, parts, [("cage", "bassin")], marks)
