"""Carte à l'encre Bagdad → Damas (al-Ghazali, 1095), tracée depuis Natural Earth (domaine public).

Côtes, Tigre, Euphrate, Jourdain, lacs : de vraies géométries, projetées sur l'écran
(équirectangulaire corrigée de la latitude) puis simplifiées. Le montage les dessine à l'encre.

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


def main():
    coast = [path(rdp(p, 0.8)) for f in load("ne_10m_coastline") for l in lines(f["geometry"]) for p in clip(l) if len(p) > 2]
    lakes = [path(rdp(p, 0.8)) + " Z" for f in load("ne_10m_lakes") for l in lines(f["geometry"]) for p in clip(l)
             if len(p) > 6]
    rivers = {}
    for f in load("ne_10m_rivers_lake_centerlines"):
        name = RIVERS.get(f["properties"].get("name") or "")
        if not name:
            continue
        for l in lines(f["geometry"]):
            for p in clip(l):
                if len(p) > 2:
                    rivers.setdefault(name, []).append(path(rdp(p, 0.8)))
    data = {"w": W, "h": H, "coast": coast, "lakes": lakes, "rivers": rivers,
            "cities": {k: proj(*v) for k, v in CITIES.items()},
            "source": "Natural Earth (domaine public), naturalearthdata.com"}
    out = os.path.join(ROOT, "src/data/carte_ghazali.json")
    json.dump(data, open(out, "w"), ensure_ascii=False)
    print(f"{len(coast)} côtes, {len(lakes)} lacs, " + ", ".join(f"{k} {len(v)}" for k, v in rivers.items()),
          f"-> {os.path.getsize(out) // 1024} Ko")
    print("villes :", data["cities"])


if __name__ == "__main__":
    main()
