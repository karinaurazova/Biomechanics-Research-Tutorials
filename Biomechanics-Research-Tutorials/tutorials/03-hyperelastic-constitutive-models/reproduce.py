"""Regenerate every committed result for Tutorial 03."""

from __future__ import annotations

from pathlib import Path
import runpy
import sys

TUTORIAL_ROOT = Path(__file__).resolve().parent
REPOSITORY_ROOT = TUTORIAL_ROOT.parents[1]
SOURCE_DIRECTORY = REPOSITORY_ROOT / "src"
EXPERIMENT_DIRECTORY = TUTORIAL_ROOT / "experiments"
EXPERIMENTS = [
    "model_catalog.py",
    "isotropic_uniaxial.py",
    "deformation_modes.py",
    "limiting_chain.py",
    "ogden_exponents.py",
    "calibration_nonuniqueness.py",
    "volumetric_penalties.py",
    "fiber_angle.py",
    "fiber_angle_map.py",
    "hgo_goh_dispersion.py",
    "myocardium_shear_modes.py",
    "derivative_verification.py",
    "objectivity_check.py",
    "gent_animation.py",
]


def main() -> None:
    """Execute all experiment entry points with the active interpreter."""
    for directory in (SOURCE_DIRECTORY, EXPERIMENT_DIRECTORY):
        if str(directory) not in sys.path:
            sys.path.insert(0, str(directory))

    for script_name in EXPERIMENTS:
        script = EXPERIMENT_DIRECTORY / script_name
        print(f"Running {script.relative_to(REPOSITORY_ROOT)}", flush=True)
        runpy.run_path(str(script), run_name="__main__")

    print("Tutorial 03 results regenerated successfully.", flush=True)


if __name__ == "__main__":
    main()
