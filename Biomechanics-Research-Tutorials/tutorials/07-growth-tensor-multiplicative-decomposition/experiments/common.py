"""Shared localization and plotting helpers for Tutorial 07."""

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
    "energy": {"en": "Reference energy", "ru": "Энергия в отсчётной конфигурации"},
    "mandel": {"en": "Mandel stress component", "ru": "Компонента напряжения Манделя"},
    "growth_stretch": {"en": "Growth stretch", "ru": "Растяжение роста"},
    "elastic_stretch": {"en": "Elastic stretch", "ru": "Упругое растяжение"},
    "total_stretch": {"en": "Total stretch", "ru": "Полное растяжение"},
    "angle": {"en": "Angle, degrees", "ru": "Угол, градусы"},
    "commutator": {"en": "Commutator norm", "ru": "Норма коммутатора"},
    "incompatibility": {"en": "Row-wise curl norm", "ru": "Норма построчного ротора"},
    "position": {"en": "Thickness coordinate", "ru": "Координата по толщине"},
    "stress": {"en": "Reduced nominal stress", "ru": "Редуцированное номинальное напряжение"},
    "curvature": {"en": "Curvature", "ru": "Кривизна"},
    "volume_ratio": {"en": "Growth volume ratio Jg", "ru": "Объёмный коэффициент роста Jg"},
    "error": {"en": "Verification error", "ru": "Ошибка верификации"},
}

TITLES = {
    "kinematics_schematic": {
        "en": "Multiplicative growth separates local mass addition from elastic compatibility",
        "ru": "Мультипликативный рост разделяет локальное добавление массы и упругую совместность",
    },
    "growth_tensor_atlas": {
        "en": "Growth tensors encode isotropic, transverse, and orthotropic changes",
        "ru": "Тензоры роста задают изотропные, поперечные и ортотропные изменения",
    },
    "determinant_bookkeeping": {
        "en": "The volume ratios satisfy J = Je Jg",
        "ru": "Объёмные коэффициенты удовлетворяют J = Je Jg",
    },
    "free_constrained_growth": {
        "en": "Free growth is stress-free; constrained growth stores elastic energy",
        "ru": "Свободный рост не создаёт напряжений, а стеснённый накапливает упругую энергию",
    },
    "frame_indifference": {
        "en": "Superposed rigid rotation does not change elastic energy",
        "ru": "Наложенный жёсткий поворот не изменяет упругую энергию",
    },
    "decomposition_nonuniqueness": {
        "en": "The same total deformation can hide different internal growth states",
        "ru": "Одна полная деформация может скрывать разные внутренние состояния роста",
    },
    "stress_relaxation": {
        "en": "Stress-driven growth relaxes elastic stress under fixed total deformation",
        "ru": "Рост, управляемый напряжением, релаксирует упругий отклик при фиксированной деформации",
    },
    "growth_law_sweep": {
        "en": "Growth rate and target stress control adaptation time and residual state",
        "ru": "Скорость роста и целевое напряжение определяют время адаптации и остаточное состояние",
    },
    "anisotropic_growth": {
        "en": "Isotropic and directional growth laws produce different internal architectures",
        "ru": "Изотропные и направленные законы роста формируют разные внутренние архитектуры",
    },
    "noncommutative_paths": {
        "en": "Rotating anisotropic growth increments are path dependent",
        "ru": "Поворачивающиеся анизотропные приращения роста зависят от пути",
    },
    "incompatibility_map": {
        "en": "Spatially varying growth is generally incompatible",
        "ru": "Пространственно неоднородный рост в общем случае несовместен",
    },
    "differential_growth_strip": {
        "en": "A through-thickness growth gradient generates bending and residual stress",
        "ru": "Градиент роста по толщине вызывает изгиб и остаточные напряжения",
    },
    "direction_pushforward": {
        "en": "Growth and elastic accommodation reorient material directions differently",
        "ru": "Рост и упругая аккомодация по-разному переориентируют материальные направления",
    },
    "benchmark_summary": {
        "en": "Verification-ready synthetic benchmark for finite-growth kinematics",
        "ru": "Синтетический verification-ready benchmark кинематики конечного роста",
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


def language_colors() -> tuple[str, str, str, str]:
    return PALETTE["blue"], PALETTE["cyan"], PALETTE["lime"], PALETTE["ink"]
