"""Regenerate every committed result for Tutorial 02."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys


TUTORIAL_ROOT = Path(__file__).resolve().parent
REPOSITORY_ROOT = TUTORIAL_ROOT.parents[1]
EXPERIMENTS = [
    "baseline.py",
    "distribution_gallery.py",
    "tensor_verification.py",
    "aligned_response.py",
    "oblique_response.py",
    "anisotropy_map.py",
    "quadrature_convergence.py",
    "population_animation.py",
]


def main() -> None:
    """Run all Tutorial 02 experiment scripts with the active Python interpreter."""
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

    print("Tutorial 02 results regenerated successfully.")


if __name__ == "__main__":
    main()
