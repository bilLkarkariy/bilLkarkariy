"""Sous-titres .srt depuis l'alignement mot à mot de la voix.

  python3 tools/srt.py src/data/v01.vo.json out/v01.fr.srt

Le texte affiché est celui du script (ponctuation, majuscules) ; les temps sont ceux des mots,
décalés de LEAD (24 images, src/cues.ts) pour tomber juste sur la vidéo.
Une ligne : 42 caractères au plus, 4,5 s au plus, coupée en fin de phrase ou sur un silence.
"""
import json
import re
import sys

LEAD = 24 / 30
MAX_CHARS, MAX_DUR, GAP = 42, 4.5, 0.45
# l'oral écrit en toutes lettres pour la voix ; à l'écran, les chiffres se lisent mieux
NOMBRES = [
    ("deux mille quatorze", "2014"), ("deux mille dix", "2010"), ("mille quatre-vingt-quinze", "1095"),
    ("cent quatre-vingt-dix", "190"), ("quarante-deux", "42"), ("dix-septième siècle", "XVIIᵉ siècle"),
    ("trois cent cinquante", "350"),
]


def tc(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def tokens(seg):
    """Les mots du texte (avec leur ponctuation) posés sur les temps des mots alignés."""
    text = re.sub(r"\[[^\]]*\]\s*", "", seg["text"])
    # la ponctuation isolée (« : », « « », « » », « — ») n'a pas de mot aligné : on la colle à son voisin
    toks = []
    pending = ""
    for t in text.split():
        if not re.search(r"\w", t):
            if t in ("«", "—", "–") or not toks:
                pending += t + " "
            else:
                toks[-1] += " " + t
        else:
            toks.append(pending + t)
            pending = ""
    words = seg["words"]
    if len(toks) == len(words):
        res = [(t, w["start"], w["end"]) for t, w in zip(toks, words)]
    else:  # nombre de mots différent (rare) : on répartit au prorata
        n = len(words)
        res = [(t, words[min(n - 1, i * n // len(toks))]["start"], words[min(n - 1, (i + 1) * n // len(toks) - 1)]["end"])
               for i, t in enumerate(toks)]
    # un nombre écrit en lettres devient un seul jeton en chiffres (il ne sera jamais coupé en deux)
    for a, b in NOMBRES:
        k = len(a.split())
        i = 0
        while i + k <= len(res):
            chunk = " ".join(x[0] for x in res[i:i + k])
            if chunk.lower().startswith(a):
                res[i:i + k] = [(b + chunk[len(a):], res[i][1], res[i + k - 1][2])]
            i += 1
    return res


def L(c):
    return len(" ".join(x[0] for x in c))


def split_long(c):
    """Coupe un morceau trop long en parts équilibrées (jamais un mot seul en fin de ligne)."""
    if L(c) <= MAX_CHARS and c[-1][2] - c[0][1] <= MAX_DUR or len(c) < 4:
        return [c]
    best = min(range(2, len(c) - 1), key=lambda i: abs(L(c[:i]) - L(c[i:])))
    return split_long(c[:best]) + split_long(c[best:])


def cues(vo):
    out = []
    for seg in vo["segments"]:
        # 1. propositions : coupées après la ponctuation ou sur un silence
        parts, cur = [], []
        for t in tokens(seg):
            if cur and t[1] - cur[-1][2] > GAP:
                parts.append(cur)
                cur = []
            cur.append(t)
            if re.search(r"[.?!…»:;,]$", t[0]):
                parts.append(cur)
                cur = []
        if cur:
            parts.append(cur)
        # 2. on regroupe les propositions courtes, on coupe les longues
        cur = []
        for p in parts:
            if cur and (L(cur + p) > MAX_CHARS or p[-1][2] - cur[0][1] > MAX_DUR or re.search(r"[.?!…»]$", cur[-1][0])):
                out += split_long(cur)
                cur = []
            cur = cur + p
        if cur:
            out += split_long(cur)
    # 3. un mot seul ne reste jamais sur son propre sous-titre : il rejoint la suite de sa phrase
    i = 0
    while i < len(out):
        if len(out[i]) == 1 and not re.search(r"[.?!…»]$", out[i][0][0]) and i + 1 < len(out):
            out[i:i + 2] = [out[i] + out[i + 1]]
        i += 1
    return out


def main(src, dst):
    vo = json.load(open(src))
    cs = cues(vo)
    lines = []
    for i, c in enumerate(cs):
        start = c[0][1] + LEAD
        end = c[-1][2] + LEAD + 0.25
        if i + 1 < len(cs):
            end = min(end, cs[i + 1][0][1] + LEAD - 0.04)
        txt = " ".join(x[0] for x in c)
        lines.append(f"{i + 1}\n{tc(start)} --> {tc(end)}\n{txt}\n")
    open(dst, "w").write("\n".join(lines))
    print(f"{dst} : {len(cs)} sous-titres")


if __name__ == "__main__":
    main(*sys.argv[1:3])
