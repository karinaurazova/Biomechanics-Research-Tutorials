import matplotlib.pyplot as plt
import numpy as np

from biomechanics_tutorials.mechanical_homeostasis import HomeostasisParameters, generate_load_protocol, simulate_scalar_homeostasis
from common import palette_cycle, save_figure, title, tr

time = np.linspace(0.0, 35.0, 3501)
load = generate_load_protocol(time, "step", amplitude=0.40, onset=3.0)
biases = [-0.12, 0.0, 0.12]
bias_results = [simulate_scalar_homeostasis(time, load, parameters=HomeostasisParameters(sensor_bias=bias, adaptation_rate=0.28)) for bias in biases]
target = 1.0 + 0.15 * (1.0 - np.exp(-np.maximum(time - 8.0, 0.0) / 6.0))
allostasis = simulate_scalar_homeostasis(time, load, parameters=HomeostasisParameters(adaptation_rate=0.28), target_stress=target)

for language in ("en", "ru"):
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    for color, bias, result in zip(palette_cycle(), biases, bias_results, strict=False):
        axes[0].plot(time, result["stress"], color=color, label=f"bias={bias:+.2f}")
    axes[0].axhline(1.0, linestyle=":")
    axes[0].set_xlabel(tr("time", language))
    axes[0].set_ylabel(tr("stress", language))
    axes[0].legend()
    axes[1].plot(time, allostasis["stress"], label=tr("true", language), linewidth=2.2)
    axes[1].plot(time, target, "--", label=tr("target", language), linewidth=2.0)
    axes[1].set_xlabel(tr("time", language))
    axes[1].set_ylabel(tr("stress", language))
    axes[1].legend()
    fig.suptitle(title("bias_allostasis", language))
    fig.tight_layout()
    save_figure(fig, "bias_allostasis", language)
