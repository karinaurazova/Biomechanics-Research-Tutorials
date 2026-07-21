"""Regenerate every committed result for Tutorial 06."""

from __future__ import annotations

from pathlib import Path
import runpy
import sys

TUTORIAL_ROOT = Path(__file__).resolve().parent
REPOSITORY_ROOT = TUTORIAL_ROOT.parents[1]
SOURCE_DIRECTORY = REPOSITORY_ROOT / "src"
EXPERIMENT_DIRECTORY = TUTORIAL_ROOT / "experiments"
EXPERIMENTS = [
    "feedback_loop.py",
    "analytical_verification.py",
    "disturbance_protocols.py",
    "rate_sweep.py",
    "nonlinear_feedback.py",
    "sensing_noise.py",
    "bias_allostasis.py",
    "delay_stability_map.py",
    "maladaptation_modes.py",
    "turnover_balance.py",
    "constituent_turnover.py",
    "vessel_adaptation.py",
    "vessel_state_space.py",
    "benchmark_summary.py",
    "recovery_animation.py",
]


def main() -> None:
    for directory in (SOURCE_DIRECTORY, EXPERIMENT_DIRECTORY):
        if str(directory) not in sys.path:
            sys.path.insert(0, str(directory))
    for script_name in EXPERIMENTS:
        script = EXPERIMENT_DIRECTORY / script_name
        print(f"Running {script.relative_to(REPOSITORY_ROOT)}", flush=True)
        runpy.run_path(str(script), run_name="__main__")
    print("Tutorial 06 results regenerated successfully.", flush=True)


if __name__ == "__main__":
    main()
