"""Plot force-length and force-velocity multipliers."""

import matplotlib.pyplot as plt
import numpy as np
from common import save_figure, title, tr
from biomechanics_tutorials.active_mechanics import force_length, force_velocity


def main():
    stretch = np.linspace(0.65, 1.55, 500)
    velocity = np.linspace(-1.0, 0.95, 500)
    for language in ("en", "ru"):
        fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
        axes[0].plot(stretch, force_length(stretch), lw=2.5)
        axes[0].axvline(1.1, ls="--", alpha=0.6)
        axes[0].set(
            xlabel=tr("stretch", language),
            ylabel=tr("multiplier", language),
            title="Force–length" if language == "en" else "Сила–длина",
        )
        axes[0].grid(alpha=0.25)
        axes[1].plot(velocity, force_velocity(velocity), lw=2.5)
        axes[1].axvline(0, ls="--", alpha=0.6)
        axes[1].axhline(1, ls="--", alpha=0.6)
        axes[1].set(
            xlabel=tr("velocity", language),
            ylabel=tr("multiplier", language),
            title="Force–velocity" if language == "en" else "Сила–скорость",
        )
        axes[1].grid(alpha=0.25)
        fig.suptitle(title("force_length_velocity", language))
        fig.tight_layout()
        save_figure(fig, "force_length_velocity", language)


if __name__ == "__main__":
    main()
