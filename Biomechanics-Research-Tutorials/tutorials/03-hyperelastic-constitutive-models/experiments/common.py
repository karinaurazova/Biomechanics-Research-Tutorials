"""Shared helpers for Tutorial 03 experiment scripts."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

TUTORIAL_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = TUTORIAL_ROOT.parents[1]
SOURCE_DIRECTORY = REPOSITORY_ROOT / "src"
if str(SOURCE_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIRECTORY))

from biomechanics_tutorials.plotting import PALETTE, apply_tutorial_style  # noqa: E402

apply_tutorial_style()

TEXT = {
    "stretch": {"en": "Stretch λ", "ru": "Растяжение λ"},
    "shear": {"en": "Shear amount γ", "ru": "Величина сдвига γ"},
    "response": {"en": "Generalized response dW/dq", "ru": "Обобщённый отклик dW/dq"},
    "energy": {"en": "Strain-energy density W", "ru": "Плотность энергии деформации W"},
    "isotropic": {"en": "Isotropic models", "ru": "Изотропные модели"},
    "fiber": {"en": "Fiber-reinforced models", "ru": "Волокнистые модели"},
    "myocardium": {"en": "Myocardial models", "ru": "Модели миокарда"},
    "catalog": {
        "en": "Sixteen hyperelastic constitutive models",
        "ru": "Шестнадцать гиперупругих определяющих моделей",
    },
    "uniaxial_title": {
        "en": "Ten isotropic models under incompressible uniaxial stretch",
        "ru": "Десять изотропных моделей при несжимаемом одноосном растяжении",
    },
    "modes_title": {
        "en": "One material law can predict different loading modes",
        "ru": "Одно определяющее соотношение в разных режимах нагружения",
    },
    "limiting_title": {
        "en": "Limiting-chain parameters control strain stiffening",
        "ru": "Параметры предельной растяжимости управляют упрочнением",
    },
    "ogden_title": {
        "en": "Ogden exponents reshape the nonlinear response",
        "ru": "Показатели Огдена изменяют нелинейную форму отклика",
    },
    "calibration_title": {
        "en": "Similar uniaxial fits do not imply identical biaxial predictions",
        "ru": "Близкие одноосные аппроксимации не гарантируют одинаковый двухосный прогноз",
    },
    "volume_title": {
        "en": "Three volumetric penalty functions",
        "ru": "Три варианта объёмной штрафной энергии",
    },
    "angle_title": {
        "en": "Fiber angle changes the apparent loading stiffness",
        "ru": "Угол волокон изменяет кажущуюся жёсткость при нагрузке",
    },
    "angle_map_title": {
        "en": "Joint effect of stretch and fiber angle",
        "ru": "Совместное влияние растяжения и угла волокон",
    },
    "dispersion_title": {
        "en": "HGO and GOH: orientation dispersion changes recruitment",
        "ru": "HGO и GOH: дисперсия ориентаций изменяет включение волокон",
    },
    "myocardium_title": {
        "en": "Myocardial models distinguish material shear planes",
        "ru": "Модели миокарда различают материальные плоскости сдвига",
    },
    "derivative_title": {
        "en": "Energy derivative verification for the Neo-Hookean model",
        "ru": "Верификация производной энергии для модели Нео-Гука",
    },
    "objectivity_title": {
        "en": "Superposed rigid rotations leave objective energies unchanged",
        "ru": "Наложенный жёсткий поворот не изменяет объективную энергию",
    },
    "volume_ratio": {"en": "Volume ratio J", "ru": "Отношение объёмов J"},
    "bulk_energy": {"en": "Volumetric energy U(J)", "ru": "Объёмная энергия U(J)"},
    "fiber_angle": {"en": "Fiber angle, degrees", "ru": "Угол волокон, градусы"},
    "model": {"en": "Model", "ru": "Модель"},
    "absolute_error": {"en": "Absolute error", "ru": "Абсолютная ошибка"},
    "step_size": {"en": "Finite-difference step", "ru": "Шаг конечной разности"},
    "uniaxial": {"en": "Uniaxial", "ru": "Одноосное"},
    "equibiaxial": {"en": "Equibiaxial", "ru": "Равноосное двухосное"},
    "plane_strain": {"en": "Plane strain", "ru": "Плоская деформация"},
    "simple_shear": {"en": "Simple shear", "ru": "Простой сдвиг"},
    "quadratic": {"en": "Quadratic", "ru": "Квадратичная"},
    "logarithmic": {"en": "Logarithmic", "ru": "Логарифмическая"},
    "simo_taylor": {"en": "Simo-Taylor", "ru": "Симо–Тейлор"},
    "frame": {
        "en": "Gent locking parameter Jm = {value:.1f}",
        "ru": "Параметр блокировки Гента Jm = {value:.1f}",
    },
}

MODEL_NAMES_RU = {
    "Neo-Hookean": "Нео-Гук",
    "Mooney-Rivlin": "Муни–Ривлин",
    "Yeoh": "Йео",
    "Rivlin polynomial (order 2)": "Полином Ривлина второго порядка",
    "Gent": "Гент",
    "Arruda-Boyce (truncated)": "Арруда–Бойс",
    "Ogden, one term": "Огден, один член",
    "Ogden, two terms": "Огден, два члена",
    "Demiray exponential": "Экспоненциальная модель Демирая",
    "Veronda-Westmann": "Веронда–Вестманн",
    "Single exponential fiber family": "Одно экспоненциальное семейство волокон",
    "HGO, two fiber families": "HGO, два семейства волокон",
    "GOH with fiber dispersion": "GOH с дисперсией волокон",
    "Guccione myocardium": "Модель Гуччоне",
    "Costa orthotropic myocardium": "Ортотропная модель Косты",
    "Holzapfel-Ogden myocardium": "Модель Хольцапфеля–Огдена",
}


def tr(key: str, language: str, **values: object) -> str:
    return TEXT[key][language].format(**values)


def model_name(name: str, language: str) -> str:
    return MODEL_NAMES_RU.get(name, name) if language == "ru" else name


def output_path(stem: str, language: str, suffix: str = ".png") -> Path:
    directory = TUTORIAL_ROOT / ("animations" if suffix == ".gif" else "figures")
    localized = f"{stem}_ru{suffix}" if language == "ru" else f"{stem}{suffix}"
    return directory / localized


def save_figure(fig: plt.Figure, stem: str, language: str) -> None:
    fig.savefig(output_path(stem, language), dpi=180)
    plt.close(fig)


def curve_colors(count: int) -> list[str]:
    base = [
        PALETTE["blue"],
        PALETTE["cyan"],
        "#7C3AED",
        "#E11D48",
        "#F59E0B",
        "#059669",
        "#334155",
        "#EC4899",
        "#0EA5E9",
        "#84CC16",
        "#8B5CF6",
        "#D97706",
        "#14B8A6",
        "#64748B",
        "#DB2777",
        "#2563EB",
    ]
    return [base[index % len(base)] for index in range(count)]


def finite_values(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mask = np.isfinite(y)
    return x[mask], y[mask]
