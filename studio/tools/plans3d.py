"""Plans 3D de la partie 2 : la maquette en carton blanc, éclairée comme une vraie pièce.

  seuls   « Puis on les laisse seuls. Et le bouton est là… »  soleil rasant par la porte ;
          la porte se ferme, la lumière se referme, il ne reste que le bouton rouge.
  bouton  « Et le plus étrange, ce n'est pas ce bouton. »     gros plan, faible profondeur de champ ;
          la lumière s'éteint sur « bouton ».
  salon   « chez les gens. Sur leur canapé. »                  le salon en maquette, une lampe chaude ;
          sur « canapé », le participant tombe dans le canapé.

Les temps viennent des mots de la voix (src/data/v01.vo.json), calculés comme dans src/V01.tsx :
si la voix change, on relance et tout se recale.

  python3 tools/plans3d.py SHOT [--test] [--step 2] [--samples 32]
  -> public/3d/<shot>/f0001.png …  (fond transparent + ombres portées, composé sur le papier)
"""
import json
import math
import os
import re
import sys
import unicodedata

import bpy
from mathutils import Euler, Vector

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
ARGS = sys.argv[1:]
SHOT = ARGS[0]
TEST = "--test" in ARGS
STEP = int(ARGS[ARGS.index("--step") + 1]) if "--step" in ARGS else 2
SAMPLES = int(ARGS[ARGS.index("--samples") + 1]) if "--samples" in ARGS else 32
OUT = os.path.join(ROOT, "public", "3d", SHOT)
FPS, LEAD = 30, 24

# ── repères sur la voix (même calcul que src/cues.ts) ───────────────────────────────────────────
VO = {s["id"]: s for s in json.load(open(os.path.join(ROOT, "src/data/v01.vo.json")))["segments"]}


def _norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    return re.sub(r"[^a-z0-9]", "", "".join(c for c in s if unicodedata.category(c) != "Mn"))


def at(pid, w=None, edge="start", nth=0):
    if w is None:
        t = VO[pid][edge]
    else:
        t = [x for x in VO[pid]["words"] if _norm(x["w"]) == _norm(w)][nth][edge]
    return LEAD + round(t * FPS)


# ── maquette (mêmes cotes que tools/maquette.py et src/theme.ts) ────────────────────────────────
ROOM_W, ROOM_D = 4.0, 3.0
WALL_T, WALL_H = 0.15, 1.1
DOOR_X0, DOOR_X1 = 0.95, 1.85
TABLE = dict(x=0.35, y=0.62, w=0.9, d=0.5, h=0.74)
CHAIR = dict(x=0.35, y=0.05, s=0.44, h=0.45)
BUTTON = dict(x=0.6, y=0.66, r=0.055)
hw, hd, t = ROOM_W / 2, ROOM_D / 2, WALL_T
FLOOR = 0.03
Z0, Z1 = FLOOR, FLOOR + WALL_H

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene


def srgb(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((v + 0.055) / 1.055) ** 2.4 if v > 0.04045 else v / 12.92 for v in c) + (1.0,)


def material(name, color, rough=0.85, emission=0.0, sheen=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = srgb(color)
    p.inputs["Roughness"].default_value = rough
    if emission:
        p.inputs["Emission Color"].default_value = srgb(color)
        p.inputs["Emission Strength"].default_value = emission
    if sheen:
        p.inputs["Sheen Weight"].default_value = sheen
    return m


CARD = material("carton", "#F1F0EC", sheen=0.15)
CARD_EDGE = material("carton_tranche", "#E4E2DC")
INK = material("encre", "#2A2824", rough=0.6)
RED = material("bouton", "#D7261E", rough=0.3, emission=0.5)


def bevel(o, w=0.006):
    m = o.modifiers.new("biseau", "BEVEL")
    m.width = w
    m.segments = 2
    m.limit_method = "ANGLE"


def box(name, x0, y0, z0, x1, y1, z1, mat=CARD, bev=0.006):
    bpy.ops.mesh.primitive_cube_add(size=1)
    o = bpy.context.object
    o.name = name
    o.scale = (x1 - x0, y1 - y0, z1 - z0)
    o.location = ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
    bpy.ops.object.transform_apply(scale=True)
    o.data.materials.append(mat)
    if bev:
        bevel(o, min(bev, (x1 - x0) / 3, (y1 - y0) / 3, (z1 - z0) / 3))
    return o


def cyl(name, x, y, z0, r, h, mat=CARD, verts=48, caps="NGON"):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, location=(x, y, z0 + h / 2), vertices=verts, end_fill_type=caps)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(mat)
    bpy.ops.object.shade_smooth()
    bevel(o, min(0.006, h / 3))
    return o


def shell():
    box("sol", -hw - t, -hd - t, 0, hw + t, hd + t, FLOOR, CARD_EDGE)
    box("mur_haut", -hw - t, hd, Z0, hw + t, hd + t, Z1)
    box("mur_gauche", -hw - t, -hd - t, Z0, -hw, hd, Z1)
    box("mur_droit", hw, -hd - t, Z0, hw + t, hd, Z1)
    box("mur_bas_a", -hw, -hd - t, Z0, DOOR_X0, -hd, Z1)
    box("mur_bas_b", DOOR_X1, -hd - t, Z0, hw, -hd, Z1)
    bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, 0))
    bpy.context.object.is_shadow_catcher = True


def lab_furniture():
    tx, ty, tw, td, th = TABLE["x"], TABLE["y"], TABLE["w"], TABLE["d"], TABLE["h"]
    box("plateau", tx - tw / 2, ty - td / 2, Z0 + th - 0.03, tx + tw / 2, ty + td / 2, Z0 + th)
    for sx in (-1, 1):
        for sy in (-1, 1):
            lx, ly = tx + sx * (tw / 2 - 0.04), ty + sy * (td / 2 - 0.04)
            box("pied", lx - 0.02, ly - 0.02, Z0, lx + 0.02, ly + 0.02, Z0 + th - 0.03, bev=0.003)
    cx, cy, cs, ch = CHAIR["x"], CHAIR["y"], CHAIR["s"], CHAIR["h"]
    box("assise", cx - cs / 2, cy - cs / 2, Z0 + ch - 0.03, cx + cs / 2, cy + cs / 2, Z0 + ch)
    for sx in (-1, 1):
        for sy in (-1, 1):
            lx, ly = cx + sx * (cs / 2 - 0.03), cy + sy * (cs / 2 - 0.03)
            box("pied_c", lx - 0.015, ly - 0.015, Z0, lx + 0.015, ly + 0.015, Z0 + ch - 0.03, bev=0.003)
    box("dossier", cx - cs / 2, cy - cs / 2, Z0 + ch, cx + cs / 2, cy - cs / 2 + 0.03, Z0 + ch + 0.42)
    bx, by, br = BUTTON["x"], BUTTON["y"], BUTTON["r"]
    top = Z0 + th
    box("boitier", bx - 0.09, by - 0.07, top, bx + 0.09, by + 0.07, top + 0.04)
    b = cyl("bouton", bx, by, top + 0.04, br, 0.03, RED)
    return b


def person(x, y, z):
    """Le participant : un pion d'encre (une personne = un point, comme dans les plans)."""
    body = cyl("corps", x, y, z, 0.12, 0.5, INK)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, location=(x, y, z + 0.64), segments=48, ring_count=24)
    head = bpy.context.object
    head.data.materials.append(INK)
    bpy.ops.object.shade_smooth()
    bpy.ops.object.empty_add(location=(x, y, z))
    root = bpy.context.object
    for o in (body, head):
        o.parent = root
        o.matrix_parent_inverse = root.matrix_world.inverted()
    return root


def world(color, strength):
    w = bpy.data.worlds.new("monde")
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = srgb(color)
    w.node_tree.nodes["Background"].inputs[1].default_value = strength
    scene.world = w


def sun(elev, azim, energy, angle=2.0, color="#FFF4E6"):
    """elev : hauteur du soleil (°) ; azim : 0 = vient de -y (côté porte), + = dévie vers -x."""
    bpy.ops.object.light_add(type="SUN", rotation=Euler((math.radians(90 - elev), 0, math.radians(azim))))
    s = bpy.context.object.data
    s.energy = energy
    s.angle = math.radians(angle)
    s.color = srgb(color)[:3]
    return s


def camera(lens=40):
    bpy.ops.object.camera_add()
    cam = bpy.context.object
    scene.camera = cam
    cam.data.lens = lens
    cam.data.clip_start, cam.data.clip_end = 0.05, 200
    return cam


def look(cam, pos, target, f):
    cam.location = pos
    cam.rotation_euler = (Vector(target) - Vector(pos)).to_track_quat("-Z", "Y").to_euler()
    cam.keyframe_insert("location", frame=f)
    cam.keyframe_insert("rotation_euler", frame=f)


def smooth(u):
    u = max(0.0, min(1.0, u))
    return u * u * (3 - 2 * u)


def orbit(target, dist, elev, azim):
    e, a = math.radians(elev), math.radians(azim)
    return Vector(target) + Vector((dist * math.cos(e) * math.sin(a), -dist * math.cos(e) * math.cos(a), dist * math.sin(e)))


def key_emission(mat, f, v):
    s = mat.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
    s.default_value = v
    s.keyframe_insert("default_value", frame=f)


# ── les plans ───────────────────────────────────────────────────────────────────────────────────
if SHOT == "seuls":
    t0 = at("p10") - 4
    N = at("p11") - 4 - t0 + 2
    door_f = at("p10", "seuls") - t0 + 1
    button_f = at("p10", "bouton") - t0 + 1
    again_f = at("p10", "remettre") - t0 + 1
    shell()
    lab_furniture()
    person(CHAIR["x"], CHAIR["y"] + 0.04, Z0 + CHAIR["h"])
    # la porte : battant sur charnière en DOOR_X1, ouvert vers l'intérieur, se rabat contre le mur
    LW = DOOR_X1 - DOOR_X0 - 0.01
    leaf = box("porte", 0, -0.02, 0, LW, 0.02, WALL_H - 0.02)
    bpy.ops.object.empty_add(location=(DOOR_X1, -hd - 0.02, Z0))
    hinge = bpy.context.object
    leaf.parent = hinge
    leaf.location = (-LW, 0, 0)  # le maillage va de 0 à LW (box fige la position) : fermé, il longe le mur vers -x
    for f, ang in ((1, -90), (door_f, -90), (door_f + 16, 0)):
        hinge.rotation_euler = (0, 0, math.radians(ang))
        hinge.keyframe_insert("rotation_euler", frame=f)
    for fc in hinge.animation_data.action.fcurves if hasattr(hinge.animation_data.action, "fcurves") else []:
        for kp in fc.keyframe_points:
            kp.interpolation = "QUAD"
            kp.easing = "EASE_IN"
    # soleil rasant, chaud, qui entre par la porte et traverse la pièce jusqu'à la chaise ;
    # le reste de la pièce dans une ombre froide. Caméra en contre-jour, face à la porte.
    sun(elev=11, azim=30, energy=9.0, angle=1.2, color="#FFDDB0")
    world("#AEBBCB", 0.16)
    # le bouton s'allume sur « bouton », pulse sur « remettre »
    key_emission(RED, 1, 0.4)
    key_emission(RED, button_f, 0.4)
    key_emission(RED, button_f + 8, 6.0)
    for i in range(3):
        key_emission(RED, again_f + i * 9, 12.0)
        key_emission(RED, again_f + i * 9 + 5, 5.0)
    cam = camera(lens=35)
    for f in range(1, N + 1):
        u = smooth(f / N)
        tgt = Vector((0.75, -0.35, 0.3)).lerp(Vector((0.55, 0.35, 0.65)), u)
        look(cam, orbit(tgt, 7.2 - 1.9 * u, 41 - 3 * u, 158 - 12 * u), tgt, f)

elif SHOT == "bouton":
    t0 = at("p18") - 4
    N = at("p19") - 1 - t0 + 2
    gone_f = at("p18", "bouton", "end") - t0 + 1
    shell()
    btn = lab_furniture()
    person(CHAIR["x"], CHAIR["y"] + 0.04, Z0 + CHAIR["h"])
    world("#AEBBCB", 0.14)
    sun(elev=14, azim=30, energy=7.0, angle=1.2, color="#FFDDB0")  # le même soleil rasant que « seuls »
    key_emission(RED, 1, 1.4)
    key_emission(RED, gone_f, 1.4)
    key_emission(RED, gone_f + 8, 0.0)
    bt = Vector((BUTTON["x"], BUTTON["y"], Z0 + TABLE["h"] + 0.06))
    cam = camera(lens=70)
    cam.data.dof.use_dof = True
    cam.data.dof.focus_distance = 1.0
    cam.data.dof.aperture_fstop = 2.8
    for f in range(1, N + 1):
        u = smooth(f / N)
        # de l'autre côté de la table : le participant, flou, derrière le bouton
        pos = orbit(bt, 1.25 - 0.2 * u, 15 + 3 * u, 132 - 10 * u)
        look(cam, pos, bt, f)
        cam.data.dof.focus_distance = (pos - bt).length
        cam.data.dof.keyframe_insert("focus_distance", frame=f)
    # la lumière tombe sur « bouton »
    s = bpy.data.lights[0]
    s.keyframe_insert("energy", frame=gone_f)
    s.energy = 0.25
    s.keyframe_insert("energy", frame=gone_f + 10)
    bg = scene.world.node_tree.nodes["Background"].inputs[1]
    bg.keyframe_insert("default_value", frame=gone_f)
    bg.default_value = 0.08
    bg.keyframe_insert("default_value", frame=gone_f + 10)

elif SHOT == "salon":
    t0 = at("p16", "chez") - 3
    N = at("p16", "Un") - 4 - t0 + 2
    drop_f = at("p16", "canapé") - t0 + 1
    shell()
    WARM = material("coussin", "#ECE8E0", sheen=0.3)
    RUG = material("tapis", "#DCD7CC", rough=1.0)
    # tapis, canapé contre le mur du haut, table basse, meuble télé, plante, lampe
    box("tapis", -1.75, -0.55, Z0, 0.55, 1.1, Z0 + 0.008, RUG, bev=0)
    box("canape_base", -1.6, 0.62, Z0, 0.4, 1.47, Z0 + 0.36)
    box("coussin_a", -1.4, 0.64, Z0 + 0.36, -0.61, 1.27, Z0 + 0.46, WARM, bev=0.02)
    box("coussin_b", -0.59, 0.64, Z0 + 0.36, 0.2, 1.27, Z0 + 0.46, WARM, bev=0.02)
    box("dossier", -1.6, 1.27, Z0 + 0.36, 0.4, 1.47, Z0 + 0.82, WARM, bev=0.02)
    box("accoudoir_g", -1.6, 0.62, Z0 + 0.36, -1.4, 1.27, Z0 + 0.6, WARM, bev=0.02)
    box("accoudoir_d", 0.2, 0.62, Z0 + 0.36, 0.4, 1.27, Z0 + 0.6, WARM, bev=0.02)
    box("table_basse", -1.05, -0.12, Z0 + 0.34, -0.15, 0.3, Z0 + 0.38)
    for sx in (-1.0, -0.2):
        for sy in (-0.07, 0.25):
            box("pied_tb", sx - 0.02, sy - 0.02, Z0, sx + 0.02, sy + 0.02, Z0 + 0.34, bev=0.003)
    box("meuble_tv", -1.4, -1.48, Z0, 0.1, -1.18, Z0 + 0.42)
    box("tv", -1.2, -1.36, Z0 + 0.42, -0.1, -1.32, Z0 + 1.02)
    SCREEN = material("ecran", "#9FB6CC", rough=0.2, emission=0.6)
    box("ecran", -1.17, -1.315, Z0 + 0.45, -0.13, -1.31, Z0 + 0.99, SCREEN, bev=0)
    cyl("pot", 1.55, 1.1, Z0, 0.16, 0.3)
    bpy.ops.mesh.primitive_ico_sphere_add(radius=0.3, subdivisions=4, location=(1.55, 1.1, Z0 + 0.62))
    bpy.context.object.data.materials.append(CARD)
    bpy.ops.object.shade_smooth()
    cyl("lampe_pied", 0.75, 1.25, Z0, 0.14, 0.02)
    cyl("lampe_tige", 0.75, 1.25, Z0, 0.012, 1.0)
    SHADE = material("abat_jour", "#F3E3C6", rough=0.9, emission=1.6)
    shade = cyl("abat_jour", 0.75, 1.25, Z0 + 0.9, 0.17, 0.22, SHADE, caps="NOTHING")
    bpy.ops.object.light_add(type="POINT", location=(0.75, 1.25, Z0 + 0.98))
    lamp = bpy.context.object.data
    lamp.energy = 320
    lamp.shadow_soft_size = 0.05
    lamp.color = srgb("#FFB46B")[:3]
    world("#9FAEC2", 0.2)
    sun(elev=22, azim=-130, energy=0.8, angle=3, color="#CFDDF0")  # lune froide par-dessus les murs
    # le participant tombe dans le canapé sur « canapé »
    p = person(-0.6, 0.98, Z0 + 0.46)
    for f, z, s in ((1, 2.6, 0.0), (drop_f - 1, 2.6, 0.0), (drop_f, 1.4, 1.0), (drop_f + 6, Z0 + 0.46, 1.0)):
        p.location.z = z
        p.scale = (s, s, s)
        p.keyframe_insert("location", frame=f)
        p.keyframe_insert("scale", frame=f)
    for f, sz in ((drop_f + 6, 1.0), (drop_f + 8, 0.82), (drop_f + 12, 1.06), (drop_f + 16, 1.0)):
        p.scale = (1.0 + (1.0 - sz) * 0.5, 1.0 + (1.0 - sz) * 0.5, sz)
        p.keyframe_insert("scale", frame=f)
    cam = camera(lens=36)
    for f in range(1, N + 1):
        u = smooth(f / N)
        tgt = Vector((-0.35, 0.25, 0.35))
        look(cam, orbit(tgt, 7.0 - 1.3 * u, 38 - 3 * u, -30 + 12 * u), tgt, f)
else:
    raise SystemExit(f"plan inconnu : {SHOT}")

# ── rendu ───────────────────────────────────────────────────────────────────────────────────────
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 16 if TEST else SAMPLES
scene.cycles.use_denoising = True
scene.cycles.max_bounces = 6
scene.render.use_persistent_data = True
scene.render.film_transparent = True
scene.render.resolution_x, scene.render.resolution_y = 1920, 1080
scene.render.fps = FPS
scene.frame_start, scene.frame_end = 1, N
try:
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"
except TypeError:
    scene.view_settings.view_transform = "Standard"
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"

scene.render.use_freestyle = True
scene.render.line_thickness_mode = "ABSOLUTE"
scene.render.line_thickness = 1.1
fs = scene.view_layers[0].freestyle_settings
ls = fs.linesets[0] if fs.linesets else fs.linesets.new("encre")
if ls.linestyle is None:
    ls.linestyle = bpy.data.linestyles.new("encre")
ls.select_by_visibility = True
ls.select_crease = True
ls.select_border = True
ls.select_silhouette = True
ls.linestyle.color = srgb("#2A2824")[:3]
ls.linestyle.alpha = 0.55

os.makedirs(OUT, exist_ok=True)
json.dump({"frames": N, "step": STEP}, open(os.path.join(OUT, "info.json"), "w"))
if TEST:
    frames = [int(x) for x in ARGS[ARGS.index("--test") + 1].split(",")] if len(ARGS) > ARGS.index("--test") + 1 and ARGS[ARGS.index("--test") + 1][0].isdigit() else [1, N // 2, N]
    for f in frames:
        scene.frame_set(f)
        scene.render.filepath = os.path.join(OUT, f"test_{f:03d}.png")
        bpy.ops.render.render(write_still=True)
else:
    scene.frame_step = STEP
    scene.render.filepath = os.path.join(OUT, "f")
    scene.render.use_overwrite = False
    scene.render.use_placeholder = True
    bpy.ops.render.render(animation=True)
print(f"{SHOT}: {N} images")
