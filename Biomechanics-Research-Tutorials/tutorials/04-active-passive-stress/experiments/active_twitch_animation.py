"""Animate activation and total isometric stress."""

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import numpy as np
from common import ANIMATION_DIRECTORY
from biomechanics_tutorials.active_mechanics import (
    activation_biexponential,
    simulate_isometric_twitch,
)


def render(language):
    time = np.linspace(0, 0.8, 220)
    activation = activation_biexponential(time)
    result = simulate_isometric_twitch(time, 1.12, activation)
    fig, axes = plt.subplots(2, 1, figsize=(7, 6), sharex=True)
    (line_a,) = axes[0].plot([], [], lw=2.5)
    (line_s,) = axes[1].plot([], [], lw=2.5)
    (marker_a,) = axes[0].plot([], [], "o")
    (marker_s,) = axes[1].plot([], [], "o")
    axes[0].set(
        xlim=(0, 0.8), ylim=(0, 1.05), ylabel="Activation" if language == "en" else "Активация"
    )
    axes[1].set(
        xlim=(0, 0.8),
        ylim=(min(result["total"]) - 3, max(result["total"]) + 3),
        xlabel="Time" if language == "en" else "Время",
        ylabel="Nominal stress" if language == "en" else "Номинальное напряжение",
    )
    [a.grid(alpha=0.25) for a in axes]
    fig.suptitle("Active twitch" if language == "en" else "Активное сокращение")

    def update(i):
        line_a.set_data(time[: i + 1], activation[: i + 1])
        line_s.set_data(time[: i + 1], result["total"][: i + 1])
        marker_a.set_data([time[i]], [activation[i]])
        marker_s.set_data([time[i]], [result["total"][i]])
        return line_a, line_s, marker_a, marker_s

    anim = FuncAnimation(fig, update, frames=range(0, len(time), 3), interval=45, blit=True)
    suffix = "" if language == "en" else "_ru"
    path = ANIMATION_DIRECTORY / f"active_twitch{suffix}.gif"
    path.parent.mkdir(parents=True, exist_ok=True)
    anim.save(path, writer=PillowWriter(fps=18))
    plt.close(fig)


def main():
    render("en")
    render("ru")


if __name__ == "__main__":
    main()
