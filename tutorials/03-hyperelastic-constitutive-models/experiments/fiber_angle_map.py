"""Generate a stretch-angle response map for the HGO model."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

from common import save_figure, tr
from biomechanics_tutorials.hyperelasticity import path_response


def main() -> None:
    stretches = np.linspace(1.0, 1.35, 65)
    angles = np.linspace(0.0, 90.0, 73)
    response = np.empty((angles.size, stretches.size))
    for row, angle in enumerate(angles):
        response[row] = path_response(
            "hgo", stretches, parameters={"fiber_angle_deg": float(angle)}
        )
    for language in ("en", "ru"):
        fig, axis = plt.subplots(figsize=(10, 6.3))
        image = axis.imshow(
            response,
            origin="lower",
            aspect="auto",
            extent=[stretches[0], stretches[-1], angles[0], angles[-1]],
            cmap="viridis",
        )
        axis.set_xlabel(tr("stretch", language))
        axis.set_ylabel(tr("fiber_angle", language))
        axis.set_title(tr("angle_map_title", language))
        colorbar = fig.colorbar(image, ax=axis)
        colorbar.set_label(tr("response", language))
        fig.tight_layout()
        save_figure(fig, "fiber_angle_map", language)


if __name__ == "__main__":
    main()
