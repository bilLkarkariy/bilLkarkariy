"""Plan 6 — « Elle saute ». Tout ce que les étapes partagent sur ce plan :
la caméra, le décor, le cadre et son mouvement, les poses clés et leur timing.
"""
import numpy as np

from studio.engine import poses
from studio.engine.mannequin import Camera
from studio.engine.scene import Box

FPS, FRAMES = 24, 30
HEAD_M, G = 0.231, 9.81                     # une tête en mètres ; pesanteur

# Feuille de layout : taille, position de la cible caméra, pixels par tête.
W, H = 4800, 3200
ORIGIN, SCALE = (2300, 1750), 185
FRAME = (3840, 2160)                        # le cadre 16:9 : plan large, Kaya y tient en entier
# Mouvement du cadre : (image, coin haut-gauche). Il suit le saut, puis redescend.
FRAME_A, FRAME_B, FRAME_C = (160, 960), (640, 330), (860, 960)
CAMERA_KEYS = [(1, FRAME_A), (9, FRAME_A), (18, FRAME_B), (20, FRAME_B), (27, FRAME_C),
               (30, FRAME_C)]

# Caméra basse, presque de profil : Kaya traverse le cadre de gauche à droite.
CAM = Camera(yaw=-65, pitch=-14, target=(0, 4.5, 4), dist=16)

# Décor, en têtes. Kaya court le long de z et saute le muret.
DECOR = [
    Box((-1.6, 0, 3.8), (14, 3.0, 5.0), weight=1.6),                              # muret
    Box((-1.8, 3.0, 3.6), (14, 3.3, 5.2), weight=1.6),                            # couvertine
    Box((30, 0, -12), (48, 15, 6), windows={"-x": (7, 5), "+z": (6, 5)}),         # immeubles, loin
    Box((34, 0, 10), (56, 21, 30), windows={"-x": (8, 7)}),
    Box((28, 0, -46), (44, 19, -22), windows={"-x": (9, 6), "+z": (6, 6)}),
    Box((40, 0, -80), (64, 26, -54), windows={"-x": (9, 8), "+z": (8, 8)}),
    Box((17.6, 0, -4.2), (18.0, 14, -3.8)),                                       # lampadaire
    Box((16.0, 13.6, -4.3), (18.0, 14, -3.7)),
]
SOL = [[(-1.6, 0, -60), (-1.6, 0, 14)], [(14, 0, -60), (14, 0, 30)],            # bords du trottoir
       [(22, 0, -80), (22, 0, 30)]]

# Poses clés : (image, nom, type, pose, position z au sol ou None en l'air).
TAKEOFF, LANDING = 11, 26
POSE_KEYS = [
    (1, "arrivée", "clé", poses.COURSE, -3.4),
    (5, "appui", "clé", poses.APPUI, -1.0),
    (8, "élan", "clé", poses.ELAN, 0.6),
    (11, "détente", "clé", poses.DETENTE, 1.6),
    (15, "montée", "passage", poses.MONTEE, None),
    (18, "sommet", "clé", poses.SOMMET, None),
    (23, "descente", "passage", poses.DESCENTE, None),
    (26, "contact", "clé", poses.CONTACT, 7.6),
    (28, "amorti", "clé", poses.RECEPTION, 7.9),
    (30, "rétablissement", "clé", poses.RETABLI, 8.0),
]


def to_px(points):
    return np.asarray(ORIGIN, float) + CAM.project(np.asarray(points, float)) * (SCALE, -SCALE)


def frame_corner(image):
    """Coin du cadre à une image donnée : départ et arrivée en douceur entre deux positions."""
    for (f0, c0), (f1, c1) in zip(CAMERA_KEYS, CAMERA_KEYS[1:]):
        if image <= f1:
            t = (image - f0) / (f1 - f0)
            t = t * t * (3 - 2 * t)
            return np.asarray(c0, float) + (np.asarray(c1, float) - c0) * t
    return np.asarray(CAMERA_KEYS[-1][1], float)


def air(model, image):
    """Position du bassin en l'air (y, z) : chute libre entre la détente et le contact."""
    ground = {f: (pose, z) for f, _, _, pose, z in POSE_KEYS if z is not None}
    (p0, z0), (p1, z1) = ground[TAKEOFF], ground[LANDING]
    y0 = model.solve(p0.at(z=z0))["pelvis"][0][1]
    y1 = model.solve(p1.at(z=z1))["pelvis"][0][1]
    t = (image - TAKEOFF) / (LANDING - TAKEOFF)
    duration = (LANDING - TAKEOFF) / FPS
    rise = G * duration ** 2 / 2 / HEAD_M              # hauteur gagnée, en têtes, au facteur t(1-t)
    return y0 + (y1 - y0) * t + rise * t * (1 - t), z0 + (z1 - z0) * t


def keys(model):
    """Les poses clés placées dans le décor : liste de dicts (image, nom, type, pose, bassin)."""
    out = []
    for image, name, kind, pose, z in POSE_KEYS:
        if z is None:
            y, z = air(model, image)
            placed = pose.at(y=y - model.root[1], z=z)
        else:
            placed = pose.at(z=z)
        pelvis = model.solve(placed)["pelvis"][0]
        out.append(dict(image=image, name=name, kind=kind, pose=placed, pelvis=pelvis))
    return out
