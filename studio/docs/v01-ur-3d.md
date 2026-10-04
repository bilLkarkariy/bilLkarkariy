# V01 UR — réemploi 3D sur la voix réelle

Aucun calcul Blender. Les images françaises sont lues par `Shot3D`, avec les correspondances de `src/data/remap3d_ur.json`. Images vidéo à 30 i/s ; fin exclusive ; images locales depuis 1. Le plan dhikr finit à `at("p52") - 10`, quand le verset apparaît pendant la voix.

| Plan | Images vidéo UR [début, fin[ | Durée (images) | PNG FR présents | Décalage début / fin depuis estimation |
|---|---:|---:|---:|---:|
| maquette | 132 → 247 | 115 | 81 | +13 / +33 |
| seuls | 2723 → 2932 | 209 | 74 | +49 / +36 |
| bouton | 4995 → 5139 | 144 | 42 | +116 / +138 |
| salon | 4270 → 4353 | 83 | 41 | +102 / +100 |
| vide | 9917 → 10520 | 603 | 515 | +487 / +526 |
| khalwa | 12224 → 12637 | 413 | 332 | +574 / +611 |
| dhikr | 15037 → 15430 | 393 | 312 | +715 / +727 |
| meublee | 20555 → 20681 | 126 | 43 | +829 / +828 |

## Repères locaux FR → UR

- **maquette** : ['p1', 'Seul']: 4 → 4; ['p1', 'téléphone']: 76 → 50; ['p1', 'lire']: 114 → 74.
- **seuls** : ['p10', 'bouton']: 66 → 79; ['p10', 'remettre']: 104 → 134; ['p10', 'seuls']: 33 → 28.
- **bouton** : ['p18', 'bouton', 'end']: 67 → 79.
- **salon** : ['p16', 'Un']: 85 → 86; ['p16', 'canapé']: 50 → 64; ['p16', 'chez']: 4 → 4.
- **vide** : ['p35', 'chaise']: 91 → 130; ['p35', 'cherches']: 307 → 362; ['p35', 'entres']: 146 → 189; ['p35', 'murs']: 249 → 312; ['p35', 'porte']: 324 → 388; ['p35', 'quoi']: 177 → 224; ['p35', 'table']: 120 → 158; ['p35', 'touches']: 240 → 295; ['p35', 'tournes']: 206 → 256; ['p36', 'pièce']: 418 → 510; ['p36', 'téléphone']: 448 → 536.
- **khalwa** : ['p44', 'Exactement']: 219 → 250; ['p44', 'quarante']: 122 → 151; ['p44', 'retire']: 47 → 28; ['p44', 'volontairement']: 59 → 63.
- **dhikr** : ['p51', "L'idée"]: 7 → 7; ['p51', 'fixe']: 114 → 156; ['p51', 'meuble']: 58 → 80; ['p51', 'part']: 156 → 207; ['p51', 'ramènes']: 193 → 272; ['p51', 'ramènes', 'start', 1]: 272 → 352; ['p51', 'repart']: 233 → 311.
- **meublee** : ['p67', 'meublé']: 11 → 11.

## Reproduction sans rendu 3D

```bash
HF_HUB_OFFLINE=1 python3 tools/report_3d_en.py --lang ur
HF_HUB_OFFLINE=1 python3 tools/remap3d_en.py --lang ur
```

Contrôler les PNG Remotion avec `WITH3D=1 FACELESS=1`, selon `docs/v01-ur-images-fixes.md`. Vérifier les changements de vitesse, les fondus et les éventuelles images tenues. Aucun PNG français n’est modifié.
