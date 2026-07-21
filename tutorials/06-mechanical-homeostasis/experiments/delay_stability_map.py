import matplotlib.pyplot as plt
import numpy as np

from biomechanics_tutorials.mechanical_homeostasis import HomeostasisParameters, generate_load_protocol, simulate_scalar_homeostasis
from common import save_figure, title, tr

time = np.linspace(0.0, 35.0, 1751)
load = generate_load_protocol(time, "step", amplitude=0.35, onset=2.0)
rates = np.linspace(0.08, 1.0, 18)
delays = np.linspace(0.0, 5.0, 19)
metric = np.empty((delays.size, rates.size))
for row, delay in enumerate(delays):
    for column, rate in enumerate(rates):
        params = HomeostasisParameters(adaptation_rate=float(rate), delay=float(delay), capacity_min=0.15, capacity_max=4.0)
        result = simulate_scalar_homeostasis(time, load, parameters=params)
        late = result["true_error"][time > 20.0]
        metric[row, column] = np.sqrt(np.mean(late**2))
examples = [
    (0.20, 0.0),
    (0.55, 1.5),
    (0.85, 4.0),
]
trajectories = []
for rate, delay in examples:
    params = HomeostasisParameters(adaptation_rate=rate, delay=delay, capacity_min=0.15, capacity_max=4.0)
    trajectories.append((rate, delay, simulate_scalar_homeostasis(time, load, parameters=params)))

for language in ("en", "ru"):
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.8))
    image = axes[0].imshow(metric, origin="lower", aspect="auto", extent=[rates[0], rates[-1], delays[0], delays[-1]], cmap="magma", vmin=0.0, vmax=np.quantile(metric, 0.92))
    axes[0].set_xlabel(tr("rate", language))
    axes[0].set_ylabel(tr("delay", language))
    colorbar = fig.colorbar(image, ax=axes[0])
    colorbar.set_label(tr("rms", language))
    for rate, delay, result in trajectories:
        axes[1].plot(time, result["stress"], label=f"k={rate:.2f}, delay={delay:.1f}")
    axes[1].axhline(1.0, linestyle=":")
    axes[1].set_xlabel(tr("time", language))
    axes[1].set_ylabel(tr("stress", language))
    axes[1].legend(fontsize=8)
    fig.suptitle(title("delay_stability_map", language))
    fig.tight_layout()
    save_figure(fig, "delay_stability_map", language)
