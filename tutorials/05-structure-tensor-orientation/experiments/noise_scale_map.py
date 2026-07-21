"""Map orientation error over noise and integration scale."""

import matplotlib.pyplot as plt
import numpy as np

from biomechanics_tutorials.structure_tensor import (
    StructureTensorParameters,
    orientation_error_metrics,
    structure_tensor_orientation,
    synthetic_parallel_fibers,
)
from common import save_figure, title, tr


def main() -> None:
    noise_levels = np.array([0.0, 0.03, 0.06, 0.10, 0.15])
    scales = np.array([0.8, 1.5, 2.5, 4.0, 7.0])
    errors = np.zeros((noise_levels.size, scales.size))
    for row, noise in enumerate(noise_levels):
        image, truth = synthetic_parallel_fibers(
            shape=(144, 144), angle_degrees=33.0, noise_std=float(noise), seed=25
        )
        mask = np.zeros(image.shape, dtype=bool)
        mask[10:-10, 10:-10] = True
        for column, scale in enumerate(scales):
            result = structure_tensor_orientation(
                image, StructureTensorParameters(1.0, float(scale))
            )
            errors[row, column] = orientation_error_metrics(
                result["orientation"], truth, mask
            )["mae_deg"]
    for language in ("en", "ru"):
        fig, ax = plt.subplots(figsize=(7.2, 5.2))
        image = ax.imshow(errors, origin="lower", aspect="auto", cmap="magma")
        ax.set_xticks(np.arange(scales.size), [f"{value:g}" for value in scales])
        ax.set_yticks(np.arange(noise_levels.size), [f"{value:.2f}" for value in noise_levels])
        ax.set(xlabel=tr("scale", language), ylabel=tr("noise", language))
        ax.set_title(title("noise_scale_map", language))
        colorbar = fig.colorbar(image, ax=ax)
        colorbar.set_label(tr("mae", language))
        for row in range(errors.shape[0]):
            for column in range(errors.shape[1]):
                ax.text(column, row, f"{errors[row, column]:.1f}", ha="center", va="center", color="white")
        save_figure(fig, "noise_scale_map", language)


if __name__ == "__main__":
    main()
