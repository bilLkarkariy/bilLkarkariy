"""Assemble des prises du playground en une voix continue qui respire.

Chaque morceau (fichier audio + paragraphes du texte qu'il contient) est
découpé par paragraphe grâce à Whisper ; on recolle en garantissant un blanc
minimum entre paragraphes, plus long quand on change d'idée ou de partie.
Rien n'est retouché à l'intérieur d'un paragraphe.

  python3 tools/assemble_takes.py   (configuration ci-dessous, vidéo 1)
"""
import difflib
import json
import os
import re
import subprocess
import sys

import numpy as np
import soundfile as sf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from takes_qa import heard_words, norm, TAG  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
PG = os.path.join(ROOT, ".cache/playground")
SR = 48000

GAP = {"relance": 0.45, "chute": 0.8, "paragraphe": 0.7, "idée": 1.2, "partie": 1.9}
PARTIES = ("Université de Virginie", "Je crois qu'on se trompe", "Un. Ton téléphone", "Revenons au bouton", "Prochaine vidéo")
# la phrase reprend la précédente pour l'appuyer : ce n'est pas une nouvelle idée, le blanc est court
# et imposé (on raccourcit le silence de la prise s'il est plus long)
RELANCES = ("Le plus étrange, c'est ça", "D'autres techniques.")
CHUTES = ("Ce mot, c'est khalwa",)  # la réponse à une attente : un temps, pas une rupture
IDEES = ("Avant de laisser", "Tu te dis peut-être", "Et le plus étrange", "Les auteurs ont une image", "Question.",
         "En deux mille dix",
         "L'ascenseur", "Mais ce problème", "Imagine une pièce", "Et les auteurs de l'étude", "Pourquoi quelqu'un",
         "Bagdad", "Attention, ce n'est pas", "Mais seul dans une pièce", "Le Coran", "La voie que je suis",
         "Je ne vais pas te demander", "Ce qui va probablement", "La dernière phrase", "Tu n'as pas un problème")
APRES_LONG = {"c'était quand ?": 2.0, "ça s'entraîne.": 2.0}  # silences voulus par le script


def decode(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def paragraph_times(path, paras, model):
    segs, _ = model.transcribe(path, language="fr", word_timestamps=True)
    hw = heard_words([{"w": w.word.strip(), "s": w.start, "e": w.end, "p": w.probability} for s in segs for w in s.words])
    ref = [(i, t) for i, p in enumerate(paras) for t in re.findall(r"[\w'’-]+", TAG.sub(" ", p)) if norm(t)]
    times = {}
    sm = difflib.SequenceMatcher(None, [norm(t) for _, t in ref], [norm(w["w"]) for w in hw], autojunk=False)
    for blk in sm.get_matching_blocks():
        for k in range(blk.size):
            pi = ref[blk.a + k][0]
            w = hw[blk.b + k]
            t0, t1 = times.get(pi, (w["s"], w["e"]))
            times[pi] = (min(t0, w["s"]), max(t1, w["e"]))
    missing = [i for i in range(len(paras)) if i not in times]
    if missing:
        raise SystemExit(f"{os.path.basename(path)} : paragraphes introuvables {missing}")
    return [times[i] for i in range(len(paras))]


def gap_after(p_text, next_text):
    """(blanc voulu, imposé ?) : imposé = on raccourcit aussi le silence s'il est plus long."""
    clean = TAG.sub("", p_text).strip()
    for end, g in APRES_LONG.items():
        if clean.endswith(end):
            return g, False
    nxt = TAG.sub("", next_text).strip()
    if nxt.startswith(RELANCES):
        return GAP["relance"], True
    if nxt.startswith(CHUTES):
        return GAP["chute"], True
    if nxt.startswith(PARTIES):
        return GAP["partie"], False
    if nxt.startswith(IDEES):
        return GAP["idée"], False
    return GAP["paragraphe"], False


def main():
    from faster_whisper import WhisperModel
    model = WhisperModel("small", device="cpu", compute_type="int8", cpu_threads=4)
    ref = open(os.path.join(PG, "ref_avant_ajouts.txt")).read().strip().split("\n\n")
    new4 = [p for p in open(os.path.join(ROOT, "script/v01_texte_playground_balises.txt")).read().strip().split("\n\n")
            if "Astaghfiroullah" in p][0]
    i_cut = next(i for i, p in enumerate(ref) if "on fait le dhikr" in p)
    i4 = next(i for i, p in enumerate(ref) if "Quatre. Pose ton attention" in p)
    # (fichier, paragraphes du texte qu'il contient, paragraphes à garder)
    pieces = [
        ("balises_1.mp3", ref[: i_cut + 1], None),
        ("balises_partie2.mp3", ref[i_cut + 1:], None),
        ("etape4.mp3", [new4], None),
    ]
    clips = []  # (texte, audio)
    for f, paras, _ in pieces:
        audio = decode(os.path.join(PG, f))
        tt = paragraph_times(os.path.join(PG, f), paras, model)
        for k, (p, (t0, t1)) in enumerate(zip(paras, tt)):
            prev_end = tt[k - 1][1] if k else 0.0
            next_start = tt[k + 1][0] if k + 1 < len(tt) else len(audio) / SR
            a = max(prev_end, t0 - min(0.3, (t0 - prev_end) / 2))
            b = min(next_start, t1 + min(0.8, (next_start - t1) / 2))
            clips.append([p, audio[int(a * SR):int(b * SR)], t0 - a, b - t1])
        print(f"{f}: {len(paras)} paragraphes", flush=True)
    # l'étape 4 régénérée remplace l'ancienne
    old = i4
    new = len(clips) - 1
    clips[old] = clips[new]
    clips.pop()
    # silence réellement présent en tête et en queue de chaque morceau (énergie, pas Whisper :
    # ses fins de mots sont parfois en avance de 0,2 s, ce qui collait les paragraphes)
    ref_db = np.percentile(np.concatenate([c[1] for c in clips]) ** 2, 99)
    thr = 10 * np.log10(ref_db + 1e-12) - 38
    hop = int(0.01 * SR)
    for c in clips:
        a = c[1]
        db = 10 * np.log10(np.mean(a[: len(a) // hop * hop].reshape(-1, hop) ** 2, axis=1) + 1e-12)
        loud = np.where(db > thr)[0]
        c[2] = loud[0] * 0.01 if len(loud) else 0.0  # silence de tête
        c[3] = (len(db) - 1 - loud[-1]) * 0.01 if len(loud) else 0.0  # silence de queue
    # blancs imposés : on retire l'excédent de silence, d'abord en queue du précédent, puis en tête
    for k in range(1, len(clips)):
        want, exact = gap_after(clips[k - 1][0], clips[k][0])
        prev, cur = clips[k - 1], clips[k]
        excess = prev[3] + cur[2] - want
        if exact and excess > 0:
            cut_tail = min(excess, max(0.0, prev[3] - want * 0.6))
            cut_head = min(excess - cut_tail, max(0.0, cur[2] - 0.05))
            if cut_tail > 0:
                prev[1] = prev[1][: len(prev[1]) - int(cut_tail * SR)]
                prev[3] -= cut_tail
            if cut_head > 0:
                cur[1] = cur[1][int(cut_head * SR):]
                cur[2] -= cut_head
    out, timeline, t = [], [], 0.0
    for k, (p, a, pre, post) in enumerate(clips):
        if k:
            want, _ = gap_after(clips[k - 1][0], p)
            have = clips[k - 1][3] + pre
            if want > have:
                out.append(np.zeros(int((want - have) * SR), np.float32))
                t += want - have
        fade = int(0.008 * SR)
        a = a.copy()
        a[:fade] *= np.linspace(0, 1, fade)
        a[-fade:] *= np.linspace(1, 0, fade)
        timeline.append({"i": k, "start": round(t + pre, 2), "texte": TAG.sub("", p).strip()[:60]})
        out.append(a)
        t += len(a) / SR
    y = np.concatenate([np.zeros(int(0.5 * SR), np.float32)] + out + [np.zeros(int(1.0 * SR), np.float32)])
    dst = os.path.join(ROOT, "public/vo/v01.wav")
    sf.write(dst, y, SR, subtype="PCM_24")
    json.dump(timeline, open(os.path.join(PG, "assemblage.json"), "w"), ensure_ascii=False, indent=1)
    # texte de référence de l'assemblage (pour l'alignement mot à mot du montage)
    seg = [{"id": f"p{k + 1}", "text": TAG.sub("", c[0]).strip(), "pause": 0} for k, c in enumerate(clips)]
    json.dump({"_doc": "Voix assemblée depuis le playground (tools/assemble_takes.py).", "lead": 0, "tail": 0, "segments": seg},
              open(os.path.join(ROOT, "script/v01_playground.json"), "w"), ensure_ascii=False, indent=1)
    print(f"-> {dst}  {len(y) / SR / 60:.2f} min, {len(clips)} paragraphes")


if __name__ == "__main__":
    main()
