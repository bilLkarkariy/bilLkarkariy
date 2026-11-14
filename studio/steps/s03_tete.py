"""Settei de Kaya — la tête de trois quarts, dessinée au crayon.

Tout est tracé au crayon, geste après geste, comme à la table :
  1. charpente au crayon bleu (crâne, croix du visage, mâchoire, cou, masse des cheveux) ;
  2. esquisse légère au graphite, qui cherche les formes ;
  3. trait appuyé : contours, yeux, mèches ;
  4. cheveux montés mèche par mèche, de la racine à la pointe, en réservant le reflet ;
  5. ombres hachurées.
Aucun aplat : la feuille ne reçoit que des coups de crayon.

    python3 -m studio.steps.s03_tete
"""
from pathlib import Path

import numpy as np

from studio.characters import kaya_tete
from studio.engine.brush import Brush
from studio.engine.canvas import Document
from studio.engine.formes import solve
from studio.engine.hand import Draftsman
from studio.engine.timelapse import timelapse
from studio.engine.vpath import parse

OUT = Path(__file__).resolve().parent.parent / "out"
K = 1.6                                  # pixels de feuille par pixel d'étude
BOX = kaya_tete.BOX

BLEU = Brush("bleu", (0.30, 0.50, 0.84), radius=2.5, density=0.85, grain=0.9)
ESQUISSE = Brush("esquisse", (0.27, 0.27, 0.30), radius=2.3, density=1.05, grain=0.85)
TRAIT = Brush("trait", (0.09, 0.09, 0.12), radius=3.5, density=2.9, min_size=0.30, grain=0.35,
              scatter=0.04, flow_gamma=0.8)
FIN = Brush("fin", (0.11, 0.11, 0.14), radius=2.2, density=2.5, min_size=0.40, grain=0.40, flow_gamma=0.9)
MECHE = Brush("meche", (0.15, 0.14, 0.19), radius=2.7, density=1.25, min_size=0.5, grain=0.85, scatter=0.10)
HACHURE = Brush("hachure", (0.22, 0.22, 0.25), radius=2.0, density=1.15, grain=0.8)
NOIR = Brush("noir", (0.07, 0.07, 0.09), radius=2.4, density=3.2, min_size=0.5, grain=0.25, flow_gamma=0.8)

ORDER = ["visage", "yeux", "cou", "frange", "calotte", "queue", "buste"]


def P(pts):
    return (np.asarray(pts, float) - BOX[:2]) * K


def length(pts):
    return float(np.hypot(*np.diff(pts, axis=0).T).sum())


def runs(pts, ok, minlen=4.0):
    """Tronçons de la polyligne où `ok` est vrai."""
    out, j, n = [], 0, len(pts)
    while j < n:
        if ok[j]:
            a = j
            while j < n and ok[j]:
                j += 1
            if j - a >= 2 and length(pts[a:j]) >= minlen:
                out.append((a, j))
        else:
            j += 1
    return out


def at(grid, px):
    """Valeurs d'une carte aux points (pixels de feuille) ; hors feuille : -9."""
    h, w = grid.shape
    x, y = px[:, 0].astype(int), px[:, 1].astype(int)
    ok = (x >= 0) & (x < w) & (y >= 0) & (y < h)
    out = np.full(len(px), -9, dtype=np.int64)
    out[ok] = grid[y[ok], x[ok]]
    return out


def profile(values):
    t = np.linspace(0, 1, len(values))
    return lambda u: np.interp(u, t, values)


# --- 1. charpente ------------------------------------------------------------------------------------

def construction(d):
    for name, path in kaya_tete.GUIDES.items():
        for sub in parse(path):
            loose = name in ("crane", "cheveux", "queue", "epaules")
            d.stroke(P(sub["pts"]), BLEU, "charpente", passes=2 if name == "crane" else 1,
                     pressure=0.55 if name in ("crane", "mediane", "yeux") else 0.45,
                     taper=(0.08, 0.2), overshoot=22 if not loose else 8, care=0.75)


# --- 2. esquisse ---------------------------------------------------------------------------------------

def esquisse(d, sol):
    """Traits de recherche : légers, repris, un peu à côté. On dessine « à travers » les formes."""
    items = sol["items"]
    for it in items:                                   # le geste de chaque mèche, de la racine à la pointe
        if it.get("lock"):
            L, R = it["lock"]
            d.stroke(P((L + R) / 2), ESQUISSE, "esquisse", pressure=0.30, taper=(0.1, 0.4), care=0.5)
    for s in sol["strokes"]:
        if s["kind"] not in ("shape", "line") or length(s["pts"]) < 50 or items[s["item"]].get("group") == "yeux":
            continue
        d.stroke(P(s["pts"]), ESQUISSE, "esquisse", passes=2, reach=300, pressure=0.30,
                 taper=(0.12, 0.25), overshoot=9, care=0.5)


# --- 3. trait ----------------------------------------------------------------------------------------------

def trait(d, sol):
    items = sol["items"]
    rank = {g: i for i, g in enumerate(ORDER)}
    strokes = sorted(sol["strokes"], key=lambda s: rank.get(items[s["item"]].get("group"), 99))
    for s in strokes:
        it = items[s["item"]]
        if s["kind"] == "ink":
            continue
        if s["kind"] not in ("shape", "line"):
            continue
        pts, w = P(s["pts"]), s["w"]
        brush = TRAIT if w >= 0.75 else FIN
        base = min(1.0, 0.92 * w if w >= 0.75 else 0.55 + 0.5 * w)
        weight = s.get("weight")
        cuts = [0] + [c for c in s.get("corners", []) if 2 < c < len(pts) - 3] + [len(pts) - 1]
        for a, b in zip(cuts, cuts[1:]):
            piece = pts[a:b + 1]
            if length(piece) < 3:
                continue
            if weight is not None:
                press = profile(base * weight[a:b + 1])
            else:
                press = base
            taper = s["taper"] if s.get("taper") else (0.07, 0.12)
            d.stroke(piece, brush, "trait", pressure=press, taper=taper, tip=0.3, care=2.2,
                     reach=420 if length(piece) > 520 else None)


def hatch_mask(d, mask, brush, layer, angle, gap, pressure, taper=(0.1, 0.3), jitter=0.2, care=1.2, minlen=5):
    """Hachures parallèles limitées à une zone de la feuille."""
    ys, xs = np.nonzero(mask)
    if len(xs) == 0:
        return
    rng = d.hand.rng
    c = np.array([xs.mean(), ys.mean()])
    dv, nv = np.array([np.cos(angle), np.sin(angle)]), np.array([-np.sin(angle), np.cos(angle)])
    rel = np.stack([xs, ys], 1) - c
    on, od = rel @ nv, rel @ dv
    for o in np.arange(on.min(), on.max() + gap, gap):
        o += rng.normal(0, jitter * gap)
        t = np.arange(od.min() - 2, od.max() + 2, 1.5)
        line = c + nv * o + dv * t[:, None]
        ok = at(mask.astype(np.int8), line) == 1
        for a, b in runs(line, ok, minlen):
            p = pressure * rng.uniform(0.8, 1.15)
            d.stroke(line[[a, b - 1]], brush, layer, pressure=p, taper=taper, care=care)


def encre(d, sol):
    """Les noirs : cils, sourcils, pupilles, noircis par des coups de crayon serrés dans le sens de la
    forme ; puis l'iris, plus sombre en haut, sous la paupière."""
    zm, tm, om, zones, items = sol["zone_map"], sol["tone_map"], sol["order_map"], sol["zones"], sol["items"]
    for i, it in enumerate(items):
        if it["kind"] != "ink":
            continue
        m = om == i
        ys, xs = np.nonzero(m)
        if len(xs) < 12:
            continue
        cov = np.cov(np.stack([xs, ys]).astype(float))
        vals, vecs = np.linalg.eigh(cov)
        axis = vecs[:, np.argmax(vals)]
        angle = float(np.arctan2(axis[1], axis[0]))
        hatch_mask(d, m, NOIR, "trait", angle=angle, gap=2.3, pressure=0.95, taper=(0.12, 0.12), jitter=0.1,
                   care=4.0, minlen=2)
        hatch_mask(d, m, NOIR, "trait", angle=angle + 0.5, gap=3.2, pressure=0.7, taper=(0.1, 0.1), care=4.0, minlen=2)
    if "iris" in zones:
        m = zm == zones.index("iris")
        hatch_mask(d, m, FIN, "trait", angle=1.3, gap=2.8, pressure=0.55, taper=(0.1, 0.2), care=3.0, minlen=3)
        hatch_mask(d, m, HACHURE, "trait", angle=0.4, gap=3.6, pressure=0.45, taper=(0.1, 0.2), care=3.0, minlen=3)
        dark = m & (tm == 1)
        hatch_mask(d, dark, NOIR, "trait", angle=1.3, gap=2.3, pressure=0.85, taper=(0.1, 0.3), care=3.0, minlen=3)
        hatch_mask(d, dark, NOIR, "trait", angle=0.2, gap=3.0, pressure=0.6, taper=(0.1, 0.3), care=3.0, minlen=3)


# --- 4. cheveux ---------------------------------------------------------------------------------------------

def shine(it, pts, t, rng):
    """Force du crayon le long d'une mèche : le reflet est une bande où l'on appuie à peine."""
    kind = it.get("shine")
    f = np.ones(len(pts))
    if not kind:
        return f
    if kind[0] == "ring":
        a, b, c, half = kaya_tete.RING
        dist = np.abs(pts[:, 1] - (a + b * (pts[:, 0] - c) ** 2 + rng.normal(0, 9)))
        half = half * rng.uniform(0.65, 1.2)
    else:
        dist, half = np.abs(t - (kind[1] + rng.normal(0, 0.012))), kind[2] * rng.uniform(0.65, 1.2)
    x = np.clip(dist / half, 0, 1)
    return 0.10 + 0.90 * x * x * (3 - 2 * x)


def under(sol, dx=7, dy=16):
    """Là où une mèche passe sous une mèche posée devant elle : on y appuie davantage."""
    om, items = sol["order_map"], sol["items"]
    hair = np.array([bool(it.get("lock")) for it in items] + [False])
    is_hair = hair[om]                                    # -1 (papier) tombe sur le dernier : faux
    dx, dy = int(dx * K), int(dy * K)
    above = np.full_like(om, -1)
    above[dy:, dx:] = om[:-dy, :-dx]
    return is_hair & hair[above] & (above > om)


def cheveux(d, sol, gap=4.6):
    items, order_map, tm = sol["items"], sol["order_map"], sol["tone_map"]
    rng = d.hand.rng
    deep = under(sol).astype(np.int8)
    rank = {"frange": 0, "calotte": 1, "queue": 2}
    locks = sorted((i for i, it in enumerate(items) if it.get("lock")),
                   key=lambda i: rank.get(items[i].get("group"), 3))
    for i in locks:
        it = items[i]
        L, R = it["lock"]
        width = float(np.median(np.hypot(*(L - R).T))) * K
        n = max(3, int(width / gap))
        t = np.linspace(0, 1, len(L))
        for u in (np.arange(n) + 0.5) / n + rng.normal(0, 0.18 / n, n):
            u = float(np.clip(u, 0.03, 0.97))
            study = (1 - u) * L + u * R
            px = P(study)
            ok = at(order_map, px) == i
            f = shine(it, study, t, rng)
            base = 0.70 * it.get("tone", 1.0) * rng.uniform(0.75, 1.15)
            root = np.clip(t / 0.16, 0, 1)
            press = base * f * (0.3 + 0.7 * root * root * (3 - 2 * root))
            press = np.clip(press * np.where(at(deep, px) == 1, 1.7, 1.0), 0.03, 1.0)
            for a, b in runs(px, ok, 6):
                d.stroke(px[a:b], MECHE, "cheveux", pressure=profile(press[a:b]),
                         taper=(0.06, 0.18), tip=0.3, care=1.4)


# --- 5. ombres -------------------------------------------------------------------------------------------------

def ombres(d, sol):
    zm, tm, zones = sol["zone_map"], sol["tone_map"], sol["zones"]
    for zone, angle, gap, p in (("peau", -1.02, 7.0, 0.40), ("sweat", -0.95, 8.5, 0.42), ("oeil", -1.02, 5.0, 0.25)):
        if zone in zones:
            hatch_mask(d, (zm == zones.index(zone)) & (tm == 1), HACHURE, "ombres", angle, gap, p)


def drawing(seed=93):
    sol = solve(kaya_tete.build(), BOX, K)
    w, h = sol["size"]
    doc = Document(w, h, seed=seed)
    construction(Draftsman(doc, seed, tremor=0.9, aim=3.5, turn=0.012, scale=0.014, bow=0.006))
    esquisse(Draftsman(doc, seed + 1, tremor=1.1, aim=4.5, turn=0.016, scale=0.02, bow=0.008), sol)
    net = Draftsman(doc, seed + 2, tremor=0.45, aim=0.9, turn=0.004, scale=0.004, bow=0.002)
    trait(net, sol)
    encre(net, sol)
    cheveux(Draftsman(doc, seed + 3, tremor=0.7, aim=1.4, turn=0.008, scale=0.008, bow=0.005), sol)
    ombres(Draftsman(doc, seed + 4, tremor=0.6, aim=1.2, turn=0.01, scale=0.01, bow=0.004), sol)
    return doc


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    doc = drawing()
    doc.save(OUT / "s03_tete.png")
    print("dessin :", OUT / "s03_tete.png", f"({len(doc.journal)} gestes)")
    import sys
    if "--video" in sys.argv:
        frames = timelapse(doc, OUT / "s03_tete.mp4", seconds=22, hold=3, scale=0.5)
        print("vidéo :", OUT / "s03_tete.mp4", f"({frames} images)")
