"""La toile : des calques de pigment posés sur une feuille de papier.

Chaque trait est aussi consigné dans un journal (`Document.journal`). Le dessin
est donc une suite de gestes rejouable, pas seulement une image.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from .paper import Paper


class Layer:
    def __init__(self, name, w, h):
        self.name = name
        self.opacity = 1.0
        self.visible = True
        self.D = np.zeros((h, w), np.float32)      # densité de pigment
        self.C = np.zeros((h, w, 3), np.float32)   # couleur pondérée par la densité

    def stamp(self, dabs, brush, tooth):
        """Dépose les dabs. Renvoie la zone modifiée (x0, y0, x1, y1) ou None."""
        h, w = self.D.shape
        box = None
        half = int(np.ceil(float(dabs[:, 2].max()) + 1.5))
        per_dab = (2 * half + 1) ** 2
        chunk = max(1, 3_000_000 // per_dab)
        oy, ox = np.mgrid[-half:half + 1, -half:half + 1]
        for i in range(0, len(dabs), chunk):
            x, y, r, dep, p = (dabs[i:i + chunk, k][:, None, None] for k in range(5))
            px = np.floor(x).astype(np.int64) + ox
            py = np.floor(y).astype(np.int64) + oy
            dist = np.hypot(px + 0.5 - x, py + 0.5 - y)
            edge = np.maximum(1.0, r * (1 - brush.hardness))
            fall = np.clip((r - dist) / edge + (0.5 if brush.hardness >= 1 else 0.0), 0, 1)
            ok = (fall > 0) & (px >= 0) & (px < w) & (py >= 0) & (py < h)
            if not ok.any():
                continue
            px, py = px[ok], py[ok]
            # Grain : à faible pression, seuls les sommets du papier prennent le pigment.
            p_full = np.broadcast_to(p, ok.shape)[ok]
            bite = np.clip((tooth[py, px] - (1 - p_full)) / 0.25 + 0.5, 0, 1)
            amount = (np.broadcast_to(dep, ok.shape)[ok] * fall[ok]
                      * ((1 - brush.grain) + brush.grain * bite))
            x0, x1, y0, y1 = px.min(), px.max() + 1, py.min(), py.max() + 1
            bw = x1 - x0
            acc = np.bincount((py - y0) * bw + (px - x0), weights=amount,
                              minlength=bw * (y1 - y0)).reshape(y1 - y0, bw).astype(np.float32)
            self.D[y0:y1, x0:x1] += acc
            self.C[y0:y1, x0:x1] += acc[..., None] * np.asarray(brush.color, np.float32)
            box = (x0, y0, x1, y1) if box is None else (
                min(box[0], x0), min(box[1], y0), max(box[2], x1), max(box[3], y1))
        return box


class Document:
    def __init__(self, w, h, seed=0, paper=None):
        self.w, self.h, self.seed = w, h, seed
        self.paper = paper or Paper(w, h, seed)
        self.layers = []
        self.journal = []       # (nom du calque, brosse, dabs)
        self._rng = np.random.default_rng(seed + 1)

    def layer(self, name):
        for layer in self.layers:
            if layer.name == name:
                return layer
        layer = Layer(name, self.w, self.h)
        self.layers.append(layer)
        return layer

    def stroke(self, layer_name, brush, pts):
        dabs = brush.dabs(np.asarray(pts, np.float32), self._rng)
        self.journal.append((layer_name, brush, dabs))
        return self.layer(layer_name).stamp(dabs, brush, self.paper.tooth)

    def label(self, xy, text, size=17, color=(0.46, 0.47, 0.52), weight="Regular"):
        """Texte imprimé sur la feuille (une légende, pas un dessin)."""
        try:
            font = ImageFont.truetype(f"/usr/share/fonts/opentype/inter/Inter-{weight}.otf", size)
        except OSError:
            font = ImageFont.load_default(size)
        mask = Image.new("L", (self.w, self.h), 0)
        ImageDraw.Draw(mask).text(xy, text, fill=255, font=font)
        a = (np.asarray(mask, np.float32) / 255)[..., None]
        self.paper.rgb = self.paper.rgb * (1 - a) + np.asarray(color, np.float32) * a

    def guide(self, y, x0, x1, strength=0.22):
        """Fin trait horizontal imprimé sur la feuille (repère de model sheet)."""
        y = int(round(y))
        self.paper.rgb[y:y + max(1, self.w // 2400), int(x0):int(x1)] *= 1 - strength

    def composite(self, box=None):
        """Image finale (float, 0..1) : chaque calque assombrit le papier."""
        x0, y0, x1, y1 = box or (0, 0, self.w, self.h)
        out = self.paper.rgb[y0:y1, x0:x1].copy()
        for layer in self.layers:
            if not layer.visible:
                continue
            d = layer.D[y0:y1, x0:x1]
            alpha = (1 - np.exp(-d)) * layer.opacity
            rgb = layer.C[y0:y1, x0:x1] / np.maximum(d, 1e-6)[..., None]
            out *= 1 - alpha[..., None] * (1 - rgb)
        return out

    def image(self):
        return Image.fromarray((self.composite() * 255 + 0.5).astype(np.uint8))

    def save(self, path):
        self.image().save(path)
