"""Contrôle qualité de prises de voix (playground ElevenLabs ou vraie voix).

Compare chaque prise au texte, paragraphe par paragraphe : mots manqués,
ajoutés (balise prononcée ?), remplacés, et mots douteux (faible confiance).
Une « erreur » présente dans toutes les prises au même endroit vient
probablement de Whisper (noms propres…) : elle est marquée « à l'oreille ».

  python3 tools/takes_qa.py TEXTE.txt .cache/playground/transcriptions.json
"""
import difflib
import json
import re
import sys
import unicodedata
from collections import defaultdict

TAG = re.compile(r"\[[^\]]*\]")


def norm(w):
    w = unicodedata.normalize("NFD", w.lower())
    return re.sub(r"[^a-z0-9]", "", "".join(c for c in w if unicodedata.category(c) != "Mn"))


def ref_words(text):
    out = []
    for i, p in enumerate(text.strip().split("\n\n")):
        for t in re.findall(r"[\w'’-]+", TAG.sub(" ", p)):
            if norm(t):
                out.append((i, t))
    return out


def heard_words(raw):
    from num2words import num2words
    merged = []
    for w in raw:
        if merged and w["w"][:1] in "'’-" and len(w["w"]) > 1:
            merged[-1] = {**merged[-1], "w": merged[-1]["w"] + w["w"], "e": w["e"], "p": min(merged[-1]["p"], w["p"])}
        else:
            merged.append(dict(w))
    out = []
    for w in merged:
        digits = re.sub(r"\D", "", w["w"])
        if digits and digits == re.sub(r"[%.,\s]", "", w["w"]):
            for part in num2words(int(digits), lang="fr").replace("-", " ").split():
                out.append({**w, "w": part})
        else:
            out.extend({**w, "w": t} for t in re.findall(r"[\w'’-]+", w["w"]) if norm(t))
    return out


def qa(text, words):
    ref = ref_words(text)
    hw = heard_words(words)
    a = [norm(t) for _, t in ref]
    b = [norm(w["w"]) for w in hw]
    per = defaultdict(lambda: {"n": 0, "ok": 0, "issues": [], "t0": None, "t1": None})
    for i, (pi, _) in enumerate(ref):
        per[pi]["n"] += 1
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        pi = ref[min(i1, len(ref) - 1)][0]
        if op == "equal":
            for k in range(i2 - i1):
                p = per[ref[i1 + k][0]]
                p["ok"] += 1
                w = hw[j1 + k]
                p["t0"] = w["s"] if p["t0"] is None else p["t0"]
                p["t1"] = w["e"]
                if w["p"] < 0.35:
                    p["issues"].append(("douteux", ref[i1 + k][1], w["w"]))
        elif op == "replace":
            per[pi]["issues"].append(("remplacé", " ".join(t for _, t in ref[i1:i2]), " ".join(w["w"] for w in hw[j1:j2])))
        elif op == "delete":
            per[pi]["issues"].append(("manquant", " ".join(t for _, t in ref[i1:i2]), ""))
        elif op == "insert":
            per[pi]["issues"].append(("ajouté", "", " ".join(w["w"] for w in hw[j1:j2])))
    return per


def main():
    text = open(sys.argv[1]).read()
    takes = json.load(open(sys.argv[2]))
    res = {k: qa(text, v) for k, v in takes.items()}
    paras = text.strip().split("\n\n")
    # signatures d'erreurs communes à toutes les prises -> Whisper, pas la voix
    sig = defaultdict(set)
    for k, per in res.items():
        for pi, p in per.items():
            for kind, r, h in p["issues"]:
                sig[(pi, kind, norm(r))].add(k)
    common = {s for s, ks in sig.items() if len(ks) == len(res)}

    print("prise            | justesse | paragraphes parfaits | problèmes propres à la prise")
    for k, per in res.items():
        n = sum(p["n"] for p in per.values())
        ok = sum(p["ok"] for p in per.values())
        own = [(pi, i) for pi, p in per.items() for i in p["issues"] if (pi, i[0], norm(i[1])) not in common]
        perfect = sum(1 for p in per.values() if not p["issues"])
        print(f"{k:16s} | {100 * ok / n:6.1f} % | {perfect:3d}/{len(paras)} | {len(own)}")
    print("\nà vérifier à l'oreille (même « erreur » dans toutes les prises : sûrement Whisper sur un nom) :")
    for pi, kind, r in sorted(common):
        if r:
            print(f"  §{pi + 1} {kind} « {r} »")
    for k, per in res.items():
        print(f"\n== {k} : problèmes propres à cette prise")
        for pi in sorted(per):
            for kind, r, h in per[pi]["issues"]:
                if (pi, kind, norm(r)) in common:
                    continue
                print(f"  §{pi + 1:<3d} {kind:9s} texte « {r} »  entendu « {h} »")
    json.dump({k: {pi: {"ok": p["ok"], "n": p["n"], "t0": p["t0"], "t1": p["t1"], "issues": p["issues"]} for pi, p in per.items()}
               for k, per in res.items()}, open(sys.argv[2].replace(".json", "_qa.json"), "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
