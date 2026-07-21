"""Compare concentrated and dispersed fiber families."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

from common import curve_colors, save_figure, tr
from biomechanics_tutorials.hyperelasticity import path_response


def main() -> None:
    stretches = np.linspace(1.0, 1.38, 180)
    kappas = [0.0, 0.08, 0.18, 1.0 / 3.0]
    colors = curve_colors(len(kappas) + 1)
    for language in ("en", "ru"):
        fig, axis = plt.subplots(figsize=(9.8, 6.2))
        hgo = path_response("hgo", stretches)
        axis.plot(stretches, hgo, linewidth=2.7, color=colors[0], label="HGO")
        for kappa, color in zip(kappas, colors[1:]):
            response = path_response("goh", stretches, parameters={"kappa": kappa})
            axis.plot(
                stretches,
                response,
                linewidth=2.1,
                color=color,
                label=f"GOH κ={kappa:.3f}",
            )
        axis.set_xlabel(tr("stretch", language))
        axis.set_ylabel(tr("response", language))
        axis.set_title(tr("dispersion_title", language))
        axis.legend()
        fig.tight_layout()
        save_figure(fig, "hgo_goh_dispersion", language)


if __name__ == "__main__":
    main()
