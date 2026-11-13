"""Le mode libre : un dessin de structure posé directement en 2D, sans modèle.

Chaque figure est décrite à la main (positions estimées à l'œil, en têtes).
Rien ne relie deux figures entre elles : c'est le dessin « de mémoire ».
Le résultat a le même format que celui du mannequin, et le même crayon le trace.
"""
import numpy as np

from .construction import Construction, Shape, hull

# Rayons des membres, repris de la feuille de modèle du personnage.
ARM, LEG, FOOT, NECK = (0.17, 0.13, 0.095), (0.27, 0.19, 0.185, 0.11), (0.13, 0.09), (0.17, 0.16)
ADJACENT = {("bras", "avant_bras"), ("avant_bras", "main"), ("cuisse", "jambe"),
            ("jambe", "pied"), ("bras", "cage"), ("cuisse", "bassin"), ("cou", "tete"),
            ("cou", "cage")}
_T = np.linspace(0, 2 * np.pi, 49)[:-1]


def _ellipse(cx, cy, rx, ry, rot=0.0):
    c, s = np.cos(np.radians(rot)), np.sin(np.radians(rot))
    x, y = rx * np.cos(_T), ry * np.sin(_T)
    return np.stack([cx + x * c - y * s, cy + x * s + y * c], axis=1)


def _tube(p, rp, q, rq):
    pts = np.vstack([_ellipse(*p, rp, rp), _ellipse(*q, rq, rq)])
    return pts[hull(pts)]


def _dense(poly, step=0.06, closed=True):
    poly = np.asarray(poly, float)
    out = []
    for i in range(len(poly) - (0 if closed else 1)):
        a, b = poly[i], poly[(i + 1) % len(poly)]
        k = max(1, int(np.ceil(np.hypot(*(b - a)) / step)))
        out.append(a + (b - a) * np.linspace(0, 1, k, endpoint=False)[:, None])
    if not closed:
        out.append(poly[-1:])
    return np.vstack(out)


def _inside(pts, poly):
    x, y = pts[:, 0][:, None], pts[:, 1][:, None]
    x1, y1 = poly[:, 0][None], poly[:, 1][None]
    x2, y2 = np.roll(poly[:, 0], -1)[None], np.roll(poly[:, 1], -1)[None]
    cross = ((y1 > y) != (y2 > y)) & (x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-12) + x1)
    return cross.sum(axis=1) % 2 == 1


def _base(name):
    return name[:-2] if name.endswith(("_L", "_R")) else name


def construct(fig):
    """fig : description 2D d'une figure (voir studio/steps/s02_libre.py)."""
    polys, rank, lines = {}, {}, []       # lines : (points, partie d'appartenance)
    marks = {}

    def add(name, poly, group):
        polys[name] = poly
        rank[name] = fig["order"].index(group)

    head = np.vstack([_ellipse(*fig["skull"]), _ellipse(*fig["jaw"])])
    add("cou", _tube(fig["neck"][0], NECK[0], fig["neck"][1], NECK[1]), "tete")
    add("tete", head[hull(head)], "tete")
    add("bassin", _ellipse(*fig["pelvis"]), "torse")
    add("cage", _ellipse(*fig["chest"]), "torse")
    for side in "LR":
        sh, el, wr, tip = (np.asarray(p, float) for p in fig[f"arm_{side}"])
        add(f"bras_{side}", _tube(sh, ARM[0], el, ARM[1]), f"bras_{side}")
        add(f"avant_bras_{side}", _tube(el, ARM[1], wr, ARM[2]), f"bras_{side}")
        mid, half = (wr + tip) / 2, np.hypot(*(tip - wr)) / 2
        ang = np.degrees(np.arctan2(tip[1] - wr[1], tip[0] - wr[0]))
        add(f"main_{side}", _ellipse(*mid, half, fig.get("hand_w", 0.13), ang), f"bras_{side}")
        hip, knee, ankle = (np.asarray(p, float) for p in fig[f"leg_{side}"])
        add(f"cuisse_{side}", _tube(hip, LEG[0], knee, LEG[1]), f"jambe_{side}")
        add(f"jambe_{side}", _tube(knee, LEG[2], ankle, LEG[3]), f"jambe_{side}")
        heel, toe = fig[f"foot_{side}"]
        add(f"pied_{side}", _tube(heel, FOOT[0], toe, FOOT[1]), f"jambe_{side}")
        for key, p in (("shoulder", sh), ("elbow", el), ("wrist", wr), ("hand", tip),
                       ("hip", hip), ("knee", knee), ("ankle", ankle)):
            marks[f"{key}_{side}"] = p

    for key in ("face", "back", "brow", "nose"):
        if key in fig:
            lines.append((fig[key], "tete"))
    for ear in fig.get("ears", []):
        lines.append((ear, "tete"))
    for key, owner in (("chest_line", "cage"), ("clav", "cage"), ("pelvis_line", "bassin")):
        if key in fig:
            lines.append((fig[key], owner))
    both = np.vstack([polys["cage"], polys["bassin"]])
    idx = hull(both)
    side = idx >= len(polys["cage"])
    for i in np.flatnonzero(side != np.roll(side, -1)):
        lines.append(([both[idx[i]], both[idx[(i + 1) % len(idx)]]], "cage+bassin"))

    def hidden(pts, owner):
        """Caché par une forme plus proche ou, aux articulations, par la forme voisine."""
        own = owner.split("+")
        out = np.zeros(len(pts), bool)
        for name, poly in polys.items():
            if name in own:
                continue
            pair = {(_base(name), _base(o)) for o in own} | {(_base(o), _base(name)) for o in own}
            same_side = any(name[-2:] == o[-2:] or not name.endswith(("_L", "_R"))
                            or not o.endswith(("_L", "_R")) for o in own)
            near = rank[name] > max(rank[o] for o in own)
            if near or (pair & ADJACENT and same_side):
                out |= _inside(pts, poly)
        return out

    con = Construction(marks=marks)
    for name, poly in polys.items():
        pts = _dense(poly)
        con.shapes.append(Shape(pts, hidden(pts, name), closed=True,
                                passes=2 if name in ("tete", "cage", "bassin") else 1))
    for pts, owner in lines:
        pts = _dense(pts, closed=False)
        con.shapes.append(Shape(pts, hidden(pts, owner)))
    con.marks.update(top=np.array([0, polys["tete"][:, 1].max()]),
                     chin=np.array([0, polys["tete"][:, 1].min()]),
                     crotch=np.array([0, polys["bassin"][:, 1].min()]),
                     sole=np.array([0, min(polys[f"pied_{s}"][:, 1].min() for s in "LR")]))
    return con


def mirror(con):
    """La même construction vue de l'autre côté (retournement horizontal)."""
    flip = np.array([-1.0, 1.0])
    return Construction([Shape(s.pts * flip, s.hidden, s.closed, s.passes) for s in con.shapes],
                        {k: v * flip for k, v in con.marks.items()})
