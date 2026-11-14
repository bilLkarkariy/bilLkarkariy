"""Ce que le dessinateur sait de la forme avant de poser le crayon.

Le personnage est décrit comme des formes superposées, du fond vers l'avant (une mèche
devant le visage, le visage devant le cou...). On en déduit ce qui est visible : un contour
n'est tracé que là où rien ne passe devant, une hachure s'arrête au bord de sa zone.
Rien ici ne dessine : ce module répond seulement à « où ai-je le droit de tracer ? ».
"""
import numpy as np
from PIL import Image, ImageDraw
from .vpath import parse




class Sheet:
    def __init__(self):
        self.items = []
        self.clip = []          # pile de polygones de découpe (points d'étude)

    def _add(self, kind, d=None, subs=None, **kw):
        it = dict(kind=kind, d=d, subs=subs, zone=None, w=1.0, on=None, name="", taper=None,
                  clips=list(self.clip))
        it.update(kw)
        self.items.append(it)
        return it

    def shape(self, zone, d=None, w=1.0, on=None, name="", **kw):
        return self._add("shape", d, zone=zone, w=w, on=on, name=name, **kw)

    def line(self, d=None, w=1.0, on=None, name="", taper=None, **kw):
        return self._add("line", d, w=w, on=on, name=name, taper=taper, **kw)

    def ink(self, d=None, on=None, name="", **kw):
        return self._add("ink", d, zone="encre", on=on, name=name, **kw)

    def shadow(self, d=None, on=None, name="", **kw):
        kw.setdefault("w", 0.45)
        return self._add("shadow", d, on=on, name=name, **kw)

    def light(self, d=None, on=None, name="", **kw):
        kw.setdefault("w", 0.45)
        return self._add("light", d, on=on, name=name, **kw)

    def guide(self, d):
        return self._add("guide", d)

    def cast(self, names, dx, dy, on):
        """Ombre portée : les formes nommées, décalées de (dx, dy), assombrissent la zone `on`."""
        return self._add("cast", "", on=on, names=names, shift=(dx, dy), w=0.0)


def _subs(it):
    return it["subs"] if it["subs"] is not None else parse(it["d"])


def solve(sheet, box, k=2.0):
    """Calcule cartes et traits visibles. Tout se fait dans la boîte englobante de chaque forme."""
    x0, y0, x1, y1 = box
    W, H = int((x1 - x0) * k), int((y1 - y0) * k)
    zones = ["papier"]
    zone_map = np.zeros((H, W), np.int16)
    order_map = np.full((H, W), -1, np.int32)
    tone_map = np.zeros((H, W), np.uint8)

    def zid(z):
        if z not in zones:
            zones.append(z)
        return zones.index(z)

    def zids(on):
        return [zid(z) for z in (on if isinstance(on, (list, tuple)) else [on])]

    def to_px(pts):
        return (np.asarray(pts, float) - (x0, y0)) * k

    def bbox(pts_list, pad=3):
        allp = np.concatenate([to_px(p) for p in pts_list])
        ax, ay = np.floor(allp.min(0)).astype(int) - pad
        bx, by = np.ceil(allp.max(0)).astype(int) + pad
        ax, ay, bx, by = max(ax, 0), max(ay, 0), min(bx, W), min(by, H)
        return (ax, ay, bx, by) if bx > ax and by > ay else None

    def poly(pts_list, bb):
        ax, ay, bx, by = bb
        img = Image.new("L", (bx - ax, by - ay), 0)
        dr = ImageDraw.Draw(img)
        for pts in pts_list:
            if len(pts) >= 3:
                dr.polygon([(x - ax, y - ay) for x, y in to_px(pts)], fill=255)
        return np.asarray(img) > 0

    parsed, limits, masks = [], [], {}
    for i, it in enumerate(sheet.items):
        if it["kind"] == "cast":
            parsed.append([]); limits.append(None)
            dx, dy = int(it["shift"][0] * k), int(it["shift"][1] * k)
            for n in it["names"]:
                for (ax, ay, bx, by), m in masks.get(n, []):
                    cx0, cy0, cx1, cy1 = max(ax + dx, 0), max(ay + dy, 0), min(bx + dx, W), min(by + dy, H)
                    if cx1 <= cx0 or cy1 <= cy0:
                        continue
                    mm = m[cy0 - dy - ay:cy1 - dy - ay, cx0 - dx - ax:cx1 - dx - ax]
                    sl = (slice(cy0, cy1), slice(cx0, cx1))
                    tone_map[sl][mm & np.isin(zone_map[sl], zids(it["on"]))] = 1
            continue
        subs = _subs(it)
        parsed.append(subs)
        bb = bbox([s["pts"] for s in subs], pad=6)
        if bb is None:
            limits.append((None, np.zeros((1, 1), bool)) if (it["clips"] or it["on"]) else None)
            continue
        sl = (slice(bb[1], bb[3]), slice(bb[0], bb[2]))
        limit = None
        for c in it["clips"]:
            cm = poly([c], bb)
            limit = cm if limit is None else (limit & cm)
        if it["on"]:
            onm = np.isin(zone_map[sl], zids(it["on"]))
            limit = onm if limit is None else (limit & onm)
        if it["kind"] in ("shape", "ink", "shadow", "light"):
            m = poly([s["pts"] for s in subs], bb)
            if limit is not None:
                m &= limit
            if it["name"]:
                masks.setdefault(it["name"], []).append((bb, m))
            if it["kind"] in ("shape", "ink"):
                zone_map[sl][m] = zid(it["zone"]); order_map[sl][m] = i; tone_map[sl][m] = 0
            else:
                tone_map[sl][m] = 1 if it["kind"] == "shadow" else 2
        limits.append(None if limit is None else (bb, limit))

    OFF = ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1))
    strokes = []
    for i, it in enumerate(sheet.items):
        if it["kind"] == "cast" or it["w"] <= 0:
            continue
        if it["kind"] in ("ink", "guide"):
            for s in parsed[i]:
                strokes.append(dict(pts=s["pts"], kind=it["kind"], w=1.0, item=i, name=it["name"], taper=None))
            continue
        for s in parsed[i]:
            pts, pen = s["pts"], s["pen"]
            q = to_px(pts)
            px, py = q[:, 0].astype(int), q[:, 1].astype(int)
            inside = (px >= 1) & (px < W - 1) & (py >= 1) & (py < H - 1)
            px, py = np.clip(px, 1, W - 2), np.clip(py, 1, H - 2)
            covered = np.ones(len(pts), bool)
            for ox, oy in OFF:
                covered &= order_map[py + oy, px + ox] > i
            vis = ~covered & inside
            if limits[i] is not None:
                bb, lm = limits[i]
                if bb is None:
                    vis[:] = False
                else:
                    near = np.zeros(len(pts), bool)
                    for ox, oy in ((0, 0), (2, 0), (-2, 0), (0, 2), (0, -2)):
                        lx, ly = px + ox - bb[0], py + oy - bb[1]
                        okk = (lx >= 0) & (lx < lm.shape[1]) & (ly >= 0) & (ly < lm.shape[0])
                        near[okk] |= lm[ly[okk], lx[okk]]
                    vis &= near
            ok = vis.copy(); ok[1:] &= vis[:-1] & pen[1:]; ok[0] = False
            n, j = len(pts), 1
            total = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(pts, axis=0).T))])
            while j < n:
                if ok[j]:
                    a = j - 1
                    while j < n and ok[j]:
                        j += 1
                    run = pts[a:j]
                    if len(run) >= 2 and total[j - 1] - total[a] > 2:
                        corners = [c - a for c in s["corners"] if a < c < j - 1]
                        weight = s["weight"][a:j] if s.get("weight") is not None else None
                        strokes.append(dict(pts=run, kind=it["kind"], w=it["w"], item=i, name=it["name"],
                                            taper=it["taper"], corners=corners, weight=weight,
                                            span=(total[a] / max(total[-1], 1e-6), total[j - 1] / max(total[-1], 1e-6))))
                else:
                    j += 1
    return dict(zones=zones, zone_map=zone_map, tone_map=tone_map, order_map=order_map,
                strokes=strokes, box=box, k=k, size=(W, H), items=sheet.items, parsed=parsed)


