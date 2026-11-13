"""Étape 5 — le layout du plan 6 (le saut).

Le layout fixe ce que l'animation ne devra plus décider : le décor en
perspective, le cadre et son mouvement, les positions clés du personnage et sa
trajectoire. Décor au graphite, personnage au crayon de couleur, cadres en rouge.

    python3 -m studio.steps.s05_layout
"""
from pathlib import Path

import numpy as np

from studio.characters import kaya
from studio.engine import scene
from studio.engine.brush import BLEU, HB, ROUGE, VERT
from studio.engine.canvas import Document
from studio.engine.construction import draw
from studio.engine.hand import Draftsman, spline
from studio.engine.mannequin import construct, occluders
from studio.engine.timelapse import timelapse
from studio.shots import plan6 as shot

OUT = Path(__file__).resolve().parent.parent / "out"
SHOWN = {"élan": BLEU, "sommet": ROUGE, "amorti": VERT}     # les trois positions du layout


def rect(d, corner, brush, label, doc):
    x, y = corner
    w, h = shot.FRAME
    pts = [(x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)]
    for a, b in zip(pts, pts[1:]):
        d.stroke(np.array([a, b], float), brush, "cadre", passes=3, pressure=0.9, overshoot=18)
    doc.label((x + 24, y + 16), label, size=44, weight="SemiBold", color=(0.72, 0.28, 0.24))


def sheet(seed=51):
    doc = Document(shot.W, shot.H, seed)
    for name in ("decor", "construction", "net", "cadre"):
        doc.layer(name)
    doc.label((120, 60), "ÉTAPE 5 · LAYOUT — PLAN 6 « ELLE SAUTE »", size=48, weight="SemiBold",
              color=(0.30, 0.31, 0.36))
    doc.label((120, 132), f"{shot.FRAMES} images · caméra basse · le cadre suit le saut : "
              "A, puis B au sommet, puis C à la réception", size=30)
    d = Draftsman(doc, seed)
    clip = (60, 200, shot.W - 60, shot.H - 60)
    cam = shot.CAM

    # Ligne d'horizon : la hauteur de l'œil de la caméra, à l'infini.
    eye = cam.target + cam.back * cam.dist
    ahead = -cam.back * (1, 0, 1)
    horizon = shot.to_px(eye + ahead / np.linalg.norm(ahead) * 1e5)[1]
    d.stroke(np.array([(80, horizon), (shot.W - 80, horizon)], float), BLEU, "construction",
             pressure=0.4, reach=900)
    doc.label((90, horizon - 44), "LIGNE D'HORIZON", size=26, color=(0.35, 0.50, 0.78))

    body, dressed = kaya.build(), kaya.design("colère")
    keys = shot.keys(body)
    shown = [k for k in keys if k["name"] in SHOWN]
    blockers = [occluders(dressed, k["pose"]) for k in shown]
    draw(d, scene.construct(shot.DECOR, cam, shot.SOL, blockers), shot.ORIGIN, shot.SCALE,
         brush=HB, layer="decor", pressure=0.5, through=0, care=1.5, clip=clip)

    path = spline(shot.to_px([k["pelvis"] for k in keys]), per=8)       # trajectoire du bassin
    for a in range(0, len(path) - 3, 5):                                # en pointillé
        d.stroke(path[a:a + 4], ROUGE, "cadre", passes=2, pressure=0.85, taper=(0.1, 0.1))

    for key in shown:
        brush = SHOWN[key["name"]]
        draw(d, construct(body, key["pose"], cam, shot.DECOR), shot.ORIGIN, shot.SCALE,
             pressure=0.3, through=0.2, clip=clip)
        draw(d, construct(dressed, key["pose"], cam, shot.DECOR), shot.ORIGIN, shot.SCALE,
             brush=brush,
             layer="net", pressure=0.95, through=0, care=1.3, clip=clip, min_size=16)
        x, y = shot.to_px(key["pelvis"])
        doc.label((x - 400, y - 30), f"image {key['image']} · {key['name']}", size=30,
                  color=tuple(c * 0.85 for c in brush.color))

    rect(d, shot.FRAME_A, ROUGE, "CADRE A · images 1 à 9", doc)
    rect(d, shot.FRAME_B, ROUGE, "CADRE B · images 18 à 20", doc)
    rect(d, shot.FRAME_C, VERT, "", doc)
    doc.label((shot.FRAME_C[0] + shot.FRAME[0] - 640, shot.FRAME_C[1] + 80),
              "CADRE C · images 27 à 30", size=44, weight="SemiBold", color=(0.20, 0.50, 0.36))
    return doc


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    doc = sheet()
    doc.save(OUT / "s05_layout.png")
    frames = timelapse(doc, OUT / "s05_layout.mp4", seconds=18, scale=0.3)
    print(f"{len(doc.journal)} traits, {frames} images -> {OUT}")
