"""Versions étrangères : aucune 3D recalculée. Chaque plan réutilise les images françaises, recalées dans le temps.

Entrée : out/validation/3d-<langue>-plan.json (tools/report_3d_en.py --lang <langue> : pour chaque plan, les repères
de mots en image locale FR et dans la langue) et src/data/renders3d.json (images FR réellement rendues).
Sortie : src/data/remap3d_<langue>.json, {plan: [[image langue, image FR], ...]}, lu par Shot3D (src/components/Light.tsx).

Entre deux repères, la lecture est linéaire. Avant le premier et après le dernier, elle reste à vitesse normale :
on tient la première image si le mot traduit arrive plus tard, on tient la dernière une fois le plan FR fini.
  python3 tools/remap3d_en.py              (anglais)
  python3 tools/remap3d_en.py --lang ur    (ourdou)
"""
import argparse, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
parser = argparse.ArgumentParser()
parser.add_argument("--lang", default="en")
LANG = parser.parse_args().lang
L = LANG.upper()
plan = json.load(open(os.path.join(ROOT, f"out/validation/3d-{LANG}-plan.json")))
done = json.load(open(os.path.join(ROOT, "src/data/renders3d.json")))

out = {}
for shot, p in plan.items():
    if shot not in done:  # la maquette suit déjà les repères traduits (src/scenes/Maquette.tsx)
        continue
    ne, nf = p["frames"], done[shot]["frames"]
    local = f"{LANG}_local"
    pairs = sorted((w[local], w["fr_local"]) for w in p["words"] if 1 <= w[local] <= ne and 1 <= w["fr_local"] <= nf)
    knots = []
    for e, f in pairs:  # une correspondance strictement croissante, sinon l'image reculerait
        if not knots or (e > knots[-1][0] and f > knots[-1][1]):
            knots.append([e, f])
    if not knots:
        knots = [[1, 1]]
    e1, f1 = knots[0]
    if f1 - (e1 - 1) >= 1:
        head = [[1, f1 - (e1 - 1)]]
    else:
        head = [[1, 1], [e1 - f1 + 1, 1]]
    ek, fk = knots[-1]
    if ek + (nf - fk) <= ne:
        tail = [[ek + (nf - fk), nf], [ne, nf]]
    else:
        tail = [[ne, fk + (ne - ek)]]
    seq = [k for k in head + knots + tail]
    clean = []
    for e, f in seq:
        if clean and e <= clean[-1][0]:
            continue
        clean.append([e, f])
    out[shot] = clean
    print(f"{shot:8s} {L} {ne:4d} images ← FR {nf:4d} : {clean}")

json.dump(out, open(os.path.join(ROOT, f"src/data/remap3d_{LANG}.json"), "w"), indent=1)
