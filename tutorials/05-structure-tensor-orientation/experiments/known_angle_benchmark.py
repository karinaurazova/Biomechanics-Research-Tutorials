"""Verify orientation recovery over known axial angles."""

import matplotlib.pyplot as plt
import numpy as np

from biomechanics_tutorials.structure_tensor import (
    StructureTensorParameters,
    axial_angle_difference,
    confidence_mask,
    structure_tensor_orientation,
    synthetic_parallel_fibers,
    weighted_axial_mean,
)
from common import save_figure, title, tr


def main() -> None:
    angles = np.arange(-80.0, 81.0, 10.0)
    estimates = []
    errors = []
    for angle in angles:
        image, _ = synthetic_parallel_fibers(
            shape=(128, 128), angle_degrees=float(angle), noise_std=0.035, seed=int(angle + 100)
        )
        result = structure_tensor_orientation(image, StructureTensorParameters(1.0, 3.0))
        mask = confidence_mask(result, 0.4, 0.15, border=8)
        estimate, _ = weighted_axial_mean(result["orientation"][mask], result["coherence"][mask])
        estimate_deg = np.rad2deg(estimate)
        estimates.append(estimate_deg)
        errors.append(abs(np.rad2deg(axial_angle_difference(estimate, np.deg2rad(angle)))))
    for language in ("en", "ru"):
        fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
        axes[0].plot(angles, angles, "--", lw=1.5, label="identity" if language == "en" else "тождество")
        axes[0].plot(angles, estimates, "o-", lw=2, label="estimate" if language == "en" else "оценка")
        axes[0].set(xlabel=tr("known_angle", language), ylabel=tr("estimated_angle", language))
        axes[0].legend()
        axes[1].plot(angles, errors, "o-", lw=2)
        axes[1].set(xlabel=tr("known_angle", language), ylabel=tr("error", language))
        fig.suptitle(title("known_angle_benchmark", language), fontsize=16)
        save_figure(fig, "known_angle_benchmark", language)


if __name__ == "__main__":
    main()
