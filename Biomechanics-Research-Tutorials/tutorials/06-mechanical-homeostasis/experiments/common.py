"""Shared plotting and localization helpers for Tutorial 06."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

from biomechanics_tutorials.plotting import PALETTE, apply_tutorial_style

TUTORIAL_ROOT = Path(__file__).resolve().parents[1]
FIGURE_DIRECTORY = TUTORIAL_ROOT / "figures"
ANIMATION_DIRECTORY = TUTORIAL_ROOT / "animations"
DATA_DIRECTORY = TUTORIAL_ROOT / "data"

TEXT = {
    "time": {"en": "Time, a.u.", "ru": "Время, усл. ед."},
    "load": {"en": "Load", "ru": "Нагрузка"},
    "stress": {"en": "Stress / target", "ru": "Напряжение / цель"},
    "capacity": {"en": "Load-bearing capacity", "ru": "Несущая способность"},
    "error": {"en": "Homeostatic error", "ru": "Гомеостатическая ошибка"},
    "rate": {"en": "Adaptation rate", "ru": "Скорость адаптации"},
    "delay": {"en": "Feedback delay", "ru": "Задержка обратной связи"},
    "rms": {"en": "Late-time RMS error", "ru": "Поздняя среднеквадратичная ошибка"},
    "production": {"en": "Production rate", "ru": "Скорость производства"},
    "removal": {"en": "Removal rate", "ru": "Скорость удаления"},
    "mass": {"en": "Constituent mass", "ru": "Масса компонента"},
    "radius": {"en": "Radius / homeostatic radius", "ru": "Радиус / гомеостатический радиус"},
    "thickness": {"en": "Thickness / homeostatic thickness", "ru": "Толщина / гомеостатическая толщина"},
    "stimulus": {"en": "Normalized mechanical stimulus", "ru": "Нормированный механический стимул"},
    "wall": {"en": "Circumferential wall stress", "ru": "Окружное напряжение стенки"},
    "shear": {"en": "Wall shear stress", "ru": "Касательное напряжение стенки"},
    "target": {"en": "Homeostatic target", "ru": "Гомеостатическая цель"},
    "true": {"en": "True stimulus", "ru": "Истинный стимул"},
    "measured": {"en": "Noisy measurement", "ru": "Шумное измерение"},
    "filtered": {"en": "Filtered signal", "ru": "Отфильтрованный сигнал"},
}

TITLES = {
    "feedback_loop": {
        "en": "Mechanical homeostasis as a closed feedback loop",
        "ru": "Механический гомеостаз как замкнутый контур обратной связи",
    },
    "analytical_verification": {
        "en": "Analytical verification of the scalar homeostasis model",
        "ru": "Аналитическая верификация скалярной модели гомеостаза",
    },
    "disturbance_protocols": {
        "en": "Different disturbances produce different adaptation histories",
        "ru": "Разные возмущения формируют разные траектории адаптации",
    },
    "rate_sweep": {
        "en": "Adaptation rate controls recovery time",
        "ru": "Скорость адаптации определяет время восстановления",
    },
    "nonlinear_feedback": {
        "en": "Dead zones and saturation change the attainable response",
        "ru": "Мёртвая зона и насыщение меняют достижимый ответ",
    },
    "sensing_noise": {
        "en": "Sensing filters suppress noise but introduce lag",
        "ru": "Фильтрация подавляет шум, но создаёт запаздывание",
    },
    "bias_allostasis": {
        "en": "Sensor bias and a moving target shift the regulated state",
        "ru": "Ошибка сенсора и движущаяся цель смещают регулируемое состояние",
    },
    "delay_stability_map": {
        "en": "Feedback gain and delay govern mechanobiological stability",
        "ru": "Усиление и задержка определяют механобиологическую устойчивость",
    },
    "maladaptation_modes": {
        "en": "Distinct mechanisms can produce maladaptation",
        "ru": "Разные механизмы могут приводить к дезадаптации",
    },
    "turnover_balance": {
        "en": "Homeostasis can coexist with continuous production and removal",
        "ru": "Гомеостаз совместим с непрерывным производством и удалением",
    },
    "constituent_turnover": {
        "en": "Constituents remodel on different time scales",
        "ru": "Компоненты ремоделируются на разных временных масштабах",
    },
    "vessel_adaptation": {
        "en": "Radius and wall thickness regulate different vascular stimuli",
        "ru": "Радиус и толщина стенки регулируют разные сосудистые стимулы",
    },
    "vessel_state_space": {
        "en": "The vascular homeostatic state is an attractor in geometry space",
        "ru": "Сосудистое гомеостатическое состояние как аттрактор в пространстве геометрии",
    },
    "benchmark_summary": {
        "en": "Synthetic benchmark of homeostatic recovery and failure",
        "ru": "Синтетический benchmark восстановления и нарушения гомеостаза",
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


def palette_cycle() -> list[str]:
    return [
        PALETTE["blue"],
        PALETTE["cyan"],
        PALETTE["lime"],
        PALETTE["slate"],
        PALETTE["ink"],
    ]
