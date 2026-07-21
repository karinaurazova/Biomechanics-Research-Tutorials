from __future__ import annotations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from biomechanics_tutorials.rve_homogenization import convergence_study, save_csv

OUT = Path(__file__).resolve().parents[1] / "data" / "resolution_experiment.csv"
rows = convergence_study((6, 8, 10, 12, 14, 16), seed=22)
save_csv(OUT, rows)
print(f"Saved {OUT}")
