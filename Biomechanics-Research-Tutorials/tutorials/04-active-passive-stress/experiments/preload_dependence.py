"""Show preload-dependent active and total peak stress."""

import matplotlib.pyplot as plt
import numpy as np
from common import save_figure, title, tr
from biomechanics_tutorials.active_mechanics import active_tension, passive_uniaxial_nominal_stress


def main():
    stretch = np.linspace(0.78, 1.42, 350)
    passive = passive_uniaxial_nominal_stress(stretch)
    active = active_tension(1.0, stretch) / stretch
    total = passive + active
    for language in ("en", "ru"):
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(stretch, passive, lw=2.2, label="Passive" if language == "en" else "Пассивное")
        ax.plot(
            stretch, active, lw=2.2, label="Peak active" if language == "en" else "Пиковое активное"
        )
        ax.plot(
            stretch, total, lw=2.7, label="Peak total" if language == "en" else "Пиковое полное"
        )
        ax.set(
            xlabel=tr("stretch", language),
            ylabel=tr("stress", language),
            title=title("preload_dependence", language),
        )
        ax.legend()
        ax.grid(alpha=0.25)
        save_figure(fig, "preload_dependence", language)


if __name__ == "__main__":
    main()
