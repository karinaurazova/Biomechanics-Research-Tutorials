"""Regenerate every committed result for Tutorial 07."""

from __future__ import annotations

from pathlib import Path
import runpy
import sys

TUTORIAL_ROOT = Path(__file__).resolve().parent
REPOSITORY_ROOT = TUTORIAL_ROOT.parents[1]
SOURCE_DIRECTORY = REPOSITORY_ROOT / "src"
EXPERIMENT_DIRECTORY = TUTORIAL_ROOT / "experiments"
EXPERIMENTS = [
    "kinematics_schematic.py",
    "growth_tensor_atlas.py",
    "determinant_bookkeeping.py",
    "free_constrained_growth.py",
    "frame_indifference.py",
    "decomposition_nonuniqueness.py",
    "stress_relaxation.py",
    "growth_law_sweep.py",
    "anisotropic_growth.py",
    "noncommutative_paths.py",
    "incompatibility_map.py",
    "differential_growth_strip.py",
    "direction_pushforward.py",
    "benchmark_summary.py",
    "relaxation_animation.py",
]


def main() -> None:
    for directory in (SOURCE_DIRECTORY, EXPERIMENT_DIRECTORY):
        if str(directory) not in sys.path:
            sys.path.insert(0, str(directory))
    for script_name in EXPERIMENTS:
        script = EXPERIMENT_DIRECTORY / script_name
        print(f"Running {script.relative_to(REPOSITORY_ROOT)}", flush=True)
        runpy.run_path(str(script), run_name="__main__")
    print("Tutorial 07 results regenerated successfully.", flush=True)


if __name__ == "__main__":
    main()
