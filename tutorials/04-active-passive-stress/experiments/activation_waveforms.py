"""Compare synthetic activation functions."""

import matplotlib.pyplot as plt
import numpy as np
from common import save_figure, title, tr
from biomechanics_tutorials.active_mechanics import (
    activation_biexponential,
    activation_half_cosine,
    calcium_gamma_transient,
)


def main():
    time = np.linspace(0, 0.9, 700)
    curves = {
        "Bi-exponential": activation_biexponential(time),
        "Half-cosine": activation_half_cosine(time),
        "Calcium-like gamma": calcium_gamma_transient(time),
    }
    ru = {
        "Bi-exponential": "Биэкспоненциальная",
        "Half-cosine": "Полукосинусная",
        "Calcium-like gamma": "Кальций-подобная гамма",
    }
    for language in ("en", "ru"):
        fig, ax = plt.subplots(figsize=(8, 4.8))
        for name, y in curves.items():
            ax.plot(time, y, lw=2.3, label=name if language == "en" else ru[name])
        ax.set(
            xlabel=tr("time", language),
            ylabel=tr("activation", language),
            title=title("activation_waveforms", language),
        )
        ax.legend()
        ax.grid(alpha=0.25)
        save_figure(fig, "activation_waveforms", language)


if __name__ == "__main__":
    main()
