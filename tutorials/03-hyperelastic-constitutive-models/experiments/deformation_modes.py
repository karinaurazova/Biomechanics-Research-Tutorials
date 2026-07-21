"""Compare selected models under four loading modes."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

from common import curve_colors, finite_values, model_name, save_figure, tr
from biomechanics_tutorials.hyperelasticity import MODEL_DEFINITIONS, path_response

MODELS = ["neo_hookean", "mooney_rivlin", "yeoh", "gent", "ogden_2", "veronda_westmann"]
MODES = [
    ("uniaxial", np.linspace(1.0, 1.45, 180), "uniaxial", "stretch"),
    ("equibiaxial", np.linspace(1.0, 1.28, 180), "equibiaxial", "stretch"),
    ("plane_strain", np.linspace(1.0, 1.45, 180), "plane_strain", "stretch"),
    ("simple_shear_xy", np.linspace(0.0, 0.80, 180), "simple_shear", "shear"),
]


def main() -> None:
    colors = curve_colors(len(MODELS))
    for language in ("en", "ru"):
        fig, axes = plt.subplots(2, 2, figsize=(13, 9))
        for axis, (mode, amounts, title_key, x_key) in zip(axes.flat, MODES):
            for key, color in zip(MODELS, colors):
                response = path_response(key, amounts, mode)
                x, y = finite_values(amounts, response)
                axis.plot(
                    x,
                    y,
                    linewidth=1.9,
                    color=color,
                    label=model_name(MODEL_DEFINITIONS[key].name, language),
                )
            axis.set_title(tr(title_key, language))
            axis.set_xlabel(tr(x_key, language))
            axis.set_ylabel(tr("response", language))
        handles, labels = axes[0, 0].get_legend_handles_labels()
        fig.legend(handles, labels, loc="lower center", ncol=3, fontsize=9)
        fig.suptitle(tr("modes_title", language), fontsize=17)
        fig.tight_layout(rect=(0, 0.08, 1, 0.96))
        save_figure(fig, "deformation_modes", language)


if __name__ == "__main__":
    main()
