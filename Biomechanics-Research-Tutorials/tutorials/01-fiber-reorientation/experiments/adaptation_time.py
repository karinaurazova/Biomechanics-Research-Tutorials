"""Evaluate the relationship between remodeling rate and adaptation time."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from biomechanics_tutorials.fiber_reorientation import adaptation_time
from biomechanics_tutorials.localization import (
    SUPPORTED_LANGUAGES,
    localized_path,
    tr,
)
from biomechanics_tutorials.plotting import PALETTE, apply_tutorial_style


def main() -> None:
    """Save the adaptation-time plot in English and Russian."""
    apply_tutorial_style()
    rates = np.linspace(0.08, 0.8, 80)
    initial = np.deg2rad(-50)
    target = np.deg2rad(30)
    tolerance = np.deg2rad(5)
    times = np.array([adaptation_time(initial, target, rate, tolerance) for rate in rates])
    base_output = Path(__file__).resolve().parents[1] / "figures" / "adaptation_time.png"
    for language in SUPPORTED_LANGUAGES:
        output = localized_path(base_output, language)
        output.parent.mkdir(parents=True, exist_ok=True)
        fig, axis = plt.subplots(figsize=(8, 5))
        axis.plot(rates, times, color=PALETTE["blue"])
        axis.set(
            xlabel=tr("remodeling_rate", language),
            ylabel=tr("time_to_5deg", language),
            title=tr("adaptation_time_title", language),
        )
        fig.tight_layout()
        fig.savefig(output, dpi=180)
        plt.close(fig)
        print(f"Saved {output}")


if __name__ == "__main__":
    main()
