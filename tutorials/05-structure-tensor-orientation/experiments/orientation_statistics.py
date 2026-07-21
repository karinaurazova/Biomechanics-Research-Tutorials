"""Convert local orientation estimates into axial summary statistics."""

import matplotlib.pyplot as plt
import numpy as np

from biomechanics_tutorials.structure_tensor import (
    StructureTensorParameters,
    confidence_mask,
    orientation_histogram,
    structure_tensor_orientation,
    synthetic_parallel_fibers,
    weighted_axial_mean,
)
from common import save_figure, title, tr


def main() -> None:
    image, _ = synthetic_parallel_fibers(angle_degrees=24.0, noise_std=0.11, seed=20)
    result = structure_tensor_orientation(image, StructureTensorParameters(1.0, 3.0))
    mask = confidence_mask(result, 0.45, 0.15, border=10)
    centers_all, density_all = orientation_histogram(result["orientation"].ravel(), bins=45)
    centers_mask, density_mask = orientation_histogram(
        result["orientation"][mask], result["coherence"][mask], bins=45
    )
    mean_all, order_all = weighted_axial_mean(result["orientation"].ravel())
    mean_mask, order_mask = weighted_axial_mean(
        result["orientation"][mask], result["coherence"][mask]
    )
    for language in ("en", "ru"):
        fig, axes = plt.subplots(1, 3, figsize=(13, 4.1))
        axes[0].imshow(image, cmap="gray", vmin=0, vmax=1)
        axes[0].set_title(tr("image", language))
        axes[1].imshow(mask, cmap="gray", vmin=0, vmax=1)
        axes[1].set_title(tr("mask", language))
        axes[2].plot(centers_all, density_all, lw=2, label="all" if language == "en" else "все")
        axes[2].plot(
            centers_mask,
            density_mask,
            lw=2,
            label="confidence weighted" if language == "en" else "с весом доверия",
        )
        axes[2].axvline(np.rad2deg(mean_all), ls="--", color="gray")
        axes[2].axvline(np.rad2deg(mean_mask), ls="--", color="black")
        axes[2].set(
            xlabel=tr("angle", language),
            ylabel=tr("density", language),
            title=f"R={order_all:.2f} → {order_mask:.2f}",
        )
        axes[2].legend()
        for ax in axes[:2]:
            ax.set_xticks([])
            ax.set_yticks([])
        fig.suptitle(title("orientation_statistics", language), fontsize=16)
        save_figure(fig, "orientation_statistics", language)


if __name__ == "__main__":
    main()
