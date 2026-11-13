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

# À l'arrêt, regard par-dessus l'épaule gauche.
REGARD = Pose(
    waist=ry(25), neck=ry(25), head=ry(58) @ rx(4),
    hip_L=To((0.06, -1, 0.02), twist=10), hip_R=To((-0.05, -1, -0.03), twist=-6),
    shoulder_L=To((0.16, -0.97, -0.12)), elbow_L=rx(-14),
    shoulder_R=To((-0.14, -0.98, 0.08)), elbow_R=rx(-18),
)

# Saut, au sommet : corps étiré, bras levés, genou droit monté.
SAUT = Pose(
    root=(0, 1.9, 0), ground=False,
    pelvis=rx(-6), waist=rx(-12), head=rx(-10),
    hip_R=To((-0.05, -0.50, 0.86)), knee_R=rx(112), ankle_R=rx(25),
    hip_L=To((0.04, -0.95, -0.30)), knee_L=rx(28), ankle_L=rx(40),
    shoulder_L=To((0.38, 0.86, 0.30)), elbow_L=rx(-22),
    shoulder_R=To((-0.50, 0.62, 0.52)), elbow_R=rx(-42),
)

# Réception : genoux fléchis, buste engagé, bras écartés pour l'équilibre.
RECEPTION = Pose(
    pelvis=rx(18), waist=rx(16), neck=rx(-10), head=rx(-14),
    hip_L=To((0.16, -0.42, 0.89)), knee_L=rx(108), ankle_L=Level(0),
    hip_R=To((-0.14, -0.52, 0.84)), knee_R=rx(98), ankle_R=Level(0),
    shoulder_L=To((0.62, -0.62, 0.36)), elbow_L=rx(-30),
    shoulder_R=To((-0.66, -0.52, -0.20)), elbow_R=rx(-34),
)

# Appui : les deux pieds se posent, le corps freine et commence à descendre.
APPUI = Pose(
    pelvis=rx(6), waist=rx(8), head=rx(-6),
    hip_R=To((-0.08, -0.86, 0.50)), knee_R=rx(38), ankle_R=Level(0),
    hip_L=To((0.08, -0.97, -0.22)), knee_L=rx(40), ankle_L=Level(25),
    shoulder_L=To((0.20, -0.85, -0.50)), elbow_L=rx(-30),
    shoulder_R=To((-0.20, -0.90, -0.40)), elbow_R=rx(-30),
)

# Détente : tout le corps s'étire, sur les pointes, les bras lancés vers le haut.
DETENTE = Pose(
    pelvis=rx(10), waist=rx(-4), head=rx(-8),
    hip_L=To((0.06, -0.985, -0.16)), knee_L=rx(6), ankle_L=Level(38),
    hip_R=To((-0.06, -0.96, -0.28)), knee_R=rx(10), ankle_R=Level(44),
    shoulder_L=To((0.25, 0.72, 0.64)), elbow_L=rx(-15),
    shoulder_R=To((-0.25, 0.78, 0.57)), elbow_R=rx(-15),
)

# Montée : les genoux commencent à remonter.
MONTEE = Pose(
    pelvis=rx(4), waist=rx(-6), head=rx(-6),
    hip_R=To((-0.06, -0.80, 0.60)), knee_R=rx(70), ankle_R=rx(12),
    hip_L=To((0.05, -0.96, -0.10)), knee_L=rx(35), ankle_L=rx(18),
    shoulder_L=To((0.30, 0.90, 0.30)), elbow_L=rx(-15),
    shoulder_R=To((-0.35, 0.85, 0.40)), elbow_R=rx(-15),
)

# Sommet : groupé au-dessus de l'obstacle.
SOMMET = Pose(
    pelvis=rx(-4), waist=rx(14), head=rx(-12),
    hip_R=To((-0.10, -0.28, 0.95)), knee_R=rx(118), ankle_R=rx(15),
    hip_L=To((0.10, -0.50, 0.86)), knee_L=rx(105), ankle_L=rx(20),
    shoulder_L=To((0.55, 0.50, 0.50)), elbow_L=rx(-35),
    shoulder_R=To((-0.60, 0.45, 0.45)), elbow_R=rx(-40),
)

# Descente : les jambes vont chercher le sol.
DESCENTE = Pose(
    pelvis=rx(-10), waist=rx(8), head=rx(-4),
    hip_R=To((-0.08, -0.80, 0.60)), knee_R=rx(22), ankle_R=rx(-10),
    hip_L=To((0.08, -0.88, 0.47)), knee_L=rx(35), ankle_L=rx(-5),
    shoulder_L=To((0.60, 0.30, -0.20)), elbow_L=rx(-30),
    shoulder_R=To((-0.65, 0.20, -0.10)), elbow_R=rx(-30),
)

# Contact : les pieds touchent, jambes encore presque tendues.
CONTACT = Pose(
    pelvis=rx(4), waist=rx(10), head=rx(-8),
    hip_R=To((-0.10, -0.90, 0.42)), knee_R=rx(30), ankle_R=Level(-8),
    hip_L=To((0.10, -0.93, 0.36)), knee_L=rx(34), ankle_L=Level(0),
    shoulder_L=To((0.70, -0.30, 0.20)), elbow_L=rx(-25),
    shoulder_R=To((-0.72, -0.25, 0.10)), elbow_R=rx(-25),
)

# Rétablissement : elle se redresse.
RETABLI = Pose(
    pelvis=rx(8), waist=rx(8), head=rx(-8),
    hip_L=To((0.10, -0.93, 0.35)), knee_L=rx(40), ankle_L=Level(0),
    hip_R=To((-0.10, -0.93, 0.35)), knee_R=rx(40), ankle_R=Level(0),
    shoulder_L=To((0.35, -0.90, 0.15)), elbow_L=rx(-25),
    shoulder_R=To((-0.35, -0.90, 0.15)), elbow_R=rx(-25),
)
