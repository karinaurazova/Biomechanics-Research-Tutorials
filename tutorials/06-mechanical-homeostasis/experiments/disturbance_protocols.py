import matplotlib.pyplot as plt
import numpy as np

from biomechanics_tutorials.mechanical_homeostasis import generate_load_protocol, simulate_scalar_homeostasis
from common import save_figure, title, tr

time = np.linspace(0.0, 28.0, 2801)
protocols = ["step", "pulse", "ramp", "cyclic"]
labels = {
    "en": {"step": "step", "pulse": "pulse", "ramp": "ramp", "cyclic": "cyclic"},
    "ru": {"step": "ступень", "pulse": "импульс", "ramp": "линейный рост", "cyclic": "цикл"},
}
results = {}
for kind in protocols:
    load = generate_load_protocol(time, kind, amplitude=0.45, onset=4.0, duration=7.0, period=5.0)
    results[kind] = simulate_scalar_homeostasis(time, load)

for language in ("en", "ru"):
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), sharex=True)
    for ax, kind in zip(axes.flat, protocols, strict=True):
        result = results[kind]
        ax.plot(time, result["load"], label=tr("load", language), linewidth=1.8)
        ax.plot(time, result["stress"], label=tr("stress", language), linewidth=2.2)
        ax.plot(time, result["capacity"], label=tr("capacity", language), linewidth=2.0)
        ax.axhline(1.0, linestyle=":", linewidth=1.2)
        ax.set_title(labels[language][kind])
        ax.set_xlabel(tr("time", language))
        ax.legend(fontsize=8)
    fig.suptitle(title("disturbance_protocols", language))
    fig.tight_layout()
    save_figure(fig, "disturbance_protocols", language)
