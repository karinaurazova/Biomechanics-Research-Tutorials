"""Compare volumetric penalty functions."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

from common import curve_colors, save_figure, tr
from biomechanics_tutorials.hyperelasticity import volumetric_energy


def main() -> None:
    j = np.linspace(0.72, 1.30, 240)
    kinds = ["quadratic", "logarithmic", "simo_taylor"]
    colors = curve_colors(3)
    for language in ("en", "ru"):
        fig, axis = plt.subplots(figsize=(9.5, 6.0))
        for kind, color in zip(kinds, colors):
            axis.plot(
                j,
                volumetric_energy(j, bulk_modulus=10.0, kind=kind),
                linewidth=2.3,
                color=color,
                label=tr(kind, language),
            )
        axis.axvline(1.0, color="#94A3B8", linewidth=0.9)
        axis.set_xlabel(tr("volume_ratio", language))
        axis.set_ylabel(tr("bulk_energy", language))
        axis.set_title(tr("volume_title", language))
        axis.legend()
        fig.tight_layout()
        save_figure(fig, "volumetric_penalties", language)


if __name__ == "__main__":
    main()
