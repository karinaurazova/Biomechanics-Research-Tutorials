"""Compare all isotropic models in uniaxial loading."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

from common import curve_colors, finite_values, model_name, save_figure, tr
from biomechanics_tutorials.hyperelasticity import ISOTROPIC_MODELS, MODEL_DEFINITIONS, path_response


def main() -> None:
    stretches = np.linspace(0.75, 1.60, 280)
    colors = curve_colors(len(ISOTROPIC_MODELS))
    for language in ("en", "ru"):
        fig, axis = plt.subplots(figsize=(10.5, 6.5))
        for key, color in zip(ISOTROPIC_MODELS, colors):
            values = path_response(key, stretches)
            x, y = finite_values(stretches, values)
            axis.plot(
                x,
                y,
                linewidth=2.1,
                color=color,
                label=model_name(MODEL_DEFINITIONS[key].name, language),
            )
        axis.axhline(0.0, color="#94A3B8", linewidth=0.8)
        axis.axvline(1.0, color="#94A3B8", linewidth=0.8)
        axis.set_xlabel(tr("stretch", language))
        axis.set_ylabel(tr("response", language))
        axis.set_title(tr("uniaxial_title", language))
        axis.legend(ncol=2, fontsize=8.8)
        fig.tight_layout()
        save_figure(fig, "isotropic_uniaxial", language)


if __name__ == "__main__":
    main()
