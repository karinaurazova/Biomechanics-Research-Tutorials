"""Map stress over mean angle and concentration."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import numpy as np

from biomechanics_tutorials.collagen_dispersion import DispersionParameters, nominal_stress
from biomechanics_tutorials.localization import SUPPORTED_LANGUAGES, localized_path


def load_visualization():
    """Load tutorial-local visualization functions."""
    path = Path(__file__).resolve().parents[1] / "src" / "visualization.py"
    spec = spec_from_file_location("tutorial02_visualization", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load {path}")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    """Save the anisotropy map in both languages."""
    stretch = 1.18
    mean_angles = np.deg2rad(np.linspace(0.0, 90.0, 91))
    concentrations = np.linspace(0.0, 16.0, 65)
    stress_map = np.empty((len(concentrations), len(mean_angles)))
    for index_beta, beta in enumerate(concentrations):
        for index_mean, mean in enumerate(mean_angles):
            stress_map[index_beta, index_mean] = float(
                nominal_stress(
                    stretch,
                    DispersionParameters(
                        mean_angle=float(mean),
                        concentration=float(beta),
                        quadrature_points=513,
                    ),
                )
            )
    base_output = Path(__file__).resolve().parents[1] / "figures" / "anisotropy_map.png"
    visualization = load_visualization()
    for language in SUPPORTED_LANGUAGES:
        output = localized_path(base_output, language)
        visualization.save_anisotropy_map(
            mean_angles,
            concentrations,
            stress_map,
            stretch,
            output,
            language=language,
        )
        print(f"Saved {output}")


if __name__ == "__main__":
    main()
