"""Milo : jeune adulte, 7 têtes de haut. Mannequin de référence de l'étape 2."""
from studio.characters.body import mannequin

PROPORTIONS = dict(
    root=3.90, waist=0.45, neck=1.35, head=0.33,
    skull=dict(center=(0, 0.52, 0.0), radii=(0.40, 0.45, 0.46)),
    jaw=dict(center=(0, 0.20, 0.20), radii=(0.30, 0.27, 0.27)),
    cage=dict(center=(0, 0.72, 0.02), radii=(0.60, 0.66, 0.40)),
    pelvis=dict(center=(0, -0.03, 0.0), radii=(0.52, 0.38, 0.34)),
    shoulder=(0.72, 1.24), hip=(0.30, -0.20),
    upper_arm=1.08, forearm=0.95, hand=0.62, thigh=1.75, shin=1.70,
    arm_r=(0.17, 0.13, 0.095), leg_r=(0.27, 0.19, 0.185, 0.11), neck_r=(0.17, 0.16),
    hand_ball=dict(center=(0, -0.31, 0), radii=(0.08, 0.32, 0.16)),
    foot=(((0, -0.12, -0.05), 0.13), ((0, -0.16, 0.62), 0.09)),
)


def build():
    return mannequin("milo", PROPORTIONS)
