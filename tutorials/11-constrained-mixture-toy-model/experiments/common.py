"""Shared paths, labels, and style for Tutorial 11 experiments."""
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
    directory.mkdir(exist_ok=True)
TEXT = {
    "en": {"time":"Time (synthetic units)","mass":"Normalized mass","stress":"Nominal stress",
           "stretch":"Stretch","error":"Relative error","age":"Cohort age","fraction":"Mass fraction"},
    "ru": {"time":"Время (условные единицы)","mass":"Нормированная масса","stress":"Номинальное напряжение",
           "stretch":"Удлинение","error":"Относительная ошибка","age":"Возраст когорты","fraction":"Массовая доля"},
}
def save_figure(fig: plt.Figure, stem: str, language: str) -> None:
    suffix = "" if language == "en" else "_ru"
    fig.savefig(FIGURE_DIRECTORY / f"{stem}{suffix}.png", dpi=165, bbox_inches="tight")
    plt.close(fig)
