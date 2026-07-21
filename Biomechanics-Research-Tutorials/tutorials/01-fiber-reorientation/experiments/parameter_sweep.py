"""Compare several remodeling-rate constants."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from biomechanics_tutorials.fiber_reorientation import (
    ReorientationParameters,
    angular_difference,
    simulate_reorientation,
)
from biomechanics_tutorials.localization import (
    SUPPORTED_LANGUAGES,
    localized_path,
    tr,
)
from biomechanics_tutorials.plotting import PALETTE, apply_tutorial_style


def main() -> None:
    """Save the rate comparison in both repository languages."""
    apply_tutorial_style()
    rates = [0.1, 0.2, 0.35, 0.7]
    colors = [PALETTE["slate"], PALETTE["cyan"], PALETTE["blue"], PALETTE["ink"]]
    trajectories: list[tuple[float, np.ndarray, np.ndarray]] = []
    for rate in rates:
        parameters = ReorientationParameters(rate=rate, duration=20, time_step=0.01)
        time, orientation, target = simulate_reorientation(
            np.deg2rad(-50), np.deg2rad(30), parameters
        )
        error = np.abs(np.rad2deg(angular_difference(target, orientation)))
        trajectories.append((rate, time, error))

    base_output = Path(__file__).resolve().parents[1] / "figures" / "parameter_sweep.png"
    for language in SUPPORTED_LANGUAGES:
        output = localized_path(base_output, language)
        output.parent.mkdir(parents=True, exist_ok=True)
        fig, axis = plt.subplots(figsize=(8, 5))
        for (rate, time, error), color in zip(trajectories, colors, strict=True):
            axis.plot(time, error, color=color, label=f"k = {rate}")
        axis.set(
            xlabel=tr("time", language),
            ylabel=tr("absolute_axial_error_degrees", language),
            title=tr("effect_rate_title", language),
        )
        axis.legend()
        fig.tight_layout()
        fig.savefig(output, dpi=180)
        plt.close(fig)
        print(f"Saved {output}")


if __name__ == "__main__":
    main()
