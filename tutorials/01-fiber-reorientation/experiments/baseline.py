"""Generate localized baseline fiber-reorientation figures."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import numpy as np

from biomechanics_tutorials.fiber_reorientation import (
    ReorientationParameters,
    simulate_reorientation,
)
from biomechanics_tutorials.localization import SUPPORTED_LANGUAGES, localized_path


def load_save_function():
    """Load the tutorial-local visualization helper."""
    module_path = Path(__file__).resolve().parents[1] / "src" / "visualization.py"
    spec = spec_from_file_location("tutorial01_visualization", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load {module_path}")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.save_baseline_figure


def main() -> None:
    """Run the baseline and save English and Russian figures."""
    params = ReorientationParameters(rate=0.35, duration=20.0, time_step=0.01)
    time, orientation, target = simulate_reorientation(
        np.deg2rad(-50.0), np.deg2rad(30.0), params
    )
    base_output = Path(__file__).resolve().parents[1] / "figures" / "baseline.png"
    save_figure = load_save_function()
    for language in SUPPORTED_LANGUAGES:
        output = localized_path(base_output, language)
        save_figure(time, orientation, target, output, language=language)
        print(f"Saved {output}")


if __name__ == "__main__":
    main()
