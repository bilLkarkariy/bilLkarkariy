"""Le mannequin : un personnage défini par des données, posable et vu sous n'importe quel angle.

Un modèle, c'est un squelette (articulations, longueurs) habillé de volumes
simples (ellipsoïdes, tubes). Une pose, c'est une rotation par articulation.
Les proportions vivent dans le modèle : elles ne peuvent pas dériver d'un
dessin à l'autre.

Repère du personnage : x vers sa gauche, y vers le haut, z devant lui. L'unité
est la hauteur de tête.
"""
from dataclasses import dataclass, field

import numpy as np

from .construction import Construction, Shape, hull


# ---------- rotations ----------

def _cs(deg):
    a = np.radians(deg)
    return np.cos(a), np.sin(a)


def rx(deg):
    """Autour de l'axe latéral. Positif : le haut bascule vers l'avant."""
    c, s = _cs(deg)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]], float)


def ry(deg):
    """Autour de la verticale. Positif : tourne vers la gauche du personnage."""
    c, s = _cs(deg)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]], float)


def rz(deg):
    """Autour de l'axe avant-arrière. Positif : penche vers la droite du personnage."""
    c, s = _cs(deg)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]], float)


def _unit(v):
    v = np.asarray(v, float)
    return v / np.linalg.norm(v)


def _arc(a, b):
    """Plus petite rotation amenant la direction a sur la direction b."""
    a, b = _unit(a), _unit(b)
    v, c = np.cross(a, b), float(a @ b)
    if c < -0.999999:
        return rx(180)
    k = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + k + k @ k / (1 + c)


DOWN = np.array([0.0, -1.0, 0.0])


@dataclass
class To:
    """Oriente un membre vers une direction donnée dans le repère du personnage
    entier (et non de l'os parent) : « la cuisse pointe vers l'avant »."""
    direction: tuple
    twist: float = 0.0


@dataclass
class Level:
    """Pied posé : à plat (pitch = 0) ou sur la pointe (pitch > 0), quel que soit le tibia."""
    pitch: float = 0.0
    yaw: float = 0.0


class Pose:
    def __init__(self, root=(0, 0, 0), ground=True, **joints):
        self.root = np.asarray(root, float)
        self.ground = ground        # pose le point le plus bas des pieds sur le sol
        self.joints = joints


# ---------- modèle ----------

@dataclass
class Ball:
    joint: str
    center: tuple
    radii: tuple


@dataclass
class Tube:
    a: tuple            # (articulation, point local)
    ra: float
    b: tuple
    rb: float


@dataclass
class Sweep:
    """Forme allongée et souple : une suite de stations (articulation, point, rayon)
    reliées par une courbe. Le rayon peut être un couple (largeur, profondeur).
    Sert aux mèches, aux doigts, aux membres dessinés, aux vêtements."""
    stations: list
    start: str = "round"            # "round" : bout arrondi ; "open" : bout ouvert (ourlet)
    end: str = "round"


@dataclass
class Curve:
    """Ligne de construction tracée sur un volume (axe du visage, ligne des yeux...)."""
    joint: str
    points: np.ndarray
    normals: np.ndarray = None      # si fournies : visible seulement là où la surface fait face
    skip: tuple = None              # volumes qui ne la cachent pas (par défaut : le sien)
    weight: float = 1.0
    passes: int = 1


@dataclass
class Part:
    name: str
    prims: list
    curves: list = field(default_factory=list)
    passes: int = 1
    weight: float = 1.0


@dataclass
class Model:
    name: str
    root: tuple                     # position du bassin au repos
    joints: dict                    # nom -> (parent, décalage dans le repère du parent)
    parts: list
    bridges: list                   # paires de volumes reliés par leurs tangentes (la taille)
    marks: dict                     # repères nommés -> (articulation, point local)
    feet: tuple = ("pied_L", "pied_R")

    def solve(self, pose):
        """Cinématique directe : renvoie {articulation: (position, rotation)}."""
        frames = {}
        for name, (parent, offset) in self.joints.items():
            value = pose.joints.get(name)
            if parent is None:
                rot = np.eye(3) if value is None else value
                frames[name] = (np.asarray(self.root, float) + pose.root, rot)
                continue
            ppos, prot = frames[parent]
            if value is None:
                rot = prot
            elif isinstance(value, To):
                rot = _arc(prot @ DOWN, value.direction) @ prot @ ry(value.twist)
            elif isinstance(value, Level):
                fwd = prot @ np.array([0.0, 0.0, 1.0])
                rot = ry(np.degrees(np.arctan2(fwd[0], fwd[2])) + value.yaw) @ rx(value.pitch)
            else:
                rot = prot @ value
            frames[name] = (ppos + prot @ np.asarray(offset, float), rot)
        if pose.ground:
            low = np.inf
            for part in self.parts:
                if part.name in self.feet:
                    centers, axes = self._ellipsoids(part, frames)
                    reach = np.linalg.norm(axes[:, 1, :], axis=1)    # demi-hauteur de chaque volume
                    low = min(low, float((centers[:, 1] - reach).min()))
            frames = {k: (pos - np.array([0.0, low, 0.0]), rot) for k, (pos, rot) in frames.items()}
        return frames

    @staticmethod
    def _ellipsoids(part, frames, steps=12):
        """Les volumes d'une partie, en ellipsoïdes : centres (m, 3) et axes (m, 3, 3)."""
        centers, axes = [], []
        for prim in part.prims:
            if isinstance(prim, Sweep):
                c, x, z, t, rx_, rz_ = sweep_frames(prim, frames)
                depth = np.full(len(c), 0.08)
                depth[0], depth[-1] = max(rx_[0], rz_[0], 0.02), max(rx_[-1], rz_[-1], 0.02)
                centers.extend(c)
                axes.extend(np.stack([x * np.maximum(rx_, 0.004)[:, None], t * depth[:, None],
                                      z * np.maximum(rz_, 0.004)[:, None]], axis=2))
            elif isinstance(prim, Ball):
                pos, rot = frames[prim.joint]
                centers.append(pos + rot @ np.asarray(prim.center, float))
                axes.append(rot @ np.diag(prim.radii))
            else:
                pa = frames[prim.a[0]][0] + frames[prim.a[0]][1] @ np.asarray(prim.a[1], float)
                pb = frames[prim.b[0]][0] + frames[prim.b[0]][1] @ np.asarray(prim.b[1], float)
                for t in np.linspace(0, 1, steps):
                    centers.append(pa + (pb - pa) * t)
                    axes.append(np.eye(3) * (prim.ra + (prim.rb - prim.ra) * t))
        return np.array(centers), np.array(axes)


# ---------- caméra ----------

class Camera:
    """Tourne autour du personnage. yaw = 0 : de face ; 90 : son profil gauche ; 180 : de dos.
    dist = None : vue orthographique (model sheet) ; sinon perspective, en têtes."""

    def __init__(self, yaw=0.0, pitch=0.0, target=(0, 0, 0), dist=None):
        cy, sy = _cs(yaw)
        cp, sp = _cs(pitch)
        self.back = np.array([sy * cp, sp, cy * cp])            # du sujet vers la caméra
        self.right = np.array([cy, 0.0, -sy])
        self.up = np.cross(self.back, self.right)
        self.target, self.dist = np.asarray(target, float), dist

    def project(self, pts):
        rel = np.asarray(pts, float) - self.target
        xy = np.stack([rel @ self.right, rel @ self.up], axis=-1)
        if self.dist is None:
            return xy
        return xy * (self.dist / (self.dist - rel @ self.back))[..., None]

    def rays(self, pts):
        """Direction de chaque point vers l'œil."""
        if self.dist is None:
            return np.broadcast_to(self.back, np.shape(pts)).copy()
        eye = self.target + self.back * self.dist
        v = eye - np.asarray(pts, float)
        return v / np.linalg.norm(v, axis=-1, keepdims=True)


# ---------- du 3D à la construction 2D ----------

def _sphere(n=600):
    i = np.arange(n) + 0.5
    phi, th = np.arccos(1 - 2 * i / n), np.pi * (1 + 5 ** 0.5) * i
    return np.stack([np.cos(th) * np.sin(phi), np.cos(phi), np.sin(th) * np.sin(phi)], axis=1)


_UNIT = _sphere()


class _Occluders:
    def __init__(self):
        self.c, self.inv, self.owner = [], [], []

    def add(self, centers, axes, owner):
        self.c.extend(centers)
        self.inv.extend(np.linalg.inv(axes))
        self.owner.extend([owner] * len(centers))

    def freeze(self):
        self.c, self.inv, self.owner = np.array(self.c), np.array(self.inv), np.array(self.owner)

    def hidden(self, pts, rays, skip):
        """Vrai pour les points qu'un volume (hors `skip`) cache à la caméra."""
        o = np.einsum("mij,nmj->nmi", self.inv, pts[:, None, :] - self.c[None])
        d = np.einsum("mij,nj->nmi", self.inv, rays)
        a, b, c = (d * d).sum(-1), (o * d).sum(-1), (o * o).sum(-1) - 1
        disc = b * b - a * c
        far = (-b + np.sqrt(np.maximum(disc, 0))) / a
        hit = (disc > 0) & (far > 1e-3) & ~np.isin(self.owner, list(skip))[None, :]
        return hit.any(axis=1)


def _catmull(pts, u):
    """Courbe lisse passant par pts, évaluée aux paramètres u (0 .. n-1)."""
    q = np.vstack([2 * pts[0] - pts[1], pts, 2 * pts[-1] - pts[-2]])
    i = np.clip(np.floor(u).astype(int), 0, len(pts) - 2)
    t = (u - i)[:, None]
    a, b, c, d = q[i], q[i + 1], q[i + 2], q[i + 3]
    return 0.5 * (2 * b + (c - a) * t + (2 * a - 5 * b + 4 * c - d) * t ** 2
                  + (3 * b - a - 3 * c + d) * t ** 3)


def sweep_frames(sweep, frames, step=0.05):
    """Échantillonne un Sweep : centres, axes de section (x, z), tangente, rayons."""
    c, x, z, rx_, rz_ = [], [], [], [], []
    for joint, point, r in sweep.stations:
        pos, rot = frames[joint]
        c.append(pos + rot @ np.asarray(point, float))
        x.append(rot[:, 0])
        z.append(rot[:, 2])
        a, b = (r, r) if np.isscalar(r) else r
        rx_.append(a)
        rz_.append(b)
    c = np.array(c)
    u = [i + np.linspace(0, 1, max(2, int(np.ceil(np.linalg.norm(c[i + 1] - c[i]) / step))),
                         endpoint=False) for i in range(len(c) - 1)]
    u = np.concatenate(u + [[len(c) - 1.0]])
    k = np.arange(len(c))
    f = u - np.floor(u)
    smooth = np.floor(u) + f * f * (3 - 2 * f)          # les rayons arrivent à plat sur chaque station

    def along(values, param):
        values = np.asarray(values, float)
        if values.ndim == 1:
            return np.interp(param, k, values)
        return np.stack([np.interp(param, k, values[:, j]) for j in range(values.shape[1])], axis=1)

    centers = _catmull(c, u)
    xs, zs = along(x, u), along(z, u)
    xs /= np.linalg.norm(xs, axis=1, keepdims=True)
    zs /= np.linalg.norm(zs, axis=1, keepdims=True)
    tan = np.gradient(centers, axis=0)
    tan /= np.maximum(np.linalg.norm(tan, axis=1, keepdims=True), 1e-9)
    return centers, xs, zs, tan, along(rx_, smooth), along(rz_, smooth)


def _sweep_outline(sweep, frames, cam):
    """Contour d'un Sweep vu par la caméra : listes de (points 3D, fermé ?, normales 2D sortantes)."""
    c, x, z, _, rx_, rz_ = sweep_frames(sweep, frames)
    c2 = cam.project(c)
    t2 = np.gradient(c2, axis=0)
    length = np.hypot(t2[:, 0], t2[:, 1])
    good = length > 1e-5
    if not good.any():
        t2[:] = (0.0, 1.0)
    else:
        idx = np.flatnonzero(good)
        nearest = idx[np.abs(np.arange(len(c))[:, None] - idx[None]).argmin(axis=1)]
        t2 = t2[nearest] / length[nearest][:, None]
    n2 = np.stack([-t2[:, 1], t2[:, 0]], axis=1)
    n3 = n2[:, :1] * cam.right + n2[:, 1:] * cam.up
    t3 = t2[:, :1] * cam.right + t2[:, 1:] * cam.up
    r = np.sqrt((rx_ * (n3 * x).sum(1)) ** 2 + (rz_ * (n3 * z).sum(1)) ** 2)[:, None]
    left, right = (c + r * n3, n2), ((c - r * n3)[::-1], -n2[::-1])
    ang = np.linspace(0, np.pi, 9)[1:-1, None]

    def cap(i, sign):
        if r[i, 0] < 0.02:                  # pointe : un seul point, sans arrondi
            return c[i][None] + r[i] * sign * t3[i], sign * t2[i][None]
        pts = c[i] + r[i] * sign * (np.cos(ang) * n3[i] + np.sin(ang) * t3[i])
        return pts, sign * (np.cos(ang) * n2[i] + np.sin(ang) * t2[i])

    loop = [left, cap(-1, 1) if sweep.end == "round" else None,
            right, cap(0, -1) if sweep.start == "round" else None]
    if None not in loop:
        return [(np.vstack([p for p, _ in loop]), True, np.vstack([n for _, n in loop]))]
    while loop[-1] is not None:             # fait tourner la boucle pour finir sur une coupure
        loop = loop[1:] + loop[:1]
    out, run = [], []
    for item in loop:
        if item is None:
            if run:
                out.append((np.vstack([p for p, _ in run]), False, np.vstack([n for _, n in run])))
            run = []
        else:
            run.append(item)
    return out


LIGHT = np.array([0.45, -0.89])     # les traits tournés vers le bas à droite sont plus appuyés


def _weights(normals, amount=0.38):
    return 1 + amount * (normals @ LIGHT)


def _outward(xy):
    """Normales sortantes d'un contour fermé parcouru dans le sens direct."""
    d = np.roll(xy, -1, axis=0) - np.roll(xy, 1, axis=0)
    n = np.stack([d[:, 1], -d[:, 0]], axis=1)
    return n / np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-9)


def _densify(pts3, cam, step=0.06):
    """Ajoute des points le long des grands côtés d'un contour fermé, pour que
    chaque tronçon puisse être caché indépendamment."""
    xy = cam.project(pts3)
    out = []
    for i in range(len(pts3)):
        j = (i + 1) % len(pts3)
        k = max(1, int(np.ceil(np.hypot(*(xy[j] - xy[i])) / step)))
        out.append(pts3[i] + (pts3[j] - pts3[i]) * np.linspace(0, 1, k, endpoint=False)[:, None])
    return np.vstack(out)


def construct(model, pose, cam):
    """Projette le modèle posé et renvoie sa construction 2D."""
    frames = model.solve(pose)
    occ = _Occluders()
    clouds = {}
    for part in model.parts:
        centers, axes = model._ellipsoids(part, frames)
        occ.add(centers, axes, part.name)
        if isinstance(part.prims[0], Sweep):
            continue
        # Le contour d'un volume convexe est l'enveloppe de ses points projetés.
        ends = [0, len(centers) - 1] if isinstance(part.prims[0], Tube) and len(part.prims) == 1 \
            else range(len(centers))
        clouds[part.name] = np.vstack([centers[i] + _UNIT @ axes[i].T for i in ends])
    occ.freeze()

    con = Construction()
    for part in model.parts:
        if isinstance(part.prims[0], Sweep):
            for pts3, closed, normals in _sweep_outline(part.prims[0], frames, cam):
                con.shapes.append(Shape(cam.project(pts3),
                                        occ.hidden(pts3, cam.rays(pts3), {part.name}), closed=closed,
                                        passes=part.passes, weight=part.weight, w=_weights(normals)))
        else:
            cloud = clouds[part.name]
            pts3 = _densify(cloud[hull(cam.project(cloud))], cam)
            xy = cam.project(pts3)
            con.shapes.append(Shape(xy, occ.hidden(pts3, cam.rays(pts3), {part.name}), closed=True,
                                    passes=part.passes, weight=part.weight,
                                    w=_weights(_outward(xy))))
        for curve in part.curves:
            pos, rot = frames[curve.joint]
            pts3 = pos + np.asarray(curve.points, float) @ rot.T
            rays = cam.rays(pts3)
            skip = {part.name} if curve.skip is None else set(curve.skip)
            hidden = occ.hidden(pts3, rays, skip)
            if curve.normals is not None:
                facing = ((np.asarray(curve.normals, float) @ rot.T) * rays).sum(axis=1)
                keep = facing > 0.02
                # Une ligne sur la face arrière n'est pas tracée du tout.
                for seg in np.split(np.arange(len(pts3)), np.flatnonzero(np.diff(keep)) + 1):
                    if keep[seg[0]] and len(seg) > 1:
                        con.shapes.append(Shape(cam.project(pts3[seg]), hidden[seg],
                                                passes=curve.passes, weight=curve.weight))
            else:
                con.shapes.append(Shape(cam.project(pts3), hidden, passes=curve.passes,
                                        weight=curve.weight))

    # Les deux tangentes qui relient deux volumes (cage et bassin : la taille).
    for a, b in model.bridges:
        cloud = np.vstack([clouds[a], clouds[b]])
        idx = hull(cam.project(cloud))
        side = idx >= len(clouds[a])
        for i in np.flatnonzero(side != np.roll(side, -1)):
            p, q = cloud[idx[i]], cloud[idx[(i + 1) % len(idx)]]
            pts3 = p + (q - p) * np.linspace(0, 1, 8)[:, None]
            con.shapes.append(Shape(cam.project(pts3), occ.hidden(pts3, cam.rays(pts3), {a, b})))

    for name, (joint, local) in model.marks.items():
        pos, rot = frames[joint]
        con.marks[name] = cam.project(pos + rot @ np.asarray(local, float))
    return con
