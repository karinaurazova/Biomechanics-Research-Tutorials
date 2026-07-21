"""Small localization helpers for educational figures and notebooks."""

from __future__ import annotations

from pathlib import Path
from typing import Any

SUPPORTED_LANGUAGES = ("en", "ru")

_TEXT: dict[str, dict[str, str]] = {
    # Shared
    "time": {"en": "Time", "ru": "Время"},
    "concentration": {"en": "Concentration", "ru": "Концентрация"},
    "concentration_beta": {"en": "Concentration β", "ru": "Концентрация β"},
    "nominal_stress": {"en": "Nominal stress P", "ru": "Номинальное напряжение P"},
    "nominal_stress_dimensionless": {
        "en": "Nominal stress P (dimensionless)",
        "ru": "Номинальное напряжение P (безразмерное)",
    },
    "uniaxial_stretch": {"en": "Uniaxial stretch λ", "ru": "Одноосное растяжение λ"},
    "stretch": {"en": "Stretch λ", "ru": "Растяжение λ"},
    "maximum_component_error": {
        "en": "Maximum component error",
        "ru": "Максимальная ошибка компоненты",
    },
    # Tutorial 01
    "fiber_orientation": {"en": "Fiber orientation", "ru": "Ориентация волокна"},
    "target": {"en": "Target", "ru": "Целевое направление"},
    "target_direction": {"en": "Target direction", "ru": "Целевое направление"},
    "angle_degrees": {"en": "Angle, degrees", "ru": "Угол, градусы"},
    "orientation_degrees": {"en": "Orientation, degrees", "ru": "Ориентация, градусы"},
    "axial_error_degrees": {
        "en": "Axial error, degrees",
        "ru": "Осевая ошибка, градусы",
    },
    "absolute_axial_error_degrees": {
        "en": "Absolute axial error, degrees",
        "ru": "Абсолютная осевая ошибка, градусы",
    },
    "alignment_index": {"en": "Alignment index", "ru": "Индекс выравнивания"},
    "t1_baseline_title": {
        "en": "Fiber reorientation toward a fixed target",
        "ru": "Переориентация волокон к фиксированному направлению",
    },
    "remodeling_rate": {
        "en": "Remodeling rate k, inverse time",
        "ru": "Скорость ремоделирования k, обратное время",
    },
    "time_to_5deg": {
        "en": "Time to reach 5-degree mismatch",
        "ru": "Время достижения рассогласования 5°",
    },
    "adaptation_time_title": {
        "en": "Adaptation time is inversely proportional to remodeling rate",
        "ru": "Время адаптации обратно пропорционально скорости ремоделирования",
    },
    "analytical": {"en": "Analytical", "ru": "Аналитическое решение"},
    "explicit_euler": {"en": "Explicit Euler", "ru": "Явный метод Эйлера"},
    "verification_title": {
        "en": "Verification against the fixed-target solution",
        "ru": "Верификация по решению с фиксированной целью",
    },
    "numerical_discrepancy_degrees": {
        "en": "Numerical discrepancy, degrees",
        "ru": "Численное расхождение, градусы",
    },
    "changing_cue_title": {
        "en": "Reorientation under a changing mechanical cue",
        "ru": "Переориентация при изменяющемся механическом стимуле",
    },
    "synthetic_tissue_coordinate": {
        "en": "Synthetic tissue coordinate",
        "ru": "Координата синтетической ткани",
    },
    "mean_error_frame": {
        "en": "t = {time:.1f}, mean error = {error:.1f} degrees",
        "ru": "t = {time:.1f}, средняя ошибка = {error:.1f}°",
    },
    "initial_degrees": {
        "en": "initial = {value:.1f} degrees",
        "ru": "начальный угол = {value:.1f}°",
    },
    "target_branch": {
        "en": "target branch: 30 degrees",
        "ru": "целевая ветвь: 30°",
    },
    "equivalent_branch": {
        "en": "equivalent branch: -150 degrees",
        "ru": "эквивалентная ветвь: -150°",
    },
    "unwrapped_orientation_degrees": {
        "en": "Unwrapped orientation, degrees",
        "ru": "Развёрнутая ориентация, градусы",
    },
    "orthogonal_title": {
        "en": "A 90-degree mismatch does not select a unique rotation direction",
        "ru": "Рассогласование 90° не задаёт единственное направление вращения",
    },
    "effect_rate_title": {
        "en": "Effect of remodeling rate",
        "ru": "Влияние скорости ремоделирования",
    },
    # Tutorial 02
    "axial_orientation_deg": {
        "en": "Axial orientation θ (deg)",
        "ru": "Осевая ориентация θ (град.)",
    },
    "probability_density": {
        "en": "Probability density ρ (rad⁻¹)",
        "ru": "Плотность вероятности ρ (рад⁻¹)",
    },
    "distribution_gallery_title": {
        "en": "Axial von Mises distributions: concentration controls angular spread",
        "ru": "Осевые распределения фон Мизеса: концентрация задаёт угловой разброс",
    },
    "analytical_major": {
        "en": "Analytical major",
        "ru": "Аналитическое главное",
    },
    "quadrature_major": {
        "en": "Quadrature major",
        "ru": "Численное главное",
    },
    "analytical_minor": {
        "en": "Analytical minor",
        "ru": "Аналитическое малое",
    },
    "quadrature_minor": {
        "en": "Quadrature minor",
        "ru": "Численное малое",
    },
    "orientation_tensor_eigenvalue": {
        "en": "Orientation-tensor eigenvalue",
        "ru": "Собственное значение тензора ориентации",
    },
    "tensor_verification_title": {
        "en": "Analytical and numerical orientation tensors",
        "ru": "Аналитический и численный тензоры ориентации",
    },
    "quadrature_error_title": {
        "en": "Quadrature verification error",
        "ru": "Ошибка верификации квадратуры",
    },
    "mean_fiber_angle": {
        "en": "mean fiber angle μ = {angle:.0f}°",
        "ru": "средний угол волокон μ = {angle:.0f}°",
    },
    "mean_axial_orientation": {
        "en": "Mean axial orientation μ (deg)",
        "ru": "Средняя осевая ориентация μ (град.)",
    },
    "joint_effect_title": {
        "en": "Joint effect of mean angle and dispersion at λ = {stretch:.2f}",
        "ru": "Совместное влияние среднего угла и дисперсии при λ = {stretch:.2f}",
    },
    "angular_quadrature_points": {
        "en": "Angular quadrature points N",
        "ru": "Число точек угловой квадратуры N",
    },
    "maximum_stress_error": {
        "en": "Maximum stress error",
        "ru": "Максимальная ошибка напряжения",
    },
    "convergence_title": {
        "en": "Angular-integration convergence against a dense reference",
        "ru": "Сходимость углового интегрирования относительно плотного эталона",
    },
    "synthetic_fiber_population": {
        "en": "Synthetic fiber population",
        "ru": "Синтетическая популяция волокон",
    },
    "mean_axis": {"en": "Mean axis", "ru": "Средняя ось"},
    "evolving_concentration": {
        "en": "Evolving concentration",
        "ru": "Изменение концентрации",
    },
    "dispersion_animation_title": {
        "en": "From a uniform planar distribution to a concentrated fiber family",
        "ru": "От равномерного плоского распределения к концентрированному семейству",
    },
    "orientation_distribution_title": {
        "en": "Orientation distribution: μ={angle:.0f}°, β={beta:g}",
        "ru": "Распределение ориентаций: μ={angle:.0f}°, β={beta:g}",
    },
    "tension_only_response": {
        "en": "Angularly integrated tension-only response",
        "ru": "Угловое интегрирование отклика только при растяжении",
    },
    "t2_baseline_title": {
        "en": "Tutorial 02 baseline: from orientation statistics to mechanics",
        "ru": "Модуль 02: от статистики ориентаций к механике",
    },
    "aligned_response_title": {
        "en": "Aligned mean family: greater concentration strengthens the loading direction",
        "ru": "Выровненное семейство: рост концентрации усиливает направление нагрузки",
    },
    "oblique_response_title": {
        "en": "Oblique mean family: the effect of dispersion changes with geometry",
        "ru": "Наклонное семейство: эффект дисперсии зависит от геометрии",
    },
    "concentration_spread_title": {
        "en": "Concentration controls angular spread",
        "ru": "Концентрация управляет угловым разбросом",
    },
    "mean_aligned_loading": {
        "en": "Mean aligned with loading",
        "ru": "Среднее направление совпадает с нагрузкой",
    },
    "mean_oblique_loading": {
        "en": "Mean oblique to loading",
        "ru": "Среднее направление наклонно к нагрузке",
    },
    "analytical_tensor": {
        "en": "Analytical tensor:",
        "ru": "Аналитический тензор:",
    },
    "numerical_tensor": {
        "en": "Numerical tensor:",
        "ru": "Численный тензор:",
    },
    "trace": {"en": "trace =", "ru": "след ="},
    "max_component_error_print": {
        "en": "maximum component error =",
        "ru": "максимальная ошибка компоненты =",
    },
    "max_error_print": {"en": "max error", "ru": "макс. ошибка"},
}


def tr(key: str, language: str = "en", **values: Any) -> str:
    """Return localized educational text."""
    if language not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Unsupported language: {language}")
    try:
        template = _TEXT[key][language]
    except KeyError as exc:
        raise KeyError(f"Unknown localization key: {key}") from exc
    return template.format(**values)


def localized_path(path: Path, language: str) -> Path:
    """Return the default English path or a sibling path with ``_ru`` suffix."""
    if language not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Unsupported language: {language}")
    if language == "en":
        return path
    return path.with_name(f"{path.stem}_ru{path.suffix}")
