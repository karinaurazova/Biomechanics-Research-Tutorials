"""Show the accuracy-coverage trade-off of coherence thresholding."""

import matplotlib.pyplot as plt
import numpy as np

from biomechanics_tutorials.structure_tensor import (
    StructureTensorParameters,
    confidence_mask,
    orientation_error_metrics,
    structure_tensor_orientation,
    synthetic_curved_fibers,
)
from common import save_figure, title, tr


def main() -> None:
    image, truth = synthetic_curved_fibers(noise_std=0.10, seed=11)
    result = structure_tensor_orientation(image, StructureTensorParameters(1.0, 3.0))
    thresholds = np.linspace(0.0, 0.9, 19)
    errors = []
    coverages = []
    for threshold in thresholds:
        mask = confidence_mask(result, float(threshold), 0.10, border=10)
        metrics = orientation_error_metrics(result["orientation"], truth, mask)
        errors.append(metrics["mae_deg"])
        coverages.append(metrics["coverage"])
    for language in ("en", "ru"):
        fig, ax_error = plt.subplots(figsize=(8.2, 4.8))
        ax_coverage = ax_error.twinx()
        error_line = ax_error.plot(thresholds, errors, "o-", lw=2, label=tr("mae", language))[0]
        coverage_line = ax_coverage.plot(
            thresholds, coverages, "s--", lw=2, label=tr("coverage", language)
        )[0]
        ax_error.set(xlabel=tr("threshold", language), ylabel=tr("mae", language))
        ax_coverage.set_ylabel(tr("coverage", language))
        ax_error.set_title(title("coherence_threshold", language))
        ax_error.legend([error_line, coverage_line], [error_line.get_label(), coverage_line.get_label()])
        save_figure(fig, "coherence_threshold", language)


if __name__ == "__main__":
    main()
