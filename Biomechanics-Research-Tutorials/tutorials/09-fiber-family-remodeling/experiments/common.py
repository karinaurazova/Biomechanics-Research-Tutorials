"""Shared localization and plotting helpers for Tutorial 09."""

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
    "angle": {"en": "Axial orientation, deg", "ru": "Осевая ориентация, град"},
    "density": {"en": "Orientation density", "ru": "Плотность ориентаций"},
    "order": {"en": "Order parameter", "ru": "Параметр порядка"},
    "energy": {"en": "Fiber energy", "ru": "Энергия волокон"},
    "stretch": {"en": "Stretch", "ru": "Растяжение"},
    "mass": {"en": "Fiber mass", "ru": "Масса волокон"},
    "fraction": {"en": "Mass fraction", "ru": "Массовая доля"},
    "error": {"en": "Normalized error", "ru": "Нормированная ошибка"},
    "concentration": {"en": "Concentration", "ru": "Концентрация"},
    "diffusion": {"en": "Rotational diffusivity", "ru": "Вращательная диффузия"},
    "alignment": {"en": "Alignment rate", "ru": "Скорость выравнивания"},
    "age": {"en": "Mean cohort age", "ru": "Средний возраст когорт"},
}

TITLES = {
    "modeling_taxonomy": {
        "en": "Fiber remodeling models answer different biological questions",
        "ru": "Модели ремоделирования волокон отвечают на разные биологические вопросы",
    },
    "discrete_reorientation": {
        "en": "Direct rotation aligns a discrete family with a mechanical cue",
        "ru": "Прямая ротация выравнивает дискретное семейство с механическим стимулом",
    },
    "cue_degeneracy": {
        "en": "Principal-direction cues become non-unique near equibiaxial states",
        "ru": "Стимул главного направления становится неединственным вблизи равноосных состояний",
    },
    "loading_switch": {
        "en": "Remodeling retains memory of the complete loading history",
        "ru": "Ремоделирование сохраняет память о полной истории нагружения",
    },
    "odf_evolution": {
        "en": "A continuous orientation distribution aligns and spreads simultaneously",
        "ru": "Непрерывное распределение ориентаций одновременно выравнивается и рассеивается",
    },
    "alignment_diffusion_map": {
        "en": "Alignment competes with rotational diffusion",
        "ru": "Выравнивание конкурирует с вращательной диффузией",
    },
    "dispersion_metrics": {
        "en": "One dispersion parameter cannot encode every distribution shape",
        "ru": "Один параметр дисперсии не описывает любую форму распределения",
    },
    "discrete_continuous": {
        "en": "Discrete families converge to angular integration only with sufficient resolution",
        "ru": "Дискретные семейства сходятся к угловому интегрированию только при достаточном разрешении",
    },
    "lanir_goh_comparison": {
        "en": "Angular integration and structure-tensor closure are related but not identical",
        "ru": "Угловое интегрирование и замыкание через структурный тензор связаны, но не тождественны",
    },
    "two_family_response": {
        "en": "Two symmetric fiber families create load-direction-dependent anisotropy",
        "ru": "Два симметричных семейства создают зависящую от направления анизотропию",
    },
    "recruitment_crimp": {
        "en": "Recruitment and crimp control the toe region before material stiffening",
        "ru": "Рекрутирование и извитость формируют начальный участок до материального упрочнения",
    },
    "turnover_replacement": {
        "en": "Cohort turnover remodels architecture by deposition and survival",
        "ru": "Когортный turnover перестраивает архитектуру через отложение и выживание",
    },
    "direct_vs_turnover": {
        "en": "Direct rotation and cohort replacement can fit the same endpoint with different histories",
        "ru": "Прямая ротация и замещение когорт могут совпасть в финале при разных историях",
    },
    "deposition_stretch": {
        "en": "Deposition stretch changes prestress without changing observed orientation",
        "ru": "Растяжение отложения меняет преднапряжение без изменения наблюдаемой ориентации",
    },
    "family_competition": {
        "en": "Family-specific loading redistributes collagen mass",
        "ru": "Нагрузка отдельных семейств перераспределяет массу коллагена",
    },
    "identifiability": {
        "en": "Orientation, dispersion, and mass can compensate in a single loading mode",
        "ru": "Ориентация, дисперсия и масса могут компенсировать друг друга в одном режиме",
    },
    "biology_model_map": {
        "en": "Biological mechanisms map to different internal variables",
        "ru": "Биологические механизмы отображаются в разные внутренние переменные",
    },
    "benchmark_summary": {
        "en": "Verification hierarchy for fiber-family remodeling",
        "ru": "Иерархия верификации ремоделирования семейств волокон",
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


def colors() -> tuple[str, str, str, str, str, str]:
    return (
        PALETTE["blue"],
        PALETTE["cyan"],
        PALETTE["lime"],
        PALETTE["ink"],
        PALETTE["slate"],
        "#E85D75",
    )
