"""Generate localized baseline collagen-dispersion figures."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import numpy as np

from biomechanics_tutorials.collagen_dispersion import (
    DispersionParameters,
    axial_von_mises_density,
    nominal_stress,
    orientation_grid,
)
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
    """Run the baseline and save both language versions."""
    mean = np.deg2rad(20.0)
    beta = 4.0
    theta = orientation_grid(1001)
    density = axial_von_mises_density(theta, mean, beta)
    stretches = np.linspace(1.0, 1.25, 121)
    stress = nominal_stress(
        stretches,
        DispersionParameters(
            mean_angle=mean,
            concentration=beta,
            quadrature_points=1001,
        ),
    )
    base_output = Path(__file__).resolve().parents[1] / "figures" / "baseline.png"
    visualization = load_visualization()
    for language in SUPPORTED_LANGUAGES:
        output = localized_path(base_output, language)
        visualization.save_baseline_overview(
            theta,
            density,
            stretches,
            stress,
            mean,
            beta,
            output,
            language=language,
        )
        print(f"Saved {output}")


if __name__ == "__main__":
    main()
