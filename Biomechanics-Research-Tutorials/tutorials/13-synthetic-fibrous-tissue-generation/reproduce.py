"""Recreate every Tutorial 13 result in one Python process."""
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
EXPERIMENTS = ROOT / "experiments"
if str(EXPERIMENTS) not in sys.path:
    sys.path.insert(0, str(EXPERIMENTS))

from scenarios import SCENARIOS  # noqa: E402


def main() -> None:
    for name, scenario in SCENARIOS.items():
        print(f"[Tutorial 13] {name}", flush=True)
        scenario()
    print("Tutorial 13 results regenerated successfully.")


if __name__ == "__main__":
    main()
