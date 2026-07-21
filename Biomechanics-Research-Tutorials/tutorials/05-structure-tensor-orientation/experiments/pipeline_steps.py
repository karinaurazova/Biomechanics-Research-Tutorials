"""Visualize the complete structure-tensor pipeline."""

import matplotlib.pyplot as plt
import numpy as np

from biomechanics_tutorials.structure_tensor import (
    StructureTensorParameters,
    confidence_mask,
    structure_tensor_orientation,
    synthetic_curved_fibers,
)
from common import add_orientation_colorbar, orientation_image, save_figure, title, tr


def main() -> None:
    image, truth = synthetic_curved_fibers(shape=(180, 240), noise_std=0.045, seed=10)
    result = structure_tensor_orientation(image, StructureTensorParameters(1.0, 3.0))
    mask = confidence_mask(result, 0.35, 0.12, border=8)
    gradient = np.hypot(result["gradient_x"], result["gradient_y"])
    for language in ("en", "ru"):
        fig, axes = plt.subplots(2, 3, figsize=(12.5, 7.5))
        axes[0, 0].imshow(image, cmap="gray", vmin=0, vmax=1)
        axes[0, 0].set_title(tr("image", language))
        axes[0, 1].imshow(gradient, cmap="magma")
        axes[0, 1].set_title(tr("gradient", language))
        axes[0, 2].imshow(result["coherence"], cmap="viridis", vmin=0, vmax=1)
        axes[0, 2].set_title(tr("coherence", language))
        orientation_image(axes[1, 0], truth, tr("truth", language))
        orientation_plot = orientation_image(
            axes[1, 1], result["orientation"], tr("estimate", language), mask=mask
        )
        axes[1, 2].imshow(mask, cmap="gray", vmin=0, vmax=1)
        axes[1, 2].set_title(tr("mask", language))
        for ax in axes.flat:
            ax.set_xticks([])
            ax.set_yticks([])
        add_orientation_colorbar(fig, orientation_plot, axes[1, :2], language)
        fig.suptitle(title("pipeline_steps", language), fontsize=16)
        save_figure(fig, "pipeline_steps", language)


if __name__ == "__main__":
    main()
