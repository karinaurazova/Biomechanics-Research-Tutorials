"""Verify the analytical orientation tensor against angular quadrature."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import numpy as np

from biomechanics_tutorials.collagen_dispersion import (
    numerical_orientation_tensor,
    orientation_tensor,
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
    """Save tensor-verification figures in both languages."""
    concentrations = np.linspace(0.0, 16.0, 81)
    mean = np.deg2rad(27.0)
    analytical = np.array([orientation_tensor(mean, beta) for beta in concentrations])
    numerical = np.array(
        [
            numerical_orientation_tensor(mean, beta, points=1001)
            for beta in concentrations
        ]
    )
    analytical_eigenvalues = np.linalg.eigvalsh(analytical)[:, ::-1]
    numerical_eigenvalues = np.linalg.eigvalsh(numerical)[:, ::-1]
    errors = np.max(np.abs(analytical - numerical), axis=(1, 2))
    base_output = (
        Path(__file__).resolve().parents[1] / "figures" / "tensor_verification.png"
    )
    visualization = load_visualization()
    for language in SUPPORTED_LANGUAGES:
        output = localized_path(base_output, language)
        visualization.save_tensor_verification(
            concentrations,
            analytical_eigenvalues,
            numerical_eigenvalues,
            errors,
            output,
            language=language,
        )
        print(f"Saved {output}")
    print(f"Maximum tensor component error: {errors.max():.3e}")


if __name__ == "__main__":
    main()
