"""Numerically check invariance under superposed rigid rotation."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

from common import model_name, save_figure, tr
from biomechanics_tutorials.hyperelasticity import (
    deformation_gradient,
    model_catalog,
    rotate_deformation,
    rotation_matrix_z,
    strain_energy,
)


def main() -> None:
    f = deformation_gradient("simple_shear_xy", 0.43) @ deformation_gradient("uniaxial", 1.18)
    angles = np.linspace(0.0, 2.0 * np.pi, 25, endpoint=False)
    errors = []
    definitions = model_catalog()
    for definition in definitions:
        reference = strain_energy(definition.key, f)
        values = [
            strain_energy(definition.key, rotate_deformation(f, rotation_matrix_z(angle)))
            for angle in angles
        ]
        errors.append(max(abs(value - reference) for value in values))
    errors_array = np.maximum(np.asarray(errors), 1e-18)

    for language in ("en", "ru"):
        fig, axis = plt.subplots(figsize=(11, 6.2))
        names = [model_name(definition.name, language) for definition in definitions]
        positions = np.arange(len(names))
        axis.barh(positions, errors_array)
        axis.set_yticks(positions, names, fontsize=8.5)
        axis.set_xscale("log")
        axis.set_xlabel(tr("absolute_error", language))
        axis.set_title(tr("objectivity_title", language))
        axis.invert_yaxis()
        fig.tight_layout()
        save_figure(fig, "objectivity_check", language)


if __name__ == "__main__":
    main()
