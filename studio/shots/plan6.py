"""Plan 6 — « Elle saute ». Tout ce que les étapes partagent sur ce plan :
la caméra, le décor, le cadre et son mouvement, les poses clés et leur timing.
"""
import numpy as np

from studio.engine import poses
from studio.engine.inbetween import Motion
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
    Box((-1.6, 0, 3.9), (14, 2.2, 4.9), weight=1.6),                              # muret
    Box((-1.8, 2.2, 3.75), (14, 2.45, 5.05), weight=1.6),                         # couvertine
    Box((30, 0, -12), (48, 15, 6), windows={"-x": (7, 5), "+z": (6, 5)}),         # immeubles, loin
    Box((34, 0, 10), (56, 21, 30), windows={"-x": (8, 7)}),
    Box((28, 0, -46), (44, 19, -22), windows={"-x": (9, 6), "+z": (6, 6)}),
    Box((40, 0, -80), (64, 26, -54), windows={"-x": (9, 8), "+z": (8, 8)}),
    Box((17.6, 0, -4.2), (18.0, 14, -3.8)),                                       # lampadaire
    Box((16.0, 13.6, -4.3), (18.0, 14, -3.7)),
]
SOL = [[(-1.6, 0, -60), (-1.6, 0, 14)], [(14, 0, -60), (14, 0, 30)],            # bords du trottoir
       [(22, 0, -80), (22, 0, 30)]]

# Poses clés : (image, nom, type, pose, placement, flow).
# Placement : z du bassin ; ou (articulation, z) pour planter un pied à cet endroit ; ou None
# en l'air. Flow : 1 = on traverse la pose sans ralentir, 0 = arrêt complet.
TAKEOFF, LANDING = 11, 26
PIED = "ankle_R"
POSE_KEYS = [
    (1, "arrivée", "clé", poses.COURSE, -3.6, 1.0),
    (5, "appui", "clé", poses.APPUI, (PIED, 1.0), 0.8),
    (8, "élan", "clé", poses.ELAN, (PIED, 1.0), 0.25),
    (11, "détente", "clé", poses.DETENTE, (PIED, 1.0), 1.0),
    (15, "montée", "passage", poses.MONTEE, None, 1.0),
    (18, "sommet", "clé", poses.SOMMET, None, 1.0),
    (23, "descente", "passage", poses.DESCENTE, None, 1.0),
    (26, "contact", "clé", poses.CONTACT, (PIED, 8.2), 1.0),
    (28, "amorti", "clé", poses.RECEPTION, (PIED, 8.2), 0.3),
    (30, "rétablissement", "clé", poses.RETABLI, (PIED, 8.2), 0.0),
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


def _on_ground(model, pose, place):
    """Pose posée au sol : bassin à z, ou pied planté à z."""
    if isinstance(place, tuple):
        joint, z = place
        return pose.at(z=z - model.solve(pose.at())[joint][0][2])
    return pose.at(z=place)


def air(model, image):
    """Position du bassin en l'air (y, z) : chute libre entre la détente et le contact."""
    ground = {f: (pose, place) for f, _, _, pose, place, _ in POSE_KEYS if place is not None}
    _, y0, z0 = model.solve(_on_ground(model, *ground[TAKEOFF]))["pelvis"][0]
    _, y1, z1 = model.solve(_on_ground(model, *ground[LANDING]))["pelvis"][0]
    t = (image - TAKEOFF) / (LANDING - TAKEOFF)
    duration = (LANDING - TAKEOFF) / FPS
    rise = G * duration ** 2 / 2 / HEAD_M              # hauteur gagnée, en têtes, au facteur t(1-t)
    return y0 + (y1 - y0) * t + rise * t * (1 - t), z0 + (z1 - z0) * t


def keys(model):
    """Les poses clés placées dans le décor : liste de dicts (image, nom, type, pose, bassin)."""
    out = []
    for image, name, kind, pose, place, flow in POSE_KEYS:
        if place is None:
            y, z = air(model, image)
            placed = pose.at(y=y - model.root[1], z=z)
        else:
            placed = _on_ground(model, pose, place)
        pelvis = model.solve(placed)["pelvis"][0]
        out.append(dict(image=image, name=name, kind=kind, pose=placed, pelvis=pelvis, flow=flow))
    return out


def motion(model):
    """Le mouvement complet : renvoie une fonction image -> pose (images décimales admises)."""
    placed = keys(model)
    base = Motion(model, [(k["image"], k["pose"], k["flow"]) for k in placed])
    pins = {k["image"]: model.solve(k["pose"])[PIED][0][2]
            for k, spec in zip(placed, POSE_KEYS) if isinstance(spec[4], tuple)}

    def at(image):
        pose = base.at(image)
        if TAKEOFF < image < LANDING:               # en l'air : la chute libre commande
            y, z = air(model, image)
            pose.root[1:] = y - model.root[1], z
            return pose
        pose.ground = True                          # au sol : le pied le plus bas touche terre
        planted = [f for f in pins if abs(f - image) <= 3]
        if TAKEOFF - 6 <= image <= TAKEOFF or image >= LANDING:
            target = pins[min(planted, key=lambda f: abs(f - image))]
            pose.root[2] += target - model.solve(pose)[PIED][0][2]      # le pied ne glisse pas
        return pose

    return at
