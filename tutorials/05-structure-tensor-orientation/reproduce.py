"""Regenerate every committed result for Tutorial 05."""

from __future__ import annotations

from pathlib import Path
import runpy
import sys

TUTORIAL_ROOT = Path(__file__).resolve().parent
REPOSITORY_ROOT = TUTORIAL_ROOT.parents[1]
SOURCE_DIRECTORY = REPOSITORY_ROOT / "src"
EXPERIMENT_DIRECTORY = TUTORIAL_ROOT / "experiments"
EXPERIMENTS = [
    "synthetic_gallery.py",
    "pipeline_steps.py",
    "known_angle_benchmark.py",
    "noise_scale_map.py",
    "coherence_threshold.py",
    "curved_field.py",
    "piecewise_domains.py",
    "crossing_failure.py",
    "orientation_statistics.py",
    "illumination_robustness.py",
    "boundary_artifacts.py",
    "benchmark_summary.py",
    "integration_scale_animation.py",
]


def main() -> None:
    for directory in (SOURCE_DIRECTORY, EXPERIMENT_DIRECTORY):
        if str(directory) not in sys.path:
            sys.path.insert(0, str(directory))
    for script_name in EXPERIMENTS:
        script = EXPERIMENT_DIRECTORY / script_name
        print(f"Running {script.relative_to(REPOSITORY_ROOT)}", flush=True)
        runpy.run_path(str(script), run_name="__main__")
    print("Tutorial 05 results regenerated successfully.", flush=True)


if __name__ == "__main__":
    main()
