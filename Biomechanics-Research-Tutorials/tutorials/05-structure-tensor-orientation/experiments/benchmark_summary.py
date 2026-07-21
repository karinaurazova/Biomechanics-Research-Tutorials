"""Build a compact synthetic verification benchmark."""

import csv

import matplotlib.pyplot as plt
import numpy as np

from biomechanics_tutorials.structure_tensor import (
    StructureTensorParameters,
    confidence_mask,
    orientation_error_metrics,
    structure_tensor_orientation,
    synthetic_curved_fibers,
    synthetic_parallel_fibers,
    synthetic_piecewise_fibers,
)
from common import DATA_DIRECTORY, save_figure, title


def evaluate(name, image, truth, parameters):
    result = structure_tensor_orientation(image, parameters)
    mask = confidence_mask(result, 0.35, 0.10, border=10)
    metrics = orientation_error_metrics(result["orientation"], truth, mask)
    return {"case": name, **metrics}


def main() -> None:
    cases = []
    image, truth = synthetic_parallel_fibers(angle_degrees=30, noise_std=0.02, seed=1)
    cases.append(evaluate("parallel-clean", image, truth, StructureTensorParameters(1, 3)))
    image, truth = synthetic_parallel_fibers(angle_degrees=30, noise_std=0.12, seed=2)
    cases.append(evaluate("parallel-noisy", image, truth, StructureTensorParameters(1, 5)))
    image, truth = synthetic_curved_fibers(noise_std=0.04, seed=3)
    cases.append(evaluate("curved", image, truth, StructureTensorParameters(1, 3)))
    image, truth = synthetic_piecewise_fibers(noise_std=0.03, seed=4)
    cases.append(evaluate("two-domains", image, truth, StructureTensorParameters(1, 3)))

    DATA_DIRECTORY.mkdir(parents=True, exist_ok=True)
    csv_path = DATA_DIRECTORY / "synthetic_benchmark.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(cases[0]))
        writer.writeheader()
        writer.writerows(cases)

    names = [case["case"] for case in cases]
    mae = [case["mae_deg"] for case in cases]
    p95 = [case["p95_deg"] for case in cases]
    coverage = [case["coverage"] for case in cases]
    translations = {
        "parallel-clean": "параллельные, чистые",
        "parallel-noisy": "параллельные, шум",
        "curved": "криволинейные",
        "two-domains": "две области",
    }
    x = np.arange(len(names))
    for language in ("en", "ru"):
        labels = names if language == "en" else [translations[name] for name in names]
        fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.5))
        axes[0].bar(x - 0.18, mae, width=0.36, label="MAE")
        axes[0].bar(x + 0.18, p95, width=0.36, label="P95")
        axes[0].set_xticks(x, labels, rotation=15)
        axes[0].set_ylabel("Error, degrees" if language == "en" else "Ошибка, градусы")
        axes[0].legend()
        axes[1].bar(x, coverage)
        axes[1].set_xticks(x, labels, rotation=15)
        axes[1].set_ylim(0, 1)
        axes[1].set_ylabel("Coverage" if language == "en" else "Покрытие")
        fig.suptitle(title("benchmark_summary", language), fontsize=16)
        save_figure(fig, "benchmark_summary", language)


if __name__ == "__main__":
    main()
