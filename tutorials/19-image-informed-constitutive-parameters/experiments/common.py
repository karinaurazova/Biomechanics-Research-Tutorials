from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / 'src'
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

TUTORIAL = Path(__file__).resolve().parents[1]
DATA = TUTORIAL / 'data'
FIGURES = TUTORIAL / 'figures'
DATA.mkdir(exist_ok=True)
FIGURES.mkdir(exist_ok=True)


def write_rows(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError('No rows to write.')
    keys = list(rows[0].keys())
    with path.open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)
