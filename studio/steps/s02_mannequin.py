"""Étape 2 — le mannequin de construction, comparé au dessin libre.

Mêmes dessins dans les deux modes : cinq angles debout, puis trois poses de
profil. Avec le mannequin, tout est projeté depuis un seul modèle 3D. En mode
libre, chaque figure est posée à la main, sans lien avec les autres.

    python3 -m studio.steps.s02_mannequin
"""
from pathlib import Path

import numpy as np

from studio.characters import milo
from studio.engine import libre, poses
from studio.engine.canvas import Document
from studio.engine.construction import draw
from studio.engine.hand import Draftsman
from studio.engine.mannequin import Camera, construct
from studio.engine.video import Video
from studio.steps import s02_libre

OUT = Path(__file__).resolve().parent.parent / "out"
W, H, SCALE = 2400, 1640, 72
VIEWS = ("Face", "Trois quarts", "Profil", "Trois quarts dos", "Dos")
ACTIONS = (("Marche", poses.MARCHE), ("Course", poses.COURSE), ("Élan", poses.ELAN))
TOUR_X = [200 + i * 285 for i in range(5)]
ACTION_X = [1640, 1940, 2200]
LEVELS = ("top", "chin", "shoulder", "crotch", "knee", "sole")
LIMBS = (("bras", "shoulder", "elbow"), ("avant-bras", "elbow", "wrist"),
         ("cuisse", "hip", "knee"), ("jambe", "knee", "ankle"))


def mannequin_set(model):
    tour = [construct(model, poses.A_POSE, Camera(yaw)) for yaw in (0, 45, 90, 135, 180)]
    actions = [construct(model, pose, Camera(-90)) for _, pose in ACTIONS]
    return tour, actions


def libre_set():
    return ([libre.construct(f) for f in s02_libre.TOUR],
            [libre.construct(f) for f in s02_libre.ACTIONS])


def level(con, name):
    """Hauteur d'un repère (moyenne gauche-droite pour les articulations)."""
    if name in con.marks:
        return float(con.marks[name][1])
    if name == "sole":
        return 0.0
    return float(np.mean([con.marks[f"{name}_{s}"][1] for s in "LR"]))


def measure(tour, actions):
    """Écarts en % : hauteur des repères entre les cinq angles, puis longueur
    des membres entre les trois poses de profil."""
    heights = {n: [level(c, n) for c in tour] for n in LEVELS}
    align = max(max(v) - min(v) for v in heights.values()) * 100
    drift = {}
    for name, a, b in LIMBS:
        lengths = [np.hypot(*(c.marks[f"{a}_{s}"] - c.marks[f"{b}_{s}"]))
                   for c in actions for s in "LR"]
        drift[name] = (max(lengths) - min(lengths)) / np.mean(lengths) * 100
    return align, drift


def sheet(model):
    doc = Document(W, H, seed=11)
    doc.label((70, 44), "ÉTAPE 2 · LE MANNEQUIN DE CONSTRUCTION", size=24, weight="SemiBold",
              color=(0.30, 0.31, 0.36))
    d = Draftsman(doc, seed=11)
    rows = (("A · Avec mannequin : un seul modèle 3D, projeté sous chaque angle et dans chaque pose",
             mannequin_set(model), 690),
            ("B · Sans mannequin : chaque figure est posée à la main, sans lien avec les autres",
             libre_set(), 1420))
    front = rows[0][1][0][0]
    report = []
    for title, (tour, actions), ground in rows:
        doc.label((70, ground - 585), title, size=19, weight="SemiBold")
        for name in LEVELS:
            doc.guide(ground - level(front, name) * SCALE, 60, 1500)
        for x, name, con in zip(TOUR_X, VIEWS, tour):
            doc.label((x - 60, ground + 28), name, size=15)
            draw(d, con, (x, ground), SCALE)
        doc.guide(ground, 1560, W - 60)
        for x, (name, _), con in zip(ACTION_X, ACTIONS, actions):
            doc.label((x - 30, ground + 28), name, size=15)
            draw(d, con, (x, ground), SCALE)
        align, drift = measure(tour, actions)
        worst = max(drift, key=drift.get)
        text = (f"Repères entre les cinq angles : écart maximal {align:.0f} % d'une tête.   "
                f"Longueur des membres à l'image entre les trois poses : jusqu'à "
                f"{drift[worst]:.0f} % d'écart ({worst})")
        text += (", dû au seul raccourci : en 3D les longueurs sont fixes." if title[0] == "A"
                 else ", sans modèle pour dire quelle longueur est la bonne.")
        doc.label((70, ground + 62), text, size=15)
        report.append((title[:1], align, drift))
    return doc, report


def spin(model, path, loops=3, hold=6):
    """Le personnage tourne sur lui-même : huit dessins par tour, dans les deux modes."""
    w, h, scale, ground = 1280, 720, 78, 668
    base = Document(w, h, seed=5)
    base.label((60, 30), "Avec mannequin", size=20, weight="SemiBold")
    base.label((700, 30), "Sans mannequin", size=20, weight="SemiBold")
    base.label((60, 58), "Huit dessins par tour, redessinés à chaque passage", size=14)
    base.guide(ground, 40, w - 40)
    free = [libre.construct(f) for f in s02_libre.TOUR]
    free += [libre.mirror(free[i]) for i in (3, 2, 1)]         # 225°, 270°, 315°
    video = Video(path, w, h, fps=24)
    for turn in range(loops):
        for i in range(8):
            doc = Document(w, h, paper=base.paper)
            d = Draftsman(doc, seed=100 + turn * 8 + i)
            draw(d, construct(model, poses.A_POSE, Camera(i * 45)), (330, ground), scale, pressure=0.8)
            draw(d, free[i], (970, ground), scale, pressure=0.8)
            video.add(doc.composite(), hold)
    return video.close()


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    model = milo.build()
    doc, report = sheet(model)
    doc.save(OUT / "s02_mannequin.png")
    for row, align, drift in report:
        print(row, f"alignement {align:.1f} %",
              " ".join(f"{k} {v:.1f} %" for k, v in drift.items()))
    frames = spin(model, OUT / "s02_tour.mp4")
    print(f"{len(doc.journal)} traits, {frames} images -> {OUT}")
