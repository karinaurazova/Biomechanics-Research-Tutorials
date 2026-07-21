from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np

from biomechanics_tutorials.physics_informed_learning import (
    evaluate_prediction,
    generate_bar_dataset,
    inverse_stiffness_scale_sweep,
    make_learning_history,
    run_case_suite,
    run_weight_sweep,
)

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
DATA.mkdir(exist_ok=True)

def write_csv(path: Path, header, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)

def main():
    data = generate_bar_dataset()
    np.savez(
        DATA / "physics_informed_learning_dataset.npz",
        x=data.x,
        theta=data.theta,
        rho_f=data.rho_f,
        kappa=data.kappa,
        connectivity=data.connectivity,
        stiffness_true=data.stiffness_true,
        stiffness_image=data.stiffness_image,
        displacement_true=data.displacement_true,
        strain_true=data.strain_true,
        stress_true=data.stress_true,
        obs_x=data.obs_x,
        obs_u=data.obs_u,
        traction=data.traction,
    )
    cases = run_case_suite(data)
    rows = []
    for name, pred in cases.items():
        m = evaluate_prediction(data, pred)
        rows.append([name, m["u_mae"], m["u_rmse"], m["strain_mae"], m["stress_mae"], m["pde_residual_rms"], m["traction_error"]])
    write_csv(DATA / "case_metrics.csv", ["case", "u_mae", "u_rmse", "strain_mae", "stress_mae", "pde_residual_rms", "traction_error"], rows)

    sweep = run_weight_sweep(data)
    write_csv(DATA / "physics_weight_sweep.csv", ["lambda_pde", "u_mae", "strain_mae", "pde_residual_rms", "traction_error"], [[r["lambda_pde"], r["u_mae"], r["strain_mae"], r["pde_residual_rms"], r["traction_error"]] for r in sweep])

    inv = inverse_stiffness_scale_sweep(data)
    write_csv(DATA / "inverse_stiffness_scale.csv", ["alpha", "objective", "u_mae", "strain_mae", "pde_residual_rms", "traction_error"], [[r["alpha"], r["objective"], r["u_mae"], r["strain_mae"], r["pde_residual_rms"], r["traction_error"]] for r in inv])

    hist = make_learning_history(data)
    write_csv(DATA / "learning_history.csv", ["step", "lambda_pde", "u_mae", "strain_mae", "pde_residual_rms", "traction_error"], [[r["step"], r["lambda_pde"], r["u_mae"], r["strain_mae"], r["pde_residual_rms"], r["traction_error"]] for r in hist])

    best = min(inv, key=lambda r: r["objective"])
    (DATA / "benchmark_summary.json").write_text(json.dumps({"tutorial": 24, "best_alpha": best["alpha"], "best_objective": best["objective"], "n_cases": len(cases)}, indent=2), encoding="utf-8")
    print("Tutorial 24 reproduced successfully")

if __name__ == "__main__":
    main()
