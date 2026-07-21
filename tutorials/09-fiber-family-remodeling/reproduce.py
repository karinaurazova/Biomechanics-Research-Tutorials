"""Regenerate every committed result for Tutorial 09 in one Python process."""

from __future__ import annotations

import os
from pathlib import Path
import sys

TUTORIAL_ROOT = Path(__file__).resolve().parent
REPOSITORY_ROOT = TUTORIAL_ROOT.parents[1]
SOURCE_DIRECTORY = REPOSITORY_ROOT / "src"
EXPERIMENT_DIRECTORY = TUTORIAL_ROOT / "experiments"
SCENARIOS = [
    "modeling_taxonomy",
    "discrete_reorientation",
    "cue_degeneracy",
    "loading_switch",
    "odf_evolution",
    "alignment_diffusion_map",
    "dispersion_metrics",
    "discrete_continuous",
    "lanir_goh_comparison",
    "two_family_response",
    "recruitment_crimp",
    "turnover_replacement",
    "direct_vs_turnover",
    "deposition_stretch",
    "family_competition",
    "identifiability",
    "biology_model_map",
    "benchmark_summary",
    "odf_animation",
]


def main() -> None:
    os.environ.setdefault("MPLBACKEND", "Agg")
    for directory in (SOURCE_DIRECTORY, EXPERIMENT_DIRECTORY):
        if str(directory) not in sys.path:
            sys.path.insert(0, str(directory))

    from scenarios import render_scenario

    for name in SCENARIOS:
        render_scenario(name)
        print(f"Completed Tutorial 09 scenario: {name}", flush=True)

    print("Tutorial 09 results regenerated successfully.", flush=True)


if __name__ == "__main__":
    main()
