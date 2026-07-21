import matplotlib.pyplot as plt
import numpy as np

from biomechanics_tutorials.mechanical_homeostasis import simulate_vessel_homeostasis, vessel_equilibrium
from common import save_figure, title, tr

time = np.linspace(0.0, 70.0, 3501)
pressure = np.where(time < 4.0, 1.0, 1.35)
flow = np.where(time < 4.0, 1.0, 1.60)
result = simulate_vessel_homeostasis(time, pressure, flow)
radius_eq, thickness_eq = vessel_equilibrium(1.35, 1.60)

for language in ("en", "ru"):
    fig, axes = plt.subplots(2, 1, figsize=(11, 7.5), sharex=True)
    axes[0].plot(time, result["radius"], label=tr("radius", language), linewidth=2.2)
    axes[0].plot(time, result["thickness"], label=tr("thickness", language), linewidth=2.2)
    axes[0].axhline(radius_eq, linestyle=":")
    axes[0].axhline(thickness_eq, linestyle=":")
    axes[0].legend()
    axes[0].set_ylabel("geometry ratio" if language == "en" else "отношение геометрии")
    axes[1].plot(time, result["shear_ratio"], label=tr("shear", language), linewidth=2.2)
    axes[1].plot(time, result["wall_stress_ratio"], label=tr("wall", language), linewidth=2.2)
    axes[1].axhline(1.0, linestyle=":")
    axes[1].set_xlabel(tr("time", language))
    axes[1].set_ylabel(tr("stimulus", language))
    axes[1].legend()
    fig.suptitle(title("vessel_adaptation", language))
    fig.tight_layout()
    save_figure(fig, "vessel_adaptation", language)
