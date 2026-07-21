import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import numpy as np

from biomechanics_tutorials.mechanical_homeostasis import generate_load_protocol, simulate_scalar_homeostasis
from common import ANIMATION_DIRECTORY, title, tr
from biomechanics_tutorials.plotting import apply_tutorial_style

time = np.linspace(0.0, 24.0, 1201)
load = generate_load_protocol(time, "step", amplitude=0.55, onset=3.0)
result = simulate_scalar_homeostasis(time, load)
frame_indices = np.linspace(0, time.size - 1, 42, dtype=int)
ANIMATION_DIRECTORY.mkdir(parents=True, exist_ok=True)

for language in ("en", "ru"):
    apply_tutorial_style()
    fig, axes = plt.subplots(2, 1, figsize=(8.5, 6.5), sharex=True)
    stress_line, = axes[0].plot([], [], linewidth=2.6)
    capacity_line, = axes[1].plot([], [], linewidth=2.6)
    axes[0].axhline(1.0, linestyle=":")
    axes[0].set_xlim(time[0], time[-1])
    axes[0].set_ylim(0.85, 1.62)
    axes[1].set_xlim(time[0], time[-1])
    axes[1].set_ylim(0.90, 1.62)
    axes[0].set_ylabel(tr("stress", language))
    axes[1].set_ylabel(tr("capacity", language))
    axes[1].set_xlabel(tr("time", language))
    fig.suptitle(title("feedback_loop", language))

    def update(frame):
        index = frame_indices[frame]
        stress_line.set_data(time[: index + 1], result["stress"][: index + 1])
        capacity_line.set_data(time[: index + 1], result["capacity"][: index + 1])
        return stress_line, capacity_line

    animation = FuncAnimation(fig, update, frames=len(frame_indices), interval=90, blit=True)
    suffix = "" if language == "en" else "_ru"
    animation.save(ANIMATION_DIRECTORY / f"homeostatic_recovery{suffix}.gif", writer=PillowWriter(fps=10))
    plt.close(fig)
