"""Recreate every Tutorial 19 result in one Python process."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
EXPERIMENTS = ROOT / 'experiments'
if str(EXPERIMENTS) not in sys.path:
    sys.path.insert(0, str(EXPERIMENTS))

from constitutive_identification import main as calibration_main  # noqa: E402
from parameter_sweep import main as sweep_main  # noqa: E402


def main() -> None:
    calibration_main()
    sweep_main()
    print('Tutorial 19 results regenerated successfully.')


if __name__ == '__main__':
    main()
