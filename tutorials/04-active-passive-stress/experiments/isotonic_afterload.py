"""Generate quasi-static isotonic shortening curves."""

import matplotlib.pyplot as plt
import numpy as np
from common import save_figure, title, tr
from biomechanics_tutorials.active_mechanics import (
    activation_biexponential,
    simulate_isotonic_shortening,
)


def main():
    time = np.linspace(0, 0.8, 500)
    activation = activation_biexponential(time)
    loads = [10.0, 22.0, 34.0]
    for language in ("en", "ru"):
        fig, axes = plt.subplots(2, 1, figsize=(8, 7), sharex=True)
        for load in loads:
            r = simulate_isotonic_shortening(time, activation, load)
            label = f"Afterload {load:g}" if language == "en" else f"Постнагрузка {load:g}"
            axes[0].plot(time, r["stretch"], lw=2.1, label=label)
            axes[1].plot(time, r["total"], lw=2.1, label=label)
        axes[0].set(ylabel=tr("stretch", language))
        axes[1].set(xlabel=tr("time", language), ylabel=tr("stress", language))
        axes[0].legend()
        [a.grid(alpha=0.25) for a in axes]
        fig.suptitle(title("isotonic_afterload", language))
        fig.tight_layout()
        save_figure(fig, "isotonic_afterload", language)


if __name__ == "__main__":
    main()
