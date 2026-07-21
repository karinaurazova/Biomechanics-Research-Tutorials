"""Generate isometric twitches at several preloads."""

import matplotlib.pyplot as plt
import numpy as np
from common import save_figure, title, tr
from biomechanics_tutorials.active_mechanics import (
    activation_biexponential,
    simulate_isometric_twitch,
)


def main():
    time = np.linspace(0, 0.8, 900)
    activation = activation_biexponential(time)
    stretches = [0.95, 1.05, 1.15, 1.25]
    for language in ("en", "ru"):
        fig, ax = plt.subplots(figsize=(8, 5))
        for lam in stretches:
            r = simulate_isometric_twitch(time, lam, activation)
            ax.plot(time, r["total"], lw=2, label=f"λ = {lam:.2f}")
        ax.set(
            xlabel=tr("time", language),
            ylabel=tr("stress", language),
            title=title("isometric_twitches", language),
        )
        ax.legend()
        ax.grid(alpha=0.25)
        save_figure(fig, "isometric_twitches", language)


if __name__ == "__main__":
    main()
