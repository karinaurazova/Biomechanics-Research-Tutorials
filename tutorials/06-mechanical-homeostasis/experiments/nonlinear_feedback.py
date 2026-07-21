import matplotlib.pyplot as plt
import numpy as np

from biomechanics_tutorials.mechanical_homeostasis import HomeostasisParameters, feedback_response, generate_load_protocol, simulate_scalar_homeostasis
from common import palette_cycle, save_figure, title, tr

errors = np.linspace(-1.0, 1.0, 500)
responses = [
    ("linear", feedback_response(errors)),
    ("dead zone", feedback_response(errors, dead_zone=0.12)),
    ("saturated", feedback_response(errors, response_limit=0.25)),
    ("both", feedback_response(errors, dead_zone=0.12, response_limit=0.25)),
]
time = np.linspace(0.0, 35.0, 3501)
load = generate_load_protocol(time, "step", amplitude=0.75, onset=3.0)
parameter_sets = [
    ("linear", HomeostasisParameters(adaptation_rate=0.3)),
    ("dead zone", HomeostasisParameters(adaptation_rate=0.3, dead_zone=0.12)),
    ("saturated", HomeostasisParameters(adaptation_rate=0.3, response_limit=0.25)),
    ("both", HomeostasisParameters(adaptation_rate=0.3, dead_zone=0.12, response_limit=0.25)),
]
trajectories = [(name, simulate_scalar_homeostasis(time, load, parameters=params)) for name, params in parameter_sets]

for language in ("en", "ru"):
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    for color, (name, values) in zip(palette_cycle(), responses, strict=False):
        axes[0].plot(errors, values, color=color, label=name)
    axes[0].axhline(0.0, linewidth=1)
    axes[0].axvline(0.0, linewidth=1)
    axes[0].set_xlabel(tr("error", language))
    axes[0].set_ylabel("Feedback response" if language == "en" else "Ответ обратной связи")
    axes[0].legend(fontsize=8)
    for color, (name, result) in zip(palette_cycle(), trajectories, strict=False):
        axes[1].plot(time, result["stress"], color=color, label=name)
    axes[1].axhline(1.0, linestyle=":")
    axes[1].set_xlabel(tr("time", language))
    axes[1].set_ylabel(tr("stress", language))
    axes[1].legend(fontsize=8)
    fig.suptitle(title("nonlinear_feedback", language))
    fig.tight_layout()
    save_figure(fig, "nonlinear_feedback", language)
