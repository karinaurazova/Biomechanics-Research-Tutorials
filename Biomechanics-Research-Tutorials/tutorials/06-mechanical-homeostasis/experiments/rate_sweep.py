import matplotlib.pyplot as plt
import numpy as np

from biomechanics_tutorials.mechanical_homeostasis import HomeostasisParameters, generate_load_protocol, homeostasis_metrics, simulate_scalar_homeostasis
from common import palette_cycle, save_figure, title, tr

time = np.linspace(0.0, 30.0, 3001)
load = generate_load_protocol(time, "step", amplitude=0.55, onset=3.0)
rates = [0.08, 0.18, 0.35, 0.70]
results = []
for rate in rates:
    result = simulate_scalar_homeostasis(time, load, parameters=HomeostasisParameters(adaptation_rate=rate))
    metrics = homeostasis_metrics(time[time >= 3.0], result["true_error"][time >= 3.0])
    results.append((rate, result, metrics))

for language in ("en", "ru"):
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    for color, (rate, result, _) in zip(palette_cycle(), results, strict=False):
        axes[0].plot(time, result["stress"], color=color, label=f"k={rate:.2f}")
    axes[0].axhline(1.0, linestyle=":")
    axes[0].set_xlabel(tr("time", language))
    axes[0].set_ylabel(tr("stress", language))
    axes[0].legend()
    axes[1].plot(rates, [item[2]["iae"] for item in results], "o-", label="IAE")
    axes[1].plot(rates, [item[2]["settling_time"] for item in results], "s-", label="settling" if language == "en" else "установление")
    axes[1].set_xlabel(tr("rate", language))
    axes[1].set_ylabel("Recovery metric" if language == "en" else "Метрика восстановления")
    axes[1].legend()
    fig.suptitle(title("rate_sweep", language))
    fig.tight_layout()
    save_figure(fig, "rate_sweep", language)
