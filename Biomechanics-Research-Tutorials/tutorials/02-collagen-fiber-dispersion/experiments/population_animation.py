"""Animate a synthetic increase in fiber concentration."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

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
    """Save English and Russian GIF animations."""
    base_output = (
        Path(__file__).resolve().parents[1] / "animations" / "dispersion_transition.gif"
    )
    visualization = load_visualization()
    for language in SUPPORTED_LANGUAGES:
        output = localized_path(base_output, language)
        visualization.save_dispersion_animation(output, language=language)
        print(f"Saved {output}")


if __name__ == "__main__":
    main()
