"""Show the influence of mean fiber angle."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

from common import curve_colors, save_figure, tr
from biomechanics_tutorials.hyperelasticity import path_response


def main() -> None:
    stretches = np.linspace(1.0, 1.35, 160)
    angles = [0.0, 20.0, 40.0, 60.0, 80.0]
    colors = curve_colors(len(angles))
    for language in ("en", "ru"):
        fig, axis = plt.subplots(figsize=(9.5, 6.0))
        for angle, color in zip(angles, colors):
            response = path_response("hgo", stretches, parameters={"fiber_angle_deg": angle})
            axis.plot(stretches, response, linewidth=2.2, color=color, label=f"α={angle:.0f}°")
        axis.set_xlabel(tr("stretch", language))
        axis.set_ylabel(tr("response", language))
        axis.set_title(tr("angle_title", language))
        axis.legend()
        fig.tight_layout()
        save_figure(fig, "fiber_angle", language)


if __name__ == "__main__":
    main()
