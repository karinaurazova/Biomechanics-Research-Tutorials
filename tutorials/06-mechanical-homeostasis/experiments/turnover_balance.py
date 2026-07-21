import matplotlib.pyplot as plt
import numpy as np

from biomechanics_tutorials.mechanical_homeostasis import ConstituentTurnoverParameters, simulate_constituent_turnover
from common import save_figure, title, tr

time = np.linspace(0.0, 30.0, 1201)
error = np.zeros_like(time)
error[(time >= 6.0) & (time < 16.0)] = 0.22
constituent = ConstituentTurnoverParameters("matrix", 1.0, 7.0, production_sensitivity=1.8, removal_sensitivity=0.2)
result = simulate_constituent_turnover(time, error, [constituent])

for language in ("en", "ru"):
    fig, axes = plt.subplots(2, 1, figsize=(11, 7), sharex=True)
    axes[0].plot(time, result["production"][0], label=tr("production", language), linewidth=2.2)
    axes[0].plot(time, result["removal"][0], label=tr("removal", language), linewidth=2.2)
    axes[0].fill_between(time, result["production"][0], result["removal"][0], alpha=0.18)
    axes[0].set_ylabel("rate" if language == "en" else "скорость")
    axes[0].legend()
    axes[1].plot(time, result["mass"][0], linewidth=2.4)
    axes[1].axhline(1.0, linestyle=":")
    axes[1].set_xlabel(tr("time", language))
    axes[1].set_ylabel(tr("mass", language))
    fig.suptitle(title("turnover_balance", language))
    fig.tight_layout()
    save_figure(fig, "turnover_balance", language)
