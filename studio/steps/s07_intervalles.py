"""Étape 7 — les intervalles du plan 6.

Entre les clés, chaque articulation suit une courbe lisse : les arcs viennent de
là. Le flow des clés donne les ralentis (élan, amorti) et les passages rapides
(détente). Au sol, le pied d'appui reste planté ; en l'air, le bassin tombe en
chute libre ; la queue de cheval suit avec du retard.

Sorties : la feuille d'espacement, puis l'animation à 12 et à 24 dessins par seconde.

    python3 -m studio.steps.s07_intervalles
"""
from pathlib import Path

import numpy as np

from studio.characters import kaya
from studio.engine import scene
from studio.engine.brush import BLEU, HB, ROUGE, VERT
from studio.engine.canvas import Document
from studio.engine.construction import draw
from studio.engine.hand import Draftsman, ellipse, TAU
from studio.engine.mannequin import construct
from studio.shots import plan6 as shot
from studio.shots.render import ShotRenderer

OUT = Path(__file__).resolve().parent.parent / "out"
INK = (0.30, 0.31, 0.36)
TRACKS = (("bassin", "pelvis", ROUGE), ("main droite", "wrist_R", BLEU),
          ("pied droit", "ankle_R", VERT), ("tête", "head", HB))


def sways(body, at):
    """Retard de la queue de cheval, image par image, dans le repère de la tête :
    elle part à l'opposé de la vitesse de la tête, puis rattrape."""
    frames = [body.solve(at(f)) for f in range(0, shot.FRAMES + 2)]
    head = np.array([fr["head"][0] for fr in frames])
    out, lag = {}, np.zeros(3)
    for f in range(1, shot.FRAMES + 1):
        velocity = (head[f + 1] - head[f - 1]) / 2
        lag = 0.55 * lag + 0.45 * (-1.6 * velocity)
        local = frames[f]["head"][1].T @ lag
        out[f] = local * min(1.0, 0.7 / max(np.linalg.norm(local), 1e-9))
    return out


def spacing_sheet(body, dressed, at, seed=71):
    """Feuille d'espacement : où est chaque partie du corps à chaque image."""
    doc = Document(shot.W, shot.H, seed)
    for name in ("decor", "net"):
        doc.layer(name)
    doc.label((120, 60), "ÉTAPE 7 · ESPACEMENT — PLAN 6 « ELLE SAUTE »", size=48,
              weight="SemiBold", color=INK)
    doc.label((120, 132), "Un point par image. Points serrés : mouvement lent. Points écartés : "
              "mouvement rapide. Les clés sont entourées et numérotées.", size=30)
    for i, (label, _, brush) in enumerate(TRACKS):
        doc.label((120 + i * 420, 200), f"● {label}", size=30,
                  color=tuple(c * 0.85 for c in brush.color))
    d = Draftsman(doc, seed)
    clip = (60, 260, shot.W - 60, shot.H - 60)
    draw(d, scene.construct(shot.DECOR, shot.CAM, shot.SOL), shot.ORIGIN, shot.SCALE, brush=HB,
         layer="decor", pressure=0.3, through=0, care=1.5, clip=clip)
    keys = shot.keys(body)
    for key in keys:                    # les clés, en silhouette légère
        draw(d, construct(dressed, key["pose"], shot.CAM, shot.DECOR), shot.ORIGIN, shot.SCALE,
             brush=HB, layer="decor", pressure=0.5, through=0, clip=clip, min_size=150)
    key_images = {k["image"] for k in keys}
    fine = np.arange(1, shot.FRAMES + 0.01, 0.25)
    solved = {round(float(f), 2): body.solve(at(f)) for f in fine}
    for label, joint, brush in TRACKS:
        path = shot.to_px([solved[round(float(f), 2)][joint][0] for f in fine])
        d.stroke(path, brush, "net", passes=2, pressure=0.75, taper=(0.02, 0.02))
        for f in range(1, shot.FRAMES + 1):
            x, y = shot.to_px(solved[float(f)][joint][0])
            big = f in key_images
            d.stroke(ellipse((x, y), 15 if big else 6, 15 if big else 6, 0,
                             d.hand.rng.uniform(0, TAU), TAU * 1.2), brush, "net",
                     passes=2, pressure=0.9, care=3)
            if big and joint == "pelvis":
                doc.label((x + 22, y - 44), str(f), size=30, weight="SemiBold",
                          color=tuple(c * 0.8 for c in brush.color))
    return doc


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    body = kaya.build()
    at = shot.motion(body)
    spacing_sheet(body, kaya.design("colère"), at).save(OUT / "s07_espacement.png")

    sway = sways(body, at)
    poses = {f: at(f) for f in range(1, shot.FRAMES + 1)}
    cons = {f: construct(kaya.design("colère", sway[f]), poses[f], shot.CAM, shot.DECOR)
            for f in poses}
    renderer = ShotRenderer(shot, list(cons.values()), seed=72)
    images = {f: renderer.drawing(cons[f], construct(body, poses[f], shot.CAM, shot.DECOR), 100 + f)
              for f in poses}
    renderer.play(OUT / "s07_animation_24.mp4", lambda f: images[f], loops=4)
    renderer.play(OUT / "s07_animation_12.mp4", lambda f: images[f - (f + 1) % 2], loops=4)
    print(f"{len(images)} dessins -> {OUT}")
