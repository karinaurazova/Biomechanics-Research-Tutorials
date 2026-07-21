"""Generate a gallery of synthetic orientation fields."""

import matplotlib.pyplot as plt

from biomechanics_tutorials.structure_tensor import (
    synthetic_crossing_fibers,
    synthetic_curved_fibers,
    synthetic_fan_fibers,
    synthetic_parallel_fibers,
    synthetic_piecewise_fibers,
)
from common import save_figure, title


def main() -> None:
    cases = [
        ("Parallel", "Параллельные", synthetic_parallel_fibers(angle_degrees=28, noise_std=0.02)[0]),
        ("Curved", "Криволинейные", synthetic_curved_fibers(shape=(192, 192))[0]),
        ("Fan", "Веер", synthetic_fan_fibers()[0]),
        ("Two domains", "Две области", synthetic_piecewise_fibers(shape=(192, 192))[0]),
        ("Crossing", "Пересечение", synthetic_crossing_fibers()[0]),
    ]
    for language in ("en", "ru"):
        fig, axes = plt.subplots(1, 5, figsize=(15.5, 3.5))
        for ax, (name_en, name_ru, image) in zip(axes, cases):
            ax.imshow(image, cmap="gray", vmin=0, vmax=1)
            ax.set_title(name_en if language == "en" else name_ru)
            ax.set_xticks([])
            ax.set_yticks([])
        fig.suptitle(title("synthetic_gallery", language), fontsize=16)
        save_figure(fig, "synthetic_gallery", language)


if __name__ == "__main__":
    main()
