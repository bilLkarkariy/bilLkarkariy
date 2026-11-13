"""Le papier : une couleur de fond et un relief (le « grain »).

Le grain est ce qui donne l'aspect crayon : le graphite se dépose d'abord sur
les sommets du papier, et ne remplit les creux que si l'on appuie.
"""
import numpy as np
from PIL import Image


def _octave(rng, w, h, scale):
    """Bruit lisse dont les taches font environ `scale` pixels."""
    sw, sh = w // scale + 3, h // scale + 3
    small = Image.fromarray(rng.random((sh, sw), dtype=np.float32))
    big = small.resize((sw * scale, sh * scale), Image.BICUBIC)
    return np.asarray(big, dtype=np.float32)[:h, :w]


class Paper:
    def __init__(self, w, h, seed=0, color=(0.962, 0.953, 0.925)):
        self.w, self.h, self.seed = w, h, seed
        rng = np.random.default_rng(seed)

        relief = (0.34 * rng.random((h, w), dtype=np.float32)
                  + 0.40 * _octave(rng, w, h, 2)
                  + 0.26 * _octave(rng, w, h, 4))
        # Égalisation par rang : `tooth` est uniforme sur [0, 1], donc
        # « tooth > 1 - pression » couvre une fraction de surface = pression.
        rank = np.empty(relief.size, dtype=np.float32)
        rank[np.argsort(relief, axis=None)] = np.linspace(0, 1, relief.size, dtype=np.float32)
        self.tooth = rank.reshape(h, w)

        shade = _octave(rng, w, h, 240) - 0.5          # feuille pas tout à fait plane
        fibre = self.tooth - 0.5
        rgb = np.asarray(color, np.float32) * (1 + 0.020 * shade + 0.016 * fibre)[..., None]
        self.rgb = np.clip(rgb, 0, 1).astype(np.float32)
