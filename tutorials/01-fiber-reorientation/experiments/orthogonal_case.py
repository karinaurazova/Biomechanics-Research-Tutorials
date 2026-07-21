"""Demonstrate non-uniqueness at an exactly 90-degree axial mismatch."""

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


def axial_unwrap(values: np.ndarray) -> np.ndarray:
    """Unwrap an axial angle sequence for trajectory visualization."""
    return 0.5 * np.unwrap(2.0 * values)


def main() -> None:
    """Save the orthogonal-branch diagnostic in English and Russian."""
    apply_tutorial_style()
    target = np.deg2rad(30)
    epsilon = 0.5
    parameters = ReorientationParameters(rate=0.35, duration=16, time_step=0.01)
    cases = [(-60 + epsilon, PALETTE["blue"]), (-60 - epsilon, PALETTE["cyan"])]
    trajectories = []
    for initial_degrees, color in cases:
        time, orientation, _ = simulate_reorientation(
            np.deg2rad(initial_degrees), target, parameters
        )
        trajectories.append((initial_degrees, color, time, axial_unwrap(orientation)))

    base_output = Path(__file__).resolve().parents[1] / "figures" / "orthogonal_case.png"
    for language in SUPPORTED_LANGUAGES:
        output = localized_path(base_output, language)
        output.parent.mkdir(parents=True, exist_ok=True)
        fig, axis = plt.subplots(figsize=(8, 5))
        for initial_degrees, color, time, orientation in trajectories:
            axis.plot(
                time,
                np.rad2deg(orientation),
                color=color,
                label=tr("initial_degrees", language, value=initial_degrees),
            )
        axis.axhline(
            30,
            color=PALETTE["ink"],
            linestyle="--",
            label=tr("target_branch", language),
        )
        axis.axhline(
            -150,
            color=PALETTE["slate"],
            linestyle=":",
            label=tr("equivalent_branch", language),
        )
        axis.set(
            xlabel=tr("time", language),
            ylabel=tr("unwrapped_orientation_degrees", language),
            title=tr("orthogonal_title", language),
        )
        axis.legend()
        fig.tight_layout()
        fig.savefig(output, dpi=180)
        plt.close(fig)
        print(f"Saved {output}")


if __name__ == "__main__":
    main()
