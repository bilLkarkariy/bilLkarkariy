"""Étape 3 — le model sheet : le personnage habillé, sous cinq angles.

Le mannequin est tracé au crayon bleu, puis le personnage au graphite par-dessus.
Les deux viennent du même squelette, donc les cinq vues s'alignent.

    python3 -m studio.steps.s03_model_sheet
"""
from pathlib import Path

from studio.characters import kaya
from studio.engine.brush import HB
from studio.engine.canvas import Document
from studio.engine.construction import draw
from studio.engine.hand import Draftsman
from studio.engine.mannequin import Camera, Pose, To, construct
from studio.engine.timelapse import timelapse

OUT = Path(__file__).resolve().parent.parent / "out"
W, H, SCALE, GROUND = 2400, 1400, 150, 1300
VIEWS = (("Face", 0), ("Trois quarts", 45), ("Profil", 90), ("Trois quarts dos", 135), ("Dos", 180))
NEUTRE = Pose(shoulder_L=To((0.26, -0.97, 0)), shoulder_R=To((-0.26, -0.97, 0)),
              hip_L=To((0.03, -1, 0), twist=8), hip_R=To((-0.03, -1, 0), twist=-8))


def sheet(seed=21):
    doc = Document(W, H, seed)
    for name in ("construction", "net"):
        doc.layer(name)
    doc.label((60, 36), "ÉTAPE 3 · MODEL SHEET — KAYA", size=24, weight="SemiBold",
              color=(0.30, 0.31, 0.36))
    d = Draftsman(doc, seed)
    body, dressed = kaya.build(), kaya.design()
    front = construct(body, NEUTRE, Camera(0))
    for name in ("top", "chin", "shoulder_L", "crotch", "knee_L"):
        doc.guide(GROUND - front.marks[name][1] * SCALE, 40, W - 40)
    doc.guide(GROUND, 40, W - 40)
    for i, (name, yaw) in enumerate(VIEWS):
        x = 270 + i * 465
        doc.label((x - 50, GROUND + 30), name, size=16)
        cam = Camera(yaw)
        draw(d, construct(body, NEUTRE, cam), (x, GROUND), SCALE, pressure=0.32, through=0.25)
        draw(d, construct(dressed, NEUTRE, cam), (x, GROUND), SCALE, brush=HB, layer="net",
             pressure=0.8, through=0, care=1.8)
    return doc


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    doc = sheet()
    doc.save(OUT / "s03_model_sheet.png")
    frames = timelapse(doc, OUT / "s03_model_sheet.mp4", seconds=16, scale=0.6)
    print(f"{len(doc.journal)} traits, {frames} images -> {OUT}")
