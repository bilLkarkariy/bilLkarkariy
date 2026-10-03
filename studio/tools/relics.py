"""Objets d'archive : le vrai papier détouré (bord déchiré, transparence), au même format que
tools/capture.py, pour être posé sur le bureau par src/components/Citation.tsx (prop `cutout`).

Le fond blanc du scan (relié aux bords de l'image) devient transparent : la feuille garde sa
vraie forme, et son ombre sur le bureau aussi. Les passages sont des zones dessinées à la main
(écriture manuscrite), en px de l'image source.

  python3 tools/relics.py script/relics_v01.json [id ...]
  -> public/captures/<id>.png + src/data/captures/<id>.json
"""
import json
import os
import sys
import urllib.request

import numpy as np
import pymupdf
from PIL import Image, ImageFilter
from scipy import ndimage

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "public/captures")
META = os.path.join(ROOT, "src/data/captures")
CACHE = os.path.join(ROOT, ".cache/docs")


def fetch(url):
    path = os.path.join(CACHE, os.path.basename(url.split("?")[0]))
    if not os.path.exists(path):
        os.makedirs(CACHE, exist_ok=True)
        urllib.request.urlretrieve(url, path)
    return path


def source(job):
    """Image du scan : la n-ième image d'une page de PDF, ou un fichier image."""
    path = fetch(job["src"])
    if path.lower().endswith(".pdf"):
        doc = pymupdf.open(path)
        xref = doc[job.get("page", 0)].get_images(full=True)[job.get("image", 0)][0]
        path = os.path.join(CACHE, f"{job['id']}_src.{doc.extract_image(xref)['ext']}")
        open(path, "wb").write(doc.extract_image(xref)["image"])
    return Image.open(path).convert("RGB")


def cutout(im, white=232):
    """Alpha : transparent là où le blanc du fond touche le bord ; bord adouci d'un demi-pixel."""
    a = np.asarray(im).astype(np.int16)
    bright = (a.min(axis=2) >= white) & (a.max(axis=2) - a.min(axis=2) < 14)  # blanc neutre (le papier est crème)
    lab, _ = ndimage.label(bright)
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bg = np.isin(lab, list(edge))
    bg = ndimage.binary_opening(bg, iterations=1)
    alpha = Image.fromarray(np.where(bg, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6))
    out = im.convert("RGBA")
    out.putalpha(alpha)
    box = alpha.getbbox()
    return out.crop(box), box


def main():
    jobs = json.load(open(sys.argv[1]))
    only = set(sys.argv[2:])
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(META, exist_ok=True)
    for job in jobs:
        if only and job["id"] not in only:
            continue
        im = source(job)
        if job.get("print"):  # photographie : un tirage à bord blanc, rectangulaire
            b = round(im.width * 0.035)
            rgba = Image.new("RGBA", (im.width + 2 * b, im.height + 2 * b), (247, 245, 239, 255))
            rgba.paste(im.convert("RGB"), (b, b))
            bx, by = -b, -b
        else:
            rgba, (bx, by, _, _) = cutout(im, job.get("white", 232))
        dpr = rgba.width / job.get("css_w", 680)  # même rôle que le ×2,5 des captures web
        rgba.save(os.path.join(OUT, job["id"] + ".png"), optimize=True)
        hl = [{"text": h["text"], "rects": [
            {"x": round((r[0] - bx) / dpr, 1), "y": round((r[1] - by) / dpr, 1),
             "w": round((r[2] - r[0]) / dpr, 1), "h": round((r[3] - r[1]) / dpr, 1)} for r in h["rects"]]}
            for h in job.get("highlights", [])]
        meta = {"id": job["id"], "url": job.get("url", job["src"]), "source": job.get("source", ""),
                "w": round(rgba.width / dpr, 1), "h": round(rgba.height / dpr, 1), "dpr": round(dpr, 3),
                "cutout": True, "highlights": hl}
        json.dump(meta, open(os.path.join(META, job["id"] + ".json"), "w"), ensure_ascii=False, indent=1)
        print(f"{job['id']:16s} {rgba.width}×{rgba.height} px source → {meta['w']:.0f}×{meta['h']:.0f}, {len(hl)} passages")


if __name__ == "__main__":
    main()
