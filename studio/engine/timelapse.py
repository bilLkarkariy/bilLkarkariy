"""Rejoue le journal d'un document, trait après trait, et en fait une vidéo."""
import numpy as np

from .canvas import Document
from .video import Video


def timelapse(doc, path, seconds=10.0, fps=30, hold=2.0, scale=1.0):
    """Écrit une vidéo MP4 du dessin en train de se faire. Renvoie le nombre d'images."""
    travel = sum(float(np.hypot(*np.diff(d[:, :2], axis=0).T).sum()) for _, _, d in doc.journal)
    per_frame = max(1.0, travel / (seconds * fps))      # pixels de trait par image

    replay = Document(doc.w, doc.h, doc.seed, paper=doc.paper)
    for layer in doc.layers:
        replay.layer(layer.name)
    frame = replay.composite()

    video = Video(path, doc.w, doc.h, fps, scale)

    def emit():
        video.add(frame)

    budget, dirty = per_frame, None
    for name, brush, dabs in doc.journal:
        step = np.concatenate([[0.0], np.hypot(*np.diff(dabs[:, :2], axis=0).T)])
        i = 0
        while i < len(dabs):
            # Avance le long du trait jusqu'à épuiser le budget de l'image courante.
            run = np.cumsum(step[i + 1:]) if i + 1 < len(dabs) else np.array([])
            n = int(np.searchsorted(run, budget)) + 1
            box = replay.layer(name).stamp(dabs[i:i + n], brush, replay.paper.tooth)
            budget -= float(run[n - 2]) if n >= 2 else 0.0
            i += n
            if box is not None:
                dirty = box if dirty is None else (min(dirty[0], box[0]), min(dirty[1], box[1]),
                                                   max(dirty[2], box[2]), max(dirty[3], box[3]))
            if i < len(dabs):       # budget épuisé au milieu du trait : on sort une image
                if dirty is not None:
                    x0, y0, x1, y1 = dirty
                    frame[y0:y1, x0:x1] = replay.composite(dirty)
                    dirty = None
                emit()
                budget = per_frame
    if dirty is not None:
        x0, y0, x1, y1 = dirty
        frame[y0:y1, x0:x1] = replay.composite(dirty)
    video.add(frame, int(hold * fps) + 1)
    return video.close()
