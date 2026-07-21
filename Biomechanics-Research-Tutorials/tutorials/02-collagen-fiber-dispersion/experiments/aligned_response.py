"""Compare dispersed-fiber responses when the mean is aligned with loading."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import numpy as np

from biomechanics_tutorials.collagen_dispersion import (
    DispersionParameters,
    FiberMaterialParameters,
    nominal_stress,
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
    """Save aligned-loading response curves in both languages."""
    stretches = np.linspace(1.0, 1.25, 121)
    concentrations = (0.0, 1.0, 4.0, 12.0)
    material = FiberMaterialParameters()
    curves = {
        beta: nominal_stress(
            stretches,
            DispersionParameters(
                mean_angle=0.0,
                concentration=beta,
                quadrature_points=1001,
            ),
            material,
        )
        for beta in concentrations
    }
    base_output = Path(__file__).resolve().parents[1] / "figures" / "aligned_response.png"
    visualization = load_visualization()
    for language in SUPPORTED_LANGUAGES:
        output = localized_path(base_output, language)
        visualization.save_response_curves(
            stretches,
            curves,
            0.0,
            output,
            title_key="aligned_response_title",
            language=language,
        )
        print(f"Saved {output}")


if __name__ == "__main__":
    main()
