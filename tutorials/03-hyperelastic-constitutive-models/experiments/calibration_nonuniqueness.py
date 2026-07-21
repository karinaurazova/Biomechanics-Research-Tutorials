"""Illustrate non-uniqueness of limited uniaxial calibration."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import least_squares

from common import curve_colors, save_figure, tr
from biomechanics_tutorials.hyperelasticity import path_response


def fit_mooney(stretches: np.ndarray, target: np.ndarray, initial: tuple[float, float]):
    def residual(values: np.ndarray) -> np.ndarray:
        return path_response(
            "mooney_rivlin",
            stretches,
            parameters={"c10": values[0], "c01": values[1]},
        ) - target

    result = least_squares(residual, np.asarray(initial), bounds=(0.0, 2.0))
    return {"c10": float(result.x[0]), "c01": float(result.x[1])}


def main() -> None:
    calibration_stretch = np.linspace(1.0, 1.22, 45)
    target = path_response("yeoh", calibration_stretch)
    fit_a = fit_mooney(calibration_stretch, target, (0.48, 0.02))
    fit_b = fit_mooney(calibration_stretch, target, (0.05, 0.45))
    stretch = np.linspace(1.0, 1.55, 190)
    colors = curve_colors(3)

    for language in ("en", "ru"):
        fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))
        labels = [
            "Synthetic Yeoh target" if language == "en" else "Синтетическая цель Йео",
            f"MR-A: C10={fit_a['c10']:.3f}, C01={fit_a['c01']:.3f}",
            f"MR-B: C10={fit_b['c10']:.3f}, C01={fit_b['c01']:.3f}",
        ]
        for axis, mode, title_key in [
            (axes[0], "uniaxial", "uniaxial"),
            (axes[1], "equibiaxial", "equibiaxial"),
        ]:
            curves = [
                path_response("yeoh", stretch, mode),
                path_response("mooney_rivlin", stretch, mode, fit_a),
                path_response("mooney_rivlin", stretch, mode, fit_b),
            ]
            for curve, color, label in zip(curves, colors, labels):
                axis.plot(stretch, curve, linewidth=2.2, color=color, label=label)
            axis.set_title(tr(title_key, language))
            axis.set_xlabel(tr("stretch", language))
            axis.set_ylabel(tr("response", language))
        axes[0].axvspan(1.0, 1.22, alpha=0.10, color="#175CFF")
        axes[0].legend(fontsize=8.5)
        fig.suptitle(tr("calibration_title", language), fontsize=16)
        fig.tight_layout(rect=(0, 0, 1, 0.95))
        save_figure(fig, "calibration_nonuniqueness", language)


if __name__ == "__main__":
    main()
