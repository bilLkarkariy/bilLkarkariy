"""Étape 5 — le layout du plan 6 (le saut).

Le layout fixe ce que l'animation ne devra plus décider : le décor en
perspective, le cadre et son mouvement, les positions clés du personnage et sa
trajectoire. Décor au graphite, personnage au crayon de couleur, cadres en rouge.

    python3 -m studio.steps.s05_layout
"""
from pathlib import Path

import numpy as np

from studio.characters import kaya
from studio.engine import poses, scene
from studio.engine.brush import BLEU, HB, ROUGE, VERT
from studio.engine.canvas import Document
from studio.engine.construction import draw
from studio.engine.hand import Draftsman
from studio.engine.mannequin import Camera, construct, occluders
from studio.engine.scene import Box
from studio.engine.timelapse import timelapse

OUT = Path(__file__).resolve().parent.parent / "out"
W, H = 4800, 3200
ORIGIN, SCALE = (2300, 1750), 185           # où tombe la cible de la caméra ; pixels par tête
FRAME = (2800, 1575)                        # le cadre 16:9
FRAME_A, FRAME_B = (760, 1380), (1500, 420)    # coin haut-gauche au début et à la fin du plan

# Caméra basse, de trois quarts : Kaya traverse le cadre de gauche à droite.
CAM = Camera(yaw=-65, pitch=-14, target=(0, 4.5, 4), dist=16)

# Décor, en têtes (une tête vaut environ 23 cm). Kaya court le long de z et saute le muret.
DECOR = [
    Box((-1.6, 0, 3.8), (14, 3.0, 5.0), weight=1.6),                              # muret
    Box((-1.8, 3.0, 3.6), (14, 3.3, 5.2), weight=1.6),                            # couvertine
    Box((30, 0, -12), (48, 15, 6), windows={"-x": (7, 5), "+z": (6, 5)}),         # immeubles, loin
    Box((34, 0, 10), (56, 21, 30), windows={"-x": (8, 7)}),
    Box((28, 0, -46), (44, 19, -22), windows={"-x": (9, 6), "+z": (6, 6)}),
    Box((40, 0, -80), (64, 26, -54), windows={"-x": (9, 8), "+z": (8, 8)}),
    Box((17.6, 0, -4.2), (18.0, 14, -3.8)),                                       # lampadaire
    Box((16.0, 13.6, -4.3), (18.0, 14, -3.7)),
]
SOL = [[(-1.6, 0, -60), (-1.6, 0, 14)], [(14, 0, -60), (14, 0, 30)],            # bords du trottoir
       [(22, 0, -80), (22, 0, 30)]]

# Positions clés : (nom, pose, crayon).
KEYS = [("1 · élan", poses.ELAN.at(z=1.2), BLEU),
        ("2 · sommet", poses.SAUT.at(y=3.1, z=4.4), ROUGE),
        ("3 · réception", poses.RECEPTION.at(z=7.8), VERT)]
ARC = [(0, 2.0, 1.2), (0, 7.0, 4.4), (0, 2.3, 7.8)]       # trajectoire du bassin


def to_px(points):
    return np.asarray(ORIGIN, float) + CAM.project(np.asarray(points, float)) * (SCALE, -SCALE)


def parabola(a, b, c, n=40):
    """Courbe passant par trois points : départ, sommet, arrivée."""
    a, b, c = (np.asarray(p, float) for p in (a, b, c))
    t = np.linspace(0, 1, n)[:, None]
    return a * (1 - t) * (1 - 2 * t) + b * 4 * t * (1 - t) + c * t * (2 * t - 1)


def rect(d, corner, size, brush, label, doc):
    x, y = corner
    w, h = size
    pts = [(x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)]
    for a, b in zip(pts, pts[1:]):
        d.stroke(np.array([a, b], float), brush, "cadre", passes=3, pressure=0.9, overshoot=18)
    doc.label((x + 24, y + 16), label, size=44, weight="SemiBold", color=(0.72, 0.28, 0.24))


def sheet(seed=51):
    doc = Document(W, H, seed)
    for name in ("decor", "construction", "net", "cadre"):
        doc.layer(name)
    doc.label((120, 60), "ÉTAPE 5 · LAYOUT — PLAN 6 « ELLE SAUTE »", size=48, weight="SemiBold",
              color=(0.30, 0.31, 0.36))
    doc.label((120, 132), "30 images · caméra basse · PAN du cadre A vers le cadre B, "
              "en suivant le saut", size=30)
    d = Draftsman(doc, seed)
    clip = (60, 200, W - 60, H - 60)

    # Ligne d'horizon : la hauteur de l'œil de la caméra, à l'infini.
    eye = CAM.target + CAM.back * CAM.dist
    ahead = -CAM.back * (1, 0, 1)
    horizon = to_px(eye + ahead / np.linalg.norm(ahead) * 1e5)[1]
    d.stroke(np.array([(80, horizon), (W - 80, horizon)], float), BLEU, "construction",
             pressure=0.4, reach=900)
    doc.label((90, horizon - 44), "LIGNE D'HORIZON", size=26, color=(0.35, 0.50, 0.78))

    body, dressed = kaya.build(), kaya.design("colère")
    blockers = [occluders(dressed, pose) for _, pose, _ in KEYS]
    draw(d, scene.construct(DECOR, CAM, SOL, blockers), ORIGIN, SCALE, brush=HB, layer="decor",
         pressure=0.5, through=0, care=1.5, clip=clip)

    arc = parabola(*ARC)
    path = to_px(arc)
    for a, b in zip(range(0, len(path) - 2, 3), range(2, len(path), 3)):     # pointillé
        d.stroke(path[a:b + 1], ROUGE, "cadre", passes=2, pressure=0.85, taper=(0.1, 0.1))

    for (name, pose, brush), anchor in zip(KEYS, ARC):
        draw(d, construct(body, pose, CAM), ORIGIN, SCALE, pressure=0.3, through=0.2, clip=clip)
        draw(d, construct(dressed, pose, CAM), ORIGIN, SCALE, brush=brush, layer="net",
             pressure=0.95, through=0, care=1.3, clip=clip, min_size=16)
        x, y = to_px(anchor)
        doc.label((x - 330, y - 30), name, size=30, color=tuple(c * 0.85 for c in brush.color))

    rect(d, FRAME_A, FRAME, ROUGE, "CADRE A · image 1", doc)
    rect(d, FRAME_B, FRAME, ROUGE, "CADRE B · image 30", doc)
    return doc


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    doc = sheet()
    doc.save(OUT / "s05_layout.png")
    frames = timelapse(doc, OUT / "s05_layout.mp4", seconds=18, scale=0.3)
    print(f"{len(doc.journal)} traits, {frames} images -> {OUT}")
