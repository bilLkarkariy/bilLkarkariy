"""Vraies pages PDF (articles, communiqués) au même format que tools/capture.py.

Le PDF est vectoriel : on rend la zone voulue directement à la taille d'affichage ×2,5,
le texte reste parfaitement net. Les passages à surligner sont trouvés dans le texte
du PDF (un rectangle par ligne). Un passage coupé par un trait d'union en fin de ligne
s'écrit comme une liste de morceaux : ["ple were less happy … wan", "dering than …"].

  python3 tools/pdfcap.py script/captures_pdf_v01.json [id ...]
  -> public/captures/<id>.png + src/data/captures/<id>.json
"""
import json
import os
import sys
import urllib.request

import pymupdf

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "public/captures")
META = os.path.join(ROOT, "src/data/captures")
CACHE = os.path.join(ROOT, ".cache/docs")
DPR = 2.5


def fetch(url):
    path = os.path.join(CACHE, os.path.basename(url.split("?")[0]).replace("%20", "_"))
    if not os.path.exists(path):
        os.makedirs(CACHE, exist_ok=True)
        urllib.request.urlretrieve(url, path)
    return path


def find(page, clip, phrase):
    """Rectangles (un par ligne) d'un passage, mot à mot et sensible à la casse ;
    un mot coupé en fin de ligne (« peo- » + « ple ») compte pour un seul mot."""
    # ordre de lecture (bloc, ligne, mot) : un tri par position mélangerait les colonnes
    words = sorted((w for w in page.get_text("words")
                    if clip.contains(pymupdf.Point((w[0] + w[2]) / 2, (w[1] + w[3]) / 2))), key=lambda w: (w[5], w[6], w[7]))
    toks = []  # (texte, [boîtes])
    i = 0
    while i < len(words):
        w = words[i]
        if w[4].endswith(("-", "‐")) and i + 1 < len(words) and (words[i + 1][5], words[i + 1][6]) != (w[5], w[6]):
            toks.append((w[4][:-1] + words[i + 1][4], [w, words[i + 1]]))
            i += 2
        else:
            toks.append((w[4], [w]))
            i += 1
    bare = lambda t: t.strip(",.;:()[]“”\"'?!")  # ponctuation collée au mot : « University, », « (“How »
    want = [bare(t) for t in phrase.split()]
    for k in range(len(toks) - len(want) + 1):
        if all(bare(toks[k + j][0]) == want[j] for j in range(len(want))):
            boxes = [b for t in toks[k:k + len(want)] for b in t[1]]
            lines = {}
            for b in boxes:
                lines.setdefault((b[5], b[6]), []).append(b)
            return [pymupdf.Rect(min(b[0] for b in bs), min(b[1] for b in bs), max(b[2] for b in bs), max(b[3] for b in bs))
                    for bs in lines.values()]
    return []


def main():
    jobs = json.load(open(sys.argv[1]))
    only = set(sys.argv[2:])
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(META, exist_ok=True)
    for job in jobs:
        if only and job["id"] not in only:
            continue
        page = pymupdf.open(fetch(job["pdf"]))[job.get("page", 0)]
        clip = pymupdf.Rect(job["clip"])
        css_w = job.get("css_w", 860)  # largeur de référence en px CSS (comme une page web de 860 px)
        s = css_w / clip.width
        hl = []
        for h in job.get("highlights", []):
            if isinstance(h, dict):  # zone dessinée à la main (texte en image : figures)
                rects, label = [pymupdf.Rect(h["rect"])], h["text"]
            else:
                label = h
                rects = find(page, clip, h)
                if not rects:
                    raise SystemExit(f"{job['id']} : passage introuvable dans la zone : {h}")
            rects.sort(key=lambda r: (round(r.y0), r.x0))
            hl.append({"text": label, "rects": [
                {"x": round((r.x0 - clip.x0) * s, 1), "y": round((r.y0 - clip.y0) * s, 1),
                 "w": round(r.width * s, 1), "h": round(r.height * s, 1)} for r in rects]})
        pix = page.get_pixmap(matrix=pymupdf.Matrix(s * DPR, s * DPR), clip=clip, alpha=False)
        pix.save(os.path.join(OUT, job["id"] + ".png"))
        meta = {"id": job["id"], "url": job["pdf"], "source": job.get("source", ""),
                "w": round(clip.width * s, 1), "h": round(clip.height * s, 1), "dpr": DPR, "highlights": hl}
        json.dump(meta, open(os.path.join(META, job["id"] + ".json"), "w"), ensure_ascii=False, indent=1)
        print(f"{job['id']:16s} {meta['w']:.0f}×{meta['h']:.0f} px, {len(hl)} passages "
              f"({', '.join(str(len(h['rects'])) + ' l.' for h in hl)})")


if __name__ == "__main__":
    main()
