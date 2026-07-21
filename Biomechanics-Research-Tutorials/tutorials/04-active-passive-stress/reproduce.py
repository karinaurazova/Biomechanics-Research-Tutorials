"""Regenerate every committed result for Tutorial 04."""

from __future__ import annotations
from pathlib import Path
import runpy
import sys

TUTORIAL_ROOT = Path(__file__).resolve().parent
REPOSITORY_ROOT = TUTORIAL_ROOT.parents[1]
SOURCE_DIRECTORY = REPOSITORY_ROOT / "src"
EXPERIMENT_DIRECTORY = TUTORIAL_ROOT / "experiments"
EXPERIMENTS = [
    "activation_waveforms.py",
    "force_length_velocity.py",
    "stress_decomposition.py",
    "preload_dependence.py",
    "isometric_twitches.py",
    "isotonic_afterload.py",
    "active_approaches_uniaxial.py",
    "active_approaches_shear.py",
    "active_strain_kinematics.py",
    "calcium_crossbridge.py",
    "transverse_activation.py",
    "activation_stretch_map.py",
    "active_twitch_animation.py",
]


def main():
    for directory in (SOURCE_DIRECTORY, EXPERIMENT_DIRECTORY):
        if str(directory) not in sys.path:
            sys.path.insert(0, str(directory))
    for script_name in EXPERIMENTS:
        script = EXPERIMENT_DIRECTORY / script_name
        print(f"Running {script.relative_to(REPOSITORY_ROOT)}", flush=True)
        runpy.run_path(str(script), run_name="__main__")
    print("Tutorial 04 results regenerated successfully.", flush=True)


if __name__ == "__main__":
    main()
