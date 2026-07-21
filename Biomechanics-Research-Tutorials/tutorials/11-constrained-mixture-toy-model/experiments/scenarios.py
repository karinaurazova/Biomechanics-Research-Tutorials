"""Localized result generation for Tutorial 11."""

from __future__ import annotations
from functools import lru_cache
import csv
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
from common import ANIMATION_DIRECTORY, DATA_DIRECTORY, TEXT, save_figure
from biomechanics_tutorials.constrained_mixture import (
    MixtureSimulationParameters,
    generic_loading_protocol,
    cohort_elastic_stretch,
    fiber_specific_tension,
    history_truncation_error,
    initialize_generic_constituents,
    mixture_mass_fractions,
    model_state_count,
    imaging_to_mixture_prior,
    simulate_constrained_mixture,
    simulate_homogenized_mixture,
    survival_fraction,
)


def _t(language, en, ru):
    return en if language == "en" else ru


def _component_label(language: str, name: str) -> str:
    labels = {
        "cardiomyocytes": ("primary fibers / cells", "основные волокна / клетки"),
        "collagen_plus": ("collagen +45°", "коллаген +45°"),
        "collagen_minus": ("collagen −45°", "коллаген −45°"),
        "matrix": ("matrix", "матрикс"),
    }
    en, ru = labels.get(name, (name, name))
    return en if language == "en" else ru


def _loading_label(language: str, name: str) -> str:
    labels = {
        "pressure-like": ("transverse-dominated", "поперечно-доминирующий"),
        "volume-like": ("axial-dominated", "продольно-доминирующий"),
    }
    en, ru = labels.get(name, (name, name))
    return en if language == "en" else ru


def _pair(stem, builder):
    for language in ("en", "ru"):
        save_figure(builder(language), stem, language)


@lru_cache(maxsize=None)
def _result(mode: str, duration: int = 100, points: int = 251):
    time = np.linspace(0.0, float(duration), points)
    constituents = initialize_generic_constituents()
    return (
        time,
        constituents,
        simulate_constrained_mixture(
            time,
            generic_loading_protocol(mode),
            constituents,
            MixtureSimulationParameters(history_cutoff_fraction=1e-7),
        ),
    )


def model_taxonomy():
    counts = model_state_count(4, 250, 1)

    def build(language):
        fig, ax = plt.subplots(figsize=(8.8, 5.2))
        labels = (
            ["Kinematic growth", "Homogenized mixture", "Full cohort history"]
            if language == "en"
            else ["Кинематический рост", "Гомогенизированная смесь", "Полная история когорт"]
        )
        vals = [
            counts["kinematic_growth"],
            counts["homogenized_mixture"],
            counts["full_history_mixture"],
        ]
        ax.bar(labels, vals)
        ax.set_yscale("log")
        ax.tick_params(axis="x", rotation=15)
        ax.set_ylabel(_t(language, "Approximate state count", "Приблизительное число состояний"))
        ax.set_title(
            _t(
                language,
                "Model choice changes both biology and computational memory",
                "Выбор модели меняет и биологию, и вычислительную память",
            )
        )
        return fig

    _pair("model_taxonomy", build)


def mixture_architecture():
    names = ["Cardiomyocytes", "Collagen +45°", "Collagen −45°", "Matrix"]
    names_ru = ["Кардиомиоциты", "Коллаген +45°", "Коллаген −45°", "Матрикс"]
    masses = [0.58, 0.12, 0.12, 0.18]
    half = [45, 18, 18, 70]
    prestretch = [1.06, 1.04, 1.04, 1.0]

    def build(language):
        fig, axes = plt.subplots(1, 3, figsize=(13, 4.6))
        labels = names if language == "en" else names_ru
        axes[0].bar(labels, masses)
        axes[0].set_ylabel(TEXT[language]["fraction"])
        axes[0].tick_params(axis="x", rotation=20)
        axes[1].bar(labels, half)
        axes[1].set_ylabel(_t(language, "Half-life", "Период полураспада"))
        axes[1].tick_params(axis="x", rotation=20)
        axes[2].bar(labels, prestretch)
        axes[2].axhline(1, ls="--", lw=1)
        axes[2].set_ylabel(_t(language, "Deposition stretch", "Удлинение отложения"))
        axes[2].tick_params(axis="x", rotation=20)
        fig.suptitle(
            _t(
                language,
                "Generic fibrous constrained mixture",
                "Универсальная constrained-mixture модель волокнистой ткани",
            )
        )
        return fig

    _pair("mixture_architecture", build)


def homeostatic_initialization():
    time, cons, res = _result("homeostasis", 60, 201)

    def build(language):
        fig, axes = plt.subplots(1, 2, figsize=(11, 4.7))
        for c in cons:
            axes[0].plot(time, res["mass"][c.name], label=_component_label(language, c.name))
            axes[1].plot(time, res["stress"][c.name], label=_component_label(language, c.name))
        axes[0].set_xlabel(TEXT[language]["time"])
        axes[0].set_ylabel(TEXT[language]["mass"])
        axes[1].set_xlabel(TEXT[language]["time"])
        axes[1].set_ylabel(TEXT[language]["stress"])
        axes[0].set_title(
            _t(language, "Balanced production and removal", "Баланс производства и удаления")
        )
        axes[1].set_title(
            _t(
                language,
                "Constituent homeostatic stress",
                "Гомеостатические напряжения компонентов",
            )
        )
        axes[0].legend(fontsize=8)
        axes[1].legend(fontsize=8)
        return fig

    _pair("homeostatic_initialization", build)


def cohort_survival():
    age = np.linspace(0, 100, 400)

    def build(language):
        fig, ax = plt.subplots(figsize=(8.4, 5))
        for half, label_en, label_ru in [
            (12, "collagen", "коллаген"),
            (45, "primary family", "основное семейство"),
            (70, "matrix", "матрикс"),
        ]:
            label = label_en if language == "en" else label_ru
            ax.plot(age, survival_fraction(age, half), label=f"{label}: t1/2={half}")
        ax.axhline(0.5, ls="--", lw=1)
        ax.set_xlabel(TEXT[language]["age"])
        ax.set_ylabel(_t(language, "Surviving fraction", "Доля сохранившегося материала"))
        ax.set_title(
            _t(
                language,
                "Different constituents retain different histories",
                "Разные компоненты сохраняют разную историю",
            )
        )
        ax.legend()
        return fig

    _pair("cohort_survival", build)


def deposition_stretch():
    stretch = np.linspace(0.95, 1.18, 250)

    def build(language):
        fig, axes = plt.subplots(1, 2, figsize=(11, 4.7))
        for gh in [1.0, 1.04, 1.08]:
            axes[0].plot(stretch, fiber_specific_tension(stretch * gh, 8, 8), label=f"G_h={gh:.2f}")
        axes[0].set_xlabel(TEXT[language]["stretch"])
        axes[0].set_ylabel(TEXT[language]["stress"])
        axes[0].legend()
        birth = np.array([1.0, 1.08, 1.16])
        current = 1.1
        for gh in [1.0, 1.04, 1.08]:
            axes[1].plot(
                birth, cohort_elastic_stretch(current, birth, gh), marker="o", label=f"G_h={gh:.2f}"
            )
        axes[1].set_xlabel(_t(language, "Stretch at deposition", "Удлинение при отложении"))
        axes[1].set_ylabel(_t(language, "Current elastic stretch", "Текущее упругое удлинение"))
        axes[1].legend()
        fig.suptitle(
            _t(
                language,
                "Deposition stretch stores cohort-specific prestress",
                "Deposition stretch задаёт преднапряжение каждой когорты",
            )
        )
        return fig

    _pair("deposition_stretch", build)


def stress_decomposition():
    time, cons, res = _result("combined", 90, 241)

    def build(language):
        fig, axes = plt.subplots(1, 2, figsize=(11, 4.8))
        bottom = np.zeros_like(time)
        for c in cons:
            y = np.maximum(res["stress"][c.name], 0)
            axes[0].fill_between(
                time, bottom, bottom + y, label=_component_label(language, c.name), alpha=0.75
            )
            bottom += y
        for c in cons:
            axes[1].plot(time, res["mass"][c.name], label=_component_label(language, c.name))
        axes[0].set_xlabel(TEXT[language]["time"])
        axes[0].set_ylabel(TEXT[language]["stress"])
        axes[1].set_xlabel(TEXT[language]["time"])
        axes[1].set_ylabel(TEXT[language]["mass"])
        axes[0].set_title(
            _t(
                language,
                "Mixture stress is a constituent sum",
                "Напряжение смеси — сумма вкладов компонентов",
            )
        )
        axes[1].set_title(
            _t(
                language,
                "Masses evolve independently",
                "Массы компонентов эволюционируют независимо",
            )
        )
        axes[0].legend(fontsize=8)
        axes[1].legend(fontsize=8)
        return fig

    _pair("stress_decomposition", build)


def _overload_plot(mode, stem, title_en, title_ru):
    time, cons, res = _result(mode, 100, 251)
    fractions = mixture_mass_fractions(res)

    def build(language):
        fig, axes = plt.subplots(2, 2, figsize=(11, 8))
        axes[0, 0].plot(time, res["stretch"]["cardiomyocytes"])
        axes[0, 0].set_ylabel(TEXT[language]["stretch"])
        axes[0, 1].plot(time, res["total_stress"])
        axes[0, 1].set_ylabel(TEXT[language]["stress"])
        for c in cons:
            axes[1, 0].plot(time, res["mass"][c.name], label=_component_label(language, c.name))
        for name, y in fractions.items():
            axes[1, 1].plot(time, y, label=_component_label(language, name))
        axes[1, 0].set_ylabel(TEXT[language]["mass"])
        axes[1, 1].set_ylabel(TEXT[language]["fraction"])
        for ax in axes.flat:
            ax.set_xlabel(TEXT[language]["time"])
        axes[1, 0].legend(fontsize=7)
        axes[1, 1].legend(fontsize=7)
        fig.suptitle(_t(language, title_en, title_ru))
        return fig

    _pair(stem, build)


def pressure_overload():
    _overload_plot(
        "pressure",
        "pressure_overload",
        "Pressure-like overload: cross-fiber demand and fibrosis",
        "Pressure-like перегрузка: поперечный стимул и фиброз",
    )


def volume_overload():
    _overload_plot(
        "volume",
        "volume_overload",
        "Volume-like overload: fiber stretch and myocyte adaptation",
        "Продольно-доминирующее нагружение: растяжение и адаптация основного семейства",
    )


def overload_comparison():
    tp, _, rp = _result("pressure", 100, 251)
    tv, _, rv = _result("volume", 100, 251)

    def build(language):
        fig, axes = plt.subplots(1, 3, figsize=(13, 4.5))
        for t, r, label in [(tp, rp, "pressure-like"), (tv, rv, "volume-like")]:
            localized = _loading_label(language, label)
            axes[0].plot(t, r["mass"]["cardiomyocytes"], label=localized)
            axes[1].plot(
                t,
                r["mass"]["collagen_plus"] + r["mass"]["collagen_minus"],
                label=localized,
            )
            axes[2].plot(t, r["total_stress"], label=localized)
        titles_en = ["Cardiomyocyte mass", "Collagen mass", "Total stress"]
        titles_ru = ["Масса основного семейства", "Масса коллагена", "Полное напряжение"]
        for i, ax in enumerate(axes):
            ax.set_xlabel(TEXT[language]["time"])
            ax.set_title((titles_en if language == "en" else titles_ru)[i])
            ax.legend()
        fig.suptitle(
            _t(
                language,
                "Constituent-specific laws produce different phenotypes",
                "Компонент-специфические законы формируют разные фенотипы",
            )
        )
        return fig

    _pair("overload_comparison", build)


def reversal():
    ts, _, rs = _result("combined", 110, 276)
    tr, _, rr = _result("reversal", 110, 276)

    def build(language):
        fig, axes = plt.subplots(1, 2, figsize=(11, 4.7))
        axes[0].plot(ts, rs["total_mass"], label=_t(language, "sustained", "длительная"))
        axes[0].plot(tr, rr["total_mass"], label=_t(language, "reversal", "снятие нагрузки"))
        axes[1].plot(ts, rs["total_stress"], label=_t(language, "sustained", "длительная"))
        axes[1].plot(tr, rr["total_stress"], label=_t(language, "reversal", "снятие нагрузки"))
        axes[0].set_ylabel(TEXT[language]["mass"])
        axes[1].set_ylabel(TEXT[language]["stress"])
        for ax in axes:
            ax.set_xlabel(TEXT[language]["time"])
            ax.legend()
        fig.suptitle(
            _t(
                language,
                "Reversal is partial because old and new cohorts coexist",
                "Обратимость неполна, поскольку старые и новые когорты сосуществуют",
            )
        )
        return fig

    _pair("reversal", build)


def fibrosis_hypertrophy():
    t, _, r = _result("combined", 100, 251)
    myo = r["mass"]["cardiomyocytes"]
    col = r["mass"]["collagen_plus"] + r["mass"]["collagen_minus"]

    def build(language):
        fig, ax = plt.subplots(figsize=(7.2, 6))
        points = ax.scatter(myo, col, c=t, s=18)
        fig.colorbar(points, ax=ax, label=TEXT[language]["time"])
        ax.set_xlabel(_t(language, "Primary-family mass", "Масса основного семейства"))
        ax.set_ylabel(_t(language, "Collagen mass", "Масса коллагена"))
        ax.set_title(
            _t(
                language,
                "Hypertrophy and fibrosis are coupled but distinct axes",
                "Гипертрофия и фиброз — связанные, но разные оси",
            )
        )
        return fig

    _pair("fibrosis_hypertrophy", build)


def collagen_degradation():
    time = np.linspace(0, 90, 226)
    cons = initialize_generic_constituents()
    base = simulate_constrained_mixture(time, generic_loading_protocol("combined"), cons)
    degraded = [
        c
        if "collagen" not in c.name
        else c.__class__(**{**c.__dict__, "half_life": 7.0, "removal_gain": 1.2})
        for c in cons
    ]
    deg = simulate_constrained_mixture(time, generic_loading_protocol("combined"), degraded)

    def build(language):
        fig, axes = plt.subplots(1, 2, figsize=(11, 4.7))
        for r, label in [
            (base, _t(language, "baseline turnover", "базовый turnover")),
            (deg, _t(language, "accelerated degradation", "ускоренная деградация")),
        ]:
            axes[0].plot(
                time, r["mass"]["collagen_plus"] + r["mass"]["collagen_minus"], label=label
            )
            axes[1].plot(time, r["total_stress"], label=label)
        axes[0].set_ylabel(_t(language, "Collagen mass", "Масса коллагена"))
        axes[1].set_ylabel(TEXT[language]["stress"])
        for ax in axes:
            ax.set_xlabel(TEXT[language]["time"])
            ax.legend()
        fig.suptitle(
            _t(
                language,
                "Collagen loss alters passive mechanics and the remaining stimulus",
                "Потеря коллагена изменяет пассивную механику и последующий стимул",
            )
        )
        return fig

    _pair("collagen_degradation", build)


def history_dependence():
    time = np.linspace(0, 100, 251)
    cons = initialize_generic_constituents()
    a = simulate_constrained_mixture(time, generic_loading_protocol("reversal"), cons)
    b = simulate_constrained_mixture(time, generic_loading_protocol("homeostasis"), cons)

    def build(language):
        fig, axes = plt.subplots(1, 2, figsize=(11, 4.7))
        axes[0].plot(
            time,
            a["total_stress"],
            label=_t(language, "loaded then unloaded", "нагружение и разгрузка"),
        )
        axes[0].plot(
            time, b["total_stress"], label=_t(language, "always baseline", "всегда baseline")
        )
        axes[1].plot(
            time,
            a["total_mass"],
            label=_t(language, "loaded then unloaded", "нагружение и разгрузка"),
        )
        axes[1].plot(
            time, b["total_mass"], label=_t(language, "always baseline", "всегда baseline")
        )
        axes[0].set_ylabel(TEXT[language]["stress"])
        axes[1].set_ylabel(TEXT[language]["mass"])
        for ax in axes:
            ax.set_xlabel(TEXT[language]["time"])
            ax.legend()
        fig.suptitle(
            _t(
                language,
                "Same present load does not imply the same internal state",
                "Одинаковая текущая нагрузка не означает одинаковое внутреннее состояние",
            )
        )
        return fig

    _pair("history_dependence", build)


def cohort_vs_homogenized():
    time = np.linspace(0, 100, 251)
    cons = initialize_generic_constituents()
    protocol = generic_loading_protocol("combined")
    full = simulate_constrained_mixture(time, protocol, cons)
    hom = simulate_homogenized_mixture(time, protocol, cons)
    err = np.abs(full["total_stress"] - hom["total_stress"]) / np.maximum(
        np.abs(full["total_stress"]), 1e-9
    )

    def build(language):
        fig, axes = plt.subplots(1, 3, figsize=(13, 4.5))
        axes[0].plot(time, full["total_mass"], label=_t(language, "full history", "полная история"))
        axes[0].plot(
            time,
            hom["total_mass"],
            "--",
            label=_t(language, "homogenized", "гомогенизированная"),
        )
        axes[1].plot(
            time,
            full["total_stress"],
            label=_t(language, "full history", "полная история"),
        )
        axes[1].plot(
            time,
            hom["total_stress"],
            "--",
            label=_t(language, "homogenized", "гомогенизированная"),
        )
        axes[2].plot(time, err)
        axes[0].set_ylabel(TEXT[language]["mass"])
        axes[1].set_ylabel(TEXT[language]["stress"])
        axes[2].set_ylabel(TEXT[language]["error"])
        for ax in axes:
            ax.set_xlabel(TEXT[language]["time"])
            ax.legend() if ax is not axes[2] else None
        fig.suptitle(
            _t(
                language,
                "Homogenization compresses history and introduces approximation error",
                "Гомогенизация сжимает историю и вносит ошибку приближения",
            )
        )
        return fig

    _pair("cohort_vs_homogenized", build)


def history_truncation():
    time, cons, res = _result("combined", 100, 251)
    c = next(x for x in cons if x.name == "collagen_plus")
    cohorts = res["final_cohorts"]["collagen_plus"]
    current_stretch = res["stretch"]["collagen_plus"][-1]
    windows = np.linspace(2, 100, 60)
    errors = [history_truncation_error(current_stretch, cohorts, c, time[-1], w) for w in windows]

    def build(language):
        fig, ax = plt.subplots(figsize=(8.3, 5))
        ax.plot(windows, errors)
        ax.set_yscale("log")
        ax.set_xlabel(_t(language, "Retained history window", "Сохраняемое окно истории"))
        ax.set_ylabel(TEXT[language]["error"])
        ax.set_title(
            _t(
                language,
                "Short history reduces cost but can erase load-bearing cohorts",
                "Короткая история снижает стоимость, но удаляет несущие когорты",
            )
        )
        return fig

    _pair("history_truncation", build)


def stability_map():
    gains = np.linspace(0.3, 3.0, 13)
    half = np.linspace(6, 45, 13)
    final = np.zeros((len(half), len(gains)))
    time = np.linspace(0, 70, 141)
    base = initialize_generic_constituents()
    for i, h in enumerate(half):
        for j, g in enumerate(gains):
            modified = [
                c
                if "collagen" not in c.name
                else c.__class__(
                    **{**c.__dict__, "half_life": float(h), "production_gain": float(g)}
                )
                for c in base
            ]
            r = simulate_homogenized_mixture(time, generic_loading_protocol("pressure"), modified)
            final[i, j] = r["total_mass"][-1] / r["total_mass"][0]

    def build(language):
        fig, ax = plt.subplots(figsize=(7.6, 6))
        im = ax.contourf(gains, half, final, levels=25)
        fig.colorbar(im, ax=ax, label=_t(language, "Final mass ratio", "Итоговое отношение масс"))
        ax.set_xlabel(
            _t(language, "Collagen production gain", "Чувствительность синтеза коллагена")
        )
        ax.set_ylabel(_t(language, "Collagen half-life", "Период полураспада коллагена"))
        ax.set_title(
            _t(
                language,
                "Mechanobiological phenotype depends on kinetics and feedback",
                "Механобиологический фенотип зависит от кинетики и обратной связи",
            )
        )
        return fig

    _pair("stability_map", build)


def half_life_sensitivity():
    time = np.linspace(0, 90, 181)
    base = initialize_generic_constituents()

    def build(language):
        fig, axes = plt.subplots(1, 2, figsize=(11, 4.7))
        for h in [8, 18, 35]:
            mod = [
                c if "collagen" not in c.name else c.__class__(**{**c.__dict__, "half_life": h})
                for c in base
            ]
            r = simulate_homogenized_mixture(time, generic_loading_protocol("pressure"), mod)
            axes[0].plot(
                time, r["mass"]["collagen_plus"] + r["mass"]["collagen_minus"], label=f"t1/2={h}"
            )
            axes[1].plot(time, r["total_stress"], label=f"t1/2={h}")
        axes[0].set_ylabel(_t(language, "Collagen mass", "Масса коллагена"))
        axes[1].set_ylabel(TEXT[language]["stress"])
        for ax in axes:
            ax.set_xlabel(TEXT[language]["time"])
            ax.legend()
        fig.suptitle(
            _t(
                language,
                "Turnover time changes both adaptation speed and mechanical memory",
                "Время turnover меняет скорость адаптации и механическую память",
            )
        )
        return fig

    _pair("half_life_sensitivity", build)


def polarimetry_bridge():
    x = np.linspace(-1, 1, 100)
    y = np.linspace(-1, 1, 80)
    X, Y = np.meshgrid(x, y)
    angle = 35 * np.sin(np.pi * X) * np.cos(0.5 * np.pi * Y)
    beta = np.clip(0.25 + 0.7 * np.exp(-2 * (X**2 + Y**2)), 0, 1)
    structural_contrast = 0.3 + 0.7 * (X + 1) / 2
    prior = imaging_to_mixture_prior(angle, beta, structural_contrast)

    def build(language):
        fig, axes = plt.subplots(1, 4, figsize=(15, 4))
        data = [
            angle,
            beta,
            prior["collagen_fraction"],
            prior["family_plus_degrees"] - prior["family_minus_degrees"],
        ]
        titles_en = ["Mean angle", "Directional order β", "Fibrous-mass prior", "Family separation"]
        titles_ru = [
            "Средний угол",
            "Ориентационный порядок β",
            "Априорная доля волокнистой фазы",
            "Разведение семейств",
        ]
        for ax, z, title in zip(axes, data, titles_en if language == "en" else titles_ru):
            im = ax.imshow(z, origin="lower", aspect="auto")
            fig.colorbar(im, ax=ax, shrink=0.8)
            ax.set_title(title)
            ax.set_xticks([])
            ax.set_yticks([])
        fig.suptitle(
            _t(
                language,
                "Synthetic bridge from orientation-sensitive imaging to mixture priors",
                "Синтетический переход от ориентационно-чувствительной визуализации к prior-параметрам смеси",
            )
        )
        return fig

    _pair("polarimetry_bridge", build)


def observability_map():
    mechanisms_en = ["Mass", "Production", "Removal", "Age", "Prestretch", "Orientation", "Stress"]
    mechanisms_ru = [
        "Масса",
        "Синтез",
        "Удаление",
        "Возраст",
        "Предрастяжение",
        "Ориентация",
        "Напряжение",
    ]
    observables_en = [
        "Histology",
        "Orientation imaging",
        "Mechanical test",
        "Isotope tracing",
        "Biomarkers",
        "Imaging geometry",
    ]
    observables_ru = [
        "Гистология",
        "Ориентационная визуализация",
        "Механический тест",
        "Изотопное мечение",
        "Биомаркеры",
        "Геометрия по данным визуализации",
    ]
    matrix = np.array(
        [
            [1, 1, 0, 1, 1, 1],
            [0, 0, 0, 1, 1, 0],
            [0, 0, 0, 1, 1, 0],
            [0, 0, 0, 1, 0, 0],
            [0, 0, 1, 0, 0, 0],
            [1, 1, 1, 0, 0, 1],
            [0, 0, 1, 0, 0, 1],
        ]
    )

    def build(language):
        fig, ax = plt.subplots(figsize=(9, 5.8))
        ax.imshow(matrix, aspect="auto", vmin=0, vmax=1)
        observables = observables_en if language == "en" else observables_ru
        mechanisms = mechanisms_en if language == "en" else mechanisms_ru
        ax.set_xticks(range(len(observables)), observables, rotation=25, ha="right")
        ax.set_yticks(range(len(mechanisms)), mechanisms)
        ax.set_title(
            _t(
                language,
                "No single observation identifies the full mixture state",
                "Ни одно измерение не идентифицирует полное состояние смеси",
            )
        )
        return fig

    _pair("observability_map", build)


def identifiability():
    gains = np.linspace(0.5, 2.5, 35)
    half = np.linspace(8, 35, 35)
    G, H = np.meshgrid(gains, half)
    target = 1.28
    prediction = 1 + 0.18 * G * np.sqrt(H / 18)
    loss = (prediction - target) ** 2

    def build(language):
        fig, ax = plt.subplots(figsize=(7.5, 6))
        im = ax.contourf(G, H, np.log10(loss + 1e-6), levels=30)
        fig.colorbar(im, ax=ax, label=_t(language, "log10 loss", "log10 функции потерь"))
        ax.set_xlabel(_t(language, "Production gain", "Чувствительность синтеза"))
        ax.set_ylabel(_t(language, "Half-life", "Период полураспада"))
        ax.set_title(
            _t(
                language,
                "One endpoint admits a valley of compensating parameters",
                "Одна конечная точка допускает долину компенсирующих параметров",
            )
        )
        return fig

    _pair("identifiability", build)


def benchmark_summary():
    time = np.linspace(0, 50, 151)
    cons = initialize_generic_constituents()
    home = simulate_constrained_mixture(time, generic_loading_protocol("homeostasis"), cons)
    pressure = simulate_constrained_mixture(time, generic_loading_protocol("pressure"), cons)
    checks = [
        ("homeostatic_mass_error", abs(home["total_mass"][-1] / home["total_mass"][0] - 1), 0.025),
        (
            "pressure_collagen_gain",
            (pressure["mass"]["collagen_plus"][-1] + pressure["mass"]["collagen_minus"][-1])
            / (pressure["mass"]["collagen_plus"][0] + pressure["mass"]["collagen_minus"][0])
            - 1,
            0.005,
        ),
        ("positive_mass", float(np.min(pressure["total_mass"]) <= 0), 0.0),
        (
            "initial_stress_sum",
            abs(pressure["total_stress"][0] - sum(v[0] for v in pressure["stress"].values())),
            1e-10,
        ),
    ]
    path = DATA_DIRECTORY / "constrained_mixture_benchmark.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["check", "value", "tolerance", "passed"])
        for name, value, tol in checks:
            passed = value <= tol if name != "pressure_collagen_gain" else value >= tol
            w.writerow([name, value, tol, passed])

    def build(language):
        fig, ax = plt.subplots(figsize=(9, 5.2))
        labels_en = [
            "homeostatic mass error",
            "pressure collagen gain",
            "nonpositive mass",
            "stress-sum residual",
        ]
        labels_ru = [
            "ошибка гомеостатической массы",
            "прирост коллагена при перегрузке",
            "неположительная масса",
            "невязка суммы напряжений",
        ]
        labels = labels_en if language == "en" else labels_ru
        values = [max(abs(x[1]), 1e-12) for x in checks]
        ax.bar(labels, values)
        ax.set_yscale("log")
        ax.tick_params(axis="x", rotation=20)
        ax.set_ylabel(_t(language, "Diagnostic magnitude", "Диагностическая величина"))
        ax.set_title(
            _t(
                language,
                "Verification hierarchy: identities before biological interpretation",
                "Иерархия проверки: сначала тождества, затем биологическая интерпретация",
            )
        )
        return fig

    _pair("benchmark_summary", build)


def cohort_animation():
    time, _, res = _result("reversal", 100, 161)
    names = ["cardiomyocytes", "collagen_plus", "collagen_minus", "matrix"]
    for language in ("en", "ru"):
        fig, ax = plt.subplots(figsize=(6.4, 4.2))
        display_names = [_component_label(language, name) for name in names]
        bars = ax.bar(display_names, [res["mass"][n][0] for n in names])
        ax.set_ylim(0, max(res["total_mass"]) * 0.8)
        ax.tick_params(axis="x", rotation=18)
        ax.set_ylabel(TEXT[language]["mass"])
        title = ax.set_title("")

        def update(frame):
            for bar, name in zip(bars, names):
                bar.set_height(res["mass"][name][frame])
            title.set_text(
                _t(
                    language,
                    f"Cohort mixture at t={time[frame]:.1f}",
                    f"Состояние смеси при t={time[frame]:.1f}",
                )
            )
            return [*bars, title]

        ani = animation.FuncAnimation(
            fig, update, frames=range(0, len(time), 8), interval=120, blit=False
        )
        suffix = "" if language == "en" else "_ru"
        ani.save(ANIMATION_DIRECTORY / f"constrained_mixture{suffix}.gif", writer="pillow", dpi=70)
        plt.close(fig)


SCENARIOS = {
    "model_taxonomy": model_taxonomy,
    "mixture_architecture": mixture_architecture,
    "homeostatic_initialization": homeostatic_initialization,
    "cohort_survival": cohort_survival,
    "deposition_stretch": deposition_stretch,
    "stress_decomposition": stress_decomposition,
    "pressure_overload": pressure_overload,
    "volume_overload": volume_overload,
    "overload_comparison": overload_comparison,
    "reversal": reversal,
    "fibrosis_hypertrophy": fibrosis_hypertrophy,
    "collagen_degradation": collagen_degradation,
    "history_dependence": history_dependence,
    "cohort_vs_homogenized": cohort_vs_homogenized,
    "history_truncation": history_truncation,
    "stability_map": stability_map,
    "half_life_sensitivity": half_life_sensitivity,
    "polarimetry_bridge": polarimetry_bridge,
    "observability_map": observability_map,
    "identifiability": identifiability,
    "benchmark_summary": benchmark_summary,
    "cohort_animation": cohort_animation,
}


def render_scenario(name):
    if name not in SCENARIOS:
        raise KeyError(name)
    SCENARIOS[name]()
