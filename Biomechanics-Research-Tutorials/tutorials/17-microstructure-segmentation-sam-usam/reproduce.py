"""Recreate every Tutorial 17 synthetic segmentation result."""
from __future__ import annotations
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
from microstructure_segmentation import reproduce

if __name__ == "__main__":
    rows = reproduce(ROOT)
    print(f"Tutorial 17 results regenerated successfully: {len(rows)} methods evaluated.")
