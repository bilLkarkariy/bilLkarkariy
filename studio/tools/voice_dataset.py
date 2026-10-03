"""Prépare des échantillons propres pour cloner la voix de Billel.

Chaque extrait est défini par une phrase de début et une phrase de fin (texte
réellement prononcé) : on retrouve leurs mots avec Whisper, on coupe sur les
silences, on raccourcit les longues pauses, on retire le grondement et on
harmonise le volume. Les reprises et apartés restent dehors.

  python3 tools/voice_dataset.py   -> .cache/voice_clean/*.wav + rapport
"""
import glob
import json
import os
import re
import subprocess
import unicodedata

import numpy as np
import soundfile as sf

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SRC = os.path.join(ROOT, ".cache/voice_src")
OUT = os.path.join(ROOT, ".cache/voice_clean")
SR = 48000

# (fichier, région approx. en s, [(début, fin), ...]) : plusieurs morceaux = on saute ce qu'il y a entre
CLIPS = [
    ("03", (79.0, 173.0), [("Le jaune par exemple", "fabrique le jaune"),
                           ("Donc le jaune que tu vois", "capables de les mesurer")]),
    ("04", (105.0, 140.0), [("Le réel c'est ce qui est solide", "jamais formulé")]),
    ("02", (198.0, 233.0), [("il essaie de deviner sous quelle lumière", "Donc il corrige")]),
    ("01", (295.0, 316.0), [("je m'appelle", "d'éveil")]),
    ("03", (225.0, 250.0), [("Mais il est troublant", "réellement")]),
    ("01", (0.0, 40.0), [("La lumière n'est pas", "histoire d'internet")]),
]


def norm(w):
    w = unicodedata.normalize("NFD", w.lower())
    return re.sub(r"[^a-z0-9]", "", "".join(c for c in w if unicodedata.category(c) != "Mn"))


def find(words, phrase, after=0.0, last=False):
    target = [norm(t) for t in phrase.split()]
    seq = [norm(w["w"]) for w in words]
    import difflib
    same = lambda u, v: u == v or difflib.SequenceMatcher(None, u, v).ratio() >= 0.75  # essaie / essaye
    hits = [i for i in range(len(seq) - len(target) + 1)
            if all(same(seq[i + k], target[k]) for k in range(len(target))) and words[i]["start"] >= after]
    if not hits:
        raise SystemExit(f"introuvable : « {phrase} »")
    i = hits[-1] if last else hits[0]
    return words[i]["start"], words[i + len(target) - 1]["end"]


def decode(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).astype(np.float64)


def compress_silences(x, max_gap=0.5, keep=0.38, thr_db=-48):
    hop = int(0.01 * SR)
    fr = x[: len(x) // hop * hop].reshape(-1, hop)
    db = 20 * np.log10(np.sqrt(np.mean(fr ** 2, axis=1)) + 1e-9)
    quiet = db < max(thr_db, np.max(db) - 42)
    out, k = [], 0
    while k < len(quiet):
        if quiet[k]:
            j = k
            while j < len(quiet) and quiet[j]:
                j += 1
            n = j - k
            if n * 0.01 > max_gap:  # on garde le début et la fin du silence, on retire le milieu
                h = int(keep / 2 / 0.01)
                out.append(x[k * hop:(k + h) * hop])
                out.append(x[(j - h) * hop:j * hop])
            else:
                out.append(x[k * hop:j * hop])
            k = j
        else:
            j = k
            while j < len(quiet) and not quiet[j]:
                j += 1
            out.append(x[k * hop:j * hop])
            k = j
    out.append(x[len(quiet) * hop:])
    return np.concatenate(out)


def main():
    from faster_whisper import WhisperModel
    model = WhisperModel("small", device="cpu", compute_type="int8", cpu_threads=4)
    os.makedirs(OUT, exist_ok=True)
    for f in glob.glob(os.path.join(OUT, "*.wav")):
        os.remove(f)
    report = []
    for n, (fid, (r0, r1), parts) in enumerate(CLIPS, 1):
        path = glob.glob(os.path.join(SRC, f"{fid}_*.mp3"))[0]
        segs, _ = model.transcribe(path, language="fr", word_timestamps=True, clip_timestamps=[r0, r1])
        words = []
        for w in (w for s in segs for w in s.words):  # recolle « c » + « 'est », « occupe » + « -toi »
            tok = w.word.strip()
            if words and tok[:1] in "'’-" and len(tok) > 1:
                words[-1] = {"w": words[-1]["w"] + tok, "start": words[-1]["start"], "end": w.end}
            else:
                words.append({"w": tok, "start": w.start, "end": w.end})
        audio = decode(path)
        pieces, t = [], r0
        for a, b in parts:
            s0, _ = find(words, a, after=t, last=a.lower().startswith("il essaie"))
            _, e1 = find(words, b, after=s0)
            t = e1
            seg = audio[int(max(0, s0 - 0.12) * SR):int((e1 + 0.28) * SR)]
            fade = int(0.01 * SR)
            seg[:fade] *= np.linspace(0, 1, fade)
            seg[-fade:] *= np.linspace(1, 0, fade)
            pieces += [seg, np.zeros(int(0.4 * SR))]
        x = compress_silences(np.concatenate(pieces[:-1]))
        tmp = os.path.join(OUT, f"_tmp{n}.wav")
        dst = os.path.join(OUT, f"billel_{n:02d}.wav")
        sf.write(tmp, x.astype(np.float32), SR)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-af",
                        "highpass=f=70,loudnorm=I=-20:TP=-3:LRA=9", "-ar", str(SR), "-c:a", "pcm_s16le", dst], check=True)
        os.remove(tmp)
        y, _ = sf.read(dst)
        check, _ = model.transcribe(dst, language="fr")
        text = " ".join(s.text.strip() for s in check)
        report.append({"fichier": os.path.basename(dst), "source": fid, "durée": round(len(y) / SR, 1), "texte": text})
        print(f"{os.path.basename(dst)}  {len(y) / SR:5.1f}s  | {text}", flush=True)
    total = sum(r["durée"] for r in report)
    print(f"total {total / 60:.2f} min")
    json.dump(report, open(os.path.join(OUT, "rapport.json"), "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
