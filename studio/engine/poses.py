"""Poses de base. Une pose ne contient que des rotations : elle vaut pour tout personnage."""
from .mannequin import Level, Pose, To, rx, ry, rz

# Debout, bras écartés du corps : la pose neutre des model sheets.
A_POSE = Pose(
    shoulder_L=To((0.45, -0.89, 0)), shoulder_R=To((-0.45, -0.89, 0)),
    hip_L=To((0.03, -1, 0), twist=8), hip_R=To((-0.03, -1, 0), twist=-8),
)

# Marche, position de contact : jambe droite devant, talon posé ; bras opposés.
MARCHE = Pose(
    pelvis=ry(8), waist=ry(-16) @ rx(4), head=ry(8) @ rx(-3),
    hip_R=To((0, -0.88, 0.47)), knee_R=rx(6), ankle_R=Level(-18),
    hip_L=To((0, -0.93, -0.37)), knee_L=rx(14), ankle_L=Level(28),
    shoulder_L=To((0.10, -0.90, 0.42)), elbow_L=rx(-28),
    shoulder_R=To((-0.10, -0.92, -0.38)), elbow_R=rx(-14),
)

# Course : buste engagé, genou droit levé, poussée sur la jambe gauche.
COURSE = Pose(
    pelvis=rx(12) @ ry(10), waist=ry(-22) @ rx(10), neck=rx(-8), head=ry(12) @ rx(-12),
    hip_R=To((0, -0.42, 0.91)), knee_R=rx(98), ankle_R=Level(12),
    hip_L=To((0, -0.86, -0.51)), knee_L=rx(22), ankle_L=Level(48),
    shoulder_L=To((0.12, -0.72, 0.68)), elbow_L=rx(-95),
    shoulder_R=To((-0.14, -0.66, -0.74)), elbow_R=rx(-88),
)

# Accroupi, bras en arrière : l'anticipation avant un saut.
ELAN = Pose(
    pelvis=rx(32), waist=rx(26), neck=rx(-22), head=rx(-26),
    hip_L=To((0.14, -0.22, 0.96)), knee_L=rx(128), ankle_L=Level(0),
    hip_R=To((-0.14, -0.22, 0.96)), knee_R=rx(128), ankle_R=Level(0),
    shoulder_L=To((0.22, -0.42, -0.88)), elbow_L=rx(-16),
    shoulder_R=To((-0.22, -0.42, -0.88)), elbow_R=rx(-16),
)
