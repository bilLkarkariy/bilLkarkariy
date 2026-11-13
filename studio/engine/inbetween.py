"""Les intervalles : les poses entre deux clés.

Chaque articulation suit une courbe lisse passant par ses clés. Le « flow » d'une
clé règle comment on la traverse : 1 = sans ralentir (mouvement continu),
0 = arrêt complet (ralenti à l'arrivée, départ en douceur).
"""
import numpy as np

from .mannequin import Pose


def _quat(m):
    """Matrice de rotation -> quaternion (w, x, y, z)."""
    t = np.trace(m)
    if t > 0:
        s = np.sqrt(t + 1.0) * 2
        q = [0.25 * s, (m[2, 1] - m[1, 2]) / s, (m[0, 2] - m[2, 0]) / s, (m[1, 0] - m[0, 1]) / s]
    else:
        i = int(np.argmax(np.diag(m)))
        j, k = (i + 1) % 3, (i + 2) % 3
        s = np.sqrt(1.0 + m[i, i] - m[j, j] - m[k, k]) * 2
        q = [0.0] * 4
        q[0] = (m[k, j] - m[j, k]) / s
        q[1 + i], q[1 + j], q[1 + k] = 0.25 * s, (m[j, i] + m[i, j]) / s, (m[k, i] + m[i, k]) / s
    return np.array(q)


def _matrix(q):
    w, x, y, z = q / np.linalg.norm(q)
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                     [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                     [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


def curve(times, values, flow, t):
    """Courbe de Hermite passant par les clés ; la vitesse en chaque clé est celle
    de ses voisines, multipliée par son flow."""
    times, values = np.asarray(times, float), np.asarray(values, float)
    n = len(times)
    slopes = np.zeros_like(values)
    for i in range(n):
        a, b = max(i - 1, 0), min(i + 1, n - 1)
        slopes[i] = (values[b] - values[a]) / (times[b] - times[a]) * flow[i]
    i = int(np.clip(np.searchsorted(times, t, side="right") - 1, 0, n - 2))
    h = times[i + 1] - times[i]
    s = np.clip((t - times[i]) / h, 0, 1)
    return ((2 * s ** 3 - 3 * s ** 2 + 1) * values[i] + (s ** 3 - 2 * s ** 2 + s) * h * slopes[i]
            + (-2 * s ** 3 + 3 * s ** 2) * values[i + 1] + (s ** 3 - s ** 2) * h * slopes[i + 1])


class Motion:
    """Mouvement défini par des poses clés datées. `at(image)` renvoie la pose interpolée."""

    def __init__(self, model, keys):
        """keys : liste de (image, pose, flow)."""
        self.model = model
        self.times = [k[0] for k in keys]
        self.flow = [k[2] for k in keys]
        self.root, self.quats = [], {name: [] for name in model.joints}
        for _, pose, _ in keys:
            frames = model.solve(pose)
            for name, (parent, _) in model.joints.items():
                rot = frames[name][1]
                local = rot if parent is None else frames[parent][1].T @ rot
                q = _quat(local)
                if self.quats[name] and q @ self.quats[name][-1] < 0:
                    q = -q                      # même rotation, chemin le plus court
                self.quats[name].append(q)
            self.root.append(frames[next(iter(model.joints))][0])

    def at(self, t):
        joints = {name: _matrix(curve(self.times, q, self.flow, t))
                  for name, q in self.quats.items()}
        root = curve(self.times, self.root, self.flow, t)
        return Pose(root=root - np.asarray(self.model.root, float), ground=False, **joints)
