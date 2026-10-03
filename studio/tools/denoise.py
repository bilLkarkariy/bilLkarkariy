"""Débruitage local et gratuit, sans changer la voix.

  python3 tools/denoise.py ENTRÉE SORTIE.wav [--lim 12]

1. coupe-bas 70 Hz (grondement ; la voix de Billel commence vers 100-145 Hz)
2. DeepFilterNet 3 (réseau spécialisé parole), atténuation plafonnée à --lim dB :
   il baisse le bruit au plus de --lim dB, il ne « lave » pas la voix
3. rapport : bruit retiré dans les passages calmes, et écart de timbre de la
   voix (spectre moyen des passages parlés, avant/après, par bande).
"""
import argparse
import subprocess

import numpy as np
import soundfile as sf
import torch

SR = 48000


def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-af", "highpass=f=70",
                          "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def frames(x, hop=960):
    fr = x[: len(x) // hop * hop].reshape(-1, hop)
    return fr, 20 * np.log10(np.sqrt(np.mean(fr ** 2, axis=1)) + 1e-9)


def ltas(fr, mask):
    w = np.hanning(fr.shape[1])
    return np.mean(np.abs(np.fft.rfft(fr[mask] * w, axis=1)) ** 2, axis=0)


def report(before, after):
    fb, db = frames(before)
    fa, _ = frames(after)
    speech = db > np.percentile(db, 90) - 12
    calm = (db < np.percentile(db, 90) - 30) & (db > -95)
    fq = np.fft.rfftfreq(fb.shape[1], 1 / SR)
    sb, sa = ltas(fb, speech), ltas(fa, speech)
    cb, ca = ltas(fb, calm), ltas(fa, calm)
    print("bande        | timbre de la voix (après - avant) | bruit au calme (après - avant)")
    for lo, hi in ((80, 200), (200, 500), (500, 1500), (1500, 4000), (4000, 8000), (8000, 16000)):
        m = (fq >= lo) & (fq < hi)
        dv = 10 * np.log10(sa[m].sum() / sb[m].sum())
        dn = 10 * np.log10(ca[m].sum() / cb[m].sum())
        print(f"{lo:>5}-{hi:<5} Hz | {dv:+6.2f} dB{'':24s}| {dn:+6.1f} dB")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--lim", type=float, default=12.0)
    a = ap.parse_args()
    import os
    from df.enhance import enhance, init_df
    # le téléchargement auto (github.com/.../raw) est refusé par le proxy : modèle récupéré
    # depuis raw.githubusercontent.com dans ~/.cache/DeepFilterNet (voir tools/setup.sh)
    local = os.path.expanduser("~/.cache/DeepFilterNet/DeepFilterNet3")
    model, state, _ = init_df(model_base_dir=local if os.path.isdir(local) else None)
    x = load(a.src)
    y = enhance(model, state, torch.from_numpy(x)[None], atten_lim_db=a.lim)[0].numpy()
    n = min(len(x), len(y))
    x, y = x[:n], y[:n]
    sf.write(a.dst, y, SR, subtype="PCM_24")
    print(f"-> {a.dst}  ({n / SR / 60:.1f} min, atténuation max {a.lim:.0f} dB)")
    report(x, y)


if __name__ == "__main__":
    main()
