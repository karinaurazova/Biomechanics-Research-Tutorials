"""Decompose passive, active, and total nominal stress."""

import matplotlib.pyplot as plt
import numpy as np
from common import save_figure, title, tr
from biomechanics_tutorials.active_mechanics import active_tension, passive_uniaxial_nominal_stress


def main():
    stretch = np.linspace(0.82, 1.4, 400)
    passive = passive_uniaxial_nominal_stress(stretch)
    active = active_tension(0.75, stretch) / stretch
    total = passive + active
    labels = {"en": ["Passive", "Active", "Total"], "ru": ["Пассивное", "Активное", "Полное"]}
    for language in ("en", "ru"):
        fig, ax = plt.subplots(figsize=(8, 5))
        for y, label in zip([passive, active, total], labels[language]):
            ax.plot(stretch, y, lw=2.4, label=label)
        ax.axhline(0, color="0.6", lw=0.8)
        ax.set(
            xlabel=tr("stretch", language),
            ylabel=tr("stress", language),
            title=title("stress_decomposition", language),
        )
        ax.legend()
        ax.grid(alpha=0.25)
        save_figure(fig, "stress_decomposition", language)


if __name__ == "__main__":
    main()
