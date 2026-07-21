"""Simulate adaptation to a changing target direction."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from biomechanics_tutorials.fiber_reorientation import (
    ReorientationParameters,
    simulate_reorientation,
)
from biomechanics_tutorials.localization import (
    SUPPORTED_LANGUAGES,
    localized_path,
    tr,
)
from biomechanics_tutorials.plotting import PALETTE, apply_tutorial_style


def target_direction(time: float) -> float:
    """Return the prescribed piecewise-constant target direction."""
    if time < 7:
        return np.deg2rad(-20)
    if time < 14:
        return np.deg2rad(45)
    return np.deg2rad(5)


def main() -> None:
    """Save changing-target plots in English and Russian."""
    apply_tutorial_style()
    parameters = ReorientationParameters(rate=0.45, duration=22, time_step=0.01)
    time, orientation, target = simulate_reorientation(
        np.deg2rad(-50), target_direction, parameters
    )
    base_output = Path(__file__).resolve().parents[1] / "figures" / "changing_target.png"
    for language in SUPPORTED_LANGUAGES:
        output = localized_path(base_output, language)
        output.parent.mkdir(parents=True, exist_ok=True)
        fig, axis = plt.subplots(figsize=(8, 5))
        axis.plot(
            time,
            np.rad2deg(target),
            color=PALETTE["ink"],
            linestyle="--",
            label=tr("target_direction", language),
        )
        axis.plot(
            time,
            np.rad2deg(orientation),
            color=PALETTE["blue"],
            label=tr("fiber_orientation", language),
        )
        axis.set(
            xlabel=tr("time", language),
            ylabel=tr("angle_degrees", language),
            title=tr("changing_cue_title", language),
        )
        axis.legend()
        fig.tight_layout()
        fig.savefig(output, dpi=180)
        plt.close(fig)
        print(f"Saved {output}")


if __name__ == "__main__":
    main()
