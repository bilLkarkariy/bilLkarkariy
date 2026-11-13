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
class Curve:
    """Ligne de construction tracée sur un volume (axe du visage, ligne des yeux...)."""
    joint: str
    points: np.ndarray
    normals: np.ndarray = None      # si fournies : visible seulement là où la surface fait face
    skip: tuple = None              # volumes qui ne la cachent pas (par défaut : le sien)


@dataclass
class Part:
    name: str
    prims: list
    curves: list = field(default_factory=list)
    passes: int = 1


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
    def _ellipsoids(part, frames, steps=7):
        """Les volumes d'une partie, en ellipsoïdes : centres (m, 3) et axes (m, 3, 3)."""
        centers, axes = [], []
        for prim in part.prims:
            if isinstance(prim, Ball):
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

def _sphere(n=320):
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
        # Le contour d'un volume convexe est l'enveloppe de ses points projetés.
        ends = [0, len(centers) - 1] if isinstance(part.prims[0], Tube) and len(part.prims) == 1 \
            else range(len(centers))
        clouds[part.name] = np.vstack([centers[i] + _UNIT @ axes[i].T for i in ends])
    occ.freeze()

    con = Construction()
    for part in model.parts:
        cloud = clouds[part.name]
        pts3 = _densify(cloud[hull(cam.project(cloud))], cam)
        con.shapes.append(Shape(cam.project(pts3), occ.hidden(pts3, cam.rays(pts3), {part.name}),
                                closed=True, passes=part.passes))
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
                        con.shapes.append(Shape(cam.project(pts3[seg]), hidden[seg]))
            else:
                con.shapes.append(Shape(cam.project(pts3), hidden))

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
