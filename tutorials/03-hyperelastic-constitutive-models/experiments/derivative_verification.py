"""Verify numerical energy differentiation against an analytical result."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

from common import save_figure, tr
from biomechanics_tutorials.hyperelasticity import (
    neo_hookean_uniaxial_nominal_stress,
    path_response,
)


def main() -> None:
    stretches = np.linspace(0.78, 1.50, 190)
    analytical = neo_hookean_uniaxial_nominal_stress(stretches)
    numerical = path_response("neo_hookean", stretches, relative_step=1e-5)
    steps = np.logspace(-2, -8, 35)
    point = 1.25
    exact_point = float(neo_hookean_uniaxial_nominal_stress(point))
    errors = np.array(
        [
            abs(float(path_response("neo_hookean", [point], relative_step=step)[0]) - exact_point)
            for step in steps
        ]
    )

    for language in ("en", "ru"):
        fig, axes = plt.subplots(1, 2, figsize=(13, 5.3))
        axes[0].plot(stretches, analytical, linewidth=2.7, label="Analytical" if language == "en" else "Аналитическое")
        axes[0].plot(stretches, numerical, "--", linewidth=2.0, label="Finite difference" if language == "en" else "Конечная разность")
        axes[0].set_xlabel(tr("stretch", language))
        axes[0].set_ylabel(tr("response", language))
        axes[0].legend()
        axes[1].loglog(steps, errors, marker="o", markersize=4)
        axes[1].set_xlabel(tr("step_size", language))
        axes[1].set_ylabel(tr("absolute_error", language))
        fig.suptitle(tr("derivative_title", language), fontsize=16)
        fig.tight_layout(rect=(0, 0, 1, 0.94))
        save_figure(fig, "derivative_verification", language)


if __name__ == "__main__":
    main()
