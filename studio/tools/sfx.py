"""Design sonore synthétisé (aucune banque de sons, aucun droit à gérer).

python3 tools/sfx.py -> public/sfx/*.wav (48 kHz mono)
"""
import os

import numpy as np
import soundfile as sf
from scipy import signal

SR = 48000
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "public", "sfx")
rng = np.random.default_rng(7)


def t(d):
    return np.arange(int(d * SR)) / SR


def bp(x, lo, hi, order=4):
    sos = signal.butter(order, [lo, hi], btype="band", fs=SR, output="sos")
    return signal.sosfilt(sos, x)


def lp(x, f, order=4):
    return signal.sosfilt(signal.butter(order, f, btype="low", fs=SR, output="sos"), x)


def hp(x, f, order=4):
    return signal.sosfilt(signal.butter(order, f, btype="high", fs=SR, output="sos"), x)


def env(n, attack, decay):
    x = np.arange(n) / SR
    return np.minimum(1, x / max(attack, 1e-4)) * np.exp(-x / decay)


def save(name, x, peak_db):
    x = x / (np.max(np.abs(x)) + 1e-9) * 10 ** (peak_db / 20)
    fade = min(len(x), int(0.004 * SR))
    x[-fade:] *= np.linspace(1, 0, fade)
    sf.write(os.path.join(OUT, name + ".wav"), x.astype(np.float32), SR)


def roomtone(d=90):
    """Le son d'une pièce : grave, presque rien, jamais du silence numérique."""
    n = int(d * SR)
    brown = np.cumsum(rng.standard_normal(n))
    brown = hp(brown, 25, 2)
    low = lp(brown, 220)
    air = bp(rng.standard_normal(n), 2500, 7000, 2) * 0.004
    hum = 0.0015 * np.sin(2 * np.pi * 50 * t(d)) + 0.0006 * np.sin(2 * np.pi * 100 * t(d))
    drift = 1 + 0.15 * np.sin(2 * np.pi * 0.07 * t(d))
    x = low / np.std(low) * 0.01 * drift + air + hum
    fade = int(2 * SR)
    x[:fade] *= np.linspace(0, 1, fade)
    x[-fade:] *= np.linspace(1, 0, fade)
    save("roomtone", x, -30)


def phone_down():
    """Téléphone posé face contre le bureau."""
    d = 0.35
    knock = np.sin(2 * np.pi * (170 - 50 * t(d)) * t(d)) * env(int(d * SR), 0.001, 0.035)
    click = bp(rng.standard_normal(int(d * SR)), 1800, 6000) * env(int(d * SR), 0.0003, 0.006)
    x = knock * 0.9 + click * 0.6
    second = np.zeros_like(x)
    k = int(0.045 * SR)
    second[k:] = (knock * 0.35 + click * 0.25)[: len(x) - k]
    save("phone_down", x + second, -9)


def tick():
    d = 0.06
    x = bp(rng.standard_normal(int(d * SR)), 2500, 7000) * env(int(d * SR), 0.0002, 0.004)
    save("tick", x, -20)


def pencil(d=1.6):
    """Mine de crayon sur papier : bruit filtré, granuleux, irrégulier."""
    n = int(d * SR)
    grain = bp(rng.standard_normal(n), 1800, 7500, 2)
    rough = lp(np.abs(rng.standard_normal(n)), 30, 2)
    rough = rough / rough.max()
    strokes = 0.6 + 0.4 * np.sin(2 * np.pi * 2.3 * t(d) + 1.3 * np.sin(2 * np.pi * 0.7 * t(d)))
    shape = np.minimum(1, t(d) / 0.08) * np.minimum(1, (d - t(d)) / 0.2)
    save("pencil", grain * rough * strokes * shape, -24)


def button_click():
    """Bouton poussoir : enfoncement net + relâchement plus léger."""
    d = 0.25
    n = int(d * SR)

    def one(amp, ring):
        body = np.sin(2 * np.pi * ring * t(d)) * env(n, 0.0002, 0.012)
        snap = hp(rng.standard_normal(n), 3000) * env(n, 0.0001, 0.0025)
        thump = np.sin(2 * np.pi * 95 * t(d)) * env(n, 0.001, 0.03)
        return amp * (0.7 * snap + 0.35 * body + 0.6 * thump)

    x = one(1.0, 2400)
    rel = one(0.45, 2900)
    k = int(0.085 * SR)
    x[k:] += rel[: n - k]
    save("button_click", x, -6)


def zap():
    """Décharge : crépitement + bourdonnement électrique, très court."""
    d = 0.42
    n = int(d * SR)
    gates = (rng.random(n // 48 + 1) < 0.45).repeat(48)[:n].astype(float)
    crackle = hp(rng.standard_normal(n), 1500) * lp(gates, 900, 2)
    saw = signal.sawtooth(2 * np.pi * 118 * t(d)) + 0.5 * signal.sawtooth(2 * np.pi * 236.5 * t(d))
    buzz = np.tanh(3 * saw) * 0.35
    e = env(n, 0.001, 0.12)
    snap = hp(rng.standard_normal(n), 4000) * env(n, 0.0001, 0.004)
    x = (crackle * 0.8 + buzz) * e + snap * 0.9
    save("zap", x, -5)


def sub():
    """Impact grave pour un chiffre : se sent plus qu'il ne s'entend."""
    d = 1.6
    f = 58 * np.exp(-t(d) * 0.9) + 36
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * env(int(d * SR), 0.006, 0.45)
    x += 0.15 * lp(rng.standard_normal(len(x)), 400) * env(len(x), 0.002, 0.05)
    save("sub", x, -6)


def paper():
    """Feuille qui glisse sur le bureau."""
    d = 0.9
    n = int(d * SR)
    x = bp(rng.standard_normal(n), 700, 5000, 2)
    swell = np.sin(np.pi * np.clip(t(d) / 0.75, 0, 1)) ** 1.5
    flutter = 0.75 + 0.25 * lp(rng.standard_normal(n), 25, 2) / 0.05
    save("paper", x * swell * np.clip(flutter, 0.3, 1.3), -16)


def marker():
    """Feutre qui caviarde une ligne."""
    d = 1.0
    n = int(d * SR)
    x = bp(rng.standard_normal(n), 900, 4500, 2)
    squeak = np.sin(2 * np.pi * (1300 + 80 * np.sin(2 * np.pi * 3 * t(d))) * t(d)) * 0.08
    shape = np.minimum(1, t(d) / 0.04) * np.minimum(1, (d - t(d)) / 0.12)
    save("marker", (x + squeak) * shape, -18)


def door():
    """Porte qui se referme : souffle d'air, choc sourd du battant, clic du pêne."""
    d = 0.7
    n = int(d * SR)
    air = bp(rng.standard_normal(n), 200, 1200, 2) * np.minimum(1, t(d) / 0.12) * np.exp(-np.maximum(0, t(d) - 0.12) / 0.03)
    k = int(0.12 * SR)
    thump = np.zeros(n)
    th = np.sin(2 * np.pi * (85 - 25 * t(d)) * t(d)) * env(n, 0.002, 0.08)
    thump[k:] = th[: n - k]
    latch = np.zeros(n)
    lc = bp(rng.standard_normal(n), 2000, 6000) * env(n, 0.0003, 0.007)
    k2 = int(0.15 * SR)
    latch[k2:] = lc[: n - k2]
    save("door", air * 0.12 + thump + latch * 0.5, -8)


def clock():
    """Tic de minuteur : bois sec, très court."""
    d = 0.12
    n = int(d * SR)
    x = bp(rng.standard_normal(n), 1500, 5000) * env(n, 0.0002, 0.006)
    x += np.sin(2 * np.pi * 1150 * t(d)) * env(n, 0.0005, 0.02) * 0.4
    save("clock", x, -14)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn in (roomtone, phone_down, tick, pencil, button_click, zap, sub, paper, marker, door, clock):
        fn()
    print("sfx ->", sorted(os.listdir(OUT)))
