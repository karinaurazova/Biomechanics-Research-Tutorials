"""Compare explicit Euler integration with the analytical solution."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from biomechanics_tutorials.fiber_reorientation import (
    ReorientationParameters,
    analytical_constant_target,
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
    """Save analytical-verification plots in both repository languages."""
    apply_tutorial_style()
    initial = np.deg2rad(-50)
    target_angle = np.deg2rad(30)
    parameters = ReorientationParameters(rate=0.35, duration=20, time_step=0.05)
    time, numerical, target = simulate_reorientation(initial, target_angle, parameters)
    analytical = analytical_constant_target(time, initial, target_angle, parameters.rate)
    discrepancy = np.abs(np.rad2deg(angular_difference(analytical, numerical)))
    base_output = (
        Path(__file__).resolve().parents[1] / "figures" / "analytical_verification.png"
    )
    for language in SUPPORTED_LANGUAGES:
        output = localized_path(base_output, language)
        output.parent.mkdir(parents=True, exist_ok=True)
        fig, axes = plt.subplots(2, 1, figsize=(8, 7), sharex=True)
        axes[0].plot(
            time,
            np.rad2deg(analytical),
            color=PALETTE["ink"],
            linestyle="--",
            label=tr("analytical", language),
        )
        axes[0].plot(
            time,
            np.rad2deg(numerical),
            color=PALETTE["blue"],
            label=tr("explicit_euler", language),
        )
        axes[0].plot(
            time,
            np.rad2deg(target),
            color=PALETTE["cyan"],
            linestyle=":",
            label=tr("target", language),
        )
        axes[0].set(
            ylabel=tr("orientation_degrees", language),
            title=tr("verification_title", language),
        )
        axes[0].legend()
        axes[1].plot(time, discrepancy, color=PALETTE["blue"])
        axes[1].set(
            xlabel=tr("time", language),
            ylabel=tr("numerical_discrepancy_degrees", language),
        )
        fig.tight_layout()
        fig.savefig(output, dpi=180)
        plt.close(fig)
        print(f"Saved {output}; maximum discrepancy = {discrepancy.max():.4f} degrees")


if __name__ == "__main__":
    main()
