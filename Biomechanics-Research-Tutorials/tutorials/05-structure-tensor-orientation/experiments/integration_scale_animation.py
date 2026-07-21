"""Animate the effect of integration scale on a noisy piecewise field."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation, PillowWriter

from biomechanics_tutorials.plotting import apply_tutorial_style
from biomechanics_tutorials.structure_tensor import (
    StructureTensorParameters,
    structure_tensor_orientation,
    synthetic_piecewise_fibers,
)
from common import ANIMATION_DIRECTORY


def render(language: str) -> Path:
    apply_tutorial_style()
    image, _ = synthetic_piecewise_fibers(shape=(160, 220), noise_std=0.08, seed=24)
    scales = np.linspace(0.7, 8.0, 22)
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.7))
    axes[0].imshow(image, cmap="gray", vmin=0, vmax=1)
    axes[0].set_title("Synthetic image" if language == "en" else "Синтетическое изображение")
    orientation_artist = axes[1].imshow(np.zeros_like(image), cmap="twilight", vmin=-90, vmax=90)
    coherence_artist = axes[2].imshow(np.zeros_like(image), cmap="viridis", vmin=0, vmax=1)
    axes[2].set_title("Coherence" if language == "en" else "Когерентность")
    for ax in axes:
        ax.set_xticks([])
        ax.set_yticks([])

    def update(frame):
        scale = float(scales[frame])
        result = structure_tensor_orientation(image, StructureTensorParameters(1.0, scale))
        orientation_artist.set_data(np.rad2deg(result["orientation"]))
        coherence_artist.set_data(result["coherence"])
        axes[1].set_title(
            (f"Orientation, σᵢ={scale:.1f}" if language == "en" else f"Ориентация, σᵢ={scale:.1f}")
        )
        return orientation_artist, coherence_artist

    animation = FuncAnimation(fig, update, frames=len(scales), interval=170, blit=False)
    ANIMATION_DIRECTORY.mkdir(parents=True, exist_ok=True)
    suffix = "" if language == "en" else "_ru"
    path = ANIMATION_DIRECTORY / f"integration_scale{suffix}.gif"
    animation.save(path, writer=PillowWriter(fps=6))
    plt.close(fig)
    return path


def main() -> None:
    render("en")
    render("ru")


if __name__ == "__main__":
    main()
