"""Show scale-dependent blurring at an orientation boundary."""

import matplotlib.pyplot as plt
import numpy as np

from biomechanics_tutorials.structure_tensor import (
    StructureTensorParameters,
    structure_tensor_orientation,
    synthetic_piecewise_fibers,
)
from common import save_figure, title, tr


def main() -> None:
    image, truth = synthetic_piecewise_fibers(noise_std=0.025, seed=8)
    scales = [1.0, 3.0, 7.0]
    profiles = []
    row_slice = slice(image.shape[0] // 2 - 20, image.shape[0] // 2 + 20)
    for scale in scales:
        result = structure_tensor_orientation(image, StructureTensorParameters(1.0, scale))
        doubled = np.exp(2j * result["orientation"][row_slice])
        profile = 0.5 * np.angle(np.mean(doubled, axis=0))
        profiles.append(np.rad2deg(profile))
    truth_profile = np.rad2deg(truth[image.shape[0] // 2])
    x = np.arange(image.shape[1]) - image.shape[1] / 2
    for language in ("en", "ru"):
        fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.5))
        axes[0].imshow(image, cmap="gray", vmin=0, vmax=1)
        axes[0].axvline(image.shape[1] / 2, color="white", ls="--")
        axes[0].set_title(tr("image", language))
        axes[0].set_xticks([])
        axes[0].set_yticks([])
        axes[1].plot(x, truth_profile, "k--", lw=2, label=tr("truth", language))
        for scale, profile in zip(scales, profiles):
            axes[1].plot(x, profile, lw=2, label=f"σᵢ={scale:g}")
        axes[1].set(xlabel="x, pixels" if language == "en" else "x, пиксели", ylabel=tr("angle", language))
        axes[1].legend()
        fig.suptitle(title("piecewise_domains", language), fontsize=16)
        save_figure(fig, "piecewise_domains", language)


if __name__ == "__main__":
    main()
