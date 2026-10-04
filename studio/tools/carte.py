"""Carte à l'encre Bagdad → Damas (al-Ghazali, 1095), tracée depuis Natural Earth (domaine public).

Terres, côtes, Tigre, Euphrate, Jourdain, lacs : de vraies géométries, projetées sur l'écran
(équirectangulaire corrigée de la latitude) puis simplifiées. Les terres sont des surfaces pleines
(la mer est ce qui reste) : on voit d'un coup d'œil où est la terre, où est l'eau. Les noms des fleuves
sont posés sur leur propre tracé.

  python3 tools/carte.py   -> src/data/carte_ghazali.json
"""
import json
import math
import os
import urllib.request

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
GEO = os.path.join(ROOT, ".cache/geo")
NE = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/"

# cadre : de la Méditerranée au golfe Persique
LON0, LON1, LAT0, LAT1 = 33.4, 47.6, 29.0, 38.4
W, H = 1920, 1080
K = math.cos(math.radians((LAT0 + LAT1) / 2))
SC = min(W / ((LON1 - LON0) * K), H / (LAT1 - LAT0))
OX = (W - (LON1 - LON0) * K * SC) / 2
OY = (H - (LAT1 - LAT0) * SC) / 2

CITIES = {
    "bagdad": (44.366, 33.315),
    "damas": (36.292, 33.513),
}
RIVERS = {"Tigris": "Tigre", "Euphrates": "Euphrate", "Al Furat": "Euphrate", "Firat": "Euphrate", "Dicle": "Tigre",
          "Jordan": "Jourdain"}


def proj(lon, lat):
    return round(OX + (lon - LON0) * K * SC, 1), round(OY + (LAT1 - lat) * SC, 1)


def load(name):
    path = os.path.join(GEO, name + ".geojson")
    if not os.path.exists(path):
        os.makedirs(GEO, exist_ok=True)
        urllib.request.urlretrieve(NE + name + ".geojson", path)
    return json.load(open(path))["features"]


def lines(geom):
    t, c = geom["type"], geom["coordinates"]
    if t == "LineString":
        return [c]
    if t == "MultiLineString":
        return c
    if t == "Polygon":
        return c
    if t == "MultiPolygon":
        return [r for p in c for r in p]
    return []


def rdp(pts, eps):
    if len(pts) < 3:
        return pts
    if tuple(pts[0]) == tuple(pts[-1]):  # contour fermé (lac) : en deux moitiés, sinon tout s'efface
        m = len(pts) // 2
        return rdp(pts[: m + 1], eps)[:-1] + rdp(pts[m:], eps)
    (x0, y0), (x1, y1) = pts[0], pts[-1]
    dx, dy = x1 - x0, y1 - y0
    n = math.hypot(dx, dy) or 1e-9
    d = [abs(dy * (x - x0) - dx * (y - y0)) / n for x, y in pts[1:-1]]
    i = max(range(len(d)), key=d.__getitem__)
    if d[i] <= eps:
        return [pts[0], pts[-1]]
    return rdp(pts[: i + 2], eps)[:-1] + rdp(pts[i + 1:], eps)


def clip(line):
    """Morceaux de la ligne qui passent dans le cadre (avec une marge)."""
    out, cur = [], []
    for lon, lat in line:
        if LON0 - 1 <= lon <= LON1 + 1 and LAT0 - 1 <= lat <= LAT1 + 1:
            cur.append(proj(lon, lat))
        elif cur:
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out


def path(pts):
    return "M" + " L".join(f"{x} {y}" for x, y in pts)


# les terres débordent largement du cadre : la caméra peut zoomer et glisser sans tomber sur un bord
LAND_BOX = (27.0, 24.0, 54.0, 42.0)
# (nom affiché, fleuve, latitude où poser le nom)
RIVER_LABELS = [("Tigre", "Tigre", 34.75), ("Euphrate", "Euphrate", 34.45)]


def land():
    from shapely.geometry import box, shape
    from shapely.ops import unary_union
    b = box(*LAND_BOX)
    geo = unary_union([shape(f["geometry"]).intersection(b) for f in load("ne_10m_land")]).simplify(0.01)
    polys = list(geo.geoms) if hasattr(geo, "geoms") else [geo]
    fills, rings = [], []
    for poly in polys:
        if poly.area < 0.02:
            continue
        rs = [poly.exterior] + list(poly.interiors)
        fills.append(" ".join(path([proj(*c) for c in r.coords]) + " Z" for r in rs))
        rings += [path([proj(*c) for c in r.coords]) for r in rs]
    # la côte à l'encre est le bord même des terres : le trait tombe toujours entre la terre et l'eau
    # (les bords du cadre LAND_BOX sont loin hors champ, même au plus fort zoom)
    return fills, rings


def river_label(paths_lonlat, lat):
    """Point du fleuve le plus proche de la latitude voulue, et l'angle du tracé à cet endroit."""
    best = None
    for line in paths_lonlat:
        for (a, b) in zip(line, line[1:]):
            d = abs((a[1] + b[1]) / 2 - lat)
            if best is None or d < best[0]:
                best = (d, a, b)
    _, a, b = best
    (x0, y0), (x1, y1) = proj(*a), proj(*b)
    ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
    if ang > 90:
        ang -= 180
    if ang < -90:
        ang += 180
    return round((x0 + x1) / 2, 1), round((y0 + y1) / 2, 1), round(ang, 1)


def main():
    fills, coast = land()
    lakes = [path(rdp(p, 0.8)) + " Z" for f in load("ne_10m_lakes") for l in lines(f["geometry"]) for p in clip(l)
             if len(p) > 6]
    rivers, raw = {}, {}
    for f in load("ne_10m_rivers_lake_centerlines"):
        name = RIVERS.get(f["properties"].get("name") or "")
        if not name:
            continue
        for l in lines(f["geometry"]):
            raw.setdefault(name, []).append(l)
            for p in clip(l):
                if len(p) > 2:
                    rivers.setdefault(name, []).append(path(rdp(p, 0.8)))
    labels = [{"t": t, **dict(zip(("x", "y", "a"), river_label(raw[r], lat)))} for t, r, lat in RIVER_LABELS]
    data = {"w": W, "h": H, "land": fills, "coast": coast, "lakes": lakes, "rivers": rivers, "riverLabels": labels,
            "seas": [{"t": "Mer Méditerranée", "x": proj(33.9, 34.0)[0], "y": proj(33.9, 34.0)[1], "a": -70, "s": 40},
                     {"t": "Golfe Persique", "x": proj(49.15, 29.45)[0], "y": proj(49.15, 29.45)[1], "a": 0, "s": 26}],
            "regions": [{"t": "DÉSERT DE SYRIE", "x": proj(39.6, 32.4)[0], "y": proj(39.6, 32.4)[1]}],
            "cities": {k: proj(*v) for k, v in CITIES.items()},
            "source": "Natural Earth (domaine public), naturalearthdata.com"}
    out = os.path.join(ROOT, "src/data/carte_ghazali.json")
    json.dump(data, open(out, "w"), ensure_ascii=False)
    print(f"{len(coast)} côtes, {len(lakes)} lacs, " + ", ".join(f"{k} {len(v)}" for k, v in rivers.items()),
          f"-> {os.path.getsize(out) // 1024} Ko")
    print("villes :", data["cities"])


if __name__ == "__main__":
    main()
