"""Regenerate every committed result for Tutorial 01."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys


TUTORIAL_ROOT = Path(__file__).resolve().parent
REPOSITORY_ROOT = TUTORIAL_ROOT.parents[1]
EXPERIMENTS = [
    "baseline.py",
    "analytical_verification.py",
    "parameter_sweep.py",
    "adaptation_time.py",
    "changing_load.py",
    "orthogonal_case.py",
    "fiber_population_animation.py",
]


def main() -> None:
    """Run all Tutorial 01 experiment scripts with the active Python interpreter."""
    environment = os.environ.copy()
    source_directory = str(REPOSITORY_ROOT / "src")
    current_pythonpath = environment.get("PYTHONPATH", "")
    environment["PYTHONPATH"] = os.pathsep.join(
        item for item in [source_directory, current_pythonpath] if item
    )

    for script_name in EXPERIMENTS:
        script = TUTORIAL_ROOT / "experiments" / script_name
        print(f"Running {script.relative_to(REPOSITORY_ROOT)}")
        subprocess.run(
            [sys.executable, str(script)],
            check=True,
            cwd=REPOSITORY_ROOT,
            env=environment,
        )

    print("Tutorial 01 results regenerated successfully.")


if __name__ == "__main__":
    main()
