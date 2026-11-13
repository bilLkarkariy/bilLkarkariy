"""La construction : le dessin de structure d'un personnage, en 2D.

C'est le format commun aux deux modes. Le mode mannequin l'obtient en projetant
un modèle 3D ; le mode libre le reçoit tel quel, posé à la main. Ensuite le
même crayon dessine les deux.
"""
from dataclasses import dataclass, field

import numpy as np

from .brush import BLEU


@dataclass
class Shape:
    pts: np.ndarray          # (n, 2) en têtes, x vers la droite, y vers le haut
    hidden: np.ndarray       # (n,) vrai là où une autre forme passe devant
    closed: bool = False
    passes: int = 1
    weight: float = 1.0      # force du trait, relative au reste du dessin
    w: np.ndarray = None     # force point par point (pleins et déliés), ou None


@dataclass
class Construction:
    shapes: list = field(default_factory=list)
    marks: dict = field(default_factory=dict)    # repères nommés (x, y), pour mesurer


def hull(pts):
    """Indices de l'enveloppe convexe d'un nuage de points 2D, dans l'ordre du contour."""
    order = np.lexsort((pts[:, 1], pts[:, 0]))

    def half(idx):
        out = []
        for i in idx:
            while len(out) >= 2:
                o, a = pts[out[-2]], pts[out[-1]]
                if (a[0] - o[0]) * (pts[i][1] - o[1]) - (a[1] - o[1]) * (pts[i][0] - o[0]) > 0:
                    break
                out.pop()
            out.append(i)
        return out

    return np.array(half(order)[:-1] + half(order[::-1])[:-1])


def _runs(hidden, closed):
    """Découpe un tracé en tronçons (début, fin, caché), fin incluse."""
    n = len(hidden)
    change = np.flatnonzero(hidden[1:] != hidden[:-1]) + 1
    if len(change) == 0:
        return 0, [(0, n if closed else n - 1, int(hidden[0]))]
    shift = int(change[0]) if closed else 0      # un contour fermé démarre sur une transition
    h = np.roll(hidden, -shift)
    cuts = [0] + list(np.flatnonzero(h[1:] != h[:-1]) + 1) + [n]
    return shift, [(a, min(b, n - 1) if not closed else b, int(h[a])) for a, b in zip(cuts, cuts[1:])]


def _profile(base, w):
    """Pression le long d'un tronçon : suit les poids w, répartis sur sa longueur."""
    if w is None or len(w) < 2:
        return base
    t = np.linspace(0, 1, len(w))
    return lambda u: base * np.interp(u, t, w)


def draw(d, con, origin, scale, brush=BLEU, layer="construction", pressure=0.6, through=0.3,
         care=1.0, clip=None):
    """Dessine une construction au crayon. `through` : force des traits cachés
    (0 pour ne pas les tracer), comme quand on dessine « en transparence ».
    `clip` : cadre (x0, y0, x1, y1) en pixels hors duquel rien n'est tracé."""
    origin = np.asarray(origin, float)
    rng = d.hand.rng
    for shape in con.shapes:
        px = origin + shape.pts * (scale, -scale)
        n = len(px)
        if n < 2:
            continue
        hidden, w = shape.hidden, shape.w
        skip = np.zeros(n, bool)
        if clip is not None:
            skip = ((px[:, 0] < clip[0]) | (px[:, 0] > clip[2])
                    | (px[:, 1] < clip[1]) | (px[:, 1] > clip[3]))
        state = np.where(skip, 2, hidden.astype(int))       # 0 visible, 1 caché, 2 hors cadre
        if shape.closed and not state.any():
            start = int(rng.integers(n))
            order = np.roll(np.arange(n), -start)
            order = np.concatenate([order, order[:max(2, n // 7)]])
            d.stroke(px[order], brush, layer, passes=shape.passes, taper=(0.1, 0.25), care=care,
                     pressure=_profile(pressure * shape.weight, None if w is None else w[order]))
            continue
        shift, runs = _runs(state, shape.closed)
        order = np.roll(np.arange(n), -shift)
        if shape.closed:
            order = np.concatenate([order, order[:1]])
        for a, b, kind in runs:
            piece = order[a:b + 1]
            if len(piece) < 2 or kind == 2 or (kind == 1 and through <= 0):
                continue
            if np.hypot(*np.diff(px[piece], axis=0).T).sum() < 4:
                continue
            base = pressure * shape.weight * (through if kind == 1 else 1.0)
            d.stroke(px[piece], brush, layer, passes=1 if kind == 1 else shape.passes, care=care,
                     pressure=_profile(base, None if w is None else w[piece]))
