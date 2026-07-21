"""Shared paths, labels, and style for Tutorial 10 experiments."""

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

from biomechanics_tutorials.plotting import PALETTE, apply_tutorial_style  # noqa: E402

__all__ = ["ANIMATION_DIRECTORY", "DATA_DIRECTORY", "FIGURE_DIRECTORY", "PALETTE", "TEXT", "save_figure"]

apply_tutorial_style()
FIGURE_DIRECTORY.mkdir(exist_ok=True)
ANIMATION_DIRECTORY.mkdir(exist_ok=True)
DATA_DIRECTORY.mkdir(exist_ok=True)

TEXT = {
    "en": {
        "time": "Time (synthetic units)",
        "mass": "Normalized mass",
        "stress": "Normalized stress",
        "age": "Cohort age",
        "stiffness": "Effective stiffness",
        "production": "Production",
        "removal": "Removal",
        "collagen": "Collagen",
        "enzyme": "Enzyme activity",
        "stretch": "Stretch",
        "position": "Position",
        "error": "Relative error",
    },
    "ru": {
        "time": "Время (условные единицы)",
        "mass": "Нормированная масса",
        "stress": "Нормированное напряжение",
        "age": "Возраст когорты",
        "stiffness": "Эффективная жёсткость",
        "production": "Синтез",
        "removal": "Удаление",
        "collagen": "Коллаген",
        "enzyme": "Ферментативная активность",
        "stretch": "Удлинение",
        "position": "Координата",
        "error": "Относительная ошибка",
    },
}


def save_figure(fig: plt.Figure, stem: str, language: str) -> None:
    suffix = "" if language == "en" else "_ru"
    fig.savefig(FIGURE_DIRECTORY / f"{stem}{suffix}.png", dpi=170)
    plt.close(fig)
