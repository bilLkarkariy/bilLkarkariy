"""Voix temporaire (ElevenLabs, ou Piper hors ligne) puis alignement mot à mot (Whisper).

  python3 tools/vo.py tts   script/hook.json            -> public/vo/hook.wav
  python3 tools/vo.py align script/hook.json AUDIO.wav  -> src/data/hook.vo.json

L'alignement marche pareil sur la vraie prise de Billel : on ne dépend que du
texte du script, jamais de minutages écrits à la main.
"""
import difflib
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import unicodedata

import numpy as np
import soundfile as sf

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
VOICE = os.path.join(ROOT, ".cache/piper/fr_FR-tom-medium.onnx")
SR = 48000
COSTS = []  # coût annoncé par ElevenLabs pour chaque appel réellement envoyé (hors cache)


def env_key(name):
    if os.environ.get(name):
        return os.environ[name]
    path = os.path.join(ROOT, ".env")
    if os.path.exists(path):
        for line in open(path):
            k, _, v = line.strip().partition("=")
            if k == name:
                return v
    raise SystemExit(f"{name} manquant (studio/.env)")


def elevenlabs(text, cfg, prev_text, next_text, dst):
    """Un segment, avec ses voisins en contexte pour garder une prosodie continue.
    Mis en cache : relancer le rendu ne recoûte pas de caractères."""
    import urllib.error
    import urllib.request
    body = {
        "text": text,
        "model_id": cfg.get("model", "eleven_multilingual_v2"),
        "voice_settings": cfg.get("settings", {}),
        "previous_text": prev_text,
        "next_text": next_text,
    }
    key = hashlib.sha1(json.dumps([cfg.get("voice_id"), body], sort_keys=True).encode()).hexdigest()[:16]
    cache = os.path.join(ROOT, ".cache/tts", key + ".mp3")
    if not os.path.exists(cache):
        os.makedirs(os.path.dirname(cache), exist_ok=True)
        req = urllib.request.Request(
            f"https://api.elevenlabs.io/v1/text-to-speech/{cfg['voice_id']}?output_format=mp3_44100_128",
            data=json.dumps(body).encode(),
            headers={"xi-api-key": env_key("ELEVENLABS_API_KEY"), "Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                open(cache, "wb").write(r.read())
                COSTS.append(int(r.headers.get("character-cost") or 0))
        except urllib.error.HTTPError as e:
            if e.code != 400:
                raise
            for k in ("previous_text", "next_text"):  # modèles sans « request stitching »
                body.pop(k)
            req.data = json.dumps(body).encode()
            with urllib.request.urlopen(req, timeout=120) as r:
                open(cache, "wb").write(r.read())
                COSTS.append(int(r.headers.get("character-cost") or 0))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", cache, "-ar", str(SR), "-ac", "1", dst], check=True)


def norm(w):
    w = unicodedata.normalize("NFD", w.lower())
    w = "".join(c for c in w if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", w)


# Écriture arabe (ourdou) : un mot = une suite de lettres, signes et chiffres (comme tools/vo_estime.py) ;
# pour comparer, on retire les signes et on ramène les variantes arabes de Whisper aux lettres ourdoues.
ARABIC_SCRIPT = {"ur", "ar"}
FOLD_UR = str.maketrans({"ي": "ی", "ى": "ی", "ك": "ک", "ه": "ہ", "ۀ": "ۂ"})


def norm_arabic(w, lang="ur"):
    w = unicodedata.normalize("NFD", w)
    w = "".join(c for c in w if unicodedata.category(c)[0] in "LN")
    return w.translate(FOLD_UR) if lang == "ur" else w


TAG = re.compile(r"\[[^\]]*\]")  # balises d'intonation ElevenLabs : [pause], [whispers]…


def spoken(text):
    return re.sub(r"\s+", " ", TAG.sub("", text)).strip()


def tokens(text, lang=None):
    if lang in ARABIC_SCRIPT:
        out, cur = [], ""
        for c in spoken(text) + " ":
            if unicodedata.category(c)[0] in "LMN":
                cur += c
            elif cur:
                out.append(cur)
                cur = ""
        return [t for t in out if norm_arabic(t, lang)]
    return [t for t in re.findall(r"[\w'’-]+", spoken(text)) if norm(t)]


def expand_numbers(words, language="fr"):
    if language in ARABIC_SCRIPT:  # num2words ne connaît pas l'ourdou : un nombre entendu en chiffres reste non apparié
        return list(words)
    from num2words import num2words
    out = []
    for w in words:
        digits = re.sub(r"[^\d]", "", w["word"])
        if digits and digits == re.sub(r"[%.,\s]", "", w["word"].strip()):
            parts = num2words(int(digits), lang=language).replace("-", " ").split()
            n = len(parts)
            for i, p in enumerate(parts):  # répartit la durée du nombre sur ses mots
                a = w["start"] + (w["end"] - w["start"]) * i / n
                b = w["start"] + (w["end"] - w["start"]) * (i + 1) / n
                out.append({"word": p, "start": a, "end": b})
        else:
            out.append(w)
    return out


def snap_to_energy(audio_path, times, thr_db=-38.0, hop=0.01):
    """Whisper colle souvent le silence au mot suivant : on recale chaque début
    (et chaque fin) de mot sur l'attaque réelle du signal."""
    a, sr = sf.read(audio_path)
    if a.ndim > 1:
        a = a.mean(axis=1)
    n = int(hop * sr)
    rms = np.sqrt(np.mean(a[: len(a) // n * n].reshape(-1, n) ** 2, axis=1) + 1e-12)
    db = 20 * np.log10(rms / (np.max(rms) + 1e-12))
    loud = db > thr_db
    min_gap = int(0.12 / hop)  # un vrai silence dure au moins 120 ms

    def silences(i0, i1):
        runs, k = [], i0
        while k < i1:
            if not loud[k]:
                j = k
                while j < i1 and not loud[j]:
                    j += 1
                if j - k >= min_gap:
                    runs.append((k, j))
                k = j
            else:
                k += 1
        return runs

    out = []
    for s0, e0 in times:
        i0, i1 = int(s0 / hop), min(len(loud), max(int(s0 / hop) + 1, int(round(e0 / hop))))
        # blocs de parole séparés par de vrais silences ; le mot = le plus long bloc
        # (la fenêtre de Whisper déborde souvent sur la pause d'avant ou d'après)
        cuts = [i0] + [k for r in silences(i0, i1) for k in r] + [i1]
        blocks = [(cuts[j], cuts[j + 1]) for j in range(0, len(cuts) - 1, 2)]
        best, best_n = None, 0
        for b0, b1 in blocks:
            on = np.where(loud[b0:b1])[0]
            if len(on) > best_n:
                best, best_n = (b0 + on[0], b0 + on[-1] + 1), len(on)
        if best is None:
            out.append((s0, e0))
            continue
        out.append((best[0] * hop, max(best[1] * hop, best[0] * hop + 0.05)))
    return out


def isolate(path):
    """Isolateur vocal ElevenLabs : retire le bruit que le clone a appris de ses
    échantillons (souffle, grondement). Puis coupe-bas 70 Hz. Mis en cache."""
    key = hashlib.sha1(open(path, "rb").read()).hexdigest()[:16]
    cache = os.path.join(ROOT, ".cache/isolated", key + ".audio")
    if not os.path.exists(cache):
        os.makedirs(os.path.dirname(cache), exist_ok=True)
        r = subprocess.run(["curl", "-sS", "-f", "-o", cache, "-D", cache + ".headers", "-X", "POST",
                            "https://api.elevenlabs.io/v1/audio-isolation",
                            "-H", "xi-api-key: " + env_key("ELEVENLABS_API_KEY"),
                            "-F", f"audio=@{path};type=audio/wav"], capture_output=True, text=True)
        if r.returncode:
            raise SystemExit("isolation ElevenLabs : " + r.stderr)
    tmp = path + ".tmp.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", cache, "-af", "highpass=f=70",
                    "-ar", str(SR), "-ac", "1", tmp], check=True)
    a, _ = sf.read(tmp)
    os.remove(tmp)
    sf.write(path, a * 0.5 / np.max(np.abs(a)), SR)
    hdr = cache + ".headers"
    cost = [l.split(":", 1)[1].strip() for l in open(hdr) if l.lower().startswith(("character-cost", "x-character", "credit"))] if os.path.exists(hdr) else []
    print("isolation -> ok", f"(coût annoncé : {', '.join(cost)})" if cost else "")


def tts(script_path):
    sc = json.load(open(script_path))
    cfg = sc.get("tts", {})
    engine = cfg.get("engine", "piper")
    if engine == "elevenlabs" and not cfg.get("voice_id"):
        raise SystemExit("Voix non choisie : génération refusée avant tout accès aux identifiants.")
    chunks = [np.zeros(int(sc["lead"] * SR))]
    with tempfile.TemporaryDirectory() as tmp:
        for seg in sc["segments"]:
            rs = os.path.join(tmp, seg["id"] + "_48k.wav")
            if engine == "elevenlabs":
                texts = [x["text"] for x in sc["segments"]]
                i = texts.index(seg["text"])
                elevenlabs(seg["text"], cfg, " ".join(texts[max(0, i - 2):i]), " ".join(texts[i + 1:i + 2]), rs)
            else:
                raw = os.path.join(tmp, seg["id"] + ".wav")
                subprocess.run(["python3", "-m", "piper", "-m", VOICE, "-f", raw, "--length-scale", "0.97"],
                               input=seg["text"].encode(), check=True, capture_output=True)
                subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-ar", str(SR), "-ac", "1", rs], check=True)
            a, _ = sf.read(rs)
            loud = np.where(np.abs(a) > 0.01)[0]
            a = a[max(0, loud[0] - 480): loud[-1] + 2400]
            chunks += [a, np.zeros(int(seg["pause"] * SR))]
    chunks.append(np.zeros(int(sc["tail"] * SR)))
    # nivellement doux : chaque segment fait la moitié du chemin vers le niveau médian
    # (une phrase [softly] reste douce, mais ne disparaît pas sous l'ambiance)
    rms = {i: np.sqrt(np.mean(c ** 2)) for i, c in enumerate(chunks) if len(c) and np.any(c)}
    ref = np.median(list(rms.values()))
    for i, r in rms.items():
        chunks[i] = chunks[i] * (ref / r) ** 0.5
    audio = np.concatenate(chunks)
    audio *= 0.5 / np.max(np.abs(audio))
    out = os.path.join(ROOT, "public/vo", os.path.basename(script_path).replace(".json", ".wav"))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    sf.write(out, audio, SR)
    if cfg.get("post") == "isolate" and not os.environ.get("NO_ISOLATE"):
        isolate(out)
    print("voix ->", out, f"{len(audio) / SR:.2f}s")
    if COSTS:
        print(f"TTS : {len(COSTS)} appels envoyés, coût annoncé total {sum(COSTS)} crédits")
    return out


def align(script_path, audio_path):
    sc = json.load(open(script_path))
    if sc.get("language") in ("en", "ur"):
        from vo_alignment_en import align_recording
        return align_recording(script_path, audio_path)
    from faster_whisper import WhisperModel
    model = WhisperModel("small", device="cpu", compute_type="int8")
    # pas d'initial_prompt : avec le script complet en indice, Whisper hallucine et saute des phrases
    segs, _ = model.transcribe(audio_path, language=sc.get("language", "fr"), word_timestamps=True)
    heard = [{"word": w.word.strip(), "start": w.start, "end": w.end} for s in segs for w in s.words]
    # Whisper coupe « t'endors » en « t » + « 'endors », « occupe-toi » en « occupe » + « -toi » : on recolle
    merged = []
    for w in heard:
        if merged and w["word"][:1] in "'’-" and len(w["word"]) > 1:
            merged[-1] = {"word": merged[-1]["word"] + w["word"], "start": merged[-1]["start"], "end": w["end"]}
        else:
            merged.append(w)
    heard = expand_numbers(merged, sc.get("language", "fr"))

    lang = sc.get("language", "fr")
    nrm = (lambda t: norm_arabic(t, lang)) if lang in ARABIC_SCRIPT else norm
    script = [(seg["id"], t) for seg in sc["segments"] for t in tokens(seg["text"], lang)]
    a = [nrm(t) for _, t in script]
    b = [nrm(w["word"]) for w in heard]
    times = [None] * len(script)
    for blk in difflib.SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks():
        for k in range(blk.size):
            h = heard[blk.b + k]
            times[blk.a + k] = (h["start"], h["end"])
    # mots non reconnus : interpolés entre voisins
    for i, t in enumerate(times):
        if t is None:
            prev = next((times[j][1] for j in range(i - 1, -1, -1) if times[j]), 0.0)
            nxt = next((times[j][0] for j in range(i + 1, len(times)) if times[j]), prev)
            times[i] = (prev, nxt)
    times = snap_to_energy(audio_path, times)
    out = {"audio": os.path.relpath(audio_path, os.path.join(ROOT, "public")), "segments": []}
    for seg in sc["segments"]:
        words = [{"w": t, "start": round(times[i][0], 3), "end": round(times[i][1], 3)}
                 for i, (sid, t) in enumerate(script) if sid == seg["id"]]
        out["segments"].append({"id": seg["id"], "text": spoken(seg["text"]),
                                "start": words[0]["start"], "end": words[-1]["end"], "words": words})
    info = sf.info(audio_path)
    out["duration"] = round(info.frames / info.samplerate, 3)
    if lang != "fr":  # langue (sous-titres, chiffres) et plateau muet du verset posé à l'assemblage, s'il existe
        out["language"] = lang
        manifest = os.path.splitext(audio_path)[0] + ".assembly.json"
        if os.path.exists(manifest):
            out["silences"] = json.load(open(manifest)).get("inserts", [])
    dst = os.path.join(ROOT, "src/data", os.path.basename(script_path).replace(".json", ".vo.json"))
    json.dump(out, open(dst, "w"), ensure_ascii=False, indent=1)
    unmatched = sum(1 for i in range(len(script)) if times[i][0] == times[i][1])
    print("alignement ->", dst, f"({len(script)} mots, {unmatched} interpolés)")


if __name__ == "__main__":
    cmd, path = sys.argv[1], sys.argv[2]
    if cmd == "tts":
        wav = tts(path)
        if not os.environ.get("NO_ALIGN"):
            align(path, wav)
    elif cmd == "align":
        align(path, sys.argv[3])
