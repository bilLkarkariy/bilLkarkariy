"""Captures de vraies pages (articles, études) avec la position exacte des passages à surligner.

Pour chaque capture : on ouvre la page dans Chromium, on trouve le paragraphe
qui contient l'ancre et on le photographie (×2.5, net en 4K). Chaque passage
devient une plage de texte (Range) dont on lit les boîtes, ligne par ligne,
dans le même repère que la capture d'écran (l'écran, sans défilement entre les
deux). Le montage anime ensuite un feutre sur ces rectangles.
Option `pad` : marge autour du bloc (0 quand les paragraphes voisins sont trop proches ;
la feuille ajoute alors sa propre marge, voir `inset` dans src/components/Citation.tsx).

  python3 tools/capture.py script/captures_v01.json [id ...]
  -> public/captures/<id>.png + src/data/captures/<id>.json   (rectangles en px CSS)

Prérequis (une fois) : faire confiance au CA du proxy dans le magasin NSS de Chromium
  certutil -d sql:$HOME/.pki/nssdb -A -t "C,," -n ccr-agent-proxy -i /root/.ccr/agent-proxy-ca.crt
"""
import io
import json
import os
import sys

import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "public/captures")  # images (régénérables, hors git)
META = os.path.join(ROOT, "src/data/captures")  # rectangles des passages (lus par le montage)
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
DPR = 2.5

# trouve le bloc, le centre à l'écran, et prépare un Range par passage (gardés dans window.__ranges)
FIND = """
([anchor, phrases, block, deepest]) => {
  const norm = s => s.replace(/\\s+/g, ' ');
  const found = [...document.querySelectorAll(block)].filter(b => norm(b.textContent).includes(anchor));
  // les blocs trouvés s'emboîtent : le premier est le plus large, le dernier le plus précis
  const el = deepest ? found[found.length - 1] : found[0];
  if (!el) return {error: 'ancre introuvable : ' + anchor};
  el.scrollIntoView({block: 'center', behavior: 'instant'});
  const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
  const nodes = []; let acc = '';
  while (walker.nextNode()) { const n = walker.currentNode; nodes.push([n, acc.length]); acc += n.textContent; }
  const flat = norm(acc);
  // index dans le texte brut <-> texte aux espaces normalisés
  const map = []; let prevSpace = false;
  for (let k = 0; k < acc.length; k++) {
    const sp = /\\s/.test(acc[k]);
    if (sp && prevSpace) continue;
    map.push(k); prevSpace = sp;
  }
  const at = k => { for (let q = nodes.length - 1; q >= 0; q--) if (nodes[q][1] <= k) return [nodes[q][0], k - nodes[q][1]]; };
  window.__ranges = [];
  for (const ph of phrases) {
    const i = flat.indexOf(ph);
    if (i < 0) return {error: 'passage introuvable : ' + ph};
    const r = document.createRange();
    const [n0, o0] = at(map[i]); const [n1, o1] = at(map[i + ph.length - 1]);
    r.setStart(n0, o0); r.setEnd(n1, o1 + 1);
    if (norm(r.toString()) !== ph) return {error: 'passage mal découpé : ' + r.toString()};
    window.__ranges.push(r);
  }
  el.setAttribute('data-capture', '1');
  return {ok: true};
}
"""

BOX = """
() => { const b = document.querySelector('[data-capture]').getBoundingClientRect();
        return {x: b.left, y: b.top, w: b.width, h: b.height}; }
"""

HIDE = """
header, nav, .usa-banner, .ncbi-header, .pmc-sidenav, .pmc-header, footer, [role="banner"],
.usa-overlay, .ncbi-alerts, .pmc-sticky-header, aside, .QSIFeedbackButton, [class*="QSIFeedback"] { display: none !important; }
/* bandeaux cookies, barres collantes et fenêtres d'autres sites (Médiamétrie, Arcep, Wardah…) */
#sliding-popup, .eu-cookie-compliance-banner, #tarteaucitronRoot, #didomi-host, #onetrust-consent-sdk, .cookie-banner,
#shopify-section-announcement-bar, .announcement-bar, [role="dialog"], [aria-modal="true"] { display: none !important; }
body { background: #fff !important; }
html, body { scrollbar-width: none !important; scroll-behavior: auto !important; }
::-webkit-scrollbar { display: none !important; }
"""


def shot(pg):
    return np.asarray(Image.open(io.BytesIO(pg.screenshot())).convert("RGB")).astype(np.int16)


# rectangles d'un passage, une boîte par ligne (coordonnées de l'écran, comme la capture)
RECTS = """
(i) => {
  const rs = [...window.__ranges[i].getClientRects()].filter(r => r.width > 1 && r.height > 1);
  const lines = [];
  for (const r of rs) {
    const l = lines.find(l => Math.abs((l.top + l.bottom) / 2 - (r.top + r.bottom) / 2) < r.height / 2);
    if (l) { l.left = Math.min(l.left, r.left); l.right = Math.max(l.right, r.right);
             l.top = Math.min(l.top, r.top); l.bottom = Math.max(l.bottom, r.bottom); }
    else lines.push({left: r.left, right: r.right, top: r.top, bottom: r.bottom});
  }
  return lines.sort((a, b) => a.top - b.top);
}
"""


def main():
    jobs = json.load(open(sys.argv[1]))
    only = set(sys.argv[2:])
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(META, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME, args=["--no-sandbox"])
        ctx = b.new_context(viewport={"width": 860, "height": 1400}, device_scale_factor=DPR)
        pages = {}
        for job in jobs:
            if only and job["id"] not in only:
                continue
            url = job["url"]
            if url not in pages:
                pg = ctx.new_page()
                try:
                    # « load » puis un temps : certains sites (mesure d'audience) ne sont jamais « networkidle »
                    pg.goto(url, wait_until="load", timeout=90000)
                except Exception as e:  # noqa: BLE001
                    print(f"{job['id']:16s} ÉCHEC du chargement : {str(e).splitlines()[0]}")
                    continue
                pg.wait_for_timeout(2500)
                pg.add_style_tag(content=HIDE)
                pg.evaluate("document.fonts.ready")
                pages[url] = pg
            pg = pages[url]
            pg.evaluate("document.querySelectorAll('[data-capture]').forEach(e => e.removeAttribute('data-capture'))")
            res = pg.evaluate(FIND, [job["anchor"], job.get("highlights", []), job.get("block", "p"), job.get("deepest", False)])
            if "error" in res:
                print(f"{job['id']:16s} ÉCHEC : {res['error']}")
                continue
            pg.wait_for_timeout(300)
            box = pg.evaluate(BOX)
            pad = job.get("pad", 22)
            clean = shot(pg)
            # marge autour du bloc, sans sortir de l'écran (un indice négatif viderait le recadrage)
            x0, y0 = max(0, int((box["x"] - pad) * DPR)), max(0, int((box["y"] - pad) * DPR))
            x1 = min(clean.shape[1], int((box["x"] + box["w"] + pad) * DPR))
            y1 = min(clean.shape[0], int((box["y"] + box["h"] + pad) * DPR))
            if "crop_h" in job:  # ne garder que le haut du bloc (titre + auteurs, sans le bandeau PMC)
                y1 = min(y1, y0 + int((pad + job["crop_h"]) * DPR))
            hl = []
            ox, oy = x0 / DPR, y0 / DPR
            for i, text in enumerate(job.get("highlights", [])):
                lines = pg.evaluate(RECTS, i)
                rects = [{"x": round(l["left"] - ox, 1), "y": round(l["top"] - oy, 1),
                          "w": round(l["right"] - l["left"], 1), "h": round(l["bottom"] - l["top"], 1)}
                         for l in lines if l["top"] >= oy - 2 and l["bottom"] <= y1 / DPR + 2]
                if not rects:
                    print(f"{job['id']:16s} ÉCHEC : passage hors du cadre : {text}")
                    break
                hl.append({"text": text, "rects": rects})
            if len(hl) != len(job.get("highlights", [])):
                continue
            png = os.path.join(OUT, job["id"] + ".png")
            Image.fromarray(clean[y0:y1, x0:x1].astype(np.uint8)).save(png, optimize=True)
            meta = {"id": job["id"], "url": url, "source": job.get("source", ""),
                    "w": round((x1 - x0) / DPR, 1), "h": round((y1 - y0) / DPR, 1), "dpr": DPR, "highlights": hl}
            json.dump(meta, open(os.path.join(META, job["id"] + ".json"), "w"), ensure_ascii=False, indent=1)
            print(f"{job['id']:16s} {meta['w']:.0f}×{meta['h']:.0f} px, {len(hl)} passages "
                  f"({', '.join(str(len(h['rects'])) + ' l.' for h in hl)})")
        b.close()


if __name__ == "__main__":
    main()
