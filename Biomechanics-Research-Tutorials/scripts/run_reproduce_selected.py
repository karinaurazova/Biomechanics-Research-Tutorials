#!/usr/bin/env python3
"""Run selected tutorial reproduction scripts without committing to a full slow suite."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TUTORIALS = ROOT / "tutorials"
DEFAULT_NUMBERS = [1, 5, 13, 20, 25]


def find_tutorial(number: int) -> Path:
    matches = sorted(TUTORIALS.glob(f"{number:02d}-*"))
    if not matches:
        raise FileNotFoundError(f"Tutorial {number:02d} not found")
    return matches[0]


def parse_numbers(positional: list[int], flagged: list[int] | None) -> list[int]:
    if flagged:
        return flagged
    if positional:
        return positional
    return DEFAULT_NUMBERS


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("numbers", nargs="*", type=int, help="Tutorial numbers, for example: 1 13 17 25")
    parser.add_argument("--tutorials", nargs="+", type=int, help="Same as positional numbers; kept for README readability.")
    args = parser.parse_args()
    for n in parse_numbers(args.numbers, args.tutorials):
        tutorial = find_tutorial(n)
        script = tutorial / "reproduce.py"
        print(f"\n=== Tutorial {n:02d}: {tutorial.name} ===")
        if not script.exists():
            print(f"Missing {script}")
            return 1
        result = subprocess.run([sys.executable, str(script)], cwd=ROOT)
        if result.returncode != 0:
            return result.returncode
    print("\nSelected reproductions completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
