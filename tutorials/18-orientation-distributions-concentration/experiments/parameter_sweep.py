"""Additional parameter sweep for Tutorial 18."""

from __future__ import annotations

from common import DATA
from biomechanics_tutorials.orientation_distributions import concentration_sweep


def main() -> None:
    rows = concentration_sweep(concentrations=(0.25, 0.40, 0.55, 0.70, 0.85, 0.95), seed=180)
    lines = ["target_concentration,modality,resultant_length,kappa,js_to_ground_truth,orientation_mae_deg"]
    for row in rows:
        lines.append(
            f"{row['target_concentration']:.6g},{row['modality']},{row['resultant_length']:.8g},"
            f"{row['kappa']:.8g},{row['js_to_ground_truth']:.8g},{row['orientation_mae_deg']:.8g}"
        )
    (DATA / "extended_concentration_sweep.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("Extended Tutorial 18 sweep written.")


if __name__ == "__main__":
    main()
