"""Étape 6 — les poses clés et la feuille d'exposition du plan 6.

Trois sorties : la planche des clés (toutes les poses sur le layout, puis une
par une), la feuille d'exposition (quelle pose tombe sur quelle image, et où est
la caméra), et le test de poses, première vidéo du mouvement : chaque clé est
tenue jusqu'à la suivante.

    python3 -m studio.steps.s06_cles
"""
from pathlib import Path

import numpy as np

from studio.characters import kaya
from studio.engine import scene
from studio.engine.brush import BLEU, HB, NET, ROUGE, VERT
from studio.engine.canvas import Document
from studio.engine.construction import draw
from studio.engine.hand import Draftsman, ellipse, spline, TAU
from studio.engine.mannequin import Camera, construct
from studio.shots import plan6 as shot
from studio.shots.render import ShotRenderer

OUT = Path(__file__).resolve().parent.parent / "out"
INK = (0.30, 0.31, 0.36)
COLORS = (BLEU, ROUGE, VERT)


def keys_sheet(body, dressed, keys, seed=61):
    """Planche des clés : en haut toutes les poses dans le décor, en bas une par une."""
    top, cell_w, cell_h = 2500, 940, 880
    doc = Document(shot.W, top + 2 * cell_h + 80, seed)
    for name in ("decor", "construction", "net"):
        doc.layer(name)
    doc.label((120, 60), "ÉTAPE 6 · POSES CLÉS — PLAN 6 « ELLE SAUTE »", size=48,
              weight="SemiBold", color=INK)
    doc.label((120, 132), "Clés en couleur pleine, passages (poses intermédiaires imposées) "
              "en trait fin. En l'air, le bassin suit une chute libre calculée.", size=30)
    d = Draftsman(doc, seed)
    clip = (60, 200, shot.W - 60, top - 20)
    # Le layout est remonté pour tenir dans la moitié haute de la planche.
    origin = np.asarray(shot.ORIGIN, float) - (0, 420)
    draw(d, scene.construct(shot.DECOR, shot.CAM, shot.SOL), origin, shot.SCALE, brush=HB,
         layer="decor", pressure=0.3, through=0, care=1.5, clip=clip)
    path = spline(origin + shot.CAM.project([k["pelvis"] for k in keys])
                  * (shot.SCALE, -shot.SCALE), per=8)
    for a in range(0, len(path) - 3, 5):
        d.stroke(path[a:a + 4], HB, "net", pressure=0.6, taper=(0.1, 0.1))
    for i, key in enumerate(keys):
        brush = COLORS[i % 3]
        con = construct(dressed, key["pose"], shot.CAM, shot.DECOR)
        strong = key["kind"] == "clé"
        # Seules les grandes formes : superposées, les poses doivent rester lisibles.
        draw(d, con, origin, shot.SCALE, brush=brush, layer="net", pressure=0.9 if strong else 0.5,
             through=0, care=1.3, clip=clip, min_size=150)
        x, y = origin + shot.CAM.project(key["pelvis"]) * (shot.SCALE, -shot.SCALE)
        doc.label((x - 30, clip[3] - 60 if i % 2 else clip[1] + 20), str(key["image"]), size=40,
                  weight="SemiBold", color=tuple(c * 0.85 for c in brush.color))

    # Une case par pose : même caméra, centrée sur le bassin.
    for i, key in enumerate(keys):
        x0, y0 = 50 + (i % 5) * cell_w, top + (i // 5) * cell_h
        doc.frame(x0, y0, x0 + cell_w - 20, y0 + cell_h - 20, width=2, strength=0.4)
        doc.label((x0 + 20, y0 + 16), f"image {key['image']}", size=34, weight="SemiBold", color=INK)
        doc.label((x0 + 20, y0 + 62), f"{key['name']} · {key['kind']}", size=28)
        cam = Camera(-65, -6, tuple(key["pelvis"] + (0, 0.4, 0)), dist=18)
        centre = (x0 + cell_w / 2 - 10, y0 + cell_h / 2 + 40)
        box = (x0 + 6, y0 + 100, x0 + cell_w - 26, y0 + cell_h - 26)
        draw(d, construct(body, key["pose"], cam), centre, 100, pressure=0.4, through=0.25,
             clip=box)
        draw(d, construct(dressed, key["pose"], cam), centre, 100, brush=NET, layer="net",
             pressure=0.6, through=0, care=1.3, clip=box, min_size=14)
    return doc


def x_sheet(keys, seed=62):
    """Feuille d'exposition : une ligne par image."""
    row, top, w = 74, 330, 2200
    doc = Document(w, top + shot.FRAMES * row + 120, seed)
    doc.layer("net")
    doc.label((80, 50), "FEUILLE D'EXPOSITION — PLAN 6", size=46, weight="SemiBold", color=INK)
    doc.label((80, 118), f"{shot.FRAMES} images · {shot.FPS} images par seconde · "
              f"{shot.FRAMES / shot.FPS:.2f} s", size=28)
    cols = (("IMAGE", 80), ("ACTION", 260), ("POSE", 900), ("DESSIN TENU", 1180),
            ("CAMÉRA", 1560))
    for name, x in cols:
        doc.label((x, top - 70), name, size=28, weight="SemiBold", color=INK)
    for x in (230, 870, 1150, 1530):
        doc.paper.rgb[top - 90:top + shot.FRAMES * row, x:x + 2] *= 0.7
    d = Draftsman(doc, seed)
    by_image = {k["image"]: (i, k) for i, k in enumerate(keys)}
    notes = {1: "court", 5: "pose les deux pieds", 8: "au plus bas", 11: "quitte le sol",
             18: "au-dessus du muret", 26: "touche le sol", 28: "au plus bas",
             30: "se redresse"}
    for f in range(1, shot.FRAMES + 1):
        y = top + (f - 1) * row
        doc.guide(y, 60, w - 60, strength=0.3 if (f - 1) % 6 else 0.6)
        doc.label((100, y + 16), f"{f:02d}", size=32, color=INK)
        if shot.TAKEOFF < f < shot.LANDING:
            doc.label((270, y + 20), "en l'air" if f not in notes else notes[f], size=26)
        elif f in notes:
            doc.label((270, y + 20), notes[f], size=26)
        if f in by_image:
            i, key = by_image[f]
            doc.label((920, y + 14), key["name"], size=28, weight="SemiBold" if key["kind"] == "clé"
                      else "Regular", color=INK)
            doc.label((1215, y + 14), f"A{i + 1}", size=30, color=INK)
            if key["kind"] == "clé":            # une clé s'entoure à la main, au crayon rouge
                d.stroke(ellipse((1238, y + 34), 46, 27, 0, d.hand.rng.uniform(0, TAU), TAU * 1.1),
                         ROUGE, "net", pressure=0.7)
        else:                                   # trait vertical : le dessin précédent est tenu
            d.stroke(np.array([(1238, y + 4), (1238, y + row - 4)], float), HB, "net", pressure=0.45,
                     taper=(0, 0), tip=1)
        corner = shot.frame_corner(f)
        for name, ref in (("A", shot.FRAME_A), ("B", shot.FRAME_B), ("C", shot.FRAME_C)):
            if np.allclose(corner, ref, atol=1):
                doc.label((1590, y + 14), f"cadre {name}", size=28, color=(0.72, 0.28, 0.24))
                break
        else:
            d.stroke(np.array([(1640, y + 6), (1640, y + row - 6)], float), ROUGE, "net",
                     pressure=0.6, taper=(0, 0), tip=1)
    doc.guide(top + shot.FRAMES * row, 60, w - 60, strength=0.6)
    doc.label((1700, top + 9 * row + 14), "PAN vers B", size=26, color=(0.72, 0.28, 0.24))
    doc.label((1700, top + 20 * row + 14), "PAN vers C", size=26, color=(0.72, 0.28, 0.24))
    return doc


def pose_test(body, dressed, keys, path, seed=63):
    """Vidéo : chaque clé est tenue jusqu'à la suivante, et le cadre se déplace."""
    cons = [construct(dressed, key["pose"], shot.CAM, shot.DECOR) for key in keys]
    renderer = ShotRenderer(shot, cons, seed)
    drawings = [(key["image"], renderer.drawing(
        con, construct(body, key["pose"], shot.CAM, shot.DECOR), seed + 1 + i))
        for i, (key, con) in enumerate(zip(keys, cons))]
    return renderer.play(path, lambda f: [img for start, img in drawings if start <= f][-1])


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    body, dressed = kaya.build(), kaya.design("colère")
    keys = shot.keys(body)
    keys_sheet(body, dressed, keys).save(OUT / "s06_cles.png")
    x_sheet(keys).save(OUT / "s06_exposition.png")
    frames = pose_test(body, dressed, keys, OUT / "s06_test_poses.mp4")
    print(f"{len(keys)} poses, {frames} images -> {OUT}")
