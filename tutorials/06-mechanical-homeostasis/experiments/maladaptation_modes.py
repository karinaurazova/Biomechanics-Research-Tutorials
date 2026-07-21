import matplotlib.pyplot as plt
import numpy as np

from biomechanics_tutorials.mechanical_homeostasis import HomeostasisParameters, generate_load_protocol, simulate_scalar_homeostasis
from common import palette_cycle, save_figure, title, tr

time = np.linspace(0.0, 28.0, 2801)
load = generate_load_protocol(time, "step", amplitude=0.55, onset=3.0)
cases = [
    ("healthy", HomeostasisParameters(adaptation_rate=0.30)),
    ("wrong sign", HomeostasisParameters(adaptation_rate=0.20, feedback_sign=-1.0, capacity_min=0.2, capacity_max=3.0)),
    ("capacity limit", HomeostasisParameters(adaptation_rate=0.30, capacity_max=1.30)),
    ("biological bias", HomeostasisParameters(adaptation_rate=0.30, biological_bias=0.10)),
]
results = [(name, simulate_scalar_homeostasis(time, load, parameters=params)) for name, params in cases]

for language in ("en", "ru"):
    translated = {
        "healthy": "здоровый ответ",
        "wrong sign": "неверный знак",
        "capacity limit": "предел способности",
        "biological bias": "биологическое смещение",
    }
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    for color, (name, result) in zip(palette_cycle(), results, strict=False):
        label = name if language == "en" else translated[name]
        axes[0].plot(time, result["stress"], color=color, label=label)
        axes[1].plot(time, result["capacity"], color=color, label=label)
    axes[0].axhline(1.0, linestyle=":")
    axes[0].set_xlabel(tr("time", language))
    axes[0].set_ylabel(tr("stress", language))
    axes[1].set_xlabel(tr("time", language))
    axes[1].set_ylabel(tr("capacity", language))
    axes[0].legend(fontsize=8)
    axes[1].legend(fontsize=8)
    fig.suptitle(title("maladaptation_modes", language))
    fig.tight_layout()
    save_figure(fig, "maladaptation_modes", language)
