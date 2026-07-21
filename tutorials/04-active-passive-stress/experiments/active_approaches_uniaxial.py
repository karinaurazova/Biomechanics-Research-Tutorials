"""Compare active stress and active strain after one-point calibration."""

import matplotlib.pyplot as plt
import numpy as np
from common import save_figure, title, tr
from biomechanics_tutorials.active_mechanics import (
    active_stress_uniaxial_nominal_response,
    active_strain_uniaxial_nominal_response,
    calibrate_active_stretch,
)


def main():
    stretch = np.linspace(0.82, 1.38, 400)
    tension = 26.0
    ref = 1.12
    la = calibrate_active_stretch(ref, tension / ref)
    stress = active_stress_uniaxial_nominal_response(stretch, tension)
    strain = active_strain_uniaxial_nominal_response(stretch, la)
    for language in ("en", "ru"):
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(stretch, stress, lw=2.5, label="Active stress" if language == "en" else "Активное напряжение")
        ax.plot(stretch, strain, lw=2.5, label="Active strain" if language == "en" else "Активная деформация")
        ax.scatter(
            [ref],
            [np.interp(ref, stretch, stress)],
            zorder=5,
            label="Calibration point" if language == "en" else "Точка калибровки",
        )
        ax.set(
            xlabel=tr("stretch", language),
            ylabel=tr("stress", language),
            title=title("active_approaches_uniaxial", language),
        )
        ax.legend()
        ax.grid(alpha=0.25)
        save_figure(fig, "active_approaches_uniaxial", language)


if __name__ == "__main__":
    main()
