"""Evaluate a curved orientation field."""

import matplotlib.pyplot as plt
import numpy as np

from biomechanics_tutorials.structure_tensor import (
    StructureTensorParameters,
    axial_angle_difference,
    confidence_mask,
    orientation_error_metrics,
    structure_tensor_orientation,
    synthetic_curved_fibers,
)
from common import add_orientation_colorbar, orientation_image, save_figure, title, tr


def main() -> None:
    image, truth = synthetic_curved_fibers(noise_std=0.04, seed=9)
    result = structure_tensor_orientation(image, StructureTensorParameters(1.0, 3.2))
    mask = confidence_mask(result, 0.35, 0.10, border=10)
    error = np.abs(np.rad2deg(axial_angle_difference(result["orientation"], truth)))
    metrics = orientation_error_metrics(result["orientation"], truth, mask)
    for language in ("en", "ru"):
        fig, axes = plt.subplots(1, 4, figsize=(15, 4.2))
        axes[0].imshow(image, cmap="gray", vmin=0, vmax=1)
        axes[0].set_title(tr("image", language))
        orientation_image(axes[1], truth, tr("truth", language))
        orientation_plot = orientation_image(
            axes[2], result["orientation"], tr("estimate", language), mask=mask
        )
        error_plot = axes[3].imshow(np.where(mask, error, np.nan), cmap="inferno", vmin=0, vmax=12)
        axes[3].set_title(f"{tr('error', language)}\nMAE={metrics['mae_deg']:.2f}°")
        for ax in axes:
            ax.set_xticks([])
            ax.set_yticks([])
        add_orientation_colorbar(fig, orientation_plot, axes[1:3], language)
        fig.colorbar(error_plot, ax=axes[3], shrink=0.8)
        fig.suptitle(title("curved_field", language), fontsize=16)
        save_figure(fig, "curved_field", language)


if __name__ == "__main__":
    main()
