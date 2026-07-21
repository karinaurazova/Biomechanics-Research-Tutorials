import matplotlib.pyplot as plt
import numpy as np

from biomechanics_tutorials.mechanical_homeostasis import HomeostasisParameters, generate_load_protocol, simulate_scalar_homeostasis
from common import save_figure, title, tr

time = np.linspace(0.0, 22.0, 2201)
load = generate_load_protocol(time, "step", amplitude=0.45, onset=4.0)
raw = simulate_scalar_homeostasis(time, load, parameters=HomeostasisParameters(adaptation_rate=0.25), measurement_noise_std=0.08, seed=11)
filtered = simulate_scalar_homeostasis(time, load, parameters=HomeostasisParameters(adaptation_rate=0.25, sensing_time_constant=0.65), measurement_noise_std=0.08, seed=11)

for language in ("en", "ru"):
    fig, axes = plt.subplots(2, 1, figsize=(11, 7), sharex=True)
    axes[0].plot(time, raw["stress"], label=tr("true", language), linewidth=2.3)
    axes[0].plot(time, raw["measured_stress"], label=tr("measured", language), alpha=0.45)
    axes[0].plot(time, filtered["sensed_stress"], label=tr("filtered", language), linewidth=2.0)
    axes[0].axhline(1.0, linestyle=":")
    axes[0].set_ylabel(tr("stress", language))
    axes[0].legend()
    axes[1].plot(time, raw["capacity"], label="unfiltered" if language == "en" else "без фильтра")
    axes[1].plot(time, filtered["capacity"], label="filtered" if language == "en" else "с фильтром")
    axes[1].set_xlabel(tr("time", language))
    axes[1].set_ylabel(tr("capacity", language))
    axes[1].legend()
    fig.suptitle(title("sensing_noise", language))
    fig.tight_layout()
    save_figure(fig, "sensing_noise", language)
