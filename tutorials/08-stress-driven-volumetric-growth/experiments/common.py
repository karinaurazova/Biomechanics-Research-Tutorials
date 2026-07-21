"""Shared localization and plotting helpers for Tutorial 08."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

from biomechanics_tutorials.plotting import PALETTE, apply_tutorial_style

TUTORIAL_ROOT = Path(__file__).resolve().parents[1]
FIGURE_DIRECTORY = TUTORIAL_ROOT / "figures"
ANIMATION_DIRECTORY = TUTORIAL_ROOT / "animations"
DATA_DIRECTORY = TUTORIAL_ROOT / "data"

TEXT = {
    "time": {"en": "Time", "ru": "Время"},
    "stimulus": {"en": "Growth stimulus", "ru": "Стимул роста"},
    "error": {"en": "Normalized homeostatic error", "ru": "Нормированная гомеостатическая ошибка"},
    "jg": {"en": "Growth volume ratio Jg", "ru": "Объёмный коэффициент роста Jg"},
    "stretch": {"en": "Stretch", "ru": "Растяжение"},
    "stress": {"en": "Stress", "ru": "Напряжение"},
    "mean_stress": {"en": "Mean stress", "ru": "Среднее напряжение"},
    "von_mises": {"en": "Von Mises stress", "ru": "Напряжение Мизеса"},
    "rate": {"en": "Growth rate", "ru": "Скорость роста"},
    "position": {"en": "Material coordinate", "ru": "Материальная координата"},
    "density": {"en": "Density ratio", "ru": "Отношение плотностей"},
    "mass": {"en": "Mass ratio", "ru": "Отношение масс"},
    "rmse": {"en": "Trajectory RMSE", "ru": "RMSE траектории"},
    "target": {"en": "Homeostatic target", "ru": "Гомеостатическая цель"},
    "gain": {"en": "Adaptation gain", "ru": "Коэффициент адаптации"},
    "dt": {"en": "Time step", "ru": "Шаг по времени"},
}

TITLES = {
    "feedback_architecture": {
        "en": "Stress-driven volumetric growth is a closed constitutive feedback loop",
        "ru": "Объёмный рост, управляемый напряжением, является замкнутой определяющей обратной связью",
    },
    "stimulus_measures": {
        "en": "Different stress measures define different biological signals",
        "ru": "Разные меры напряжения задают разные биологические сигналы",
    },
    "homeostatic_surface": {
        "en": "A homeostatic surface is not the same as a single target number",
        "ru": "Гомеостатическая поверхность не сводится к одному целевому числу",
    },
    "fixed_deformation_relaxation": {
        "en": "Volumetric growth relaxes hydrostatic stress under fixed deformation",
        "ru": "Объёмный рост релаксирует гидростатическое напряжение при фиксированной деформации",
    },
    "boundary_control": {
        "en": "Displacement control and stress control produce opposite interpretations",
        "ru": "Управление перемещением и напряжением приводит к разным интерпретациям",
    },
    "load_protocols": {
        "en": "The growth trajectory depends on the complete loading history",
        "ru": "Траектория роста зависит от полной истории нагружения",
    },
    "growth_resorption": {
        "en": "Growth and resorption need not have symmetric kinetics",
        "ru": "Рост и резорбция не обязаны иметь симметричную кинетику",
    },
    "dead_zone_saturation": {
        "en": "Dead zones, saturation, and bounds shape the long-term response",
        "ru": "Мёртвая зона, насыщение и ограничения формируют долговременный ответ",
    },
    "hydrostatic_deviatoric": {
        "en": "Isotropic growth can remove mean stress while leaving shear distortion",
        "ru": "Изотропный рост может устранить среднее напряжение, сохранив сдвиговую дисторсию",
    },
    "mass_density": {
        "en": "Volume growth, mass addition, and density change are distinct statements",
        "ru": "Объёмный рост, добавление массы и изменение плотности — разные утверждения",
    },
    "time_integration": {
        "en": "Exponential updates preserve positivity; naive Euler updates may not",
        "ru": "Экспоненциальное обновление сохраняет положительность, а наивная схема Эйлера — не всегда",
    },
    "gain_stability": {
        "en": "Adaptation gain and time step jointly control numerical stability",
        "ru": "Коэффициент адаптации и шаг времени совместно определяют численную устойчивость",
    },
    "spatial_heterogeneity": {
        "en": "Heterogeneous homeostatic targets generate heterogeneous growth",
        "ru": "Неоднородные гомеостатические цели формируют неоднородный рост",
    },
    "regularization": {
        "en": "Spatial regularization suppresses localization but broadens transitions",
        "ru": "Пространственная регуляризация подавляет локализацию, но расширяет переходные зоны",
    },
    "identifiability": {
        "en": "Growth rate and homeostatic target can compensate each other",
        "ru": "Скорость роста и гомеостатическая цель могут взаимно компенсироваться",
    },
    "benchmark_summary": {
        "en": "Verification hierarchy for stress-driven volumetric growth",
        "ru": "Иерархия верификации объёмного роста, управляемого напряжением",
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


def colors() -> tuple[str, str, str, str, str]:
    return (
        PALETTE["blue"],
        PALETTE["cyan"],
        PALETTE["lime"],
        PALETTE["ink"],
        PALETTE["slate"],
    )
