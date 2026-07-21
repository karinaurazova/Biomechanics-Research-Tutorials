"""Show active-stress/active-strain divergence in shear."""

import matplotlib.pyplot as plt
import numpy as np
from common import save_figure, title, tr
from biomechanics_tutorials.active_mechanics import (
    active_stress_shear_response,
    active_strain_shear_response,
    calibrate_active_stretch,
)


def main():
    gamma = np.linspace(-0.6, 0.6, 350)
    tension = 26.0
    ref = 1.12
    la = calibrate_active_stretch(ref, tension / ref)
    stress = active_stress_shear_response(gamma, tension)
    strain = active_strain_shear_response(gamma, la)
    for language in ("en", "ru"):
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(gamma, stress, lw=2.5, label="Active stress" if language == "en" else "Активное напряжение")
        ax.plot(gamma, strain, lw=2.5, label="Active strain" if language == "en" else "Активная деформация")
        ax.set(
            xlabel=tr("shear", language),
            ylabel=tr("response", language),
            title=title("active_approaches_shear", language),
        )
        ax.legend()
        ax.grid(alpha=0.25)
        save_figure(fig, "active_approaches_shear", language)


if __name__ == "__main__":
    main()
