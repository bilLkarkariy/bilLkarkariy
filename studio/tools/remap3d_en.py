"""Ancien nom, gardé pour les documents de la version anglaise : même chose que
  python3 tools/remap3d.py --lang en
(voir tools/remap3d.py, valable pour toutes les langues ; même résultat que l'ancien script).
"""
import os
import runpy
import sys

sys.argv = [sys.argv[0], "--lang", "en", *sys.argv[1:]]
runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "remap3d.py"), run_name="__main__")
