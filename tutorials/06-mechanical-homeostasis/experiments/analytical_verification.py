import matplotlib.pyplot as plt
import numpy as np

from biomechanics_tutorials.mechanical_homeostasis import HomeostasisParameters, analytical_capacity_response, simulate_scalar_homeostasis
from common import save_figure, title, tr

time = np.linspace(0.0, 15.0, 3001)
params = HomeostasisParameters(adaptation_rate=0.35)
numerical = simulate_scalar_homeostasis(time, 1.55, 1.0, params)
analytical = analytical_capacity_response(time, 1.55, 1.0, 1.0, 0.35)
absolute_error = np.abs(numerical["capacity"] - analytical)

for language in ("en", "ru"):
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6))
    axes[0].plot(time, analytical, label="analytical" if language == "en" else "аналитическое", linewidth=3)
    axes[0].plot(time, numerical["capacity"], "--", label="numerical" if language == "en" else "численное", linewidth=2)
    axes[0].axhline(1.55, linestyle=":", label=tr("target", language))
    axes[0].set_xlabel(tr("time", language))
    axes[0].set_ylabel(tr("capacity", language))
    axes[0].legend()
    axes[1].semilogy(time, np.maximum(absolute_error, 1.0e-12))
    axes[1].set_xlabel(tr("time", language))
    axes[1].set_ylabel("absolute error" if language == "en" else "абсолютная ошибка")
    fig.suptitle(title("analytical_verification", language))
    fig.tight_layout()
    save_figure(fig, "analytical_verification", language)
