"""Quantify orientation error as a function of distance to the image boundary."""

import matplotlib.pyplot as plt
import numpy as np

from biomechanics_tutorials.structure_tensor import (
    StructureTensorParameters,
    axial_angle_difference,
    structure_tensor_orientation,
    synthetic_curved_fibers,
)
from common import save_figure, title, tr


def main() -> None:
    image, truth = synthetic_curved_fibers(shape=(180, 240), noise_std=0.045, seed=22)
    result = structure_tensor_orientation(image, StructureTensorParameters(1.2, 5.0))
    error = np.abs(np.rad2deg(axial_angle_difference(result["orientation"], truth)))
    rows, columns = image.shape
    y, x = np.mgrid[0:rows, 0:columns]
    distance = np.minimum.reduce([x, columns - 1 - x, y, rows - 1 - y])
    bins = np.arange(0, 31)
    mean_error = np.array([np.mean(error[distance == value]) for value in bins])
    for language in ("en", "ru"):
        fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.2))
        error_plot = axes[0].imshow(error, cmap="inferno", vmin=0, vmax=15)
        axes[0].set_title(tr("error", language))
        axes[0].set_xticks([])
        axes[0].set_yticks([])
        fig.colorbar(error_plot, ax=axes[0], shrink=0.8)
        axes[1].plot(bins, mean_error, "o-", lw=2)
        axes[1].axvspan(0, 10, alpha=0.15)
        axes[1].set(xlabel=tr("distance", language), ylabel=tr("mae", language))
        fig.suptitle(title("boundary_artifacts", language), fontsize=16)
        save_figure(fig, "boundary_artifacts", language)


if __name__ == "__main__":
    main()
