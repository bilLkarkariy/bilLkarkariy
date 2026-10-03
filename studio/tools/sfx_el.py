"""Bruitages et musique générés par ElevenLabs (mis en cache : relancer ne recoûte rien).

  python3 tools/sfx_el.py credits                      crédits restants
  python3 tools/sfx_el.py sfx script/sfx_v01.json      -> public/sfx/el/<nom>.wav (48 kHz mono, début calé)
  python3 tools/sfx_el.py music NOM SECONDES "prompt"  -> public/music/<nom>.mp3

Le coût réel de chaque appel (en-tête character-cost) est affiché.
"""
import hashlib
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request

import numpy as np
import soundfile as sf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vo import env_key  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
API = "https://api.elevenlabs.io/v1"
SR = 48000


def call(path, body=None, cache=None):
    """GET (body None) ou POST JSON ; renvoie (octets, coût annoncé)."""
    if cache and os.path.exists(cache):
        return open(cache, "rb").read(), 0
    req = urllib.request.Request(
        API + path,
        data=None if body is None else json.dumps(body).encode(),
        headers={"xi-api-key": env_key("ELEVENLABS_API_KEY"), "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            data = r.read()
            cost = int(r.headers.get("character-cost") or 0)
    except urllib.error.HTTPError as e:
        raise SystemExit(f"{path} : HTTP {e.code} {e.read()[:400].decode(errors='replace')}")
    if cache:
        os.makedirs(os.path.dirname(cache), exist_ok=True)
        open(cache, "wb").write(data)
    return data, cost


def credits():
    s = json.loads(call("/user/subscription")[0])
    print(f"{s['tier']} : {s['character_count']:,} / {s['character_limit']:,} utilisés, "
          f"reste {s['character_limit'] - s['character_count']:,}")


def key(*parts):
    return hashlib.sha1(json.dumps(parts, sort_keys=True).encode()).hexdigest()[:16]


def sfx(spec_path):
    specs = json.load(open(spec_path))
    out = os.path.join(ROOT, "public/sfx/el")
    os.makedirs(out, exist_ok=True)
    total = 0
    # "variants": n -> n prises du même son (<nom>_1 … <nom>_n) : jamais deux fois le même à l'oreille
    jobs = [(s, k) for s in specs for k in (range(1, s["variants"] + 1) if s.get("variants") else [0])]
    for s, k in jobs:
        body = {"text": s["prompt"], "duration_seconds": s["duration"], "prompt_influence": s.get("influence", 0.6),
                "model_id": "eleven_text_to_sound_v2"}
        cache = os.path.join(ROOT, ".cache/sfx_el", key(body, k) + ".mp3" if k else key(body) + ".mp3")
        name = f"{s['name']}_{k}" if k else s["name"]
        _, cost = call("/sound-generation?output_format=mp3_44100_192", body, cache)
        total += cost
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", cache, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                             capture_output=True, check=True).stdout
        x = np.frombuffer(raw, np.float32).copy()
        # le son doit partir à l'image où on le pose : on retire le silence de tête (garde 5 ms)
        hop = int(0.005 * SR)
        db = 10 * np.log10(np.mean(x[: len(x) // hop * hop].reshape(-1, hop) ** 2, axis=1) + 1e-12)
        loud = np.where(db > db.max() - 30)[0]
        x = x[max(0, loud[0] - 1) * hop:] if len(loud) else x
        x = x / (np.abs(x).max() + 1e-9) * 10 ** (-3 / 20)
        f = min(len(x), int(0.02 * SR))
        x[-f:] *= np.linspace(1, 0, f)
        sf.write(os.path.join(out, name + ".wav"), x, SR, subtype="PCM_24")
        print(f"{name:14s} {len(x) / SR:4.2f} s  coût {cost}")
    print(f"total : {total} crédits")


def music(name, seconds, prompt):
    body = {"prompt": prompt, "music_length_ms": int(float(seconds) * 1000), "model_id": "music_v1"}
    out = os.path.join(ROOT, "public/music", name + ".mp3")
    cache = os.path.join(ROOT, ".cache/music_el", key(body) + ".mp3")
    _, cost = call("/music?output_format=mp3_44100_192", body, cache)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    subprocess.run(["cp", cache, out], check=True)
    print(f"-> {out}  coût {cost}")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "credits":
        credits()
    elif cmd == "sfx":
        sfx(sys.argv[2])
    elif cmd == "music":
        music(sys.argv[2], sys.argv[3], sys.argv[4])
