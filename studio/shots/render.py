"""Rendu d'un plan : décor dessiné une fois, puis un dessin de personnage par image.

Deux calques de décor : le fond, toujours derrière le personnage, et le premier
plan, fait des boîtes qui passent devant lui sur au moins un dessin.
"""
import numpy as np

from studio.engine import scene
from studio.engine.brush import HB, NET
from studio.engine.canvas import Document
from studio.engine.construction import draw, matte
from studio.engine.hand import Draftsman
from studio.engine.video import Video


class ShotRenderer:
    def __init__(self, shot, cons, seed=0):
        """cons : toutes les constructions du personnage qui seront dessinées dans ce plan."""
        self.shot, self.seed = shot, seed
        self.front = sorted(set().union(*[b for con in cons for _, _, b in con.mattes]))
        back = [i for i in range(len(shot.DECOR)) if i not in self.front]
        self.base = Document(shot.W, shot.H, seed)
        d = Draftsman(self.base, seed)
        style = dict(brush=HB, pressure=0.5, through=0, care=1.5)
        draw(d, scene.construct(shot.DECOR, shot.CAM, shot.SOL, only=back), shot.ORIGIN,
             shot.SCALE, layer="decor", **style)
        draw(d, scene.construct(shot.DECOR, shot.CAM, only=self.front), shot.ORIGIN, shot.SCALE,
             layer="premier_plan", **style)
        corners = np.array([c for _, c in shot.CAMERA_KEYS])
        self.x0, self.y0 = corners.min(axis=0).astype(int)
        self.x1, self.y1 = (corners.max(axis=0) + shot.FRAME).astype(int)

    def drawing(self, con, under=None, seed=0):
        """Un dessin du personnage sur le décor. `under` : sa construction bleue, facultative.
        Renvoie l'image (uint8) de la zone parcourue par le cadre."""
        shot, w, h = self.shot, self.shot.W, self.shot.H
        doc = Document(w, h, self.seed, paper=self.base.paper)
        # Le personnage cache le fond partout, le premier plan seulement là où il est devant.
        for name, hole in (("decor", 1 - matte(con, shot.ORIGIN, shot.SCALE, w, h)),
                           ("premier_plan", 1 - matte(con, shot.ORIGIN, shot.SCALE, w, h,
                                                      self.front))):
            source, layer = self.base.layer(name), doc.layer(name)
            layer.D, layer.C = source.D * hole, source.C * hole[..., None]
        d = Draftsman(doc, seed)
        if under is not None:
            draw(d, under, shot.ORIGIN, shot.SCALE, pressure=0.25, through=0.2)
        draw(d, con, shot.ORIGIN, shot.SCALE, brush=NET, layer="net", pressure=0.7, through=0,
             care=1.3, min_size=14)
        return (doc.composite((self.x0, self.y0, self.x1, self.y1)) * 255).astype(np.uint8)

    def play(self, path, image_at, loops=3, pause=10):
        """Vidéo du plan. image_at(numéro d'image) -> dessin à montrer ; le cadre bouge à chaque image."""
        shot = self.shot
        ow, oh = shot.FRAME[0] // 2, shot.FRAME[1] // 4 * 2      # demi-taille, hauteur paire
        video = Video(path, ow, oh, fps=shot.FPS)
        for _ in range(loops):
            for f in range(1, shot.FRAMES + 1):
                cx, cy = (shot.frame_corner(f) - (self.x0, self.y0)).astype(int)
                crop = image_at(f)[cy:cy + oh * 2, cx:cx + ow * 2].astype(np.float32) / 255
                small = crop.reshape(oh, 2, ow, 2, 3).mean(axis=(1, 3))
                video.add(small)
            video.add(small, pause)
        return video.close()
