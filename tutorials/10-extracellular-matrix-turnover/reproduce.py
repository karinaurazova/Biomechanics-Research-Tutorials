"""Regenerate every committed result for Tutorial 10 in one Python process."""

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
    "homeostatic_flux_balance",
    "survival_models",
    "age_structured_cohorts",
    "cohort_vs_homogenized",
    "stress_regulated_synthesis",
    "mmp_timp_balance",
    "collagen_maturation",
    "crosslink_mechanics",
    "deposition_stretch",
    "pulse_chase",
    "overload_adaptation",
    "transient_inflammation",
    "pathology_modes",
    "multicomponent_ecm",
    "spatial_degradation_front",
    "mechanics_coupling",
    "identifiability",
    "observability_map",
    "benchmark_summary",
    "turnover_animation",
]


def main() -> None:
    os.environ.setdefault("MPLBACKEND", "Agg")
    for directory in (SOURCE_DIRECTORY, EXPERIMENT_DIRECTORY):
        if str(directory) not in sys.path:
            sys.path.insert(0, str(directory))

    from scenarios import render_scenario

    for name in SCENARIOS:
        render_scenario(name)
        print(f"Completed Tutorial 10 scenario: {name}", flush=True)

    print("Tutorial 10 results regenerated successfully.", flush=True)


if __name__ == "__main__":
    main()
