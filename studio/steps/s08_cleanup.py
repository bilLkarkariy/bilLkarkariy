"""Étape 8 — le clean-up du plan 6.

Le dessin d'animation devient le dessin définitif : plus de construction bleue,
un trait sombre et net, et la même main pour chaque forme à chaque image, pour
que la ligne ne tremble plus. Le décor reste au crayon, en retrait.

Sorties : une planche avant/après, puis l'animation mise au net à 12 et 24 dessins par seconde.

    python3 -m studio.steps.s08_cleanup
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from studio.characters import kaya
from studio.engine.brush import TRAIT
from studio.engine.mannequin import construct
from studio.shots import plan6 as shot
from studio.shots.render import ShotRenderer
from studio.steps.s07_intervalles import sways

OUT = Path(__file__).resolve().parent.parent / "out"
# Une main posée et appliquée : très peu d'écart, très peu de tremblement.
HAND = dict(tremor=0.18, aim=0.3, turn=0.002, scale=0.003, bow=0.001)
CLEAN = dict(brush=TRAIT, pressure=0.62, care=1.0, min_size=10, stable=8)
SHOWN = (8, 17, 27)             # images de la planche avant/après


def compare(renderer, body, cons, poses, clean, path):
    """Planche : le dessin d'animation en haut, sa mise au net en bas."""
    size, pad, top = 1500, 60, 190
    page = Image.new("RGB", (pad + len(SHOWN) * (size + pad), top + 2 * (size + 110)),
                     (246, 243, 236))
    pen = ImageDraw.Draw(page)
    try:
        bold = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-SemiBold.otf", 52)
        text = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Regular.otf", 36)
    except OSError:
        bold = text = ImageFont.load_default(40)
    pen.text((pad, 50), "ÉTAPE 8 · CLEAN-UP — PLAN 6", fill=(76, 79, 92), font=bold)
    for i, f in enumerate(SHOWN):
        rough = renderer.drawing(cons[f], construct(body, poses[f], shot.CAM, shot.DECOR), 100 + f)
        centre = shot.to_px(body.solve(poses[f])["waist"][0]) - (renderer.x0, renderer.y0)
        x0 = int(np.clip(centre[0] - size / 2, 0, rough.shape[1] - size))
        y0 = int(np.clip(centre[1] - size / 2, 0, rough.shape[0] - size))
        for row, (image, label) in enumerate(((rough, "dessin d'animation"),
                                              (clean[f], "mise au net"))):
            x, y = pad + i * (size + pad), top + row * (size + 110)
            page.paste(Image.fromarray(image[y0:y0 + size, x0:x0 + size]), (x, y))
            pen.rectangle((x, y, x + size, y + size), outline=(150, 150, 155), width=2)
            pen.text((x, y + size + 16), f"Image {f} · {label}", fill=(96, 99, 110), font=text)
    page.save(path)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    body = kaya.build()
    at = shot.motion(body)
    sway = sways(body, at)
    poses = {f: at(f) for f in range(1, shot.FRAMES + 1)}
    cons = {f: construct(kaya.design("colère", sway[f]), poses[f], shot.CAM, shot.DECOR)
            for f in poses}
    renderer = ShotRenderer(shot, list(cons.values()), seed=72)
    clean = {f: renderer.drawing(cons[f], seed=8, decor=0.55, hand=HAND, **CLEAN) for f in poses}
    compare(renderer, body, cons, poses, clean, OUT / "s08_avant_apres.png")
    renderer.play(OUT / "s08_cleanup_12.mp4", lambda f: clean[f - (f + 1) % 2], loops=4)
    renderer.play(OUT / "s08_cleanup_24.mp4", lambda f: clean[f], loops=4)
    print(f"{len(clean)} dessins mis au net -> {OUT}")
