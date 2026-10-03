"""Maquette d'architecte de la pièce vide (hook, 0:02-0:07).

Carton blanc, coupe à 1,1 m, un seul élément de couleur : le bouton rouge.
Caméra orthographique : axonométrie -> vue de dessus exacte, pour enchaîner
sur le plan 2D (même échelle : ORTHO_END m = 1920 px, centre = origine).

Usage : python3 tools/maquette.py [--test] [--frames N] [--res 1920x1080]
"""
import math
import os
import sys

import bpy
from mathutils import Euler, Vector

ARGS = sys.argv[1:]
TEST = "--test" in ARGS
FRAMES = int(ARGS[ARGS.index("--frames") + 1]) if "--frames" in ARGS else 165
RES = ARGS[ARGS.index("--res") + 1] if "--res" in ARGS else "1920x1080"
W, H = (int(v) for v in RES.split("x"))
OUT = os.path.join(os.path.dirname(__file__), "..", "public", "3d", "maquette")

# Géométrie partagée avec src/plan.ts (garder synchronisé)
ROOM_W, ROOM_D = 4.0, 3.0   # intérieur, m
WALL_T, WALL_H = 0.15, 1.1  # épaisseur, hauteur de coupe
DOOR_X0, DOOR_X1 = 0.95, 1.85  # ouverture dans le mur du bas (y = -ROOM_D/2)
TABLE = dict(x=0.35, y=0.62, w=0.9, d=0.5, h=0.74)
CHAIR = dict(x=0.35, y=0.05, s=0.44, h=0.45)
BUTTON = dict(x=0.6, y=0.66, r=0.055)
ORTHO_END = 7.2

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene


def srgb(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((v + 0.055) / 1.055) ** 2.4 if v > 0.04045 else v / 12.92 for v in c) + (1.0,)


def material(name, color, rough=0.85, emission=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = srgb(color)
    p.inputs["Roughness"].default_value = rough
    if emission:
        p.inputs["Emission Color"].default_value = srgb(color)
        p.inputs["Emission Strength"].default_value = emission
    return m


CARD = material("carton", "#F1F0EC")
CARD_EDGE = material("carton_tranche", "#E4E2DC")
RED = material("bouton", "#D7261E", rough=0.35, emission=0.6)


def box(name, x0, y0, z0, x1, y1, z1, mat=CARD):
    bpy.ops.mesh.primitive_cube_add(size=1)
    o = bpy.context.object
    o.name = name
    o.scale = (x1 - x0, y1 - y0, z1 - z0)
    o.location = ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
    bpy.ops.object.transform_apply(scale=True)
    o.data.materials.append(mat)
    return o


hw, hd, t = ROOM_W / 2, ROOM_D / 2, WALL_T
FLOOR = 0.03
# socle de la pièce
box("sol", -hw - t, -hd - t, 0, hw + t, hd + t, FLOOR, CARD_EDGE)
z0, z1 = FLOOR, FLOOR + WALL_H
box("mur_haut", -hw - t, hd, z0, hw + t, hd + t, z1)
box("mur_gauche", -hw - t, -hd - t, z0, -hw, hd, z1)
box("mur_droit", hw, -hd - t, z0, hw + t, hd, z1)
box("mur_bas_a", -hw, -hd - t, z0, DOOR_X0, -hd, z1)
box("mur_bas_b", DOOR_X1, -hd - t, z0, hw, -hd, z1)

# table
tx, ty, tw, td, th = TABLE["x"], TABLE["y"], TABLE["w"], TABLE["d"], TABLE["h"]
box("plateau", tx - tw / 2, ty - td / 2, z0 + th - 0.03, tx + tw / 2, ty + td / 2, z0 + th)
for sx in (-1, 1):
    for sy in (-1, 1):
        lx, ly = tx + sx * (tw / 2 - 0.04), ty + sy * (td / 2 - 0.04)
        box("pied", lx - 0.02, ly - 0.02, z0, lx + 0.02, ly + 0.02, z0 + th - 0.03)

# chaise (dossier côté -y, face à la table)
cx, cy, cs, ch = CHAIR["x"], CHAIR["y"], CHAIR["s"], CHAIR["h"]
box("assise", cx - cs / 2, cy - cs / 2, z0 + ch - 0.03, cx + cs / 2, cy + cs / 2, z0 + ch)
for sx in (-1, 1):
    for sy in (-1, 1):
        lx, ly = cx + sx * (cs / 2 - 0.03), cy + sy * (cs / 2 - 0.03)
        box("pied_c", lx - 0.015, ly - 0.015, z0, lx + 0.015, ly + 0.015, z0 + ch - 0.03)
box("dossier", cx - cs / 2, cy - cs / 2, z0 + ch, cx + cs / 2, cy - cs / 2 + 0.03, z0 + ch + 0.42)

# boîtier + bouton
bx, by, br = BUTTON["x"], BUTTON["y"], BUTTON["r"]
top = z0 + th
box("boitier", bx - 0.09, by - 0.07, top, bx + 0.09, by + 0.07, top + 0.04)
bpy.ops.mesh.primitive_cylinder_add(radius=br, depth=0.03, location=(bx, by, top + 0.055), vertices=48)
bpy.context.object.data.materials.append(RED)
bpy.ops.object.shade_smooth()

# sol de papier : attrape-ombre (le fond reste transparent, composé sur le papier dans Remotion)
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
bpy.context.object.is_shadow_catcher = True

# lumière : soleil doux en haut à gauche, ciel gris clair
bpy.ops.object.light_add(type="SUN", rotation=Euler((math.radians(38), 0, math.radians(-35))))
sun = bpy.context.object.data
sun.energy = 2.1
sun.angle = math.radians(6)
world = bpy.data.worlds.new("monde")
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = srgb("#E4E4E2")
world.node_tree.nodes["Background"].inputs[1].default_value = 1.25
scene.world = world

# caméra orthographique, une trajectoire continue
bpy.ops.object.camera_add()
cam = bpy.context.object
scene.camera = cam
cam.data.type = "ORTHO"
cam.data.clip_start, cam.data.clip_end = 0.1, 200


def ease(u):  # easeInOutCubic, ralentie au début
    return 4 * u ** 3 if u < 0.5 else 1 - (-2 * u + 2) ** 3 / 2


for f in range(FRAMES):
    u = f / (FRAMES - 1)
    e = ease(min(1.0, u / 0.92))  # tient la vue de dessus sur les dernières images
    elev = math.radians(44 + (90 - 44) * e)
    azim = math.radians(-36 * (1 - e))
    target = Vector((0, 0.1 * (1 - e), 0.45 * (1 - e)))
    d = 50
    pos = target + Vector((
        d * math.cos(elev) * math.sin(azim),
        -d * math.cos(elev) * math.cos(azim),
        d * math.sin(elev),
    ))
    cam.location = pos
    cam.rotation_euler = (Vector(target) - pos).to_track_quat("-Z", "Y").to_euler()
    cam.data.ortho_scale = 9.4 + (ORTHO_END - 9.4) * ease(u)
    cam.keyframe_insert("location", frame=f + 1)
    cam.keyframe_insert("rotation_euler", frame=f + 1)
    cam.data.keyframe_insert("ortho_scale", frame=f + 1)

# rendu
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 12 if TEST else 10
scene.render.use_persistent_data = True
scene.cycles.use_denoising = True
scene.cycles.max_bounces = 4
scene.render.film_transparent = True
scene.render.resolution_x, scene.render.resolution_y = W, H
scene.render.fps = 30
scene.frame_start, scene.frame_end = 1, FRAMES
scene.view_settings.view_transform = "Standard"
scene.view_settings.exposure = -0.25
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"

# traits d'encre (Freestyle) : la maquette est « dessinée », comme le plan
scene.render.use_freestyle = True
scene.render.line_thickness_mode = "ABSOLUTE"
scene.render.line_thickness = 1.3 * W / 1920
fs = scene.view_layers[0].freestyle_settings
ls = fs.linesets[0] if fs.linesets else fs.linesets.new("encre")
if ls.linestyle is None:
    ls.linestyle = bpy.data.linestyles.new("encre")
ls.select_by_visibility = True
ls.select_crease = True
ls.select_border = True
ls.select_silhouette = True
ls.linestyle.color = srgb("#2A2824")[:3]
ls.linestyle.alpha = 0.75

os.makedirs(OUT, exist_ok=True)
scene.render.filepath = os.path.join(os.path.abspath(OUT), "f")
if TEST:
    for f in (1, FRAMES // 2, FRAMES):
        scene.frame_set(f)
        scene.render.filepath = os.path.join(os.path.abspath(OUT), f"test_{f:03d}.png")
        bpy.ops.render.render(write_still=True)
else:
    scene.frame_step = int(ARGS[ARGS.index("--step") + 1]) if "--step" in ARGS else 1
    scene.render.use_overwrite = False  # reprend là où on s'est arrêté
    scene.render.use_placeholder = True
    bpy.ops.render.render(animation=True)
