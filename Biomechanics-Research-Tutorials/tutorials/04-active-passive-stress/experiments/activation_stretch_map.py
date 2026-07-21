"""Map total stress over activation and stretch."""

import matplotlib.pyplot as plt
import numpy as np
from common import save_figure, title, tr
from biomechanics_tutorials.active_mechanics import (
    active_tension,
    active_stress_uniaxial_nominal_response,
)


def main():
    stretches = np.linspace(0.78, 1.42, 240)
    activation = np.linspace(0, 1, 180)
    L, A = np.meshgrid(stretches, activation)
    tension = active_tension(A, L)
    total = active_stress_uniaxial_nominal_response(L, tension)
    for language in ("en", "ru"):
        fig, ax = plt.subplots(figsize=(8.4, 5.4))
        image = ax.pcolormesh(stretches, activation, total, shading="auto")
        fig.colorbar(image, ax=ax, label=tr("stress", language))
        ax.set(
            xlabel=tr("stretch", language),
            ylabel=tr("activation", language),
            title=title("activation_stretch_map", language),
        )
        save_figure(fig, "activation_stretch_map", language)


if __name__ == "__main__":
    main()
