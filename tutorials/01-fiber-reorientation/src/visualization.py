"""Plotting helpers for Tutorial 01."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from biomechanics_tutorials.fiber_reorientation import alignment_index, angular_difference
from biomechanics_tutorials.localization import tr
from biomechanics_tutorials.plotting import PALETTE, apply_tutorial_style


def save_baseline_figure(
    time: np.ndarray,
    orientation: np.ndarray,
    target: np.ndarray,
    output: Path,
    *,
    language: str = "en",
) -> None:
    """Save the localized baseline orientation, error, and alignment figure."""
    apply_tutorial_style()
    output.parent.mkdir(parents=True, exist_ok=True)
    error = np.rad2deg(angular_difference(target, orientation))
    alignment = alignment_index(orientation, target)
    fig, axes = plt.subplots(3, 1, figsize=(8, 9), sharex=True)
    axes[0].plot(
        time,
        np.rad2deg(orientation),
        color=PALETTE["blue"],
        label=tr("fiber_orientation", language),
    )
    axes[0].plot(
        time,
        np.rad2deg(target),
        color=PALETTE["ink"],
        linestyle="--",
        label=tr("target", language),
    )
    axes[0].set_ylabel(tr("angle_degrees", language))
    axes[0].legend()
    axes[1].plot(time, error, color=PALETTE["cyan"])
    axes[1].axhline(0, color=PALETTE["ink"], linewidth=1)
    axes[1].set_ylabel(tr("axial_error_degrees", language))
    axes[2].plot(time, alignment, color=PALETTE["blue"])
    axes[2].set_ylabel(tr("alignment_index", language))
    axes[2].set_xlabel(tr("time", language))
    axes[2].set_ylim(-0.02, 1.02)
    fig.suptitle(tr("t1_baseline_title", language))
    fig.tight_layout()
    fig.savefig(output, dpi=180)
    plt.close(fig)
