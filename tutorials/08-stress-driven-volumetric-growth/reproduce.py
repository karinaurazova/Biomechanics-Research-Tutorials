"""Regenerate every committed result for Tutorial 08.

Independent plotting scenarios are executed in a small process pool.  Every
script writes distinct English/Russian files, so parallel execution is safe and
reduces backend startup overhead on CI and teaching workstations.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
import os
from pathlib import Path
import subprocess
import sys

TUTORIAL_ROOT = Path(__file__).resolve().parent
REPOSITORY_ROOT = TUTORIAL_ROOT.parents[1]
SOURCE_DIRECTORY = REPOSITORY_ROOT / "src"
EXPERIMENT_DIRECTORY = TUTORIAL_ROOT / "experiments"
EXPERIMENTS = [
    "feedback_architecture.py",
    "stimulus_measures.py",
    "homeostatic_surface.py",
    "fixed_deformation_relaxation.py",
    "boundary_control.py",
    "load_protocols.py",
    "growth_resorption.py",
    "dead_zone_saturation.py",
    "hydrostatic_deviatoric.py",
    "mass_density.py",
    "time_integration.py",
    "gain_stability.py",
    "spatial_heterogeneity.py",
    "regularization.py",
    "identifiability.py",
    "benchmark_summary.py",
    "relaxation_animation.py",
]


def _run_script(script_name: str, environment: dict[str, str]) -> str:
    script = EXPERIMENT_DIRECTORY / script_name
    subprocess.run(
        [sys.executable, str(script)],
        cwd=REPOSITORY_ROOT,
        env=environment,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return script_name


def main() -> None:
    environment = os.environ.copy()
    python_paths = [str(SOURCE_DIRECTORY), str(EXPERIMENT_DIRECTORY)]
    if environment.get("PYTHONPATH"):
        python_paths.append(environment["PYTHONPATH"])
    environment["PYTHONPATH"] = os.pathsep.join(python_paths)
    environment.setdefault("MPLBACKEND", "Agg")

    completed: list[str] = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(_run_script, name, environment): name for name in EXPERIMENTS
        }
        for future in as_completed(futures):
            name = futures[future]
            try:
                completed.append(future.result())
                print(f"Completed Tutorial 08 scenario: {name}", flush=True)
            except subprocess.CalledProcessError as error:
                if error.stdout:
                    print(error.stdout, file=sys.stderr)
                if error.stderr:
                    print(error.stderr, file=sys.stderr)
                raise

    if sorted(completed) != sorted(EXPERIMENTS):
        raise RuntimeError("Not all Tutorial 08 scenarios completed")
    print("Tutorial 08 results regenerated successfully.", flush=True)


if __name__ == "__main__":
    main()
