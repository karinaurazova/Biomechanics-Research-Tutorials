"""Shared paths, labels, and visual helpers for Tutorial 12."""
from __future__ import annotations

from pathlib import Path
import sys

import matplotlib.pyplot as plt

TUTORIAL_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = TUTORIAL_ROOT.parents[1]
SOURCE_DIRECTORY = REPOSITORY_ROOT / "src"
FIGURE_DIRECTORY = TUTORIAL_ROOT / "figures"
ANIMATION_DIRECTORY = TUTORIAL_ROOT / "animations"
DATA_DIRECTORY = TUTORIAL_ROOT / "data"
if str(SOURCE_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIRECTORY))

from biomechanics_tutorials.plotting import apply_tutorial_style  # noqa: E402

apply_tutorial_style()
for directory in (FIGURE_DIRECTORY, ANIMATION_DIRECTORY, DATA_DIRECTORY):
    directory.mkdir(parents=True, exist_ok=True)

TEXT = {
    "en": {
        "radius": "Current radius",
        "normalized_radius": "Normalized wall coordinate",
        "stress": "Cauchy stress (synthetic units)",
        "angle": "Opening angle, degrees",
        "pressure": "Pressure (synthetic units)",
        "stretch": "Stretch",
        "time": "Time (synthetic units)",
        "curvature": "Released curvature",
        "error": "Relative error",
    },
    "ru": {
        "radius": "Текущий радиус",
        "normalized_radius": "Нормированная координата по толщине",
        "stress": "Напряжение Коши (условные единицы)",
        "angle": "Угол раскрытия, градусы",
        "pressure": "Давление (условные единицы)",
        "stretch": "Растяжение",
        "time": "Время (условные единицы)",
        "curvature": "Кривизна после высвобождения",
        "error": "Относительная ошибка",
    },
}


def t(language: str, en: str, ru: str) -> str:
    return en if language == "en" else ru


def save_figure(fig: plt.Figure, stem: str, language: str) -> None:
    suffix = "" if language == "en" else "_ru"
    fig.savefig(FIGURE_DIRECTORY / f"{stem}{suffix}.png", dpi=170)
    plt.close(fig)
