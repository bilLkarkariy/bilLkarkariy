"""Écriture d'une vidéo MP4 à partir d'images (tableaux float 0..1) via ffmpeg."""
import subprocess

import numpy as np


class Video:
    def __init__(self, path, w, h, fps=24, scale=1.0):
        ow, oh = int(w * scale) // 2 * 2, int(h * scale) // 2 * 2
        self.count = 0
        self._ff = subprocess.Popen(
            ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
             "-s", f"{w}x{h}", "-r", str(fps), "-i", "-",
             "-vf", f"scale={ow}:{oh}:flags=area", "-c:v", "libx264", "-pix_fmt", "yuv420p",
             "-crf", "20", "-movflags", "+faststart", str(path)],
            stdin=subprocess.PIPE)

    def add(self, frame, repeat=1):
        data = (frame * 255 + 0.5).astype(np.uint8).tobytes()
        for _ in range(repeat):
            self._ff.stdin.write(data)
        self.count += repeat

    def close(self):
        self._ff.stdin.close()
        if self._ff.wait() != 0:
            raise RuntimeError("ffmpeg a échoué")
        return self.count
