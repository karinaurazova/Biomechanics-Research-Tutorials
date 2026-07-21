from __future__ import annotations

import csv
from pathlib import Path

from biomechanics_tutorials.physics_informed_learning import (
    evaluate_prediction,
    fit_physics_informed_model,
    generate_bar_dataset,
)

out = Path(__file__).resolve().parents[1] / "data" / "noise_sweep.csv"
rows = []
for noise in [0.0, 0.001, 0.002, 0.005, 0.01, 0.02]:
    data = generate_bar_dataset(noise_level=noise)
    pred = fit_physics_informed_model(data, lambda_data=1.0, lambda_pde=10.0)
    m = evaluate_prediction(data, pred)
    rows.append([noise, m["u_mae"], m["strain_mae"], m["pde_residual_rms"]])

with out.open("w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["noise", "u_mae", "strain_mae", "pde_residual_rms"])
    writer.writerows(rows)
print(f"wrote {out}")
