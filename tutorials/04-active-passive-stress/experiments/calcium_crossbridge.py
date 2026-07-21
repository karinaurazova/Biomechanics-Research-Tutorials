"""Simulate calcium and cross-bridge dynamics."""

import matplotlib.pyplot as plt
import numpy as np
from common import save_figure, title, tr
from biomechanics_tutorials.active_mechanics import calcium_gamma_transient, simulate_crossbridge


def main():
    time = np.linspace(0, 0.8, 1800)
    target = calcium_gamma_transient(time)
    r = simulate_crossbridge(time, target)
    for language in ("en", "ru"):
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(
            time,
            target,
            lw=1.8,
            ls="--",
            label="Calcium target" if language == "en" else "Целевой кальциевый сигнал",
        )
        ax.plot(
            time,
            r["calcium"],
            lw=2.3,
            label="Filtered calcium" if language == "en" else "Фильтрованный кальций",
        )
        ax.plot(
            time,
            r["bound_fraction"],
            lw=2.3,
            label="Bound cross-bridges" if language == "en" else "Связанные кросс-мостики",
        )
        ax.set(
            xlabel=tr("time", language),
            ylabel="Normalized state" if language == "en" else "Нормированное состояние",
            title=title("calcium_crossbridge", language),
        )
        ax.legend()
        ax.grid(alpha=0.25)
        save_figure(fig, "calcium_crossbridge", language)


if __name__ == "__main__":
    main()
