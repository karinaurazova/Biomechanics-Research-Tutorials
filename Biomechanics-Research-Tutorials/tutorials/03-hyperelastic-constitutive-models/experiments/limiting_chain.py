"""Study limiting-chain parameters in Gent and Arruda-Boyce models."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

from common import curve_colors, finite_values, save_figure, tr
from biomechanics_tutorials.hyperelasticity import path_response


def main() -> None:
    stretches = np.linspace(1.0, 2.15, 300)
    colors = curve_colors(4)
    for language in ("en", "ru"):
        fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))
        for jm, color in zip([8.0, 18.0, 40.0], colors):
            response = path_response("gent", stretches, parameters={"jm": jm})
            x, y = finite_values(stretches, response)
            axes[0].plot(x, y, linewidth=2.2, color=color, label=f"Jm={jm:g}")
        axes[0].set_title("Gent" if language == "en" else "Гент")
        axes[0].set_xlabel(tr("stretch", language))
        axes[0].set_ylabel(tr("response", language))
        axes[0].legend()

        for n, color in zip([3.0, 8.0, 20.0], colors):
            response = path_response(
                "arruda_boyce", stretches, parameters={"chain_parameter": n}
            )
            x, y = finite_values(stretches, response)
            axes[1].plot(x, y, linewidth=2.2, color=color, label=f"N={n:g}")
        axes[1].set_title("Arruda-Boyce" if language == "en" else "Арруда–Бойс")
        axes[1].set_xlabel(tr("stretch", language))
        axes[1].set_ylabel(tr("response", language))
        axes[1].legend()
        fig.suptitle(tr("limiting_title", language), fontsize=16)
        fig.tight_layout(rect=(0, 0, 1, 0.95))
        save_figure(fig, "limiting_chain", language)


if __name__ == "__main__":
    main()
