"""Explore optional transverse active-stress fraction."""

import matplotlib.pyplot as plt
import numpy as np
from common import save_figure, title, tr
from biomechanics_tutorials.active_mechanics import active_stress_shear_response


def main():
    gamma = np.linspace(-0.6, 0.6, 350)
    fractions = [0.0, 0.1, 0.25, 0.5]
    for language in ("en", "ru"):
        fig, ax = plt.subplots(figsize=(8, 5))
        for fraction in fractions:
            ax.plot(
                gamma,
                active_stress_shear_response(gamma, 25.0, transverse_fraction=fraction),
                lw=2,
                label=f"η = {fraction:.2f}",
            )
        ax.set(
            xlabel=tr("shear", language),
            ylabel=tr("response", language),
            title=title("transverse_activation", language),
        )
        ax.legend()
        ax.grid(alpha=0.25)
        save_figure(fig, "transverse_activation", language)


if __name__ == "__main__":
    main()
