"""Shared helpers for Tutorial 05 experiments."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import Normalize

from biomechanics_tutorials.plotting import apply_tutorial_style

TUTORIAL_ROOT = Path(__file__).resolve().parents[1]
FIGURE_DIRECTORY = TUTORIAL_ROOT / "figures"
ANIMATION_DIRECTORY = TUTORIAL_ROOT / "animations"
DATA_DIRECTORY = TUTORIAL_ROOT / "data"

TEXT = {
    "image": {"en": "Synthetic image", "ru": "Синтетическое изображение"},
    "truth": {"en": "True orientation", "ru": "Истинная ориентация"},
    "estimate": {"en": "Estimated orientation", "ru": "Оценённая ориентация"},
    "coherence": {"en": "Coherence", "ru": "Когерентность"},
    "energy": {"en": "Tensor energy", "ru": "Энергия тензора"},
    "error": {"en": "Axial error, degrees", "ru": "Осевая ошибка, градусы"},
    "angle": {"en": "Orientation, degrees", "ru": "Ориентация, градусы"},
    "known_angle": {"en": "Known angle, degrees", "ru": "Заданный угол, градусы"},
    "estimated_angle": {"en": "Estimated angle, degrees", "ru": "Оценённый угол, градусы"},
    "noise": {"en": "Noise standard deviation", "ru": "Стандартное отклонение шума"},
    "scale": {"en": "Integration scale σᵢ", "ru": "Интеграционный масштаб σᵢ"},
    "threshold": {"en": "Coherence threshold", "ru": "Порог когерентности"},
    "coverage": {"en": "Accepted-pixel coverage", "ru": "Доля принятых пикселей"},
    "density": {"en": "Axial density", "ru": "Осевая плотность"},
    "distance": {"en": "Distance from image boundary, pixels", "ru": "Расстояние от края, пиксели"},
    "mae": {"en": "Mean absolute error, degrees", "ru": "Средняя абсолютная ошибка, градусы"},
    "gradient": {"en": "Gradient magnitude", "ru": "Модуль градиента"},
    "mask": {"en": "Confidence mask", "ru": "Маска доверия"},
}

TITLES = {
    "synthetic_gallery": {
        "en": "Synthetic fiber fields with known orientation",
        "ru": "Синтетические волокнистые поля с известной ориентацией",
    },
    "pipeline_steps": {
        "en": "From image gradients to local fiber orientation",
        "ru": "От градиентов изображения к локальной ориентации волокон",
    },
    "known_angle_benchmark": {
        "en": "Verification over the full axial-angle range",
        "ru": "Верификация на полном диапазоне осевых углов",
    },
    "noise_scale_map": {
        "en": "Noise–scale trade-off in orientation error",
        "ru": "Компромисс шум–масштаб в ошибке ориентации",
    },
    "coherence_threshold": {
        "en": "Confidence threshold trades coverage for accuracy",
        "ru": "Порог доверия меняет баланс покрытия и точности",
    },
    "curved_field": {
        "en": "Curved fibers: local orientation and error",
        "ru": "Криволинейные волокна: локальная ориентация и ошибка",
    },
    "piecewise_domains": {
        "en": "Integration scale blurs a sharp orientation boundary",
        "ru": "Интеграционный масштаб размывает резкую границу ориентаций",
    },
    "crossing_failure": {
        "en": "A single structure tensor cannot resolve two crossing families",
        "ru": "Один тензор структуры не разрешает два пересекающихся семейства",
    },
    "orientation_statistics": {
        "en": "Local estimates become axial orientation statistics",
        "ru": "Локальные оценки формируют осевую статистику ориентаций",
    },
    "illumination_robustness": {
        "en": "Uneven illumination and background normalization",
        "ru": "Неравномерное освещение и нормировка фона",
    },
    "boundary_artifacts": {
        "en": "Boundary effects motivate explicit border exclusion",
        "ru": "Краевые эффекты требуют явного исключения границы",
    },
    "benchmark_summary": {
        "en": "Synthetic verification benchmark",
        "ru": "Синтетический верификационный benchmark",
    },
}


def tr(key: str, language: str) -> str:
    return TEXT[key][language]


def title(key: str, language: str) -> str:
    return TITLES[key][language]


def save_figure(fig: plt.Figure, stem: str, language: str) -> Path:
    apply_tutorial_style()
    suffix = "" if language == "en" else "_ru"
    path = FIGURE_DIRECTORY / f"{stem}{suffix}.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return path


def orientation_image(ax, orientation: np.ndarray, title_text: str, mask=None):
    degrees = np.rad2deg(orientation)
    if mask is not None:
        degrees = np.where(mask, degrees, np.nan)
    image = ax.imshow(degrees, cmap="twilight", norm=Normalize(-90, 90), origin="upper")
    ax.set_title(title_text)
    ax.set_xticks([])
    ax.set_yticks([])
    return image


def add_orientation_colorbar(fig, image, ax, language: str):
    colorbar = fig.colorbar(image, ax=ax, shrink=0.84)
    colorbar.set_label(tr("angle", language))
