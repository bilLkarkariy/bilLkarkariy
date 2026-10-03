"""Papier, quadrillage de labo et grain : python3 tools/textures.py"""
import os
import numpy as np
from PIL import Image, ImageFilter

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "public", "tex")
W, H = 1920, 1080
rng = np.random.default_rng(3)


def blur_noise(scale, sigma):
    small = rng.standard_normal((H // scale + 2, W // scale + 2)).astype(np.float32)
    im = Image.fromarray(((small - small.min()) / np.ptp(small) * 255).astype(np.uint8))
    im = im.resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(sigma))
    a = np.asarray(im, np.float32) / 255
    return (a - a.mean()) / (a.std() + 1e-6)


def paper(base, name):
    base = np.array([int(base[i:i + 2], 16) for i in (1, 3, 5)], np.float32)
    mottling = blur_noise(60, 30) * 0.005 + blur_noise(12, 4) * 0.003
    fine = rng.standard_normal((H, W)).astype(np.float32) * 0.010
    fibers = np.zeros((H, W), np.float32)
    for _ in range(900):  # fibres courtes, très pâles
        x, y = rng.integers(0, W), rng.integers(0, H)
        ang, ln = rng.uniform(0, np.pi), rng.integers(6, 26)
        xs = (x + np.cos(ang) * np.arange(ln)).astype(int).clip(0, W - 1)
        ys = (y + np.sin(ang) * np.arange(ln)).astype(int).clip(0, H - 1)
        fibers[ys, xs] += rng.choice([-1, 1]) * 0.012
    yy, xx = np.mgrid[0:H, 0:W]
    vign = 1 - 0.05 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    lum = (1 + mottling + fine + fibers) * vign
    img = np.clip(base[None, None, :] * lum[..., None], 0, 255).astype(np.uint8)
    Image.fromarray(img).save(os.path.join(OUT, name))


def grid():
    """Papier millimétré du labo : 1 trait fin tous les 24 px, 1 appuyé tous les 120 px."""
    a = np.zeros((H, W), np.float32)
    for k in range(0, W, 24):
        a[:, k] = 0.075
    for k in range(0, H, 24):
        a[k, :] = 0.075
    for k in range(0, W, 120):
        a[:, k] = 0.13
    for k in range(0, H, 120):
        a[k, :] = 0.13
    rgba = np.zeros((H, W, 4), np.uint8)
    rgba[..., :3] = (60, 84, 96)  # gris bleuté : le monde froid de la science
    rgba[..., 3] = (a * 255).astype(np.uint8)
    Image.fromarray(rgba).save(os.path.join(OUT, "grid.png"))


def grain(n=8):
    for i in range(n):
        g = rng.standard_normal((H // 2, W // 2)).astype(np.float32)
        v = np.clip(128 + g * 40, 0, 255).astype(np.uint8)
        Image.fromarray(v).resize((W, H), Image.NEAREST).save(os.path.join(OUT, f"grain_{i}.png"))


os.makedirs(OUT, exist_ok=True)
paper("#E8E6E0", "paper_cool.png")
paper("#EEE6D6", "paper_warm.png")
grid()
grain()
print(sorted(os.listdir(OUT)))
