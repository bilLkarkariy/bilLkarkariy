"""Plans 3D : la maquette en carton blanc, éclairée comme une vraie pièce. C'est le fil rouge de la vidéo.

  seuls   « Puis on les laisse seuls. Et le bouton est là… »  soleil rasant par la porte ;
          la porte se ferme, la lumière se referme, il ne reste que le bouton rouge.
  bouton  « Et le plus étrange, ce n'est pas ce bouton. »     gros plan, faible profondeur de champ ;
          la lumière s'éteint sur « bouton ».
  salon   « chez les gens. Sur leur canapé. »                  le salon en maquette, une lampe chaude ;
          sur « canapé », le participant tombe dans le canapé.
  vide    « Imagine une pièce sans aucun meuble… Le téléphone, c'est la porte. »
          la chaise et la table disparaissent sur leurs mots ; le pion entre, tourne, touche les murs,
          cherche la porte ; sur « téléphone », la pièce s'éteint et la porte s'allume comme un écran.
  khalwa  « Dans une khalwa, on se retire volontairement. Traditionnellement quarante jours… »
          le pion entre et ferme la porte lui-même ; une petite lumière au centre ; sur « quarante jours »,
          le soleil tourne au-dessus de la maquette (jours et nuits en accéléré), la lumière reste.
  dhikr   « tu poses un meuble dans la pièce vide. Un point fixe. L'esprit part, tu le ramènes… »
          le point d'or se pose au centre ; le pion s'en éloigne et y revient, deux fois.
  meublee « Tu n'as juste jamais meublé la pièce. »   la même pièce, lumière dorée, le pion assis
          près du point d'or ; la caméra s'élève.

Les temps viennent des mots de la voix (src/data/v01.vo.json), calculés comme dans src/V01.tsx :
si la voix change, on relance et tout se recale.

  python3 tools/plans3d.py SHOT [--test [f,f,…]] [--pct 40] [--step 2] [--samples 32] [--gpu]
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


def group(name, objs, origin):
    """Un repère au sol qui porte des objets : le mettre à l'échelle 0 les fait disparaître sur place."""
    bpy.ops.object.empty_add(location=origin)
    root = bpy.context.object
    root.name = name
    for o in objs:
        o.parent = root
        o.matrix_parent_inverse = root.matrix_world.inverted()
    return root


def vanish(root, f, dur=8):
    """Le groupe gonfle à peine puis rentre dans le sol (un objet qu'on retire de la pièce)."""
    for k, sc in ((1, 1.0), (f, 1.0), (f + 3, 1.05), (f + dur, 0.0)):
        root.scale = (sc, sc, sc)
        root.keyframe_insert("scale", frame=k)


def lab_furniture(button=True):
    tx, ty, tw, td, th = TABLE["x"], TABLE["y"], TABLE["w"], TABLE["d"], TABLE["h"]
    before = set(bpy.data.objects)
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
    if not button:
        made = [o for o in bpy.data.objects if o not in before]  # (bpy.data.objects est trié par nom)
        return {"table": [o for o in made if o.name.startswith(("plateau", "pied")) and not o.name.startswith("pied_c")],
                "chaise": [o for o in made if o.name.startswith(("assise", "pied_c", "dossier"))]}
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


def walk(root, keys, z, bob=0.035):
    """Le pion suit des points (image, x, y) ; il sautille un peu quand il avance."""
    keys = sorted(keys)
    prev = None
    for f in range(keys[0][0], keys[-1][0] + 1):
        i = max(j for j in range(len(keys)) if keys[j][0] <= f)
        if i == len(keys) - 1:
            x, y = keys[i][1], keys[i][2]
        else:
            (f0, x0, y0), (f1, x1, y1) = keys[i][:3], keys[i + 1][:3]
            u = smooth((f - f0) / (f1 - f0)) if keys[i + 1][3:] != ("lin",) else (f - f0) / (f1 - f0)
            x, y = x0 + (x1 - x0) * u, y0 + (y1 - y0) * u
        speed = 0 if prev is None else math.hypot(x - prev[0], y - prev[1])
        root.location = (x, y, z + bob * min(1.0, speed / 0.02) * abs(math.sin(f * 0.55)))
        root.keyframe_insert("location", frame=f)
        prev = (x, y)


def circle(f0, f1, c, start, turns, n=24):
    """Points d'un tour (ou plus) autour de c, en partant de start : le pion « tourne en rond »."""
    r = math.hypot(start[0] - c[0], start[1] - c[1])
    a0 = math.atan2(start[1] - c[1], start[0] - c[0])
    return [(round(f0 + (f1 - f0) * k / n), c[0] + r * math.cos(a0 + turns * 2 * math.pi * k / n),
             c[1] + r * math.sin(a0 + turns * 2 * math.pi * k / n), "lin") for k in range(1, n + 1)]


def squash(root, f, amount=0.18):
    """Le pion se tasse (il touche un mur, il s'assoit, il atterrit)."""
    for k, sz in ((f - 1, 1.0), (f + 2, 1.0 - amount), (f + 6, 1.0 + amount / 3), (f + 10, 1.0)):
        root.scale = (1 + (1 - sz) * 0.5, 1 + (1 - sz) * 0.5, sz)
        root.keyframe_insert("scale", frame=k)


def ramp(target, prop, keys):
    """Anime une valeur : ramp(lampe, "energy", [(image, valeur), …]) ; pour un nœud : (entrée, "default_value", …)."""
    for f, v in keys:
        setattr(target, prop, v)
        target.keyframe_insert(prop, frame=f)


GOLD = material("or", "#D9A441", rough=0.25, emission=0.0)


def gold_point(x, y, z):
    """Le point fixe : une petite perle d'or qui éclaire la pièce (le Nom, dans le dhikr)."""
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.055, location=(x, y, z), segments=48, ring_count=24)
    o = bpy.context.object
    o.name = "point_or"
    o.data.materials.append(GOLD)
    bpy.ops.object.shade_smooth()
    bpy.ops.object.light_add(type="POINT", location=(x, y, z + 0.12))
    lamp = bpy.context.object
    lamp.data.color = srgb("#FFC46B")[:3]
    lamp.data.shadow_soft_size = 0.04
    lamp.parent = o
    lamp.matrix_parent_inverse = o.matrix_world.inverted()
    return o, lamp.data


def door_leaf():
    """Le battant de la porte, sur sa charnière (ouvert à -90°, fermé à 0°)."""
    LW = DOOR_X1 - DOOR_X0 - 0.01
    leaf = box("porte", 0, -0.02, 0, LW, 0.02, WALL_H - 0.02)
    bpy.ops.object.empty_add(location=(DOOR_X1, -hd - 0.02, Z0))
    hinge = bpy.context.object
    leaf.parent = hinge
    leaf.location = (-LW, 0, 0)
    return hinge


def swing(hinge, keys):
    for f, ang in keys:
        hinge.rotation_euler = (0, 0, math.radians(ang))
        hinge.keyframe_insert("rotation_euler", frame=f)


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
elif SHOT == "vide":
    # « Imagine une pièce sans aucun meuble. Pas de chaise, pas de table. Tu entres. Tu fais quoi ?
    #   Tu tournes. Tu touches les murs. Et au bout d'un moment, tu cherches la porte.
    #   Ton esprit sans point d'appui, c'est cette pièce. Le téléphone, c'est la porte. »
    t0 = at("p35") - 4
    N = at("p36", None, "end") + 24 - t0
    F = lambda *a: at(*a) - t0 + 1
    shell()
    g = lab_furniture(button=False)
    vanish(group("chaise", g["chaise"], (CHAIR["x"], CHAIR["y"], Z0)), F("p35", "chaise"))
    vanish(group("table", g["table"], (TABLE["x"], TABLE["y"], Z0)), F("p35", "table"))
    # une lumière blanche, un peu froide, de biais : l'ombre d'un mur barre le sol nu
    sun(elev=38, azim=70, energy=3.4, angle=3, color="#F4F6FA")
    world("#C9D2DC", 0.32)
    p = person(1.4, -2.4, Z0)
    enter, quoi = F("p35", "entres"), F("p35", "quoi")
    turn0, touch = F("p35", "tournes"), F("p35", "touches")
    walls, look_f, porte = F("p35", "murs"), F("p35", "cherches"), F("p35", "porte")
    keys = [(1, 1.4, -2.4), (enter - 2, 1.4, -2.4), (enter + 16, 1.25, -0.75), (quoi + 6, 1.15, -0.55)]
    keys += circle(turn0, touch - 4, (0.55, -0.15), (1.15, -0.55), 1.15)
    # (le mur proche de la caméra cacherait le pion : il touche le mur de droite, puis celui du fond)
    keys += [(touch + 10, 1.78, 0.35), (walls + 4, 1.78, 0.35), (walls + 18, -0.9, -1.28), (look_f - 2, -0.7, -1.28),
             (porte + 4, 1.25, -1.05), (N, 1.35, -1.2)]
    walk(p, [(1, 1.4, -2.4), *keys[1:]], Z0)
    p.scale = (0, 0, 0)
    p.keyframe_insert("scale", frame=enter - 3)
    p.scale = (1, 1, 1)
    p.keyframe_insert("scale", frame=enter + 3)
    squash(p, touch + 10, 0.22)  # il touche le mur du fond
    squash(p, walls + 18, 0.22)  # puis celui du fond
    # « Le téléphone, c'est la porte » : la pièce s'éteint, l'embrasure s'allume comme un écran
    tel = F("p36", "téléphone")
    SCREEN = material("ecran_porte", "#9CC3FF", rough=0.4, emission=0.0)
    bpy.ops.mesh.primitive_plane_add(size=1, location=((DOOR_X0 + DOOR_X1) / 2, -hd - t / 2, Z0 + WALL_H / 2 - 0.01),
                                     rotation=(math.radians(90), 0, 0))
    scr = bpy.context.object
    scr.scale = (DOOR_X1 - DOOR_X0 - 0.002, WALL_H - 0.02, 1)
    scr.data.materials.append(SCREEN)
    scr.visible_shadow = False
    for f, hide in ((1, True), (tel - 3, True), (tel - 2, False)):  # éteint, l'embrasure reste une ouverture
        scr.hide_render = hide
        scr.keyframe_insert("hide_render", frame=f)
    key_emission(SCREEN, 1, 0.0)
    key_emission(SCREEN, tel - 2, 0.0)
    key_emission(SCREEN, tel + 14, 6.0)
    bpy.ops.object.light_add(type="AREA", location=((DOOR_X0 + DOOR_X1) / 2, -hd + 0.02, Z0 + WALL_H / 2),
                             rotation=(math.radians(90), 0, 0))  # émet vers +y : dans la pièce
    glow = bpy.context.object.data
    glow.shape, glow.size, glow.size_y = "RECTANGLE", DOOR_X1 - DOOR_X0, WALL_H
    glow.color = srgb("#9CC3FF")[:3]
    ramp(glow, "energy", [(1, 0.0), (tel - 2, 0.0), (tel + 14, 110.0)])
    ramp(bpy.data.lights["Sun"], "energy", [(tel - 4, 3.2), (tel + 12, 0.15)])
    ramp(scene.world.node_tree.nodes["Background"].inputs[1], "default_value", [(tel - 4, 0.32), (tel + 12, 0.04)])
    # caméra derrière le mur du fond, face à la porte (comme « seuls ») ; elle s'élève sur « cette pièce »
    cam = camera(lens=35)
    rise = F("p36", "pièce")
    for f in range(1, N + 1):
        u = smooth(f / N)
        r = smooth((f - rise) / 60)
        tgt = Vector((0.1, -0.25, 0.2))
        look(cam, orbit(tgt, 8.0 - 1.2 * u + 0.6 * r, 47 + 9 * r, 166 - 14 * u), tgt, f)

elif SHOT == "khalwa":
    # « Dans une khalwa, on se retire volontairement. Traditionnellement quarante jours, seul,
    #   guidé par un maître. Exactement ce que les étudiants de Virginie fuyaient en quinze minutes. »
    t0 = at("p44") - 6
    N = at("p44", None, "end") + 24 - t0
    F = lambda *a: at(*a) - t0 + 1
    shell()
    hinge = door_leaf()
    retire, vol = F("p44", "retire"), F("p44", "volontairement")
    jours0, jours1 = F("p44", "quarante"), F("p44", "Exactement")
    swing(hinge, [(1, -90), (vol, -90), (vol + 18, 0)])
    CX, CY = 0.0, 0.1
    p = person(1.4, -2.3, Z0)
    # il s'écarte de la porte pendant qu'elle se ferme (le battant balaie un quart de cercle de 0,9 m)
    walk(p, [(1, 1.4, -2.3), (retire - 4, 1.4, -2.3), (vol - 2, 1.05, -0.55), (vol + 22, 0.95, -0.5),
             (jours0 - 6, CX, CY - 0.32)], Z0)
    squash(p, jours0 - 6, 0.12)
    # la petite lumière au centre, devant lui : une flamme d'or qui ne bouge pas
    pt, lamp = gold_point(CX, CY + 0.05, Z0 + 0.06)
    pt.scale = (0, 0, 0)
    pt.keyframe_insert("scale", frame=vol + 10)
    pt.scale = (1, 1, 1)
    pt.keyframe_insert("scale", frame=vol + 22)
    key_emission(GOLD, 1, 0.0)
    key_emission(GOLD, vol + 10, 0.0)
    key_emission(GOLD, vol + 30, 3.0)
    ramp(lamp, "energy", [(1, 0.0), (vol + 10, 0.0), (vol + 30, 22.0)])
    # « quarante jours » : le soleil tourne au-dessus de la maquette, jours et nuits en accéléré
    bpy.ops.object.light_add(type="SUN")
    so = bpy.context.object
    so.data.angle = math.radians(1.5)
    world("#9FB0C6", 0.2)
    bg = scene.world.node_tree.nodes["Background"]
    DAYS = 3.0
    for f in range(1, N + 1):
        u = min(1.0, max(0.0, (f - jours0) / (jours1 - jours0)))
        ph = 0.18 + DAYS * smooth(u)  # 0.18 : matin ; la course finit au soir (phase .x5)
        a = 2 * math.pi * ph
        h = math.sin(a)  # hauteur du soleil (> 0 le jour)
        so.rotation_euler = Euler((math.radians(90 - max(6, 70 * h)), 0, a))
        so.keyframe_insert("rotation_euler", frame=f)
        so.data.energy = 4.5 * max(0.0, h) ** 0.6
        so.data.keyframe_insert("energy", frame=f)
        warm = 1 - max(0.0, h)
        so.data.color = (1.0, 0.86 + 0.12 * (1 - warm), 0.7 + 0.28 * (1 - warm))
        so.data.keyframe_insert("color", frame=f)
        bg.inputs[1].default_value = 0.11 + 0.21 * max(0.0, h)
        bg.inputs[1].keyframe_insert("default_value", frame=f)
    cam = camera(lens=38)
    for f in range(1, N + 1):
        u = smooth(f / N)
        tgt = Vector((0.2, -0.1, 0.2))
        look(cam, orbit(tgt, 8.8 - 1.4 * u, 52 + 4 * u, 150 - 22 * u), tgt, f)

elif SHOT == "dhikr":
    # « L'idée est simple : tu poses un meuble dans la pièce vide. Un point fixe.
    #   L'esprit part, tu le ramènes au nom. Il repart, tu le ramènes. »
    t0 = at("p51", "L'idée") - 6
    N = at("p51", None, "end") + 30 - t0
    F = lambda *a: at(*a) - t0 + 1
    shell()
    sun(elev=62, azim=25, energy=2.2, angle=6, color="#F4F6FA")  # la pièce nue, comme dans « vide »
    world("#C9D2DC", 0.24)
    CX, CY = 0.2, 0.15
    meuble, fixe = F("p51", "meuble"), F("p51", "fixe")
    part, ram1 = F("p51", "part"), F("p51", "ramènes")
    repart, ram2 = F("p51", "repart"), F("p51", "ramènes", "start", 1)
    p = person(-1.2, 0.6, Z0)
    # avant le point : il erre ; puis il vient s'asseoir près du point, s'en éloigne, revient
    keys = [(1, -1.2, 0.6), (meuble - 10, 0.9, -0.9), (meuble + 14, 1.1, -0.6), (fixe + 16, CX + 0.05, CY - 0.38),
            (part + 2, CX + 0.05, CY - 0.38), (ram1 - 2, 1.25, -1.05), (ram1 + 16, CX + 0.05, CY - 0.38),
            (repart + 2, CX + 0.05, CY - 0.38), (ram2 - 2, -1.4, 0.95), (ram2 + 18, CX + 0.05, CY - 0.38)]
    walk(p, keys, Z0)
    squash(p, fixe + 16, 0.12)
    squash(p, ram1 + 16, 0.12)
    squash(p, ram2 + 18, 0.12)
    # le point d'or descend et se pose sur « meuble », il s'allume sur « point fixe », pulse à chaque retour
    pt, lamp = gold_point(CX, CY, Z0 + 0.06)
    for f, z in ((1, 1.9), (meuble - 2, 1.9), (meuble + 8, Z0 + 0.06)):
        pt.location.z = z
        pt.keyframe_insert("location", frame=f)
    squash(pt, meuble + 8, 0.3)
    glow = [(1, 0.6), (meuble + 8, 0.6), (fixe, 0.6), (fixe + 10, 3.0)]
    light = [(1, 0.0), (meuble + 8, 2.0), (fixe, 2.0), (fixe + 10, 26.0)]
    for r in (ram1 + 16, ram2 + 18):
        glow += [(r - 2, 3.0), (r + 4, 6.0), (r + 16, 3.0)]
        light += [(r - 2, 26.0), (r + 4, 46.0), (r + 16, 26.0)]
    for f, v in glow:
        key_emission(GOLD, f, v)
    ramp(lamp, "energy", light)
    ramp(bpy.data.lights["Sun"], "energy", [(fixe, 2.2), (fixe + 20, 1.2)])
    cam = camera(lens=36)
    for f in range(1, N + 1):
        u = smooth(f / N)
        tgt = Vector((0.0, 0.0, 0.2))
        look(cam, orbit(tgt, 8.8 - 1.0 * u, 58 - 6 * u, 200 - 30 * u), tgt, f)

elif SHOT == "meublee":
    # « Tu n'as juste jamais meublé la pièce. » : la même pièce, la lumière dorée, il est resté
    t0 = at("p67", "meublé") - 10
    N = at("p68") + 30 - t0
    shell()
    CX, CY = 0.2, 0.15
    person(CX + 0.05, CY - 0.38, Z0)
    pt, lamp = gold_point(CX, CY, Z0 + 0.06)
    key_emission(GOLD, 1, 3.0)
    lamp.energy = 30.0
    sun(elev=24, azim=115, energy=5.0, angle=1.5, color="#FFD7A0")  # soleil bas et doré, de côté
    world("#B8C2D0", 0.14)
    cam = camera(lens=35)
    for f in range(1, N + 1):
        u = smooth(f / N)
        tgt = Vector((0.2, -0.1, 0.2))
        look(cam, orbit(tgt, 6.6 + 2.0 * u, 48 + 14 * u, 160 - 10 * u), tgt, f)
else:
    raise SystemExit(f"plan inconnu : {SHOT}")

# ── rendu ───────────────────────────────────────────────────────────────────────────────────────
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
if "--gpu" in ARGS:  # en local : la carte graphique (NVIDIA, AMD, Apple, Intel), 10 à 50 fois plus rapide
    prefs = bpy.context.preferences.addons["cycles"].preferences
    for kind in ("OPTIX", "CUDA", "METAL", "HIP", "ONEAPI"):
        try:
            prefs.compute_device_type = kind
        except TypeError:
            continue
        prefs.get_devices()
        gpus = [d for d in prefs.devices if d.type == kind]
        if gpus:
            for d in prefs.devices:
                d.use = d.type == kind
            scene.cycles.device = "GPU"
            print(f"GPU : {kind} ({', '.join(d.name for d in gpus)})")
            break
    else:
        print("aucune carte graphique utilisable : rendu sur le processeur")
scene.cycles.samples = SAMPLES if "--samples" in ARGS else (16 if TEST else 32)
scene.cycles.use_denoising = True
scene.cycles.max_bounces = 6
scene.render.use_persistent_data = True
scene.render.film_transparent = True
scene.render.resolution_x, scene.render.resolution_y = 1920, 1080
if "--pct" in ARGS:  # aperçu rapide : --test 1,40,80 --pct 40
    scene.render.resolution_percentage = int(ARGS[ARGS.index("--pct") + 1])
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
