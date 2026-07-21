"""Reproducible scenarios for Tutorial 12: residual stress and ring opening."""
from __future__ import annotations

import csv

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation, PillowWriter

from common import ANIMATION_DIRECTORY, DATA_DIRECTORY, TEXT, save_figure, t

from biomechanics_tutorials.plotting import PALETTE
from biomechanics_tutorials.residual_stress import (
    SectorLayer,
    closure_factor,
    equilibrated_strip,
    inverse_loss_surface,
    monte_carlo_opening_angle,
    multi_sector_angles,
    opening_sector_coordinates,
    radial_boundary_residual,
    ring_coordinates,
    solve_sector_tube,
    stress_uniformity,
)
BLUE = PALETTE["blue"]
CYAN = PALETTE["cyan"]
LIME = PALETTE["lime"]
INK = PALETTE["ink"]
SLATE = PALETTE["slate"]
RED = "#E05A5A"
ORANGE = "#FF8A34"


def _wall_coordinate(solution) -> np.ndarray:
    return (solution.radius - solution.radius[0]) / (
        solution.radius[-1] - solution.radius[0]
    )


def _pair(stem: str, builder) -> None:
    for language in ("en", "ru"):
        save_figure(builder(language), stem, language)


def modeling_taxonomy() -> None:
    def build(language: str):
        fig, axes = plt.subplots(2, 2, figsize=(12.2, 7.2))
        titles = (
            ["External prestress", "Residual stress", "Initial-stress model", "Growth / turnover origin"]
            if language == "en"
            else ["Внешнее предварительное нагружение", "Остаточное напряжение", "Модель начальных напряжений", "Рост и turnover как источник"]
        )
        bodies = (
            [
                "Stress disappears when the maintained boundary load is removed.",
                "Stress remains after external tractions vanish and is revealed by cuts.",
                "The observed geometry is used as an already stressed reference state.",
                "Incompatible growth, deposition prestretch, remodeling, swelling, or active tone create internal mismatch.",
            ]
            if language == "en"
            else [
                "Напряжение исчезает после снятия поддерживаемой внешней нагрузки.",
                "Напряжение сохраняется без внешних сил и выявляется разрезами.",
                "Наблюдаемая геометрия используется как уже напряжённое отсчётное состояние.",
                "Несовместимый рост, предрастяжение при отложении, ремоделирование, набухание или активный тонус создают внутреннее рассогласование.",
            ]
        )
        colors = ["#D8E5FF", "#D5F4EE", "#ECF8CE", "#F3E5FF"]
        for ax, title, body, color in zip(axes.flat, titles, bodies, colors):
            ax.axis("off")
            ax.text(
                0.5, 0.76, title, transform=ax.transAxes, ha="center", va="center",
                fontsize=12, fontweight="bold", wrap=True,
                bbox={"boxstyle": "round,pad=0.55", "facecolor": color, "edgecolor": BLUE},
            )
            ax.text(0.5, 0.40, body, transform=ax.transAxes, ha="center", va="center", fontsize=10.5, wrap=True)
        fig.suptitle(t(language, "Four distinct ways to represent prestress and residual stress", "Четыре разных способа представления преднапряжения и остаточных напряжений"))
        return fig

    _pair("modeling_taxonomy", build)


def opening_angle_geometry() -> None:
    angles = [0.0, 45.0, 90.0, 150.0]

    def build(language: str):
        fig, axes = plt.subplots(1, 4, figsize=(14, 3.9))
        for ax, angle in zip(axes, angles):
            xi, yi, xo, yo = opening_sector_coordinates(1.0, 1.38, angle)
            ax.plot(xi, yi, color=BLUE, lw=2.5)
            ax.plot(xo, yo, color=CYAN, lw=2.5)
            ax.plot([xi[0], xo[0]], [yi[0], yo[0]], color=SLATE)
            ax.plot([xi[-1], xo[-1]], [yi[-1], yo[-1]], color=SLATE)
            ax.set_aspect("equal")
            ax.axis("off")
            ax.set_title(f"α = {angle:.0f}°\nκ = {closure_factor(angle):.3f}")
        fig.suptitle(t(language, "The opening angle is a geometric release measure, not a stress value", "Угол раскрытия — геометрическая мера высвобождения, а не значение напряжения"))
        return fig

    _pair("opening_angle_geometry", build)


def closure_kinematics() -> None:
    layer = SectorLayer(1.0, 1.4, 100.0)
    solution = solve_sector_tube([layer], pressure=0.0)

    def build(language: str):
        fig, axes = plt.subplots(1, 3, figsize=(12.5, 4.2))
        xi, yi, xo, yo = opening_sector_coordinates(1.0, 1.4, 100.0)
        axes[0].plot(xi, yi, color=BLUE, lw=2)
        axes[0].plot(xo, yo, color=CYAN, lw=2)
        axes[0].set_title(t(language, "Stress-free open sector", "Ненапряжённый раскрытый сектор"))
        axes[0].set_aspect("equal")
        axes[0].axis("off")
        ri, rj, ro, rp = ring_coordinates(solution.current_boundaries[0], solution.current_boundaries[-1])
        axes[1].plot(ri, rj, color=BLUE, lw=2)
        axes[1].plot(ro, rp, color=CYAN, lw=2)
        axes[1].set_title(t(language, "Closed traction-free ring", "Замкнутое кольцо без внешних нагрузок"))
        axes[1].set_aspect("equal")
        axes[1].axis("off")
        x = _wall_coordinate(solution)
        axes[2].plot(x, solution.radial_stretch, label=r"$\lambda_r$")
        axes[2].plot(x, solution.circumferential_stretch, label=r"$\lambda_\theta$")
        axes[2].axhline(1.0, color=INK, ls="--", lw=1)
        axes[2].set_xlabel(TEXT[language]["normalized_radius"])
        axes[2].set_ylabel(t(language, "Principal stretch", "Главное растяжение"))
        axes[2].set_title(t(language, "Closure creates elastic accommodation", "Замыкание создаёт упругую аккомодацию"))
        axes[2].legend()
        fig.suptitle(t(language, "Sector closure maps a local stress-free state into a globally compatible ring", "Замыкание сектора переводит локально ненапряжённое состояние в совместное кольцо"))
        return fig

    _pair("closure_kinematics", build)


def unloaded_residual_stress() -> None:
    solution = solve_sector_tube([SectorLayer(1.0, 1.4, 110.0)], pressure=0.0)

    def build(language: str):
        fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.6))
        x = _wall_coordinate(solution)
        axes[0].plot(x, solution.radial_stress, label=t(language, "Radial", "Радиальное"))
        axes[0].plot(x, solution.circumferential_stress, label=t(language, "Circumferential", "Окружное"))
        axes[0].axhline(0, color=INK, lw=1)
        axes[0].set_xlabel(TEXT[language]["normalized_radius"])
        axes[0].set_ylabel(TEXT[language]["stress"])
        axes[0].legend()
        axes[0].set_title(t(language, "Self-equilibrated residual stress", "Самоуравновешенное остаточное напряжение"))
        axes[1].plot(x, solution.circumferential_stretch, color=BLUE, label=r"$\lambda_\theta$")
        axes[1].plot(x, solution.radial_stretch, color=CYAN, label=r"$\lambda_r$")
        axes[1].axhline(1, color=INK, ls="--", lw=1)
        axes[1].set_xlabel(TEXT[language]["normalized_radius"])
        axes[1].set_ylabel(TEXT[language]["stretch"])
        axes[1].legend()
        axes[1].set_title(t(language, "Residual strain is not spatially uniform", "Остаточная деформация неоднородна по толщине"))
        fig.suptitle(t(language, "Zero external traction does not imply a stress-free wall", "Отсутствие внешних сил не означает ненапряжённую стенку"))
        return fig

    _pair("unloaded_residual_stress", build)


def pressure_stress_uniformization() -> None:
    angles = [0.0, 30.0, 60.0, 100.0]
    solutions = [solve_sector_tube([SectorLayer(1.0, 1.4, a)], pressure=0.20) for a in angles]

    def build(language: str):
        fig, axes = plt.subplots(1, 2, figsize=(11, 4.8))
        for angle, solution in zip(angles, solutions):
            axes[0].plot(_wall_coordinate(solution), solution.circumferential_stress, label=f"α={angle:.0f}°")
        axes[0].set_xlabel(TEXT[language]["normalized_radius"])
        axes[0].set_ylabel(TEXT[language]["stress"])
        axes[0].set_title(t(language, "Loaded circumferential stress", "Окружное напряжение при нагружении"))
        axes[0].legend()
        uniformity = [stress_uniformity(s.circumferential_stress) for s in solutions]
        axes[1].plot(angles, uniformity, "o-", color=BLUE)
        axes[1].set_xlabel(TEXT[language]["angle"])
        axes[1].set_ylabel(t(language, "Coefficient of variation", "Коэффициент вариации"))
        axes[1].set_title(t(language, "An intermediate angle can homogenize stress", "Промежуточный угол может выравнивать напряжение"))
        fig.suptitle(t(language, "Residual stress can redistribute pressure-induced wall stress", "Остаточные напряжения перераспределяют напряжение от давления"))
        return fig

    _pair("pressure_stress_uniformization", build)


def opening_angle_sweep() -> None:
    angles = np.linspace(0.0, 180.0, 61)
    residual = []
    loaded = []
    inner_outer = []
    for angle in angles:
        unloaded = solve_sector_tube([SectorLayer(1.0, 1.4, angle)])
        pressurized = solve_sector_tube([SectorLayer(1.0, 1.4, angle)], pressure=0.2)
        residual.append(np.ptp(unloaded.circumferential_stress))
        loaded.append(stress_uniformity(pressurized.circumferential_stress))
        inner_outer.append(pressurized.circumferential_stress[0] / pressurized.circumferential_stress[-1])

    def build(language: str):
        fig, axes = plt.subplots(1, 3, figsize=(13.2, 4.4))
        axes[0].plot(angles, residual, color=BLUE)
        axes[0].set_ylabel(t(language, "Residual-stress range", "Размах остаточного напряжения"))
        axes[1].plot(angles, loaded, color=CYAN)
        axes[1].set_ylabel(t(language, "Loaded stress variation", "Неоднородность напряжения при нагрузке"))
        axes[2].plot(angles, inner_outer, color=ORANGE)
        axes[2].axhline(1.0, color=INK, ls="--", lw=1)
        axes[2].set_ylabel(t(language, "Inner / outer stress", "Напряжение внутри / снаружи"))
        for ax in axes:
            ax.set_xlabel(TEXT[language]["angle"])
        fig.suptitle(t(language, "Opening angle affects several mechanical metrics differently", "Угол раскрытия по-разному влияет на несколько механических показателей"))
        return fig

    _pair("opening_angle_sweep", build)


def axial_prestretch_coupling() -> None:
    axial = [0.9, 1.0, 1.1, 1.2]
    solutions = [solve_sector_tube([SectorLayer(1.0, 1.4, 80.0)], pressure=0.18, axial_stretch=value) for value in axial]

    def build(language: str):
        fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.5))
        for value, solution in zip(axial, solutions):
            axes[0].plot(_wall_coordinate(solution), solution.circumferential_stress, label=f"λz={value:.1f}")
        axes[0].set_xlabel(TEXT[language]["normalized_radius"])
        axes[0].set_ylabel(TEXT[language]["stress"])
        axes[0].legend()
        axes[0].set_title(t(language, "Circumferential stress", "Окружное напряжение"))
        axes[1].plot(axial, [s.current_boundaries[0] for s in solutions], "o-", label=t(language, "Inner radius", "Внутренний радиус"))
        axes[1].plot(axial, [s.current_boundaries[-1] for s in solutions], "s-", label=t(language, "Outer radius", "Наружный радиус"))
        axes[1].set_xlabel(t(language, "Axial stretch", "Осевое растяжение"))
        axes[1].set_ylabel(TEXT[language]["radius"])
        axes[1].legend()
        axes[1].set_title(t(language, "Geometry couples to axial prestretch", "Геометрия связана с осевым предрастяжением"))
        fig.suptitle(t(language, "A ring-opening measurement alone does not determine the three-dimensional prestress state", "Одно измерение раскрытия кольца не определяет трёхмерное предварительно напряжённое состояние"))
        return fig

    _pair("axial_prestretch_coupling", build)


def material_anisotropy() -> None:
    iso = solve_sector_tube([SectorLayer(1.0, 1.4, 70.0, shear_modulus=1.0)], pressure=0.18)
    mild = solve_sector_tube([SectorLayer(1.0, 1.4, 70.0, 1.0, 2.0, 1.04)], pressure=0.18)
    strong = solve_sector_tube([SectorLayer(1.0, 1.4, 70.0, 1.0, 7.0, 1.02)], pressure=0.18)

    def build(language: str):
        fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.5))
        labels = [t(language, "Isotropic", "Изотропная"), t(language, "Mild reinforcement", "Умеренное армирование"), t(language, "Strong reinforcement", "Сильное армирование")]
        for solution, label in zip([iso, mild, strong], labels):
            axes[0].plot(_wall_coordinate(solution), solution.circumferential_stress, label=label)
        axes[0].set_xlabel(TEXT[language]["normalized_radius"])
        axes[0].set_ylabel(TEXT[language]["stress"])
        axes[0].legend()
        axes[0].set_title(t(language, "Same opening angle, different stress", "Один угол раскрытия, разные напряжения"))
        axes[1].bar(labels, [stress_uniformity(s.circumferential_stress) for s in [iso, mild, strong]])
        axes[1].set_ylabel(t(language, "Stress coefficient of variation", "Коэффициент вариации напряжения"))
        axes[1].tick_params(axis="x", rotation=15)
        axes[1].set_title(t(language, "Constitutive assumptions affect the inverse result", "Определяющие предположения влияют на обратный результат"))
        fig.suptitle(t(language, "Opening geometry cannot be converted to stress without a constitutive model", "Геометрию раскрытия нельзя преобразовать в напряжение без определяющей модели"))
        return fig

    _pair("material_anisotropy", build)


def multilayer_tube() -> None:
    layers = [
        SectorLayer(1.0, 1.18, 135.0, 1.3),
        SectorLayer(1.18, 1.48, 55.0, 0.75, 3.0, 1.03),
    ]
    solution = solve_sector_tube(layers, pressure=0.18, axial_stretch=1.08)

    def build(language: str):
        fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.7))
        x = _wall_coordinate(solution)
        axes[0].plot(x, solution.circumferential_stress, color=BLUE, label=t(language, "Circumferential", "Окружное"))
        axes[0].plot(x, solution.radial_stress, color=CYAN, label=t(language, "Radial", "Радиальное"))
        interface = (solution.current_boundaries[1] - solution.radius[0]) / (solution.radius[-1] - solution.radius[0])
        axes[0].axvline(interface, color=INK, ls="--", label=t(language, "Layer interface", "Граница слоёв"))
        axes[0].set_xlabel(TEXT[language]["normalized_radius"])
        axes[0].set_ylabel(TEXT[language]["stress"])
        axes[0].legend()
        axes[0].set_title(t(language, "Layer-specific stress distribution", "Распределение напряжений по слоям"))
        axes[1].bar([t(language, "Inner layer", "Внутренний слой"), t(language, "Outer layer", "Наружный слой")], [layers[0].opening_angle_degrees, layers[1].opening_angle_degrees])
        axes[1].set_ylabel(TEXT[language]["angle"])
        axes[1].set_title(t(language, "Each layer can have its own released geometry", "Каждый слой может иметь собственную геометрию высвобождения"))
        fig.suptitle(t(language, "A single opening angle can hide layer-specific residual states", "Один угол раскрытия может скрывать разные остаточные состояния слоёв"))
        return fig

    _pair("multilayer_tube", build)


def layer_separation() -> None:
    z = np.linspace(-0.5, 0.5, 500)
    target_whole = np.where(z < 0.0, -0.018, 0.025)
    whole = equilibrated_strip(z, target_whole, np.where(z < 0.0, 1.5, 0.8))
    lower = equilibrated_strip(z[z < 0.0], target_whole[z < 0.0], 1.5)
    upper = equilibrated_strip(z[z >= 0.0], target_whole[z >= 0.0], 0.8)

    def build(language: str):
        fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.6))
        axes[0].plot(z, target_whole, color=SLATE, label=t(language, "Layer natural strain", "Естественная деформация слоя"))
        axes[0].plot(z, whole["strain"], color=BLUE, label=t(language, "Compatible strain", "Совместная деформация"))
        axes[0].set_xlabel(t(language, "Thickness coordinate", "Координата по толщине"))
        axes[0].set_ylabel(t(language, "Axial strain", "Продольная деформация"))
        axes[0].legend()
        labels = [t(language, "Bonded wall", "Связанная стенка"), t(language, "Inner layer", "Внутренний слой"), t(language, "Outer layer", "Наружный слой")]
        axes[1].bar(labels, [whole["curvature"], lower["curvature"], upper["curvature"]])
        axes[1].set_ylabel(TEXT[language]["curvature"])
        axes[1].tick_params(axis="x", rotation=15)
        axes[1].set_title(t(language, "Layer separation releases hidden mismatch", "Разделение слоёв высвобождает скрытое рассогласование"))
        fig.suptitle(t(language, "Residual stress can exist between layers even when the intact sample appears flat", "Межслойные остаточные напряжения возможны даже в визуально плоском образце"))
        return fig

    _pair("layer_separation", build)


def asymmetric_multi_sector() -> None:
    locations, angles = multi_sector_angles(95.0, 35.0, sectors=48, harmonic=2)
    metrics = []
    for angle in angles:
        solution = solve_sector_tube([SectorLayer(1.0, 1.4, float(angle))], pressure=0.16)
        metrics.append(stress_uniformity(solution.circumferential_stress))

    def build(language: str):
        fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.8), subplot_kw={"projection": None})
        axes[0].plot(np.rad2deg(locations), angles, color=BLUE)
        axes[0].axhline(np.mean(angles), color=INK, ls="--", label=t(language, "Single-angle approximation", "Приближение одним углом"))
        axes[0].set_xlabel(t(language, "Circumferential location, degrees", "Положение по окружности, градусы"))
        axes[0].set_ylabel(TEXT[language]["angle"])
        axes[0].legend()
        axes[1].scatter(angles, metrics, c=np.rad2deg(locations), cmap="viridis", s=35)
        axes[1].set_xlabel(TEXT[language]["angle"])
        axes[1].set_ylabel(t(language, "Loaded stress variation", "Неоднородность напряжения при нагрузке"))
        axes[1].set_title(t(language, "Local sectors predict different mechanics", "Локальные секторы дают разную механику"))
        fig.suptitle(t(language, "Noncircular openings require more than one global angle", "Несимметричное раскрытие нельзя описать одним глобальным углом"))
        return fig

    _pair("asymmetric_multi_sector", build)


def axial_strip_curling() -> None:
    z = np.linspace(-0.5, 0.5, 501)
    profiles = {
        t("en", "Linear", "Линейный"): 0.05 * z,
        t("en", "Boundary layer", "Пограничный слой"): 0.025 * np.tanh(8 * z),
        t("en", "Quadratic", "Квадратичный"): 0.035 * (z**2 - np.mean(z**2)),
    }

    def build(language: str):
        names = [
            t(language, "Linear", "Линейный"),
            t(language, "Boundary layer", "Пограничный слой"),
            t(language, "Quadratic", "Квадратичный"),
        ]
        values = list(profiles.values())
        results = [equilibrated_strip(z, value) for value in values]
        fig, axes = plt.subplots(1, 2, figsize=(10.7, 4.6))
        for name, value in zip(names, values):
            axes[0].plot(z, value, label=name)
        axes[0].set_xlabel(t(language, "Thickness coordinate", "Координата по толщине"))
        axes[0].set_ylabel(t(language, "Released eigenstrain", "Высвобождаемая собственная деформация"))
        axes[0].legend()
        axes[1].bar(names, [r["curvature"] for r in results])
        axes[1].set_ylabel(TEXT[language]["curvature"])
        axes[1].tick_params(axis="x", rotation=15)
        axes[1].set_title(t(language, "Not every strain profile produces the same curling", "Разные профили деформации создают разное закручивание"))
        fig.suptitle(t(language, "Strip curling complements ring opening by revealing axial or through-thickness mismatch", "Закручивание полосы дополняет раскрытие кольца и выявляет осевое или толщинное рассогласование"))
        return fig

    _pair("axial_strip_curling", build)


def solid_organ_slice() -> None:
    z = np.linspace(-1.0, 1.0, 501)
    transmural = 0.03 * np.sin(np.pi * z / 2)
    heterogeneous = 0.02 * np.tanh(4 * z) + 0.007 * np.sin(3 * np.pi * z)
    a = equilibrated_strip(z, transmural)
    b = equilibrated_strip(z, heterogeneous)

    def build(language: str):
        fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.6))
        axes[0].plot(z, transmural, label=t(language, "Smooth transmural mismatch", "Плавное трансмуральное рассогласование"))
        axes[0].plot(z, heterogeneous, label=t(language, "Regional heterogeneity", "Региональная неоднородность"))
        axes[0].set_xlabel(t(language, "Normalized depth", "Нормированная глубина"))
        axes[0].set_ylabel(t(language, "Local natural strain", "Локальная естественная деформация"))
        axes[0].legend()
        axes[1].bar([t(language, "Smooth", "Плавный"), t(language, "Heterogeneous", "Неоднородный")], [a["curvature"], b["curvature"]])
        axes[1].set_ylabel(TEXT[language]["curvature"])
        axes[1].set_title(t(language, "A cut slice reports only selected moments of the hidden field", "Разрез сообщает лишь отдельные моменты скрытого поля"))
        fig.suptitle(t(language, "Cut-release methods extend beyond vessels to myocardium, skin, intestine, and other soft tissues", "Методы высвобождения разрезом применимы не только к сосудам, но и к миокарду, коже, кишечнику и другим мягким тканям"))
        return fig

    _pair("solid_organ_slice", build)


def growth_gradient_strip() -> None:
    z = np.linspace(-0.5, 0.5, 401)
    amplitudes = np.linspace(0.0, 0.08, 9)
    curvatures = []
    energies = []
    for amplitude in amplitudes:
        result = equilibrated_strip(z, amplitude * z, 1.0 + 0.4 * z)
        curvatures.append(result["curvature"])
        energies.append(np.trapezoid(np.asarray(result["stress"]) ** 2, z) / 2)

    def build(language: str):
        fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.5))
        axes[0].plot(amplitudes, curvatures, "o-", color=BLUE)
        axes[0].set_xlabel(t(language, "Growth-gradient amplitude", "Амплитуда градиента роста"))
        axes[0].set_ylabel(TEXT[language]["curvature"])
        axes[1].plot(amplitudes, energies, "s-", color=ORANGE)
        axes[1].set_xlabel(t(language, "Growth-gradient amplitude", "Амплитуда градиента роста"))
        axes[1].set_ylabel(t(language, "Residual elastic energy", "Остаточная упругая энергия"))
        fig.suptitle(t(language, "Incompatible growth converts spatial mismatch into residual curvature and stress", "Несовместимый рост превращает пространственное рассогласование в остаточную кривизну и напряжение"))
        return fig

    _pair("growth_gradient_strip", build)


def initial_stress_vs_stress_free() -> None:
    solution = solve_sector_tube([SectorLayer(1.0, 1.4, 100.0)])
    x = _wall_coordinate(solution)
    initial = solution.circumferential_stress.copy()
    reconstructed = solution.circumferential_stress.copy()
    naive = np.zeros_like(initial)

    def build(language: str):
        fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.5))
        axes[0].plot(x, reconstructed, label=t(language, "Stress-free sector reconstruction", "Реконструкция из ненапряжённого сектора"), lw=2.5)
        axes[0].plot(x, initial, "--", label=t(language, "Initial-stress representation", "Представление через начальные напряжения"), lw=2)
        axes[0].plot(x, naive, ":", label=t(language, "Naive unloaded reference", "Наивная ненагруженная отсчётная конфигурация"))
        axes[0].set_xlabel(TEXT[language]["normalized_radius"])
        axes[0].set_ylabel(TEXT[language]["stress"])
        axes[0].legend()
        axes[1].bar(
            [t(language, "Explicit sector", "Явный сектор"), t(language, "Initial stress", "Начальное напряжение"), t(language, "Naive", "Наивная")],
            [0.0, np.max(np.abs(initial - reconstructed)), np.max(np.abs(initial - naive))],
        )
        axes[1].set_yscale("symlog", linthresh=1e-12)
        axes[1].set_ylabel(t(language, "Stress-field mismatch", "Рассогласование поля напряжений"))
        axes[1].tick_params(axis="x", rotation=15)
        fig.suptitle(t(language, "Different reference choices can be equivalent only when their constitutive bookkeeping is consistent", "Разные отсчётные описания эквивалентны только при согласованном учёте определяющих соотношений"))
        return fig

    _pair("initial_stress_vs_stress_free", build)


def measurement_uncertainty() -> None:
    angles = monte_carlo_opening_angle(90.0, 7.0, 600, seed=12)
    stress_metric = []
    for angle in angles:
        solution = solve_sector_tube([SectorLayer(1.0, 1.4, float(angle))], pressure=0.18)
        stress_metric.append(stress_uniformity(solution.circumferential_stress))
    stress_metric = np.asarray(stress_metric)

    def build(language: str):
        fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.5))
        axes[0].hist(angles, bins=28, color=BLUE, alpha=0.85)
        axes[0].set_xlabel(TEXT[language]["angle"])
        axes[0].set_ylabel(t(language, "Sample count", "Число реализаций"))
        axes[1].scatter(angles, stress_metric, s=10, alpha=0.35, color=CYAN)
        axes[1].set_xlabel(TEXT[language]["angle"])
        axes[1].set_ylabel(t(language, "Loaded stress variation", "Неоднородность напряжения при нагрузке"))
        fig.suptitle(t(language, "Geometric measurement uncertainty propagates nonlinearly into inferred stress", "Погрешность геометрического измерения нелинейно переносится в восстановленное напряжение"))
        return fig

    _pair("measurement_uncertainty", build)


def identifiability() -> None:
    truth = SectorLayer(1.0, 1.4, 100.0, 1.5)
    solution = solve_sector_tube([truth], pressure=0.12)
    angles = np.linspace(55.0, 145.0, 45)
    moduli = np.linspace(0.6, 2.5, 50)
    loss = inverse_loss_surface(solution.current_boundaries[0], solution.current_boundaries[-1], 0.12, angles, moduli)

    def build(language: str):
        fig, ax = plt.subplots(figsize=(8.3, 6.1))
        image = ax.contourf(moduli, angles, np.log10(loss + 1e-9), levels=35, cmap="viridis")
        ax.plot([1.5], [100.0], "*", ms=14, color="white", markeredgecolor=INK, label=t(language, "Generating parameters", "Порождающие параметры"))
        ax.set_xlabel(t(language, "Shear modulus", "Модуль сдвига"))
        ax.set_ylabel(TEXT[language]["angle"])
        ax.set_title(t(language, "One loaded geometry admits a parameter valley", "Одна нагруженная геометрия допускает долину параметров"))
        fig.colorbar(image, ax=ax, label=t(language, "log10 inverse loss", "log10 функции ошибки"))
        ax.legend()
        return fig

    _pair("identifiability", build)


def multi_cut_protocol() -> None:
    methods_en = ["One radial cut", "Multiple radial cuts", "Axial strip", "Layer separation", "Full-field inverse"]
    methods_ru = ["Один радиальный разрез", "Несколько радиальных разрезов", "Продольная полоса", "Разделение слоёв", "Полнополевая обратная задача"]
    circum = [1.0, 1.0, 0.2, 0.7, 1.0]
    axial = [0.0, 0.1, 1.0, 0.5, 1.0]
    local = [0.1, 0.5, 0.4, 0.7, 1.0]

    def build(language: str):
        labels = methods_en if language == "en" else methods_ru
        fig, ax = plt.subplots(figsize=(10.5, 5.3))
        y = np.arange(len(labels))
        ax.barh(y, circum, label=t(language, "Circumferential release", "Окружное высвобождение"))
        ax.barh(y, axial, left=circum, label=t(language, "Axial release", "Осевое высвобождение"))
        ax.barh(y, local, left=np.asarray(circum) + np.asarray(axial), label=t(language, "Spatial localization", "Пространственная локализация"))
        ax.set_yticks(y, labels)
        ax.set_xlabel(t(language, "Qualitative information content", "Качественная информативность"))
        ax.legend(ncols=3, loc="lower center", bbox_to_anchor=(0.5, -0.28))
        ax.set_title(t(language, "No single cut protocol reconstructs the full residual-stress tensor", "Ни один отдельный протокол разреза не восстанавливает полный тензор остаточных напряжений"))
        return fig

    _pair("multi_cut_protocol", build)


def stress_homogenization_map() -> None:
    pressures = np.linspace(0.04, 0.32, 23)
    angles = np.linspace(0.0, 170.0, 35)
    metric = np.empty((angles.size, pressures.size))
    for i, angle in enumerate(angles):
        for j, pressure in enumerate(pressures):
            solution = solve_sector_tube([SectorLayer(1.0, 1.4, float(angle))], pressure=float(pressure))
            metric[i, j] = stress_uniformity(solution.circumferential_stress)

    def build(language: str):
        fig, ax = plt.subplots(figsize=(9.2, 5.8))
        image = ax.contourf(pressures, angles, metric, levels=30, cmap="magma_r")
        optimum = angles[np.argmin(metric, axis=0)]
        ax.plot(pressures, optimum, color="white", lw=2.3, label=t(language, "Minimum-variation angle", "Угол минимальной неоднородности"))
        ax.set_xlabel(TEXT[language]["pressure"])
        ax.set_ylabel(TEXT[language]["angle"])
        ax.legend()
        fig.colorbar(image, ax=ax, label=t(language, "Stress coefficient of variation", "Коэффициент вариации напряжения"))
        ax.set_title(t(language, "The mechanically optimal opening angle depends on loading", "Механически оптимальный угол раскрытия зависит от нагрузки"))
        return fig

    _pair("stress_homogenization_map", build)


def growth_homeostasis() -> None:
    time = np.linspace(0.0, 40.0, 161)
    angle = np.empty_like(time)
    angle[0] = 15.0
    target = 0.03
    gain = 45.0
    variation = np.empty_like(time)
    for i in range(time.size):
        solution = solve_sector_tube([SectorLayer(1.0, 1.4, float(angle[i]))], pressure=0.2)
        variation[i] = stress_uniformity(solution.circumferential_stress)
        if i + 1 < time.size:
            angle[i + 1] = np.clip(angle[i] - (time[i + 1] - time[i]) * gain * (variation[i] - target), 0.0, 170.0)

    def build(language: str):
        fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.5))
        axes[0].plot(time, angle, color=BLUE)
        axes[0].set_xlabel(TEXT[language]["time"])
        axes[0].set_ylabel(TEXT[language]["angle"])
        axes[1].plot(time, variation, color=ORANGE)
        axes[1].axhline(target, color=INK, ls="--", label=t(language, "Homeostatic target", "Гомеостатическая цель"))
        axes[1].set_xlabel(TEXT[language]["time"])
        axes[1].set_ylabel(t(language, "Stress variation", "Неоднородность напряжения"))
        axes[1].legend()
        fig.suptitle(t(language, "Stress-modulated growth can generate an evolving residual-stress state", "Рост, управляемый напряжением, может формировать изменяющееся остаточно-напряжённое состояние"))
        return fig

    _pair("growth_homeostasis", build)


def _benchmark_rows() -> list[dict[str, float | str | bool]]:
    unloaded = solve_sector_tube([SectorLayer(1.0, 1.4, 100.0)])
    inner, outer = radial_boundary_residual(unloaded)
    pressurized = solve_sector_tube([SectorLayer(1.0, 1.4, 60.0)], pressure=0.2)
    naive = solve_sector_tube([SectorLayer(1.0, 1.4, 0.0)], pressure=0.2)
    z = np.linspace(-0.5, 0.5, 401)
    strip = equilibrated_strip(z, 0.04 * z)
    multilayer = solve_sector_tube([
        SectorLayer(1.0, 1.2, 120.0, 1.2),
        SectorLayer(1.2, 1.5, 60.0, 0.8),
    ], pressure=0.12)
    return [
        {"test": "inner radial traction", "value": abs(inner), "criterion": 1e-6, "passed": abs(inner) < 1e-6},
        {"test": "outer radial traction", "value": abs(outer), "criterion": 1e-8, "passed": abs(outer) < 1e-8},
        {"test": "incompressibility", "value": float(np.max(np.abs(unloaded.radial_stretch * unloaded.circumferential_stretch - 1.0))), "criterion": 1e-10, "passed": True},
        {"test": "strip force residual", "value": abs(float(strip["force_residual"])), "criterion": 1e-8, "passed": abs(float(strip["force_residual"])) < 1e-8},
        {"test": "strip moment residual", "value": abs(float(strip["moment_residual"])), "criterion": 1e-8, "passed": abs(float(strip["moment_residual"])) < 1e-8},
        {"test": "stress homogenization", "value": stress_uniformity(pressurized.circumferential_stress) / stress_uniformity(naive.circumferential_stress), "criterion": 1.0, "passed": stress_uniformity(pressurized.circumferential_stress) < stress_uniformity(naive.circumferential_stress)},
        {"test": "multilayer finite fields", "value": float(np.any(~np.isfinite(multilayer.circumferential_stress))), "criterion": 0.0, "passed": bool(np.all(np.isfinite(multilayer.circumferential_stress)))},
    ]


def benchmark_summary() -> None:
    rows = _benchmark_rows()
    path = DATA_DIRECTORY / "residual_stress_benchmark.csv"
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=["test", "value", "criterion", "passed"])
        writer.writeheader()
        writer.writerows(rows)

    translations = {
        "inner radial traction": "невязка внутренней радиальной нагрузки",
        "outer radial traction": "невязка наружной радиальной нагрузки",
        "incompressibility": "невязка несжимаемости",
        "strip force residual": "невязка силы в полосе",
        "strip moment residual": "невязка момента в полосе",
        "stress homogenization": "выравнивание напряжения",
        "multilayer finite fields": "конечность полей многослойной модели",
    }

    def build(language: str):
        fig, ax = plt.subplots(figsize=(10, 5.5))
        labels = [str(row["test"]) if language == "en" else translations[str(row["test"])] for row in rows]
        values = [max(abs(float(row["value"])) / max(abs(float(row["criterion"])), 1e-14), 1e-8) for row in rows]
        colors = [LIME if bool(row["passed"]) else RED for row in rows]
        y = np.arange(len(rows))
        ax.barh(y, np.log10(values), color=colors)
        ax.set_yticks(y, labels)
        ax.axvline(0.0, color=INK, ls="--")
        ax.set_xlabel(t(language, "log10(value / criterion)", "log10(значение / критерий)"))
        ax.set_title(t(language, "Verification hierarchy: mechanics first, interpretation second", "Иерархия проверки: сначала механика, затем интерпретация"))
        for index, row in enumerate(rows):
            ax.text(np.log10(values[index]), index, t(language, "  PASS", "  ПРОЙДЕНО") if row["passed"] else t(language, "  FAIL", "  НЕ ПРОЙДЕНО"), va="center", fontsize=8)
        return fig

    _pair("benchmark_summary", build)


def ring_opening_animation() -> None:
    layer = SectorLayer(1.0, 1.4, 120.0)
    closed = solve_sector_tube([layer])
    frames = 32
    for language in ("en", "ru"):
        fig, ax = plt.subplots(figsize=(5.4, 5.4))
        ax.set_aspect("equal")
        ax.axis("off")
        inner_line, = ax.plot([], [], color=BLUE, lw=3)
        outer_line, = ax.plot([], [], color=CYAN, lw=3)
        side_1, = ax.plot([], [], color=SLATE, lw=1.5)
        side_2, = ax.plot([], [], color=SLATE, lw=1.5)
        title = ax.set_title("")
        limit = 1.75
        ax.set_xlim(-limit, limit)
        ax.set_ylim(-limit, limit)

        def update(frame: int):
            fraction = frame / (frames - 1)
            angle = layer.opening_angle_degrees * fraction
            if frame == 0:
                xi, yi, xo, yo = ring_coordinates(closed.current_boundaries[0], closed.current_boundaries[-1])
            else:
                xi, yi, xo, yo = opening_sector_coordinates(1.0, 1.4, angle)
            inner_line.set_data(xi, yi)
            outer_line.set_data(xo, yo)
            side_1.set_data([xi[0], xo[0]], [yi[0], yo[0]])
            side_2.set_data([xi[-1], xo[-1]], [yi[-1], yo[-1]])
            title.set_text(t(language, f"Release after a cut: α={angle:.0f}°", f"Высвобождение после разреза: α={angle:.0f}°"))
            return inner_line, outer_line, side_1, side_2, title

        animation = FuncAnimation(fig, update, frames=frames, interval=90, blit=False)
        suffix = "" if language == "en" else "_ru"
        animation.save(ANIMATION_DIRECTORY / f"ring_opening{suffix}.gif", writer=PillowWriter(fps=11), dpi=90)
        plt.close(fig)


SCENARIOS = {
    "modeling_taxonomy": modeling_taxonomy,
    "opening_angle_geometry": opening_angle_geometry,
    "closure_kinematics": closure_kinematics,
    "unloaded_residual_stress": unloaded_residual_stress,
    "pressure_stress_uniformization": pressure_stress_uniformization,
    "opening_angle_sweep": opening_angle_sweep,
    "axial_prestretch_coupling": axial_prestretch_coupling,
    "material_anisotropy": material_anisotropy,
    "multilayer_tube": multilayer_tube,
    "layer_separation": layer_separation,
    "asymmetric_multi_sector": asymmetric_multi_sector,
    "axial_strip_curling": axial_strip_curling,
    "solid_organ_slice": solid_organ_slice,
    "growth_gradient_strip": growth_gradient_strip,
    "initial_stress_vs_stress_free": initial_stress_vs_stress_free,
    "measurement_uncertainty": measurement_uncertainty,
    "identifiability": identifiability,
    "multi_cut_protocol": multi_cut_protocol,
    "stress_homogenization_map": stress_homogenization_map,
    "growth_homeostasis": growth_homeostasis,
    "benchmark_summary": benchmark_summary,
    "ring_opening_animation": ring_opening_animation,
}


def render_scenario(name: str) -> None:
    SCENARIOS[name]()
