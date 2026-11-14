"""Chemins façon SVG (M L C Q Z absolus, plus X = segment non tracé) -> polylignes."""
import re
import numpy as np

TOKEN = re.compile(r"([MLCQZX])|(-?\d*\.?\d+)")


def parse(d, step=2.5):
    """Liste de sous-chemins : dict(pts (n,2), pen (n,) vrai si le segment qui arrive au point
    est tracé, corners [indices], closed)."""
    toks = TOKEN.findall(d)
    out, pts, pen, corners, i, cmd = [], [], [], [], 0, None
    cur = np.zeros(2)

    def num():
        nonlocal i
        v = float(toks[i][1]); i += 1
        return v

    def pt():
        return np.array([num(), num()])

    def flush(closed=False):
        nonlocal pts, pen, corners
        if len(pts) > 1:
            out.append(dict(pts=np.array(pts), pen=np.array(pen, bool), corners=list(corners), closed=closed))
        pts, pen, corners = [], [], []

    def seg(points, drawn=True):
        for p in points:
            pts.append(p); pen.append(drawn)
        corners.append(len(pts) - 1)

    while i < len(toks):
        if toks[i][0]:
            cmd = toks[i][0]; i += 1
            if cmd == "Z":
                if pts and np.hypot(*(pts[-1] - pts[0])) > 0.5:
                    n = max(2, int(np.hypot(*(pts[0] - pts[-1])) / step))
                    a, b = pts[-1].copy(), pts[0].copy()
                    seg([a + (b - a) * t for t in np.linspace(0, 1, n + 1)[1:]])
                flush(True)
                continue
        if cmd == "M":
            flush()
            cur = pt(); pts = [cur.copy()]; pen = [False]; corners = [0]; cmd = "L"
        elif cmd in "LX":
            p = pt()
            n = max(2, int(np.hypot(*(p - cur)) / step))
            seg([cur + (p - cur) * t for t in np.linspace(0, 1, n + 1)[1:]], cmd == "L")
            cur = p
        elif cmd == "C":
            a, b, p = pt(), pt(), pt()
            length = np.hypot(*(a - cur)) + np.hypot(*(b - a)) + np.hypot(*(p - b))
            n = max(4, int(length / step))
            seg([(1 - t)**3 * cur + 3 * (1 - t)**2 * t * a + 3 * (1 - t) * t * t * b + t**3 * p
                 for t in np.linspace(0, 1, n + 1)[1:]])
            cur = p
        elif cmd == "Q":
            a, p = pt(), pt()
            n = max(4, int((np.hypot(*(a - cur)) + np.hypot(*(p - a))) / step))
            seg([(1 - t)**2 * cur + 2 * (1 - t) * t * a + t * t * p for t in np.linspace(0, 1, n + 1)[1:]])
            cur = p
        else:
            raise ValueError(cmd)
    flush()
    return out


def ellipse(cx, cy, rx, ry):
    k = 0.5523
    return (f"M {cx - rx} {cy} C {cx - rx} {cy - k * ry} {cx - k * rx} {cy - ry} {cx} {cy - ry} "
            f"C {cx + k * rx} {cy - ry} {cx + rx} {cy - k * ry} {cx + rx} {cy} "
            f"C {cx + rx} {cy + k * ry} {cx + k * rx} {cy + ry} {cx} {cy + ry} "
            f"C {cx - k * rx} {cy + ry} {cx - rx} {cy + k * ry} {cx - rx} {cy} Z")
