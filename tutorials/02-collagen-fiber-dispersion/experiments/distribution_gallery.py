"""Generate localized galleries of axial orientation distributions."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import numpy as np

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
    """Save the gallery in English and Russian."""
    base_output = (
        Path(__file__).resolve().parents[1] / "figures" / "distribution_gallery.png"
    )
    visualization = load_visualization()
    for language in SUPPORTED_LANGUAGES:
        output = localized_path(base_output, language)
        visualization.save_distribution_gallery(
            (0.0, 1.0, 4.0, 12.0),
            np.deg2rad(20.0),
            output,
            language=language,
        )
        print(f"Saved {output}")


if __name__ == "__main__":
    main()
