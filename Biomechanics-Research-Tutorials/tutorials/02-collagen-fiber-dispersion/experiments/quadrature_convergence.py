"""Measure angular-quadrature convergence of nominal stress."""

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
    """Save quadrature-convergence figures in both languages."""
    stretches = np.linspace(1.0, 1.25, 101)
    mean = np.deg2rad(37.0)
    beta = 7.0
    reference = nominal_stress(
        stretches,
        DispersionParameters(
            mean_angle=mean,
            concentration=beta,
            quadrature_points=8193,
        ),
    )
    points = np.array([33, 65, 129, 257, 513, 1025])
    errors = np.empty(len(points))
    for index, count in enumerate(points):
        candidate = nominal_stress(
            stretches,
            DispersionParameters(
                mean_angle=mean,
                concentration=beta,
                quadrature_points=int(count),
            ),
        )
        errors[index] = np.max(np.abs(candidate - reference))
    base_output = (
        Path(__file__).resolve().parents[1] / "figures" / "quadrature_convergence.png"
    )
    visualization = load_visualization()
    for language in SUPPORTED_LANGUAGES:
        output = localized_path(base_output, language)
        visualization.save_quadrature_convergence(
            points,
            errors,
            output,
            language=language,
        )
        print(f"Saved {output}")
    print("points,error")
    for count, error in zip(points, errors, strict=True):
        print(f"{count},{error:.8e}")


if __name__ == "__main__":
    main()
