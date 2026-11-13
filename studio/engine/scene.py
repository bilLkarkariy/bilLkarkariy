"""Le décor : des volumes simples (boîtes) vus par la même caméra que le personnage.

Une boîte donne ses arêtes visibles ; les autres boîtes cachent ce qui passe
derrière elles. Des grilles de fenêtres et des lignes au sol complètent le plan.
"""
from dataclasses import dataclass

import numpy as np

from .construction import Construction, Shape

_AXES = np.eye(3)


@dataclass
class Box:
    lo: tuple
    hi: tuple
    windows: dict = None        # face ("+x", "-z"...) -> (colonnes, rangées)
    weight: float = 1.0         # force du trait (premier plan plus appuyé)


def hidden_by(pts, rays, boxes):
    """Tableau (points, boîtes) : vrai si la boîte cache le point à la caméra."""
    out = np.zeros((len(pts), len(boxes)), bool)
    inv = 1.0 / np.where(np.abs(rays) < 1e-9, 1e-9, rays)
    for i, box in enumerate(boxes):
        t1 = (np.asarray(box.lo, float) + 1e-3 - pts) * inv
        t2 = (np.asarray(box.hi, float) - 1e-3 - pts) * inv
        near, far = np.minimum(t1, t2).max(axis=1), np.maximum(t1, t2).min(axis=1)
        out[:, i] = (far > 1e-3) & (far >= near)
    return out


def _hidden(pts, rays, boxes, skip=-1):
    """Vrai pour les points qu'une boîte (hors `skip`) cache à la caméra."""
    by = hidden_by(pts, rays, boxes)
    if skip >= 0:
        by[:, skip] = False
    return by.any(axis=1)


def _segment(a, b, step=0.25):
    n = max(2, int(np.ceil(np.linalg.norm(np.subtract(b, a)) / step)) + 1)
    return np.linspace(a, b, n)


def construct(boxes, cam, lines=(), blockers=(), near=1.0, only=None):
    """Construction 2D du décor. `lines` : tracés 3D libres (bords de trottoir...).
    `blockers` : volumes de personnages (mannequin.occluders) qui cachent le décor.
    `only` : indices des boîtes à dessiner (toutes continuent de cacher les autres)."""
    con = Construction()

    def add(pts, skip=-1, weight=1.0):
        if cam.dist is not None:
            pts = pts[(pts - cam.target) @ cam.back < cam.dist - near]
        if len(pts) > 1:
            rays = cam.rays(pts)
            hidden = _hidden(pts, rays, boxes, skip)
            for blocker in blockers:
                hidden |= blocker.hidden(pts, rays, ())
            con.shapes.append(Shape(cam.project(pts), hidden, weight=weight))

    for i, box in enumerate(boxes):
        if only is not None and i not in only:
            continue
        lo, hi = np.asarray(box.lo, float), np.asarray(box.hi, float)
        centre = (lo + hi) / 2

        def facing(axis, sign):
            point = centre.copy()
            point[axis] = hi[axis] if sign > 0 else lo[axis]
            return (cam.rays(point[None])[0] @ (_AXES[axis] * sign)) > 0

        for axis in range(3):                   # les quatre arêtes parallèles à chaque axe
            u, v = [k for k in range(3) if k != axis]
            for su in (-1, 1):
                for sv in (-1, 1):
                    if not (facing(u, su) or facing(v, sv)):
                        continue
                    a = lo.copy()
                    a[u] = hi[u] if su > 0 else lo[u]
                    a[v] = hi[v] if sv > 0 else lo[v]
                    b = a.copy()
                    b[axis] = hi[axis]
                    add(_segment(a, b), i, box.weight)
        for face, (cols, rows) in (box.windows or {}).items():
            sign, axis = (1 if face[0] == "+" else -1), "xyz".index(face[1])
            if not facing(axis, sign):
                continue
            u = 2 if axis == 0 else 0           # axe horizontal de la façade
            w, h = (hi[u] - lo[u]) / cols, (hi[1] - lo[1]) / rows
            for c in range(cols):
                for r in range(rows):
                    u0, u1 = lo[u] + (c + 0.22) * w, lo[u] + (c + 0.78) * w
                    v0, v1 = lo[1] + (r + 0.25) * h, lo[1] + (r + 0.75) * h
                    corners = []
                    for uu, vv in ((u0, v0), (u1, v0), (u1, v1), (u0, v1), (u0, v0)):
                        q = np.zeros(3)
                        q[axis] = hi[axis] if sign > 0 else lo[axis]
                        q[u], q[1] = uu, vv
                        corners.append(q)
                    add(np.vstack([_segment(a, b, 0.5)[:-1] for a, b in zip(corners, corners[1:])]
                                  + [corners[-1][None]]), weight=box.weight * 0.8)
    for line in lines:
        pts = np.asarray(line, float)
        add(np.vstack([_segment(a, b, 0.5)[:-1] for a, b in zip(pts, pts[1:])] + [pts[-1:]]))
    return con
