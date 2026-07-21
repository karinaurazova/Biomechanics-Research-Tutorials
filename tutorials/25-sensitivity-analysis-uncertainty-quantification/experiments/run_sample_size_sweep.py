#!/usr/bin/env python3
"""Run a small sample-size convergence sweep for Tutorial 25."""
from pathlib import Path
import sys
import pandas as pd
ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
from biomechanics_tutorials.sensitivity_uncertainty import monte_carlo
rows = []
for n in [128, 256, 512, 1024, 2048, 4096]:
    _, _, summary = monte_carlo(n=n, seed=100+n)
    rows.append({"n": n, "peak_mean": summary["peak_stress"]["mean"], "peak_q05": summary["peak_stress"]["q05"], "peak_q95": summary["peak_stress"]["q95"]})
out = Path(__file__).resolve().parents[1] / "data" / "sample_size_experiment.csv"
pd.DataFrame(rows).to_csv(out, index=False)
print(out)
