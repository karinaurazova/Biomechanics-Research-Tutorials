"""Assess uneven illumination and a simple background normalization."""

import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import gaussian_filter

from biomechanics_tutorials.structure_tensor import (
    StructureTensorParameters,
    confidence_mask,
    orientation_error_metrics,
    structure_tensor_orientation,
    synthetic_parallel_fibers,
)
from common import add_orientation_colorbar, orientation_image, save_figure, title


def normalize_background(image: np.ndarray, sigma: float = 30.0) -> np.ndarray:
    background = gaussian_filter(image, sigma, mode="reflect")
    normalized = image / np.maximum(background, 0.05)
    normalized -= normalized.min()
    normalized /= max(normalized.max(), 1e-12)
    return normalized


def main() -> None:
    image, truth = synthetic_parallel_fibers(
        angle_degrees=-22.0,
        noise_std=0.04,
        seed=14,
        illumination_gradient=0.75,
    )
    normalized = normalize_background(image)
    raw_result = structure_tensor_orientation(image, StructureTensorParameters(1.0, 3.0))
    norm_result = structure_tensor_orientation(normalized, StructureTensorParameters(1.0, 3.0))
    raw_mask = confidence_mask(raw_result, 0.35, 0.15, border=10)
    norm_mask = confidence_mask(norm_result, 0.35, 0.15, border=10)
    raw_error = orientation_error_metrics(raw_result["orientation"], truth, raw_mask)["mae_deg"]
    norm_error = orientation_error_metrics(norm_result["orientation"], truth, norm_mask)["mae_deg"]
    for language in ("en", "ru"):
        fig, axes = plt.subplots(1, 4, figsize=(14.5, 4.0))
        axes[0].imshow(image, cmap="gray", vmin=0, vmax=1)
        axes[0].set_title("Raw" if language == "en" else "Исходное")
        axes[1].imshow(normalized, cmap="gray", vmin=0, vmax=1)
        axes[1].set_title("Normalized" if language == "en" else "Нормированное")
        orientation_image(
            axes[2], raw_result["orientation"], f"Raw MAE={raw_error:.2f}°" if language == "en" else f"Исходная MAE={raw_error:.2f}°", raw_mask
        )
        orientation_plot = orientation_image(
            axes[3], norm_result["orientation"], f"Normalized MAE={norm_error:.2f}°" if language == "en" else f"После нормировки MAE={norm_error:.2f}°", norm_mask
        )
        for ax in axes:
            ax.set_xticks([])
            ax.set_yticks([])
        add_orientation_colorbar(fig, orientation_plot, axes[2:], language)
        fig.suptitle(title("illumination_robustness", language), fontsize=16)
        save_figure(fig, "illumination_robustness", language)


if __name__ == "__main__":
    main()
