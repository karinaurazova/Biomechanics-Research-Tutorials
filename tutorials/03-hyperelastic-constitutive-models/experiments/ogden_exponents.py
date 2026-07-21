"""Show the effect of Ogden exponents."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

from common import curve_colors, save_figure, tr
from biomechanics_tutorials.hyperelasticity import path_response


def main() -> None:
    stretches = np.linspace(0.72, 1.55, 260)
    exponents = [1.0, 2.0, 4.0, 8.0]
    colors = curve_colors(len(exponents))
    for language in ("en", "ru"):
        fig, axis = plt.subplots(figsize=(9.5, 6.0))
        for alpha, color in zip(exponents, colors):
            response = path_response(
                "ogden_1", stretches, parameters={"alpha1": alpha, "mu1": 1.0}
            )
            axis.plot(stretches, response, linewidth=2.3, color=color, label=f"α={alpha:g}")
        axis.axhline(0.0, color="#94A3B8", linewidth=0.8)
        axis.axvline(1.0, color="#94A3B8", linewidth=0.8)
        axis.set_xlabel(tr("stretch", language))
        axis.set_ylabel(tr("response", language))
        axis.set_title(tr("ogden_title", language))
        axis.legend()
        fig.tight_layout()
        save_figure(fig, "ogden_exponents", language)


if __name__ == "__main__":
    main()
