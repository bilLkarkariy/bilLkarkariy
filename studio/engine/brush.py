"""Les outils : chaque brosse transforme un geste (x, y, pression) en « dabs »,
de petits dépôts de pigment posés le long du trait, comme dans Clip Studio.
"""
from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class Brush:
    name: str
    color: tuple            # pigment (r, g, b), fusionné en « produit » sur le papier
    radius: float           # rayon de la mine à pleine pression, en pixels
    density: float          # quantité de pigment d'un passage à pleine pression
    min_size: float = 0.55  # taille à pression nulle, en fraction du rayon
    hardness: float = 1.0   # 1 = bord net, 0 = bord très flou
    grain: float = 0.8      # sensibilité au grain du papier
    spacing: float = 0.3    # distance entre deux dabs, en fraction du rayon
    scatter: float = 0.08   # dispersion aléatoire des dabs
    flow_gamma: float = 1.3 # courbe pression -> quantité de pigment

    def dabs(self, pts, rng):
        """pts : tableau (n, 3) de x, y, pression. Renvoie x, y, rayon, dépôt, pression."""
        x, y, p = pts[:, 0], pts[:, 1], np.clip(pts[:, 2], 0.0, 1.0)
        n = len(p)
        r = self.radius * (self.min_size + (1 - self.min_size) * p ** 0.7)
        x = x + rng.normal(0, self.scatter, n) * r
        y = y + rng.normal(0, self.scatter, n) * r
        dep = self.density * p ** self.flow_gamma * (self.spacing / 2)
        dep = dep * rng.uniform(0.8, 1.2, n)
        return np.stack([x, y, r, dep, p], axis=1).astype(np.float32)


# Crayons de couleur d'animateur (type Col-Erase) et mines graphite.
BLEU = Brush("bleu", (0.30, 0.50, 0.84), radius=1.7, density=0.95, grain=0.85)
ROUGE = Brush("rouge", (0.84, 0.27, 0.22), radius=1.7, density=0.95, grain=0.85)
VERT = Brush("vert", (0.22, 0.60, 0.42), radius=1.7, density=0.95, grain=0.85)
HB = Brush("hb", (0.22, 0.22, 0.24), radius=1.35, density=1.5, grain=0.7)
B2 = Brush("2b", (0.11, 0.11, 0.13), radius=1.75, density=2.4, grain=0.6, flow_gamma=1.1)
# Crayon de mise au net : la pression change fortement l'épaisseur (pleins et déliés).
NET = Brush("net", (0.13, 0.13, 0.15), radius=2.1, density=2.3, min_size=0.28, grain=0.55,
            flow_gamma=0.9)
# Crayon gras de storyboard : trait large et un peu sale, pour dessiner vite et petit.
STORY = Brush("story", (0.14, 0.14, 0.16), radius=2.7, density=1.9, min_size=0.4, grain=0.75)
ESTOMPE = Brush("tranche", (0.24, 0.24, 0.26), radius=8.0, density=0.5, min_size=0.8,
                hardness=0.55, grain=0.95, spacing=0.18, scatter=0.04)
# Trait vectoriel parfait : sert uniquement de point de comparaison.
VECTEUR = Brush("vecteur", (0.15, 0.15, 0.17), radius=1.5, density=4.0, min_size=1.0,
                grain=0.0, scatter=0.0, flow_gamma=0.0)
