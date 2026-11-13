"""Étape 3 (suite) — planche d'expressions.

Même tête, même angle : seuls changent les sourcils, les paupières, la bouche
et une légère inclinaison de la tête.

    python3 -m studio.steps.s03_expressions
"""
from pathlib import Path

from studio.characters import kaya
from studio.engine.brush import NET
from studio.engine.canvas import Document
from studio.engine.construction import draw
from studio.engine.hand import Draftsman
from studio.engine.mannequin import Camera, Pose, construct, rx, rz
from studio.steps.s03_model_sheet import NEUTRE, ZOOM

OUT = Path(__file__).resolve().parent.parent / "out"
W, H, SCALE = 2400, 900, 330
# Expression -> inclinaison de la tête.
HEADS = (("neutre", None), ("joie", rz(-7) @ rx(-4)), ("colère", rx(8)),
         ("surprise", rx(-6)), ("tristesse", rz(6) @ rx(12)))


def sheet(seed=31, zoom=ZOOM):
    z = zoom
    doc = Document(W * z, H * z, seed)
    for name in ("construction", "net"):
        doc.layer(name)
    doc.label((60 * z, 36 * z), "ÉTAPE 3 · EXPRESSIONS — KAYA", size=24 * z, weight="SemiBold",
              color=(0.30, 0.31, 0.36))
    d = Draftsman(doc, seed)
    body = kaya.build()
    cam = Camera(yaw=28, pitch=4, target=(0, 6.35, 0))
    for i, (expr, tilt) in enumerate(HEADS):
        x = (250 + i * 475) * z
        pose = Pose(**NEUTRE.joints, **({"head": tilt} if tilt is not None else {}))
        clip = (x - 228 * z, 120 * z, x + 228 * z, 800 * z)
        doc.label((x - 40 * z, 826 * z), expr.capitalize(), size=17 * z)
        draw(d, construct(body, pose, cam), (x, 440 * z), SCALE * z, pressure=0.3, through=0.2,
             clip=clip)
        draw(d, construct(kaya.design(expr), pose, cam), (x, 440 * z), SCALE * z, brush=NET,
             layer="net", pressure=0.62, through=0, care=1.8, clip=clip)
    return doc


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    doc = sheet()
    doc.save(OUT / "s03_expressions.png")
    print(f"{len(doc.journal)} traits -> {OUT}")
