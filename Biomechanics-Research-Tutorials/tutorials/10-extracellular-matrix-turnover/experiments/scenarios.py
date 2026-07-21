"""Localized result generation for Tutorial 10."""

from __future__ import annotations

import csv
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np

from common import ANIMATION_DIRECTORY, DATA_DIRECTORY, PALETTE, TEXT, save_figure
from biomechanics_tutorials.ecm_turnover import (
    CollagenKineticsParameters,
    MatrixComponent,
    MechanobiologyParameters,
    SurvivalParameters,
    collagen_fiber_tension,
    compare_model_state_count,
    hazard_rate,
    matrix_nominal_stress,
    mmp_timp_activity,
    pulse_chase_fraction,
    simulate_cohort_turnover,
    simulate_collagen_maturation,
    simulate_homogenized_turnover,
    simulate_multicomponent_ecm,
    simulate_spatial_degradation,
    survival_fraction,
    tangent_modulus,
    turnover_metrics,
)


def _title(language: str, en: str, ru: str) -> str:
    return en if language == "en" else ru


def _pair(stem: str, builder) -> None:
    for language in ("en", "ru"):
        save_figure(builder(language), stem, language)


def modeling_taxonomy() -> None:
    levels = ["Net mass ODE", "Maturation ODE", "Cohort history", "Spatial cohorts"]
    levels_ru = ["ОДУ массы", "ОДУ созревания", "История когорт", "Пространственные когорты"]
    counts = compare_model_state_count(120, 4)
    values = list(counts.values())

    def build(language: str):
        fig, ax = plt.subplots(figsize=(9, 5.4))
        labels = levels if language == "en" else levels_ru
        bars = ax.bar(labels, values)
        ax.set_yscale("log")
        ax.set_ylabel(_title(language, "Approximate state count", "Приблизительное число состояний"))
        ax.set_title(_title(language, "Model hierarchy: more biology requires more state", "Иерархия моделей: больше биологии — больше состояний"))
        ax.tick_params(axis="x", rotation=18)
        for bar, value in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2, value * 1.12, str(value), ha="center")
        return fig

    _pair("modeling_taxonomy", build)


def homeostatic_flux_balance() -> None:
    time = np.linspace(0.0, 50.0, 501)
    half_life = 12.0
    production = np.log(2.0) / half_life
    result = simulate_homogenized_turnover(time, production, half_life, initial_mass=1.0)

    def build(language: str):
        fig, axes = plt.subplots(1, 2, figsize=(11, 4.6))
        axes[0].plot(time, result["mass"], label=_title(language, "Mass", "Масса"))
        axes[0].set_xlabel(TEXT[language]["time"])
        axes[0].set_ylabel(TEXT[language]["mass"])
        axes[0].set_title(_title(language, "Stationary mass", "Стационарная масса"))
        axes[1].plot(time, result["production"], label=TEXT[language]["production"])
        axes[1].plot(time, result["removal"], "--", label=TEXT[language]["removal"])
        axes[1].set_xlabel(TEXT[language]["time"])
        axes[1].set_ylabel(_title(language, "Flux", "Поток"))
        axes[1].set_title(_title(language, "Dynamic balance with non-zero fluxes", "Динамический баланс при ненулевых потоках"))
        for ax in axes:
            ax.legend()
        fig.suptitle(_title(language, "Homeostasis is not absence of turnover", "Гомеостаз не означает отсутствия обновления"))
        return fig

    _pair("homeostatic_flux_balance", build)


def survival_models() -> None:
    age = np.linspace(0.0, 50.0, 400)
    parameters = [
        SurvivalParameters("exponential", 15.0),
        SurvivalParameters("weibull", 15.0, 0.7),
        SurvivalParameters("weibull", 15.0, 2.0),
    ]
    labels_en = ["Exponential", "Weibull: decreasing hazard", "Weibull: increasing hazard"]
    labels_ru = ["Экспоненциальная", "Вейбулл: убывающий риск", "Вейбулл: возрастающий риск"]

    def build(language: str):
        fig, axes = plt.subplots(1, 2, figsize=(11, 4.6))
        labels = labels_en if language == "en" else labels_ru
        for params, label in zip(parameters, labels):
            axes[0].plot(age, survival_fraction(age, params), label=label)
            axes[1].plot(age[1:], hazard_rate(age[1:], params), label=label)
        axes[0].axhline(0.5, ls="--", lw=1)
        axes[0].set_xlabel(TEXT[language]["age"])
        axes[0].set_ylabel(_title(language, "Survival fraction", "Доля выжившего материала"))
        axes[1].set_xlabel(TEXT[language]["age"])
        axes[1].set_ylabel(_title(language, "Hazard rate", "Интенсивность удаления"))
        axes[0].set_title(_title(language, "Survival functions", "Функции выживания"))
        axes[1].set_title(_title(language, "Age-dependent removal", "Возраст-зависимое удаление"))
        axes[0].legend()
        axes[1].legend()
        return fig

    _pair("survival_models", build)


def age_structured_cohorts() -> None:
    time = np.linspace(0.0, 60.0, 601)
    result = simulate_cohort_turnover(
        time,
        production_protocol=lambda t: 0.045 if t < 20.0 else 0.075,
        survival_parameters=SurvivalParameters("weibull", 16.0, 1.6),
        deposition_stretch_protocol=lambda t: 1.03 if t < 30.0 else 1.08,
    )

    def build(language: str):
        fig, axes = plt.subplots(2, 2, figsize=(11, 8))
        axes[0, 0].plot(time, result["mass"])
        axes[0, 0].set_ylabel(TEXT[language]["mass"])
        axes[0, 0].set_title(_title(language, "Surviving ECM mass", "Сохранившаяся масса ECM"))
        axes[0, 1].plot(time, result["mean_age"])
        axes[0, 1].set_ylabel(_title(language, "Mean age", "Средний возраст"))
        axes[0, 1].set_title(_title(language, "Age structure", "Возрастная структура"))
        axes[1, 0].plot(time, result["retained_initial_fraction"])
        axes[1, 0].set_ylabel(_title(language, "Initial cohort fraction", "Доля исходной когорты"))
        axes[1, 1].plot(time, result["mean_deposition_stretch"])
        axes[1, 1].set_ylabel(_title(language, "Mean deposition stretch", "Среднее deposition stretch"))
        for ax in axes.flat:
            ax.set_xlabel(TEXT[language]["time"])
        fig.suptitle(_title(language, "Cohort history carries information beyond total mass", "История когорт содержит больше информации, чем общая масса"))
        return fig

    _pair("age_structured_cohorts", build)


def cohort_vs_homogenized() -> None:
    time = np.linspace(0.0, 50.0, 1001)
    half_life = 10.0
    production = np.log(2.0) / half_life
    cohort = simulate_cohort_turnover(time, production, SurvivalParameters("exponential", half_life))
    homogenized = simulate_homogenized_turnover(time, production, half_life)
    relative_error = np.abs(cohort["mass"] - homogenized["mass"]) / np.maximum(homogenized["mass"], 1e-12)

    def build(language: str):
        fig, axes = plt.subplots(1, 2, figsize=(11, 4.6))
        axes[0].plot(time, cohort["mass"], label=_title(language, "Explicit cohorts", "Явные когорты"))
        axes[0].plot(time, homogenized["mass"], "--", label=_title(language, "Homogenized ODE", "Гомогенизированное ОДУ"))
        axes[0].set_xlabel(TEXT[language]["time"])
        axes[0].set_ylabel(TEXT[language]["mass"])
        axes[0].legend()
        axes[1].plot(time, relative_error)
        axes[1].set_xlabel(TEXT[language]["time"])
        axes[1].set_ylabel(TEXT[language]["error"])
        axes[1].set_yscale("log")
        axes[1].set_title(_title(language, "Equivalence for constant hazard", "Эквивалентность при постоянном риске"))
        return fig

    _pair("cohort_vs_homogenized", build)


def stress_regulated_synthesis() -> None:
    stress = np.linspace(0.5, 1.6, 300)
    feedbacks = [
        MechanobiologyParameters(production_gain=0.5),
        MechanobiologyParameters(production_gain=1.5),
        MechanobiologyParameters(production_gain=3.0, dead_zone=0.1),
    ]

    from biomechanics_tutorials.ecm_turnover import production_multiplier

    def build(language: str):
        fig, ax = plt.subplots(figsize=(8.5, 5))
        labels = (
            ["low gain", "high gain", "high gain + dead zone"]
            if language == "en"
            else ["низкая чувствительность", "высокая чувствительность", "высокая + мёртвая зона"]
        )
        for params, label in zip(feedbacks, labels):
            ax.plot(stress, production_multiplier(stress, params), label=label)
        ax.axvline(1.0, ls="--", lw=1)
        ax.set_xlabel(TEXT[language]["stress"])
        ax.set_ylabel(_title(language, "Production multiplier", "Множитель синтеза"))
        ax.set_title(_title(language, "Stress-sensitive collagen production", "Напряжение-зависимый синтез коллагена"))
        ax.legend()
        return fig

    _pair("stress_regulated_synthesis", build)


def mmp_timp_balance() -> None:
    mmp = np.linspace(0.0, 4.0, 180)
    timp = np.linspace(0.0, 4.0, 180)
    M, T = np.meshgrid(mmp, timp)
    activity = mmp_timp_activity(M, T)

    def build(language: str):
        fig, ax = plt.subplots(figsize=(7.5, 6))
        image = ax.contourf(M, T, activity, levels=30)
        fig.colorbar(image, ax=ax, label=TEXT[language]["enzyme"])
        ax.set_xlabel("MMP")
        ax.set_ylabel("TIMP")
        ax.set_title(_title(language, "Competition between collagenase and inhibition", "Конкуренция коллагеназы и ингибирования"))
        return fig

    _pair("mmp_timp_balance", build)


def collagen_maturation() -> None:
    time = np.linspace(0.0, 60.0, 601)
    result = simulate_collagen_maturation(time)

    def build(language: str):
        fig, axes = plt.subplots(1, 2, figsize=(11, 4.8))
        labels = (
            ["Precursor", "Immature", "Mature"]
            if language == "en"
            else ["Предшественник", "Незрелый", "Зрелый"]
        )
        for key, label in zip(["precursor", "immature", "mature"], labels):
            axes[0].plot(time, result[key], label=label)
        axes[0].set_xlabel(TEXT[language]["time"])
        axes[0].set_ylabel(TEXT[language]["mass"])
        axes[0].set_title(_title(language, "Synthesis–secretion–maturation cascade", "Каскад синтез–секреция–созревание"))
        axes[0].legend()
        axes[1].plot(time, result["crosslinks"], label=_title(language, "Cross-link fraction", "Доля сшивок"))
        axes[1].plot(time, result["effective_stiffness"], label=TEXT[language]["stiffness"])
        axes[1].set_xlabel(TEXT[language]["time"])
        axes[1].set_title(_title(language, "Mechanical quality matures after mass deposition", "Механическое качество созревает после отложения массы"))
        axes[1].legend()
        return fig

    _pair("collagen_maturation", build)


def crosslink_mechanics() -> None:
    stretch = np.linspace(0.95, 1.18, 250)
    fractions = [0.0, 0.35, 0.75]

    def build(language: str):
        fig, axes = plt.subplots(1, 2, figsize=(11, 4.8))
        for fraction in fractions:
            stress = matrix_nominal_stress(stretch, 1.0, 1.0, fraction)
            axes[0].plot(stretch, stress, label=f"x={fraction:.2f}")
        crosslinks = np.linspace(0.0, 1.0, 100)
        modulus = [tangent_modulus(1.1, 1.0, 1.0, value) for value in crosslinks]
        axes[1].plot(crosslinks, modulus)
        axes[0].set_xlabel(TEXT[language]["stretch"])
        axes[0].set_ylabel(TEXT[language]["stress"])
        axes[0].set_title(_title(language, "Same collagen mass, different cross-link state", "Одинаковая масса, разное состояние сшивок"))
        axes[0].legend()
        axes[1].set_xlabel(_title(language, "Cross-link fraction", "Доля сшивок"))
        axes[1].set_ylabel(TEXT[language]["stiffness"])
        axes[1].set_title(_title(language, "Tangent stiffness at λ=1.1", "Касательная жёсткость при λ=1.1"))
        return fig

    _pair("crosslink_mechanics", build)


def deposition_stretch() -> None:
    stretch = np.linspace(0.9, 1.18, 260)
    prestretches = [0.98, 1.0, 1.05, 1.10]

    def build(language: str):
        fig, ax = plt.subplots(figsize=(8.5, 5.2))
        for prestretch in prestretches:
            ax.plot(
                stretch,
                collagen_fiber_tension(stretch, deposition_stretch=prestretch, crosslink_fraction=0.45),
                label=f"G={prestretch:.2f}",
            )
        ax.axvline(1.0, ls="--", lw=1)
        ax.set_xlabel(TEXT[language]["stretch"])
        ax.set_ylabel(TEXT[language]["stress"])
        ax.set_title(_title(language, "Deposition stretch shifts recruitment and prestress", "Растяжение при отложении изменяет рекрутирование и преднапряжение"))
        ax.legend()
        return fig

    _pair("deposition_stretch", build)


def pulse_chase() -> None:
    time = np.linspace(0.0, 60.0, 601)
    laws = [
        SurvivalParameters("exponential", 15.0),
        SurvivalParameters("weibull", 15.0, 0.7),
        SurvivalParameters("weibull", 15.0, 2.0),
    ]

    def build(language: str):
        fig, ax = plt.subplots(figsize=(8.5, 5))
        labels = (
            ["Exponential", "Weibull k=0.7", "Weibull k=2"]
            if language == "en"
            else ["Экспоненциальная", "Вейбулл k=0.7", "Вейбулл k=2"]
        )
        for law, label in zip(laws, labels):
            ax.plot(time, pulse_chase_fraction(time, 8.0, law), label=label)
        ax.axvspan(0.0, 8.0, alpha=0.12)
        ax.set_xlabel(TEXT[language]["time"])
        ax.set_ylabel(_title(language, "Labelled fraction", "Доля метки"))
        ax.set_title(_title(language, "Synthetic pulse–chase experiment", "Синтетический pulse–chase эксперимент"))
        ax.legend()
        return fig

    _pair("pulse_chase", build)


def overload_adaptation() -> None:
    time = np.linspace(0.0, 80.0, 801)
    control = simulate_collagen_maturation(time, stress_protocol=1.0)
    overload = simulate_collagen_maturation(time, stress_protocol=lambda t: 1.0 if t < 10.0 else 1.35)

    def build(language: str):
        fig, axes = plt.subplots(1, 2, figsize=(11, 4.8))
        for result, label in [
            (control, _title(language, "Control", "Контроль")),
            (overload, _title(language, "Sustained overload", "Длительная перегрузка")),
        ]:
            axes[0].plot(time, result["mature"], label=label)
            axes[1].plot(time, result["effective_stiffness"], label=label)
        axes[0].set_xlabel(TEXT[language]["time"])
        axes[0].set_ylabel(_title(language, "Mature collagen", "Зрелый коллаген"))
        axes[1].set_xlabel(TEXT[language]["time"])
        axes[1].set_ylabel(TEXT[language]["stiffness"])
        axes[0].set_title(_title(language, "Mass adaptation", "Адаптация массы"))
        axes[1].set_title(_title(language, "Mechanical consequence", "Механическое следствие"))
        axes[0].legend()
        axes[1].legend()
        return fig

    _pair("overload_adaptation", build)


def transient_inflammation() -> None:
    time = np.linspace(0.0, 80.0, 801)
    def inflammation(t: float) -> float:
        return 1.0 if 12.0 <= t <= 30.0 else 0.0

    result = simulate_collagen_maturation(time, inflammation_protocol=inflammation)

    def build(language: str):
        fig, axes = plt.subplots(2, 1, figsize=(9, 7), sharex=True)
        axes[0].plot(time, result["mmp"], label="MMP")
        axes[0].plot(time, result["timp"], label="TIMP")
        axes[0].plot(time, result["enzyme_activity"], "--", label=_title(language, "Effective activity", "Эффективная активность"))
        axes[0].legend()
        axes[0].set_ylabel(TEXT[language]["enzyme"])
        axes[1].plot(time, result["mature"], label=_title(language, "Mature collagen", "Зрелый коллаген"))
        axes[1].plot(time, result["crosslinks"], label=_title(language, "Cross-links", "Сшивки"))
        axes[1].plot(time, result["effective_stiffness"], label=TEXT[language]["stiffness"])
        axes[1].axvspan(12.0, 30.0, alpha=0.12)
        axes[1].set_xlabel(TEXT[language]["time"])
        axes[1].legend()
        fig.suptitle(_title(language, "Transient inflammation leaves a mechanical memory", "Преходящее воспаление оставляет механическую память"))
        return fig

    _pair("transient_inflammation", build)


def pathology_modes() -> None:
    time = np.linspace(0.0, 90.0, 901)
    baseline = simulate_collagen_maturation(time)
    fibrotic_params = CollagenKineticsParameters(
        basal_synthesis=0.13,
        crosslink_formation_rate=0.15,
        mature_degradation_rate=0.018,
    )
    fibrotic = simulate_collagen_maturation(time, parameters=fibrotic_params)
    degradative_params = CollagenKineticsParameters(
        basal_synthesis=0.06,
        mature_degradation_rate=0.055,
        mmp_inflammation_gain=3.0,
    )
    degradative = simulate_collagen_maturation(time, inflammation_protocol=0.6, parameters=degradative_params)

    def build(language: str):
        fig, axes = plt.subplots(1, 2, figsize=(11, 4.8))
        labels = [
            _title(language, "Homeostatic", "Гомеостатический"),
            _title(language, "Fibrotic", "Фибротический"),
            _title(language, "Degradative", "Деградационный"),
        ]
        for result, label in zip([baseline, fibrotic, degradative], labels):
            axes[0].plot(time, result["mature"], label=label)
            axes[1].plot(time, result["effective_stiffness"], label=label)
        axes[0].set_xlabel(TEXT[language]["time"])
        axes[0].set_ylabel(_title(language, "Mature collagen", "Зрелый коллаген"))
        axes[1].set_xlabel(TEXT[language]["time"])
        axes[1].set_ylabel(TEXT[language]["stiffness"])
        axes[0].legend()
        axes[1].legend()
        fig.suptitle(_title(language, "Different pathologies are not a single turnover multiplier", "Разные патологии нельзя свести к одному множителю turnover"))
        return fig

    _pair("pathology_modes", build)


def multicomponent_ecm() -> None:
    time = np.linspace(0.0, 100.0, 1001)
    components = [
        MatrixComponent("Elastin", 0.8, 0.0003, 800.0, 0.6),
        MatrixComponent("Collagen I", 1.0, np.log(2.0) / 25.0, 25.0, 2.4, 1.05, 0.7, 0.15),
        MatrixComponent("Collagen III", 0.45, np.log(2.0) * 0.45 / 12.0, 12.0, 1.2, 1.02, 1.0, 0.3),
        MatrixComponent("Proteoglycan", 0.3, np.log(2.0) * 0.3 / 6.0, 6.0, 0.25, 1.0, 0.3, 0.5),
    ]
    result = simulate_multicomponent_ecm(time, components, stress_protocol=lambda t: 1.0 if t < 15 else 1.25)

    def build(language: str):
        fig, axes = plt.subplots(1, 2, figsize=(11, 4.8))
        for index, name in enumerate(result["names"]):
            axes[0].plot(time, result["mass"][:, index], label=str(name))
        axes[0].set_xlabel(TEXT[language]["time"])
        axes[0].set_ylabel(TEXT[language]["mass"])
        axes[0].legend()
        axes[1].plot(time, result["effective_stiffness"])
        axes[1].set_xlabel(TEXT[language]["time"])
        axes[1].set_ylabel(TEXT[language]["stiffness"])
        axes[0].set_title(_title(language, "Component-specific turnover", "Компонент-специфический turnover"))
        axes[1].set_title(_title(language, "Composition-to-mechanics map", "Связь состава и механики"))
        return fig

    _pair("multicomponent_ecm", build)


def spatial_degradation_front() -> None:
    time = np.linspace(0.0, 2.0, 401)
    coordinate = np.linspace(0.0, 1.0, 121)
    def source(x: np.ndarray, t: float) -> np.ndarray:
        amplitude = 3.5 if t < 0.7 else 0.0
        return amplitude * np.exp(-((x - 0.5) / 0.07) ** 2)

    result = simulate_spatial_degradation(
        time,
        coordinate,
        np.ones_like(coordinate),
        source,
        enzyme_diffusivity=0.003,
        collagen_production=0.015,
    )
    indices = [0, 80, 180, 400]

    def build(language: str):
        fig, axes = plt.subplots(1, 2, figsize=(11, 4.8))
        for index in indices:
            label = f"t={time[index]:.1f}"
            axes[0].plot(coordinate, result["enzyme"][index], label=label)
            axes[1].plot(coordinate, result["collagen"][index], label=label)
        axes[0].set_xlabel(TEXT[language]["position"])
        axes[0].set_ylabel(TEXT[language]["enzyme"])
        axes[1].set_xlabel(TEXT[language]["position"])
        axes[1].set_ylabel(TEXT[language]["collagen"])
        axes[0].set_title(_title(language, "Diffusing degradation signal", "Диффундирующий сигнал деградации"))
        axes[1].set_title(_title(language, "Localized matrix loss and recovery", "Локальная потеря и восстановление матрикса"))
        axes[0].legend()
        axes[1].legend()
        return fig

    _pair("spatial_degradation_front", build)


def mechanics_coupling() -> None:
    time = np.linspace(0.0, 70.0, 701)
    result = simulate_collagen_maturation(time, stress_protocol=lambda t: 1.0 if t < 10 else 1.3)
    stretch = 1.10
    stress = matrix_nominal_stress(
        stretch,
        elastin_mass=1.0,
        collagen_mass=result["mature"],
        collagen_crosslinks=result["crosslinks"],
        collagen_deposition_stretch=1.05,
    )

    def build(language: str):
        fig, ax1 = plt.subplots(figsize=(9, 5.2))
        ax2 = ax1.twinx()
        ax1.plot(time, result["mature"], label=_title(language, "Mature collagen", "Зрелый коллаген"))
        ax1.plot(time, result["crosslinks"], label=_title(language, "Cross-links", "Сшивки"))
        ax2.plot(time, stress, ls="--", color=PALETTE["blue"], label=_title(language, "Stress at fixed stretch", "Напряжение при фиксированном удлинении"))
        ax1.set_xlabel(TEXT[language]["time"])
        ax1.set_ylabel(_title(language, "Matrix state", "Состояние матрикса"))
        ax2.set_ylabel(TEXT[language]["stress"])
        lines = ax1.lines + ax2.lines
        ax1.legend(lines, [line.get_label() for line in lines], loc="best")
        ax1.set_title(_title(language, "Turnover changes constitutive response over time", "Turnover изменяет определяющий отклик во времени"))
        return fig

    _pair("mechanics_coupling", build)


def identifiability() -> None:
    production = np.linspace(0.02, 0.18, 120)
    removal = np.linspace(0.02, 0.18, 120)
    P, R = np.meshgrid(production, removal)
    steady_mass = P / R
    target_mass = 1.0
    error = np.abs(steady_mass - target_mass)

    def build(language: str):
        fig, axes = plt.subplots(1, 2, figsize=(11, 4.8))
        image = axes[0].contourf(P, R, np.log10(error + 1e-5), levels=30)
        fig.colorbar(image, ax=axes[0], label=_title(language, "log10 mass error", "log10 ошибки массы"))
        axes[0].set_xlabel(TEXT[language]["production"])
        axes[0].set_ylabel(TEXT[language]["removal"])
        axes[0].set_title(_title(language, "A ridge of indistinguishable steady masses", "Гребень неразличимых стационарных масс"))
        flux = np.linspace(0.02, 0.18, 100)
        axes[1].plot(flux, np.ones_like(flux), label=_title(language, "Same mass", "Одинаковая масса"))
        axes[1].plot(flux, flux / flux[0], "--", label=_title(language, "Relative flux", "Относительный поток"))
        axes[1].set_xlabel(_title(language, "Balanced production = removal", "Сбалансированные синтез = удаление"))
        axes[1].set_title(_title(language, "Mass data do not identify turnover speed", "Данные о массе не определяют скорость turnover"))
        axes[1].legend()
        return fig

    _pair("identifiability", build)


def observability_map() -> None:
    processes = [
        "Production", "Degradation", "Maturation", "Cross-linking", "Prestretch", "Age structure"
    ]
    processes_ru = ["Синтез", "Деградация", "Созревание", "Сшивки", "Предрастяжение", "Возрастная структура"]
    observations = ["Mass", "Tracer", "MMP/TIMP", "Mechanical test", "Cross-link assay", "Imaging"]
    observations_ru = ["Масса", "Метка", "MMP/TIMP", "Механический тест", "Анализ сшивок", "Визуализация"]
    matrix = np.array([
        [1, 1, 0, 0, 0, 0],
        [1, 1, 1, 0, 0, 0],
        [0, 0, 0, 1, 1, 0],
        [0, 0, 0, 1, 1, 0],
        [0, 0, 0, 1, 0, 1],
        [0, 1, 0, 0, 0, 1],
    ], dtype=float)

    def build(language: str):
        fig, ax = plt.subplots(figsize=(9, 6))
        image = ax.imshow(matrix, cmap="Blues", vmin=0, vmax=1)
        ax.set_xticks(range(len(observations)), observations if language == "en" else observations_ru, rotation=25, ha="right")
        ax.set_yticks(range(len(processes)), processes if language == "en" else processes_ru)
        ax.set_title(_title(language, "No single measurement identifies every turnover mechanism", "Ни одно измерение не идентифицирует все механизмы turnover"))
        for i in range(matrix.shape[0]):
            for j in range(matrix.shape[1]):
                ax.text(j, i, "✓" if matrix[i, j] else "", ha="center", va="center")
        fig.colorbar(image, ax=ax, shrink=0.7)
        return fig

    _pair("observability_map", build)


def benchmark_summary() -> None:
    rows = []
    half_life_value = float(survival_fraction(12.0, SurvivalParameters(half_life=12.0)))
    rows.append(("survival_half_life", half_life_value, 0.5, abs(half_life_value - 0.5), 1e-12))

    time = np.linspace(0.0, 40.0, 801)
    prod = np.log(2.0) / 10.0
    cohort = simulate_cohort_turnover(time, prod, SurvivalParameters(half_life=10.0))
    homogenized = simulate_homogenized_turnover(time, prod, 10.0)
    error = abs(cohort["mass"][-1] - homogenized["mass"][-1])
    rows.append(("cohort_homogenized", cohort["mass"][-1], homogenized["mass"][-1], error, 0.01))

    metrics = turnover_metrics(time, homogenized["mass"], homogenized["production"], homogenized["removal"])
    rows.append(("mass_balance", metrics["balance_residual"], 0.0, abs(metrics["balance_residual"]), 0.005))

    maturation = simulate_collagen_maturation(np.linspace(0.0, 30.0, 301))
    crosslink_violation = max(0.0, -float(np.min(maturation["crosslinks"])), float(np.max(maturation["crosslinks"])) - 1.0)
    rows.append(("crosslink_bounds", crosslink_violation, 0.0, crosslink_violation, 1e-12))

    inflamed = simulate_collagen_maturation(np.linspace(0.0, 40.0, 401), inflammation_protocol=1.0)
    control = simulate_collagen_maturation(np.linspace(0.0, 40.0, 401), inflammation_protocol=0.0)
    response = float(control["mature"][-1] - inflamed["mature"][-1])
    rows.append(("inflammation_response", response, 0.0, 0.0 if response > 0 else abs(response), 1e-12))

    with (DATA_DIRECTORY / "ecm_turnover_benchmark.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["test", "value", "reference", "error", "tolerance", "passed"])
        for name, value, reference, row_error, tolerance in rows:
            writer.writerow([name, value, reference, row_error, tolerance, row_error <= tolerance])

    def build(language: str):
        fig, ax = plt.subplots(figsize=(9, 5.2))
        labels = [row[0].replace("_", " ") for row in rows]
        normalized = [max(row[3] / row[4], 1e-8) if row[4] > 0 else 1e-8 for row in rows]
        bars = ax.bar(labels, normalized)
        ax.axhline(1.0, ls="--", lw=1)
        ax.set_yscale("log")
        ax.set_ylabel(_title(language, "Error / tolerance", "Ошибка / допуск"))
        ax.set_title(_title(language, "Synthetic verification benchmark", "Синтетический верификационный benchmark"))
        ax.tick_params(axis="x", rotation=25)
        for bar, row in zip(bars, rows):
            ax.text(bar.get_x() + bar.get_width() / 2, max(bar.get_height() * 1.2, 2e-8), "PASS" if row[3] <= row[4] else "FAIL", ha="center", fontsize=9)
        return fig

    _pair("benchmark_summary", build)


def turnover_animation() -> None:
    time = np.linspace(0.0, 50.0, 51)
    result = simulate_collagen_maturation(
        time,
        stress_protocol=lambda t: 1.0 if t < 8.0 else 1.35,
        inflammation_protocol=lambda t: 0.7 if 20.0 <= t <= 30.0 else 0.0,
    )
    for language in ("en", "ru"):
        fig, ax = plt.subplots(figsize=(7.5, 4.8))
        ax.set_xlim(time[0], time[-1])
        ymax = 1.1 * max(np.max(result["mature"]), np.max(result["effective_stiffness"]))
        ax.set_ylim(0.0, ymax)
        ax.set_xlabel(TEXT[language]["time"])
        ax.set_ylabel(_title(language, "State", "Состояние"))
        ax.set_title(_title(language, "ECM turnover: overload, maturation, and inflammation", "Turnover ECM: перегрузка, созревание и воспаление"))
        line_mass, = ax.plot([], [], label=_title(language, "Mature collagen", "Зрелый коллаген"))
        line_stiffness, = ax.plot([], [], label=TEXT[language]["stiffness"])
        ax.legend()

        def update(frame: int):
            line_mass.set_data(time[: frame + 1], result["mature"][: frame + 1])
            line_stiffness.set_data(time[: frame + 1], result["effective_stiffness"][: frame + 1])
            return line_mass, line_stiffness

        movie = animation.FuncAnimation(fig, update, frames=time.size, interval=100, blit=True)
        suffix = "" if language == "en" else "_ru"
        movie.save(ANIMATION_DIRECTORY / f"ecm_turnover{suffix}.gif", writer=animation.PillowWriter(fps=10), dpi=90)
        plt.close(fig)


SCENARIOS = {
    "modeling_taxonomy": modeling_taxonomy,
    "homeostatic_flux_balance": homeostatic_flux_balance,
    "survival_models": survival_models,
    "age_structured_cohorts": age_structured_cohorts,
    "cohort_vs_homogenized": cohort_vs_homogenized,
    "stress_regulated_synthesis": stress_regulated_synthesis,
    "mmp_timp_balance": mmp_timp_balance,
    "collagen_maturation": collagen_maturation,
    "crosslink_mechanics": crosslink_mechanics,
    "deposition_stretch": deposition_stretch,
    "pulse_chase": pulse_chase,
    "overload_adaptation": overload_adaptation,
    "transient_inflammation": transient_inflammation,
    "pathology_modes": pathology_modes,
    "multicomponent_ecm": multicomponent_ecm,
    "spatial_degradation_front": spatial_degradation_front,
    "mechanics_coupling": mechanics_coupling,
    "identifiability": identifiability,
    "observability_map": observability_map,
    "benchmark_summary": benchmark_summary,
    "turnover_animation": turnover_animation,
}


def render_scenario(name: str) -> None:
    try:
        scenario = SCENARIOS[name]
    except KeyError as exc:
        raise ValueError(f"Unknown Tutorial 10 scenario: {name}") from exc
    scenario()
