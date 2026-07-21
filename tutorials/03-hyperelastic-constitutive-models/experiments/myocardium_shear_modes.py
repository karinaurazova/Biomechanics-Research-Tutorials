"""Compare myocardial models in three material shear planes."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

from common import curve_colors, model_name, save_figure, tr
from biomechanics_tutorials.hyperelasticity import MODEL_DEFINITIONS, MYOCARDIUM_MODELS, path_response


def main() -> None:
    shear = np.linspace(0.0, 0.55, 180)
    modes = [
        ("simple_shear_xy", "f-s"),
        ("simple_shear_xz", "f-n"),
        ("simple_shear_yz", "s-n"),
    ]
    colors = curve_colors(len(MYOCARDIUM_MODELS))
    for language in ("en", "ru"):
        fig, axes = plt.subplots(1, 3, figsize=(15, 5.3), sharey=False)
        for axis, (mode, plane) in zip(axes, modes):
            for key, color in zip(MYOCARDIUM_MODELS, colors):
                axis.plot(
                    shear,
                    path_response(key, shear, mode),
                    linewidth=2.2,
                    color=color,
                    label=model_name(MODEL_DEFINITIONS[key].name, language),
                )
            axis.set_title(f"{tr('simple_shear', language)} {plane}")
            axis.set_xlabel(tr("shear", language))
            axis.set_ylabel(tr("response", language))
        axes[0].legend(fontsize=8.5)
        fig.suptitle(tr("myocardium_title", language), fontsize=16)
        fig.tight_layout(rect=(0, 0, 1, 0.94))
        save_figure(fig, "myocardium_shear_modes", language)


if __name__ == "__main__":
    main()
