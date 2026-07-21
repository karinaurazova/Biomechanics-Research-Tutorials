"""Shared visual style and layout safeguards for the tutorial series."""

from __future__ import annotations

import math
import textwrap
from typing import Iterable

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.text import Text
from pathlib import Path

PALETTE = {
    "ink": "#0B1220",
    "blue": "#175CFF",
    "cyan": "#26C6DA",
    "mint": "#BFEFE1",
    "lime": "#B8F24A",
    "ice": "#F4FBFA",
    "slate": "#637083",
}

_PATCHED = False
_ORIGINAL_SAVEFIG = Figure.savefig


_RU_REPLACEMENTS = {
    "Active stress": "Активное напряжение",
    "active stress": "активное напряжение",
    "Active strain": "Активная деформация",
    "active strain": "активная деформация",
    "Deposition stretch": "Предрастяжение при отложении",
    "deposition stretch": "предрастяжение при отложении",
    "Pressure-like": "Поперечно-доминирующий режим",
    "pressure-like": "поперечно-доминирующий режим",
    "Volume-like": "Продольно-доминирующий режим",
    "volume-like": "продольно-доминирующий режим",
    "Raw MAE": "Исходная MAE",
    "Normalized MAE": "Нормированная MAE",
    "PASS": "ПРОЙДЕНО",
    "FAIL": "НЕ ПРОЙДЕНО",
    "Elastin": "Эластин",
    "Collagen I": "Коллаген I",
    "Collagen III": "Коллаген III",
    "Collagen": "Коллаген",
    "Proteoglycan": "Протеогликан",
    "Matrix": "Матрикс",
    "cardiomyocytes": "основные волокна / клетки",
    "Cardiomyocytes": "Основные волокна / клетки",
    "myocyte": "основное семейство",
    "Full-history": "Полная история",
    "Homogenized": "Гомогенизированная модель",
    "Kinematic growth": "Кинематический рост",
    "ODE mass": "ОДУ для массы",
    "ODE maturation": "ОДУ созревания",
    "Cohort history": "История когорт",
    "Spatial cohorts": "Пространственные когорты",
    "Young cohort": "Молодая когорта",
    "Old cohort": "Старая когорта",
    "Production": "Производство",
    "Removal": "Удаление",
    "Survival": "Выживание",
    "Turnover": "Обновление",
    "turnover": "обновление",
    "Fiber family": "Семейство волокон",
    "Ground-truth": "Точное",
    "ground-truth": "точное",
    "ground truth": "точное решение",
    "Reference image": "Исходное изображение",
    "Reference": "Исходное",
    "Deformed image": "Деформированное изображение",
    "Deformed": "Деформированное",
    "Recovered": "Восстановленное",
    "Vector error": "Векторная ошибка",
    "Normalized score": "Нормированный показатель",
    "log10 loss": "log10 функции потерь",
}


def _localize_russian_text(fig: Figure) -> None:
    """Translate common leftover English labels in Russian renderings.

    This is a final safety net. Scenario files should still provide explicit
    localized text when a phrase has a context-dependent meaning.
    """
    for artist in fig.findobj(match=Text):
        value = artist.get_text()
        if not value:
            continue
        translated = value
        for source, target in _RU_REPLACEMENTS.items():
            translated = translated.replace(source, target)
        if translated != value:
            artist.set_text(translated)


def _wrapped(text: str, width: int) -> str:
    """Wrap long human-facing text while preserving explicit line breaks."""
    if not text or len(text) <= width:
        return text
    return "\n".join(
        textwrap.fill(part, width=width, break_long_words=False, break_on_hyphens=False)
        for part in text.split("\n")
    )


def _iter_visible_ticklabels(axis) -> Iterable:
    return (label for label in axis.get_ticklabels() if label.get_visible())


def finalize_figure(fig: Figure) -> None:
    """Apply conservative layout fixes before a figure is written to disk.

    The function intentionally avoids changing scientific content. It wraps long
    titles, reduces crowded legend typography, rotates long categorical labels,
    and adds enough padding to prevent clipping in bilingual figures.
    """
    if getattr(fig, "_bmrt_finalized", False):
        return

    axes = [axis for axis in fig.axes if hasattr(axis, "get_title")]
    for axis in axes:
        title = axis.get_title()
        if title:
            axis.set_title(_wrapped(title, 58), pad=10)

        xlabel = axis.get_xlabel()
        ylabel = axis.get_ylabel()
        if xlabel:
            axis.set_xlabel(_wrapped(xlabel, 42), labelpad=7)
        if ylabel:
            axis.set_ylabel(_wrapped(ylabel, 38), labelpad=8)

        xlabels = list(_iter_visible_ticklabels(axis.xaxis))
        xtexts = [label.get_text() for label in xlabels]
        if xtexts and max(map(len, xtexts), default=0) > 12 and len(xtexts) >= 4:
            for label in xlabels:
                label.set_rotation(24)
                label.set_horizontalalignment("right")
                label.set_rotation_mode("anchor")
                label.set_fontsize(min(label.get_fontsize(), 8.5))

        ylabels = list(_iter_visible_ticklabels(axis.yaxis))
        ytexts = [label.get_text() for label in ylabels]
        if ytexts and max(map(len, ytexts), default=0) > 18:
            for label in ylabels:
                label.set_fontsize(min(label.get_fontsize(), 8.5))

        legend = axis.get_legend()
        if legend is not None:
            texts = legend.get_texts()
            labels = [text.get_text() for text in texts]
            count = len(labels)
            longest = max(map(len, labels), default=0)
            fontsize = 9.0 if count <= 4 and longest <= 20 else 8.0
            for text in texts:
                text.set_fontsize(fontsize)
                if len(text.get_text()) > 34:
                    text.set_text(_wrapped(text.get_text(), 30))
            title = legend.get_title()
            if title is not None:
                title.set_fontsize(fontsize)

    if fig._suptitle is not None:
        fig._suptitle.set_text(_wrapped(fig._suptitle.get_text(), 76))
        fig._suptitle.set_fontsize(min(fig._suptitle.get_fontsize(), 15))
        fig._suptitle.set_y(0.995)

    # Increase only genuinely cramped multi-panel canvases.
    width, height = fig.get_size_inches()
    count = max(len(axes), 1)
    if count >= 6:
        width = max(width, 3.25 * min(count, 4))
        height = max(height, 2.55 * math.ceil(count / min(count, 4)))
        fig.set_size_inches(width, height, forward=True)

    try:
        rect = (0.02, 0.02, 0.98, 0.955) if fig._suptitle is not None else (0.02, 0.02, 0.98, 0.98)
        fig.tight_layout(pad=1.35, w_pad=1.0, h_pad=1.15, rect=rect)
    except (RuntimeError, ValueError):
        pass

    fig._bmrt_finalized = True


def _safe_savefig(self: Figure, *args, **kwargs):
    # Animation writers request raw/RGBA frames after fixing the canvas size.
    # Changing layout at that stage would invalidate the frame buffer.
    frame_format = str(kwargs.get("format", "")).lower()
    if frame_format not in {"rgba", "raw"}:
        destination = args[0] if args else kwargs.get("fname", "")
        if "_ru" in Path(str(destination)).stem:
            _localize_russian_text(self)
        finalize_figure(self)
        kwargs.setdefault("bbox_inches", "tight")
        kwargs.setdefault("pad_inches", 0.24)
    return _ORIGINAL_SAVEFIG(self, *args, **kwargs)


def apply_tutorial_style() -> None:
    """Apply the shared visual style and install layout safeguards once."""
    global _PATCHED
    plt.rcParams.update(
        {
            "figure.facecolor": PALETTE["ice"],
            "axes.facecolor": "#FFFFFF",
            "axes.edgecolor": PALETTE["slate"],
            "axes.labelcolor": PALETTE["ink"],
            "axes.titlecolor": PALETTE["ink"],
            "axes.grid": True,
            "grid.alpha": 0.18,
            "grid.linewidth": 0.8,
            "text.color": PALETTE["ink"],
            "xtick.color": PALETTE["slate"],
            "ytick.color": PALETTE["slate"],
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "legend.frameon": False,
            "legend.fontsize": 9,
            "font.size": 10.5,
            "axes.titlesize": 13,
            "axes.labelsize": 10.5,
            "axes.titlepad": 10,
            "figure.dpi": 120,
            "savefig.facecolor": PALETTE["ice"],
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.24,
        }
    )
    if not _PATCHED:
        Figure.savefig = _safe_savefig
        _PATCHED = True
