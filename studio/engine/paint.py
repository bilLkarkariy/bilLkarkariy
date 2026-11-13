"""La mise en couleur : un aplat par zone, plus une ombre nette.

Pour chaque pixel du personnage, on cherche le volume réellement visible depuis
la caméra : il donne la zone (peau, cheveux, vêtement...) et l'orientation de la
surface. Une surface tournée à l'opposé de la lumière passe dans l'ombre.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from .mannequin import Sweep

SHADE = np.array([0.74, 0.68, 0.80], np.float32)        # l'ombre : plus sombre et un peu froide


def _mask(poly, x0, y0, w, h):
    img = Image.new("L", (w, h), 0)
    if len(poly) >= 3:
        ImageDraw.Draw(img).polygon([(float(x) - x0, float(y) - y0) for x, y in poly], fill=255)
    return np.asarray(img) > 0


def paint(model, pose, cam, con, origin, scale, size, palette, zone_of, boxes=(), light=None,
          threshold=0.12):
    """Couleur du personnage. Renvoie (x0, y0, rgb, alpha) : un rectangle d'image à poser
    en (x0, y0), avec alpha = 1 là où le personnage est peint.

    con      : la construction déjà projetée (pour ses contours exacts et ses yeux).
    size     : (largeur, hauteur) de la feuille, en pixels.
    palette  : zone -> (r, v, b). zone_of : nom de partie -> zone.
    boxes    : boîtes du décor qui peuvent cacher le personnage.
    """
    origin = np.asarray(origin, float)
    if light is None:               # lumière venant du haut à gauche, un peu de face
        light = -0.5 * cam.right + 0.7 * cam.up + 0.5 * cam.back
    light = light / np.linalg.norm(light)
    zones = list(palette)
    frames = model.solve(pose)

    centers, axes, zone_id, strip, depth_of = [], [], [], [], {}
    for part in model.parts:
        c, a = model._ellipsoids(part, frames)
        centers.extend(c)
        axes.extend(a)
        zone_id.extend([zones.index(zone_of(part.name))] * len(c))
        # Sur une forme allongée, l'ombre suit le tour du membre, pas ses tranches.
        tangent = a[:, :, 1] / np.linalg.norm(a[:, :, 1], axis=1, keepdims=True)
        strip.extend(tangent if isinstance(part.prims[0], Sweep) else np.zeros_like(tangent))
        depth_of[part.name] = float(((c - cam.target) @ cam.back).mean())
    centers, axes, strip = np.array(centers), np.array(axes), np.array(strip)

    def to_px(pts3):
        return origin + cam.project(pts3) * (scale, -scale)

    reach = np.linalg.norm(axes, axis=1).max(axis=1) * scale * 1.5 + 3
    cpx = to_px(centers)
    x0 = int(max(0, np.floor((cpx[:, 0] - reach).min())))
    y0 = int(max(0, np.floor((cpx[:, 1] - reach).min())))
    x1 = int(min(size[0], np.ceil((cpx[:, 0] + reach).max())))
    y1 = int(min(size[1], np.ceil((cpx[:, 1] + reach).max())))
    w, h = max(x1 - x0, 1), max(y1 - y0, 1)

    far = cam.dist if cam.dist is not None else 1000.0
    eye = cam.target + cam.back * far

    def rays(xs, ys):
        """Rayon de chaque pixel : origine et direction (t = 1 au niveau de la cible)."""
        u, v = (xs + 0.5 - origin[0]) / scale, -(ys + 0.5 - origin[1]) / scale
        on_plane = cam.target + u[..., None] * cam.right + v[..., None] * cam.up
        if cam.dist is None:
            return on_plane + cam.back * far, np.broadcast_to(-cam.back * far, on_plane.shape)
        return np.broadcast_to(eye, on_plane.shape), on_plane - eye

    zbuf = np.full((h, w), np.inf, np.float32)
    zid = np.full((h, w), -1, np.int16)
    lit = np.ones((h, w), np.float32)
    for i in range(len(centers)):
        bx0, bx1 = int(max(x0, cpx[i, 0] - reach[i])), int(min(x1, cpx[i, 0] + reach[i] + 1))
        by0, by1 = int(max(y0, cpx[i, 1] - reach[i])), int(min(y1, cpx[i, 1] + reach[i] + 1))
        if bx1 <= bx0 or by1 <= by0:
            continue
        ys, xs = np.mgrid[by0:by1, bx0:bx1]
        o, d = rays(xs, ys)
        inv = np.linalg.inv(axes[i])
        oo, dd = (o - centers[i]) @ inv.T, d @ inv.T
        a, b, c = (dd * dd).sum(-1), (oo * dd).sum(-1), (oo * oo).sum(-1) - 1
        disc = b * b - a * c
        t = (-b - np.sqrt(np.maximum(disc, 0))) / a
        sub = (slice(by0 - y0, by1 - y0), slice(bx0 - x0, bx1 - x0))
        win = (disc > 0) & (t > 0) & (t < zbuf[sub])
        if not win.any():
            continue
        normal = (oo + t[..., None] * dd) @ inv
        normal -= (normal @ strip[i])[..., None] * strip[i]
        normal /= np.maximum(np.linalg.norm(normal, axis=-1, keepdims=True), 1e-9)
        zbuf[sub][win] = t[win]
        zid[sub][win] = zone_id[i]
        lit[sub][win] = (normal @ light)[win]

    # Le décor de premier plan : là où une boîte est plus proche, le personnage n'est pas peint.
    covered = np.zeros((h, w), bool)
    if len(boxes):
        ys, xs = np.mgrid[y0:y1, x0:x1]
        o, d = rays(xs, ys)
        inv = 1.0 / np.where(np.abs(d) < 1e-9, 1e-9, d)
        nearest = np.full((h, w), np.inf, np.float32)
        for box in boxes:
            t1, t2 = (np.asarray(box.lo) - o) * inv, (np.asarray(box.hi) - o) * inv
            near, away = np.minimum(t1, t2).max(-1), np.maximum(t1, t2).min(-1)
            nearest = np.where((away >= near) & (away > 0), np.minimum(nearest, near), nearest)
        covered = np.isfinite(nearest)
        zid[nearest < zbuf] = -1

    # Les contours dessinés font foi : on bouche les petits manques, on rogne ce qui dépasse.
    inside = np.zeros((h, w), bool)
    for name, poly, behind in sorted(con.mattes, key=lambda m: -depth_of[m[0]]):    # du plus proche
        mask = _mask(origin + poly * (scale, -scale), x0, y0, w, h)
        inside |= mask
        fill = mask & (zid < 0)
        if behind:
            fill &= ~covered
        zid[fill] = zones.index(zone_of(name))
    zid[~inside] = -1

    shadow = Image.fromarray(((lit < threshold) & (zid >= 0)).astype(np.uint8) * 255)
    shadow = np.array(shadow.filter(ImageFilter.GaussianBlur(7))) > 127        # bord d'ombre lissé
    shadow &= zid >= 0

    # Détails peints par-dessus leur zone : blanc de l'œil, iris, pupille, reflet.
    for zone, over, poly in con.fills:
        mask = _mask(origin + poly * (scale, -scale), x0, y0, w, h)
        target = mask & np.isin(zid, [zones.index(z) for z in over])
        zid[target] = zones.index(zone)
        shadow[target] = False

    colors = np.array([palette[z] for z in zones], np.float32)
    rgb = colors[np.maximum(zid, 0)]
    rgb[shadow] *= SHADE
    return x0, y0, rgb, (zid >= 0).astype(np.float32)
