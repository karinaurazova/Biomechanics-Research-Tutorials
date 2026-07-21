"""Shared paths for Tutorial 18 experiments."""

from pathlib import Path
import sys

TUTORIAL_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = TUTORIAL_ROOT.parents[1]
SOURCE_DIRECTORY = REPOSITORY_ROOT / "src"
if str(SOURCE_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIRECTORY))

FIGURES = TUTORIAL_ROOT / "figures"
DATA = TUTORIAL_ROOT / "data"
ANIMATIONS = TUTORIAL_ROOT / "animations"
for directory in (FIGURES, DATA, ANIMATIONS):
    directory.mkdir(parents=True, exist_ok=True)
