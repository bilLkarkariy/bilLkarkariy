"""La main : transforme un tracé idéal en geste humain.

Un trait fait main n'est jamais le tracé exact : il part un peu à côté, tremble,
se courbe avec le poignet, et sa pression monte puis retombe. Ces défauts,
dosés, sont ce qui fait « croquis ».
"""
import numpy as np

TAU = 2 * np.pi


# ---------- tracés idéaux ----------

def line(a, b):
    return np.array([a, b], float)


def ellipse(c, rx, ry, rot=0.0, start=0.0, sweep=TAU):
    n = max(16, int(abs(sweep) * max(rx, ry) / 3))
    t = start + np.linspace(0, sweep, n)
    x, y = rx * np.cos(t), ry * np.sin(t)
    cr, sr = np.cos(rot), np.sin(rot)
    return np.stack([c[0] + x * cr - y * sr, c[1] + x * sr + y * cr], axis=1)


def spline(points, per=24):
    """Courbe lisse passant par les points (Catmull-Rom)."""
    p = np.asarray(points, float)
    if len(p) < 3:
        return p
    q = np.vstack([2 * p[0] - p[1], p, 2 * p[-1] - p[-2]])
    t = np.linspace(0, 1, per, endpoint=False)[:, None]
    out = []
    for i in range(len(p) - 1):
        a, b, c, d = q[i:i + 4]
        out.append(0.5 * (2 * b + (c - a) * t + (2 * a - 5 * b + 4 * c - d) * t ** 2
                          + (3 * b - a - 3 * c + d) * t ** 3))
    out.append(p[-1:])
    return np.vstack(out)


def resample(path, step):
    """Points régulièrement espacés de `step` pixels, et leur abscisse curviligne."""
    path = np.asarray(path, float)
    s = np.concatenate([[0.0], np.cumsum(np.hypot(*np.diff(path, axis=0).T))])
    u = np.linspace(0, s[-1], max(2, int(s[-1] / step) + 1))
    return np.stack([np.interp(u, s, path[:, 0]), np.interp(u, s, path[:, 1])], axis=1), u


def hatch_lines(poly, angle, gap, rng, jitter=0.18):
    """Segments parallèles remplissant un polygone."""
    ca, sa = np.cos(angle), np.sin(angle)
    rot = np.array([[ca, sa], [-sa, ca]])
    q = np.asarray(poly, float) @ rot.T
    out = []
    for y in np.arange(q[:, 1].min() + gap / 2, q[:, 1].max(), gap):
        y += rng.normal(0, jitter * gap)
        xs = sorted(x1 + (y - y1) * (x2 - x1) / (y2 - y1)
                    for (x1, y1), (x2, y2) in zip(q, np.roll(q, -1, axis=0))
                    if (y1 <= y < y2) or (y2 <= y < y1))
        for a, b in zip(xs[::2], xs[1::2]):
            out.append(np.array([[a, y], [b, y]]) @ rot)
    return out


# ---------- le geste ----------

def _noise(u, wavelength, rng):
    knots = rng.normal(0, 1, int(u[-1] / wavelength) + 3)
    v = u / wavelength + rng.random()
    i = np.floor(v).astype(int)
    f = v - i
    f = f * f * (3 - 2 * f)
    return knots[i] * (1 - f) + knots[i + 1] * f


def _ramp(t, width, floor):
    if width <= 0:
        return np.ones_like(t)
    f = np.clip(t / width, 0, 1)
    return floor + (1 - floor) * f * f * (3 - 2 * f)


class Hand:
    def __init__(self, seed=0, tremor=0.55, aim=1.1, turn=0.008, scale=0.010, bow=0.004):
        self.rng = np.random.default_rng(seed)
        self.tremor, self.aim, self.turn, self.scale, self.bow = tremor, aim, turn, scale, bow

    def trace(self, path, brush, pressure=0.6, taper=(0.15, 0.25), tip=0.25,
              overshoot=0.0, care=1.0):
        """Renvoie le geste (n, 3) : x, y, pression.

        pressure : nombre, ou fonction de t (0..1) pour un profil sur mesure.
        taper    : part du trait où la pression monte, puis retombe.
        care     : 1 = geste normal ; plus grand = plus appliqué, plus précis.
        """
        rng = self.rng
        path = np.asarray(path, float)
        if overshoot:
            head = path[0] - path[1]
            tail = path[-1] - path[-2]
            ext = overshoot * rng.uniform(0.4, 1.0, 2)
            path = np.vstack([path[0] + head / np.hypot(*head) * ext[0], path,
                              path[-1] + tail / np.hypot(*tail) * ext[1]])
        xy, u = resample(path, max(0.35, brush.spacing * brush.radius * 0.8))
        total = max(u[-1], 1e-6)
        t = u / total

        # Erreur de visée : le trait entier est décalé, tourné, un peu trop grand ou petit.
        centre = xy.mean(axis=0)
        ang = rng.normal(0, self.turn / care)
        ca, sa = np.cos(ang), np.sin(ang)
        xy = (xy - centre) @ np.array([[ca, sa], [-sa, ca]]) * (1 + rng.normal(0, self.scale / care))
        xy += centre + rng.normal(0, self.aim / care, 2)

        # Tremblement et courbure du poignet, perpendiculaires au trait.
        tan = np.gradient(xy, axis=0)
        tan /= np.maximum(np.hypot(tan[:, 0], tan[:, 1]), 1e-9)[:, None]
        normal = np.stack([-tan[:, 1], tan[:, 0]], axis=1)
        drift = (self.tremor / care) * (_noise(u, 70, rng) + 0.35 * _noise(u, 11, rng))
        drift += rng.normal(0, self.bow / care) * total * np.sin(np.pi * t)
        xy += normal * drift[:, None]

        base = pressure(t) if callable(pressure) else pressure
        p = base * _ramp(t, taper[0], tip) * _ramp(1 - t, taper[1], tip)
        p = p * (1 + 0.12 * _noise(u, 50, rng))
        return np.column_stack([xy, np.clip(p, 0.02, 1.0)])


class Draftsman:
    """Le dessinateur : une main qui dessine dans un document."""

    def __init__(self, doc, seed=0, **hand):
        self.doc = doc
        self.hand = Hand(seed, **hand)

    def stroke(self, path, brush, layer, passes=1, reach=None, **kw):
        """passes : nombre de fois où le trait est repassé (traits de recherche).
        reach  : longueur maximale d'un geste ; au-delà le trait est repris en plusieurs fois.
        """
        rng = self.hand.rng
        for _ in range(passes):
            for piece in self._split(path, reach, rng):
                self.doc.stroke(layer, brush, self.hand.trace(piece, brush, **kw))

    def hatch(self, poly, brush, layer, angle, gap, **kw):
        kw.setdefault("taper", (0.08, 0.45))
        for seg in hatch_lines(poly, angle, gap, self.hand.rng):
            self.doc.stroke(layer, brush, self.hand.trace(seg, brush, **kw))

    @staticmethod
    def _split(path, reach, rng):
        if not reach:
            return [path]
        xy, u = resample(path, 2.0)
        pieces, start = [], 0.0
        while True:
            end = start + reach * rng.uniform(0.75, 1.15)
            if end >= u[-1] - reach * 0.3:
                pieces.append(xy[u >= start])
                return pieces
            pieces.append(xy[(u >= start) & (u <= end)])
            start = end - reach * rng.uniform(0.08, 0.16)
