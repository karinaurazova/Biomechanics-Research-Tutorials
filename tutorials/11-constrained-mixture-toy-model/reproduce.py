"""Regenerate every committed result for Tutorial 11 in one Python process."""

from __future__ import annotations
import os
from pathlib import Path
import sys

TUTORIAL_ROOT = Path(__file__).resolve().parent
REPOSITORY_ROOT = TUTORIAL_ROOT.parents[1]
for directory in (REPOSITORY_ROOT / "src", TUTORIAL_ROOT / "experiments"):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))
os.environ.setdefault("MPLBACKEND", "Agg")
SCENARIOS = [
    "model_taxonomy",
    "mixture_architecture",
    "homeostatic_initialization",
    "cohort_survival",
    "deposition_stretch",
    "stress_decomposition",
    "pressure_overload",
    "volume_overload",
    "overload_comparison",
    "reversal",
    "fibrosis_hypertrophy",
    "collagen_degradation",
    "history_dependence",
    "cohort_vs_homogenized",
    "history_truncation",
    "stability_map",
    "half_life_sensitivity",
    "polarimetry_bridge",
    "observability_map",
    "identifiability",
    "benchmark_summary",
    "cohort_animation",
]


def main():
    from scenarios import render_scenario

    for name in SCENARIOS:
        render_scenario(name)
        print(f"Completed Tutorial 11 scenario: {name}", flush=True)
    print("Tutorial 11 results regenerated successfully.", flush=True)


if __name__ == "__main__":
    main()
