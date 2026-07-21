"""Demonstrate the one-orientation limitation on crossing fibers."""

import matplotlib.pyplot as plt
import numpy as np

from biomechanics_tutorials.structure_tensor import (
    StructureTensorParameters,
    orientation_histogram,
    structure_tensor_orientation,
    synthetic_crossing_fibers,
)
from common import add_orientation_colorbar, orientation_image, save_figure, title, tr


def main() -> None:
    image, directions = synthetic_crossing_fibers(noise_std=0.02, seed=13)
    result = structure_tensor_orientation(image, StructureTensorParameters(1.0, 4.0))
    centers, density = orientation_histogram(
        result["orientation"].ravel(), result["coherence"].ravel(), bins=45
    )
    for language in ("en", "ru"):
        fig, axes = plt.subplots(1, 4, figsize=(14.5, 4.0))
        axes[0].imshow(image, cmap="gray", vmin=0, vmax=1)
        axes[0].set_title(tr("image", language))
        orientation_plot = orientation_image(axes[1], result["orientation"], tr("estimate", language))
        axes[2].imshow(result["coherence"], cmap="viridis", vmin=0, vmax=1)
        axes[2].set_title(tr("coherence", language))
        axes[3].plot(centers, density, lw=2)
        for direction in directions:
            axes[3].axvline(np.rad2deg(direction), color="black", ls="--")
        axes[3].set(xlabel=tr("angle", language), ylabel=tr("density", language))
        for ax in axes[:3]:
            ax.set_xticks([])
            ax.set_yticks([])
        add_orientation_colorbar(fig, orientation_plot, axes[1], language)
        fig.suptitle(title("crossing_failure", language), fontsize=15)
        save_figure(fig, "crossing_failure", language)


if __name__ == "__main__":
    main()
