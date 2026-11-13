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

    # Une grande page est réduite par blocs entiers avant l'encodage : seule la zone
    # modifiée est recalculée à chaque image.
    k = max(1, int(1 / scale)) if scale < 1 else 1
    hk, wk = doc.h // k, doc.w // k

    def shrink(y0, y1, x0, x1):
        block = frame[y0 * k:y1 * k, x0 * k:x1 * k]
        return block.reshape(y1 - y0, k, x1 - x0, k, 3).mean(axis=(1, 3))

    small = shrink(0, hk, 0, wk)
    video = Video(path, wk, hk, fps, scale * k)

    def refresh(box):
        x0, y0, x1, y1 = box
        frame[y0:y1, x0:x1] = replay.composite(box)
        sx0, sy0 = x0 // k, y0 // k
        sx1, sy1 = min(wk, -(-x1 // k)), min(hk, -(-y1 // k))
        small[sy0:sy1, sx0:sx1] = shrink(sy0, sy1, sx0, sx1)

    def emit():
        video.add(small)

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
                    refresh(dirty)
                    dirty = None
                emit()
                budget = per_frame
    if dirty is not None:
        refresh(dirty)
    video.add(small, int(hold * fps) + 1)
    return video.close()
