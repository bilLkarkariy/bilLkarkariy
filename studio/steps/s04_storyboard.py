"""Étape 4 — le storyboard rough.

Une page de six cases. Chaque case est un plan : une caméra (angle, hauteur,
focale, valeur de plan), une pose, une expression, et des flèches de mouvement.
Le dessin reste un croquis : construction bleue visible, trait lâché, pas de détail
sur ce qui est trop petit dans le cadre.

    python3 -m studio.steps.s04_storyboard
"""
from pathlib import Path

import numpy as np

from studio.characters import kaya
from studio.engine import poses
from studio.engine.brush import HB, ROUGE, STORY
from studio.engine.canvas import Document
from studio.engine.construction import Construction, Shape, draw
from studio.engine.hand import Draftsman, spline
from studio.engine.mannequin import Camera, construct
from studio.engine.timelapse import timelapse

OUT = Path(__file__).resolve().parent.parent / "out"
W, H = 4800, 2760
PW, PH = 1400, 788                  # une case, au format 16:9

# Un plan : valeur, description, durée (images à 24 i/s), caméra, échelle (pixels par
# tête), décalage du sujet dans la case, pose, expression, flèches (points en pixels
# relatifs au centre de la case ; rouge = mouvement de caméra).
SHOTS = [
    dict(size="Plan large", action="Kaya court vers la droite.", frames=48,
         cam=Camera(-90, 3, (0, 3.3, 0), dist=30), scale=88, shift=(-300, 20),
         pose=poses.COURSE, expr="neutre",
         arrows=[(STORY, [(80, -60), (300, -85), (540, -50)])],
         speed=[(-640, -190, 150), (-670, -70, 190), (-630, 60, 130)]),
    dict(size="Plan moyen, contre-plongée", action="Elle fonce vers nous.", frames=36,
         cam=Camera(-22, -12, (0, 3.9, 0), dist=9), scale=128, shift=(40, 40),
         pose=poses.COURSE, expr="colère", arrows=[]),
    dict(size="Gros plan", action="Un bruit derrière elle. Elle se fige.", frames=24,
         cam=Camera(22, 2, (0, 6.38, 0)), scale=430, shift=(0, 30),
         pose=poses.A_POSE, expr="surprise", arrows=[]),
    dict(size="Plan taille, de dos", action="Elle regarde par-dessus son épaule.", frames=60,
         cam=Camera(155, 6, (0, 5.3, 0), dist=12), scale=190, shift=(-120, 40),
         pose=poses.REGARD, expr="neutre",
         arrows=[(ROUGE, [(260, 250), (420, 235), (560, 250)])], note="TRAV. latéral lent"),
    dict(size="Plan moyen, de profil", action="Elle se ramasse : élan.", frames=18,
         cam=Camera(-72, 5, (0, 2.3, 0), dist=14), scale=118, shift=(-60, 90),
         pose=poses.ELAN, expr="colère",
         arrows=[(STORY, [(-120, -230), (-150, -110), (-140, 10)])]),
    dict(size="Plan large, contre-plongée", action="Elle saute.", frames=30,
         cam=Camera(-38, -20, (0, 5.4, 0), dist=11), scale=100, shift=(60, 80),
         pose=poses.SAUT, expr="joie",
         arrows=[(STORY, [(-380, 320), (-420, 60), (-350, -220)])]),
]


def floor(cam, extent=12, step=2.0):
    """Quadrillage du sol vu par la caméra : il donne le point de fuite et l'échelle."""
    con = Construction()
    t = np.linspace(-extent, extent, 60)
    zero = np.zeros_like(t)
    for k in np.arange(-extent, extent + 0.1, step):
        for pts in (np.stack([t, zero, zero + k], axis=1), np.stack([zero + k, zero, t], axis=1)):
            if cam.dist is not None:
                pts = pts[(pts - cam.target) @ cam.back < cam.dist - 1.5]
            if len(pts) > 1:
                con.shapes.append(Shape(cam.project(pts), np.zeros(len(pts), bool)))
    return con


def arrow(d, pts, brush, layer="net"):
    pts = np.asarray(pts, float)
    path = spline(pts) if len(pts) > 2 else pts
    d.stroke(path, brush, layer, passes=2, pressure=0.85)
    tip, back = path[-1], path[-1] - path[-6 if len(path) > 6 else 0]
    back = back / np.hypot(*back)
    for ang in (2.6, -2.6):
        c, s = np.cos(ang), np.sin(ang)
        wing = np.array([back[0] * c - back[1] * s, back[0] * s + back[1] * c]) * 52
        d.stroke(np.array([tip + wing, tip]), brush, layer, passes=2, pressure=0.9)


def page(seed=41):
    doc = Document(W, H, seed)
    for name in ("construction", "net"):
        doc.layer(name)
    doc.label((150, 70), "ÉTAPE 4 · STORYBOARD ROUGH — SÉQUENCE « LE SAUT »", size=48,
              weight="SemiBold", color=(0.30, 0.31, 0.36))
    total = sum(s["frames"] for s in SHOTS)
    doc.label((150, 140), f"{len(SHOTS)} plans · {total} images · {total / 24:.1f} s à 24 i/s",
              size=30)
    d = Draftsman(doc, seed, tremor=0.9, aim=2.2)
    body = kaya.build()
    for i, shot in enumerate(SHOTS):
        x0, y0 = 150 + (i % 3) * 1550, 250 + (i // 3) * 1240
        doc.frame(x0, y0, x0 + PW, y0 + PH)
        doc.label((x0, y0 + PH + 26), f"PLAN {i + 1}", size=32, weight="SemiBold",
                  color=(0.30, 0.31, 0.36))
        doc.label((x0 + 170, y0 + PH + 28), f"{shot['size']} · {shot['frames']} images", size=30)
        doc.label((x0, y0 + PH + 78), shot["action"], size=30)
        if "note" in shot:
            doc.label((x0, y0 + PH + 128), f"Caméra : {shot['note']}", size=28,
                      color=(0.70, 0.30, 0.26))
        clip = (x0 + 8, y0 + 8, x0 + PW - 8, y0 + PH - 8)
        centre = np.array([x0 + PW / 2, y0 + PH / 2])
        origin = centre + shot["shift"]
        cam, scale = shot["cam"], shot["scale"]
        draw(d, floor(cam), origin, scale, pressure=0.4, clip=clip)
        draw(d, construct(body, shot["pose"], cam), origin, scale, pressure=0.6, through=0.25,
             clip=clip)
        draw(d, construct(kaya.design(shot["expr"]), shot["pose"], cam), origin, scale, brush=STORY,
             layer="net", pressure=0.8, through=0, care=0.9, clip=clip, min_size=30)
        for brush, pts in shot["arrows"]:
            arrow(d, centre + np.asarray(pts, float), brush)
        for x, y, length in shot.get("speed", []):
            d.stroke(np.array([centre + (x, y), centre + (x + length, y)]), HB, "net",
                     pressure=0.5, taper=(0.3, 0.5))
    return doc


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    doc = page()
    doc.save(OUT / "s04_storyboard.png")
    frames = timelapse(doc, OUT / "s04_storyboard.mp4", seconds=18, scale=0.3)
    print(f"{len(doc.journal)} traits, {frames} images -> {OUT}")
