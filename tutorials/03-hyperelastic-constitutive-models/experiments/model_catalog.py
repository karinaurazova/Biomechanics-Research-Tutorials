"""Generate the sixteen-model catalog."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

from common import curve_colors, finite_values, model_name, save_figure, tr
from biomechanics_tutorials.hyperelasticity import model_catalog, path_response


def main() -> None:
    stretches = np.linspace(0.82, 1.38, 181)
    definitions = model_catalog()
    colors = curve_colors(len(definitions))
    for language in ("en", "ru"):
        fig, axes = plt.subplots(4, 4, figsize=(15, 12), sharex=True)
        for axis, definition, color in zip(axes.flat, definitions, colors):
            response = path_response(definition.key, stretches)
            x, y = finite_values(stretches, response)
            axis.plot(x, y, linewidth=2.1, color=color)
            axis.axhline(0.0, linewidth=0.8, color="#94A3B8")
            axis.axvline(1.0, linewidth=0.8, color="#94A3B8")
            axis.set_title(model_name(definition.name, language), fontsize=10.5)
            axis.set_xlabel(tr("stretch", language))
            axis.set_ylabel(tr("response", language))
        fig.suptitle(tr("catalog", language), fontsize=18)
        fig.tight_layout(rect=(0, 0, 1, 0.97))
        save_figure(fig, "model_catalog", language)


if __name__ == "__main__":
    main()
