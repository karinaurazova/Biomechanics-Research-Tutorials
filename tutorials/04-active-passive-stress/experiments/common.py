"""Shared plotting helpers for Tutorial 04 experiments."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

from biomechanics_tutorials.plotting import apply_tutorial_style

TUTORIAL_ROOT = Path(__file__).resolve().parents[1]
FIGURE_DIRECTORY = TUTORIAL_ROOT / "figures"
ANIMATION_DIRECTORY = TUTORIAL_ROOT / "animations"

LABELS = {
    "time": {"en": "Time", "ru": "Время"},
    "activation": {"en": "Activation", "ru": "Активация"},
    "stretch": {"en": "Fiber stretch λ", "ru": "Растяжение волокна λ"},
    "velocity": {"en": "Shortening velocity", "ru": "Скорость укорочения"},
    "multiplier": {"en": "Dimensionless multiplier", "ru": "Безразмерный множитель"},
    "stress": {"en": "Nominal stress", "ru": "Номинальное напряжение"},
    "shear": {"en": "Shear amount γ", "ru": "Величина сдвига γ"},
    "response": {"en": "Generalized shear response", "ru": "Обобщённый сдвиговый отклик"},
    "calcium": {"en": "Normalized calcium", "ru": "Нормированный кальций"},
    "bound": {"en": "Bound cross-bridge fraction", "ru": "Доля связанных мостиков"},
    "afterload": {"en": "Afterload", "ru": "Постнагрузка"},
}

TITLES = {
    "activation_waveforms": {
        "en": "Synthetic activation waveforms",
        "ru": "Синтетические функции активации",
    },
    "force_length_velocity": {
        "en": "Force-length and force-velocity relations",
        "ru": "Соотношения сила–длина и сила–скорость",
    },
    "stress_decomposition": {
        "en": "Passive, active, and total stress",
        "ru": "Пассивное, активное и полное напряжение",
    },
    "preload_dependence": {
        "en": "Preload-dependent twitch response",
        "ru": "Зависимость сокращения от преднагрузки",
    },
    "isometric_twitches": {"en": "Isometric twitches", "ru": "Изометрические сокращения"},
    "isotonic_afterload": {
        "en": "Isotonic shortening under different afterloads",
        "ru": "Изотоническое укорочение при разных постнагрузках",
    },
    "active_approaches_uniaxial": {
        "en": "Active stress and active strain: uniaxial calibration",
        "ru": "Active stress и active strain: одноосная калибровка",
    },
    "active_approaches_shear": {
        "en": "Active stress and active strain: shear divergence",
        "ru": "Active stress и active strain: расхождение при сдвиге",
    },
    "active_strain_kinematics": {
        "en": "Volume-preserving active-strain kinematics",
        "ru": "Объёмосохраняющая кинематика active strain",
    },
    "calcium_crossbridge": {
        "en": "Calcium and cross-bridge dynamics",
        "ru": "Динамика кальция и кросс-мостиков",
    },
    "transverse_activation": {
        "en": "Effect of transverse active stress",
        "ru": "Влияние поперечного активного напряжения",
    },
    "activation_stretch_map": {
        "en": "Activation–stretch map of total stress",
        "ru": "Карта полного напряжения: активация–растяжение",
    },
}


def tr(key: str, language: str) -> str:
    return LABELS[key][language]


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
