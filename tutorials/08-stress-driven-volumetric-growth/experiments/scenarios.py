"""Computational scenarios for Tutorial 08."""

from __future__ import annotations

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np

from biomechanics_tutorials.growth_kinematics import GrowthMaterialParameters
from biomechanics_tutorials.plotting import apply_tutorial_style
from biomechanics_tutorials.volumetric_growth import (
    VolumetricGrowthLawParameters,
    density_ratio_from_mass,
    evaluate_growth_stimulus,
    growth_response,
    homeostatic_band_value,
    isotropic_growth_tensor,
    mass_ratio_from_growth,
    simulate_prescribed_deformation,
    simulate_prescribed_mean_stress,
    simulate_spatial_growth_field,
    update_volume_ratio_explicit_euler,
    update_volume_ratio_exponential,
)

from common import (
    ANIMATION_DIRECTORY,
    DATA_DIRECTORY,
    colors,
    save_figure,
    title,
    tr,
)

BLUE, CYAN, LIME, INK, SLATE = colors()
MATERIAL = GrowthMaterialParameters(shear_modulus=1.0, bulk_modulus=18.0)


def _law(F: np.ndarray, measure: str = "mean_mandel", rate: float = 0.18, **kwargs):
    initial = float(evaluate_growth_stimulus(F, 1.0, measure, MATERIAL)["stimulus"])
    return VolumetricGrowthLawParameters(
        rate=rate,
        target=kwargs.pop("target", 0.0),
        scale=kwargs.pop("scale", max(abs(initial), 1.0)),
        measure=measure,
        response_limit=kwargs.pop("response_limit", 2.0),
        **kwargs,
    )


def feedback_architecture(language: str) -> None:
    apply_tutorial_style()
    fig, ax = plt.subplots(figsize=(12, 4.5))
    ax.axis("off")
    labels = {
        "en": [
            "Boundary/load\nprotocol",
            "Elastic state\nFe = F Fg⁻¹",
            "Chosen stress\nmeasure",
            "Homeostatic\nerror",
            "Growth law\nd ln Jg/dt",
            "Updated natural\nvolume Jg",
        ],
        "ru": [
            "Граничный режим\nи нагрузка",
            "Упругое состояние\nFe = F Fg⁻¹",
            "Выбранная мера\nнапряжения",
            "Гомеостатическая\nошибка",
            "Закон роста\nd ln Jg/dt",
            "Обновлённый\nобъём Jg",
        ],
    }[language]
    x = np.linspace(0.08, 0.92, len(labels))
    for index, (coordinate, label) in enumerate(zip(x, labels)):
        ax.text(
            coordinate,
            0.55,
            label,
            ha="center",
            va="center",
            transform=ax.transAxes,
            bbox={"boxstyle": "round,pad=0.55", "fc": "white", "ec": BLUE, "lw": 1.7},
        )
        if index < len(labels) - 1:
            ax.annotate(
                "",
                xy=(x[index + 1] - 0.065, 0.55),
                xytext=(coordinate + 0.065, 0.55),
                xycoords=ax.transAxes,
                arrowprops={"arrowstyle": "->", "color": INK, "lw": 1.6},
            )
    ax.annotate(
        "",
        xy=(x[1], 0.32),
        xytext=(x[-1], 0.32),
        xycoords=ax.transAxes,
        arrowprops={"arrowstyle": "->", "color": CYAN, "lw": 2.0, "connectionstyle": "arc3,rad=0.22"},
    )
    ax.set_title(title("feedback_architecture", language))
    save_figure(fig, "feedback_architecture", language)


def stimulus_measures(language: str) -> None:
    stretch = np.linspace(0.88, 1.14, 180)
    measures = ["mean_cauchy", "mean_mandel", "pressure", "von_mises", "energy"]
    labels = {
        "en": ["Mean Cauchy", "Mean Mandel", "Pressure", "von Mises", "Energy"],
        "ru": ["Среднее Коши", "Среднее Манделя", "Давление", "Мизес", "Энергия"],
    }[language]
    fig, ax = plt.subplots(figsize=(9.5, 5.8))
    for measure, label in zip(measures, labels):
        values = [
            float(evaluate_growth_stimulus(value * np.eye(3), 1.0, measure, MATERIAL)["stimulus"])
            for value in stretch
        ]
        scale = max(np.max(np.abs(values)), 1.0e-12)
        ax.plot(stretch, np.asarray(values) / scale, label=label)
    ax.axhline(0.0, color=INK, linewidth=1.0)
    ax.axvline(1.0, color=SLATE, linestyle="--", linewidth=1.0)
    ax.set_xlabel(tr("stretch", language))
    ax.set_ylabel({"en": "Normalized measure", "ru": "Нормированная мера"}[language])
    ax.set_title(title("stimulus_measures", language))
    ax.legend(ncol=2)
    save_figure(fig, "stimulus_measures", language)


def homeostatic_surface(language: str) -> None:
    sigma1 = np.linspace(-1.2, 1.6, 220)
    sigma2 = np.linspace(-1.2, 1.6, 220)
    s1, s2 = np.meshgrid(sigma1, sigma2)
    mean = (s1 + s2) / 3.0
    distance = homeostatic_band_value(mean, target=0.15, half_width=0.08, scale=1.0)
    fig, ax = plt.subplots(figsize=(7.5, 6.3))
    image = ax.contourf(s1, s2, distance, levels=31, cmap="coolwarm")
    ax.contour(s1, s2, distance, levels=[0.0], colors=[INK], linewidths=2.0)
    ax.plot([-1.2, 1.6], [-1.2, 1.6], color=SLATE, linestyle="--", linewidth=1.0)
    ax.set_xlabel(r"$\sigma_1$")
    ax.set_ylabel(r"$\sigma_2$")
    ax.set_title(title("homeostatic_surface", language))
    fig.colorbar(image, ax=ax, label=tr("error", language))
    save_figure(fig, "homeostatic_surface", language)


def fixed_deformation_relaxation(language: str) -> None:
    time = np.linspace(0.0, 18.0, 361)
    deformation = 1.11 * np.eye(3)
    result = simulate_prescribed_deformation(time, deformation, material=MATERIAL, law=_law(deformation))
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.4))
    axes[0].plot(time, result["Jg"], color=BLUE)
    axes[0].axhline(np.linalg.det(deformation), color=SLATE, linestyle="--", label=r"$J_g=J$")
    axes[0].set_xlabel(tr("time", language))
    axes[0].set_ylabel(tr("jg", language))
    axes[0].legend()
    axes[1].plot(time, result["mean_mandel"], color=CYAN, label={"en": "Mean Mandel", "ru": "Среднее Манделя"}[language])
    axes[1].plot(time, result["mean_cauchy"], color=BLUE, label={"en": "Mean Cauchy", "ru": "Среднее Коши"}[language])
    axes[1].axhline(0.0, color=INK, linewidth=1.0)
    axes[1].set_xlabel(tr("time", language))
    axes[1].set_ylabel(tr("stress", language))
    axes[1].legend()
    axes[2].semilogy(time, np.maximum(result["energy"], 1.0e-12), color=LIME)
    axes[2].set_xlabel(tr("time", language))
    axes[2].set_ylabel({"en": "Elastic energy", "ru": "Упругая энергия"}[language])
    fig.suptitle(title("fixed_deformation_relaxation", language))
    fig.tight_layout()
    save_figure(fig, "fixed_deformation_relaxation", language)


def boundary_control(language: str) -> None:
    time = np.linspace(0.0, 10.0, 301)
    deformation = 1.08 * np.eye(3)
    displacement = simulate_prescribed_deformation(
        time, deformation, material=MATERIAL, law=_law(deformation, rate=0.20)
    )
    law_stress = VolumetricGrowthLawParameters(
        rate=0.20,
        target=0.0,
        scale=1.0,
        measure="mean_cauchy",
        response_limit=2.0,
    )
    stress = simulate_prescribed_mean_stress(
        time, mean_stress=0.45, material=MATERIAL, law=law_stress
    )
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.8))
    axes[0].plot(time, displacement["mean_cauchy"], color=BLUE, label={"en": "Fixed deformation", "ru": "Фиксированная деформация"}[language])
    axes[0].plot(time, stress["mean_stress"], color=CYAN, label={"en": "Fixed stress", "ru": "Фиксированное напряжение"}[language])
    axes[0].set_xlabel(tr("time", language))
    axes[0].set_ylabel(tr("mean_stress", language))
    axes[0].legend()
    axes[1].plot(time, displacement["Jg"], color=BLUE, label=r"$J_g$: disp.")
    axes[1].plot(time, stress["Jg"], color=CYAN, label=r"$J_g$: stress")
    axes[1].plot(time, stress["total_stretch"], color=LIME, label={"en": "Total stretch under stress control", "ru": "Полное растяжение при управлении напряжением"}[language])
    axes[1].set_xlabel(tr("time", language))
    axes[1].set_ylabel({"en": "State variable", "ru": "Переменная состояния"}[language])
    axes[1].legend()
    fig.suptitle(title("boundary_control", language))
    fig.tight_layout()
    save_figure(fig, "boundary_control", language)


def load_protocols(language: str) -> None:
    time = np.linspace(0.0, 20.0, 501)
    protocols = {
        "step": np.where(time < 2.0, 1.0, 1.09),
        "ramp": 1.0 + 0.09 * np.clip((time - 2.0) / 8.0, 0.0, 1.0),
        "pulse": 1.0 + 0.09 * ((time >= 3.0) & (time <= 10.0)),
        "cyclic": 1.04 + 0.035 * np.sin(2.0 * np.pi * time / 5.0),
    }
    names = {
        "en": {"step": "Step", "ramp": "Ramp", "pulse": "Pulse", "cyclic": "Cyclic"},
        "ru": {"step": "Ступень", "ramp": "Линейный рост", "pulse": "Импульс", "cyclic": "Цикл"},
    }[language]
    fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    for key, stretch in protocols.items():
        history = np.array([value * np.eye(3) for value in stretch])
        law = _law(1.09 * np.eye(3), rate=0.16)
        result = simulate_prescribed_deformation(time, history, material=MATERIAL, law=law)
        axes[0].plot(time, stretch, label=names[key])
        axes[1].plot(time, result["Jg"], label=names[key])
    axes[0].set_ylabel(tr("stretch", language))
    axes[1].set_ylabel(tr("jg", language))
    axes[1].set_xlabel(tr("time", language))
    axes[0].legend(ncol=4)
    axes[1].legend(ncol=4)
    fig.suptitle(title("load_protocols", language))
    fig.tight_layout()
    save_figure(fig, "load_protocols", language)


def growth_resorption(language: str) -> None:
    time = np.linspace(0.0, 14.0, 351)
    cases = [
        (1.10, 1.0, 1.0, {"en": "Symmetric overload", "ru": "Симметричная перегрузка"}[language]),
        (1.10, 1.8, 0.5, {"en": "Fast growth", "ru": "Быстрый рост"}[language]),
        (0.92, 1.0, 1.0, {"en": "Symmetric unloading", "ru": "Симметричная разгрузка"}[language]),
        (0.92, 1.8, 0.35, {"en": "Slow resorption", "ru": "Медленная резорбция"}[language]),
    ]
    fig, ax = plt.subplots(figsize=(9.5, 5.7))
    for stretch, positive, negative, label in cases:
        deformation = stretch * np.eye(3)
        law = _law(
            deformation,
            rate=0.20,
            tensile_gain=positive,
            compressive_gain=negative,
        )
        result = simulate_prescribed_deformation(time, deformation, material=MATERIAL, law=law)
        ax.plot(time, result["Jg"], label=label)
    ax.axhline(1.0, color=SLATE, linestyle="--")
    ax.set_xlabel(tr("time", language))
    ax.set_ylabel(tr("jg", language))
    ax.set_title(title("growth_resorption", language))
    ax.legend(ncol=2)
    save_figure(fig, "growth_resorption", language)


def dead_zone_saturation(language: str) -> None:
    error = np.linspace(-2.5, 2.5, 400)
    configurations = [
        (0.0, None, {"en": "Linear", "ru": "Линейный"}[language]),
        (0.15, None, {"en": "Dead zone", "ru": "Мёртвая зона"}[language]),
        (0.0, 0.7, {"en": "Saturation", "ru": "Насыщение"}[language]),
        (0.15, 0.7, {"en": "Both", "ru": "Оба эффекта"}[language]),
    ]
    fig, ax = plt.subplots(figsize=(9.5, 5.7))
    for dead_zone, limit, label in configurations:
        law = VolumetricGrowthLawParameters(
            dead_zone=dead_zone, response_limit=limit, rate=1.0
        )
        response = [growth_response(value, law) for value in error]
        ax.plot(error, response, label=label)
    ax.axhline(0.0, color=INK, linewidth=1.0)
    ax.axvline(0.0, color=INK, linewidth=1.0)
    ax.set_xlabel(tr("error", language))
    ax.set_ylabel({"en": "Dimensionless response", "ru": "Безразмерный ответ"}[language])
    ax.set_title(title("dead_zone_saturation", language))
    ax.legend()
    save_figure(fig, "dead_zone_saturation", language)


def hydrostatic_deviatoric(language: str) -> None:
    time = np.linspace(0.0, 25.0, 501)
    hydro = 1.12 * np.eye(3)
    uniaxial = np.diag([1.25, 1.0, 1.0])
    result_h = simulate_prescribed_deformation(time, hydro, material=MATERIAL, law=_law(hydro, rate=0.23))
    result_u = simulate_prescribed_deformation(time, uniaxial, material=MATERIAL, law=_law(uniaxial, rate=0.23))
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.8))
    for result, name, color in [
        (result_h, {"en": "Hydrostatic constraint", "ru": "Гидростатическое стеснение"}[language], BLUE),
        (result_u, {"en": "Uniaxial constraint", "ru": "Одноосное стеснение"}[language], CYAN),
    ]:
        axes[0].plot(time, result["mean_mandel"], color=color, label=name)
        axes[1].plot(time, result["von_mises"], color=color, label=name)
    axes[0].axhline(0.0, color=INK, linewidth=1.0)
    axes[0].set_ylabel({"en": "Mean Mandel stress", "ru": "Среднее напряжение Манделя"}[language])
    axes[1].set_ylabel(tr("von_mises", language))
    for ax in axes:
        ax.set_xlabel(tr("time", language))
        ax.legend()
    fig.suptitle(title("hydrostatic_deviatoric", language))
    fig.tight_layout()
    save_figure(fig, "hydrostatic_deviatoric", language)


def mass_density(language: str) -> None:
    jg = np.linspace(0.65, 1.65, 180)
    constant_density_mass = mass_ratio_from_growth(jg, 1.0)
    constant_mass_density = density_ratio_from_mass(jg, 1.0)
    mixed_mass = mass_ratio_from_growth(jg, 1.0 + 0.18 * (jg - 1.0))
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.8))
    axes[0].plot(jg, constant_density_mass, color=BLUE, label={"en": "Constant density", "ru": "Постоянная плотность"}[language])
    axes[0].plot(jg, np.ones_like(jg), color=SLATE, linestyle="--", label={"en": "Constant mass", "ru": "Постоянная масса"}[language])
    axes[0].plot(jg, mixed_mass, color=CYAN, label={"en": "Mass and density both change", "ru": "Меняются масса и плотность"}[language])
    axes[0].set_xlabel(tr("jg", language))
    axes[0].set_ylabel(tr("mass", language))
    axes[0].legend()
    axes[1].plot(jg, np.ones_like(jg), color=BLUE, label={"en": "Constant density", "ru": "Постоянная плотность"}[language])
    axes[1].plot(jg, constant_mass_density, color=CYAN, label={"en": "Constant mass", "ru": "Постоянная масса"}[language])
    axes[1].plot(jg, 1.0 + 0.18 * (jg - 1.0), color=LIME, label={"en": "Prescribed density change", "ru": "Заданное изменение плотности"}[language])
    axes[1].set_xlabel(tr("jg", language))
    axes[1].set_ylabel(tr("density", language))
    axes[1].legend()
    fig.suptitle(title("mass_density", language))
    fig.tight_layout()
    save_figure(fig, "mass_density", language)


def time_integration(language: str) -> None:
    dt = np.linspace(0.0, 1.0, 160)
    rates = [-0.8, -1.5, -3.0]
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.8))
    for rate in rates:
        euler = [update_volume_ratio_explicit_euler(1.0, rate, value) for value in dt]
        exponential = [update_volume_ratio_exponential(1.0, rate, value, 1.0e-6, 10.0) for value in dt]
        axes[0].plot(dt, euler, label=f"rate={rate:g}")
        axes[1].plot(dt, exponential, label=f"rate={rate:g}")
    axes[0].axhline(0.0, color=INK, linewidth=1.0)
    axes[0].set_title({"en": "Explicit Euler", "ru": "Явный Эйлер"}[language])
    axes[1].set_title({"en": "Exponential update", "ru": "Экспоненциальное обновление"}[language])
    for ax in axes:
        ax.set_xlabel(tr("dt", language))
        ax.set_ylabel(tr("jg", language))
        ax.legend()
    fig.suptitle(title("time_integration", language))
    fig.tight_layout()
    save_figure(fig, "time_integration", language)


def gain_stability(language: str) -> None:
    gains = np.linspace(0.05, 1.2, 18)
    steps = np.linspace(0.03, 1.0, 18)
    classification = np.zeros((steps.size, gains.size))
    deformation = 1.12 * np.eye(3)
    initial_stimulus = float(evaluate_growth_stimulus(deformation, 1.0, "mean_mandel", MATERIAL)["stimulus"])
    for i, dt in enumerate(steps):
        time = np.arange(0.0, 12.0 + dt, dt)
        for j, gain in enumerate(gains):
            law = VolumetricGrowthLawParameters(
                rate=gain,
                target=0.0,
                scale=max(abs(initial_stimulus), 1.0),
                measure="mean_mandel",
                response_limit=None,
                jg_min=0.05,
                jg_max=10.0,
            )
            result = simulate_prescribed_deformation(time, deformation, material=MATERIAL, law=law)
            final = abs(result["mean_mandel"][-1]) / max(abs(result["mean_mandel"][0]), 1.0e-12)
            crossings = np.sum(np.diff(np.sign(result["mean_mandel"])) != 0)
            if final < 0.03 and crossings <= 1:
                classification[i, j] = 0.0
            elif final < 0.15:
                classification[i, j] = 1.0
            else:
                classification[i, j] = 2.0
    fig, ax = plt.subplots(figsize=(8.2, 6.2))
    image = ax.imshow(
        classification,
        origin="lower",
        aspect="auto",
        extent=[gains[0], gains[-1], steps[0], steps[-1]],
        cmap="viridis",
        vmin=0.0,
        vmax=2.0,
    )
    ax.set_xlabel(tr("gain", language))
    ax.set_ylabel(tr("dt", language))
    ax.set_title(title("gain_stability", language))
    cbar = fig.colorbar(image, ax=ax, ticks=[0, 1, 2])
    cbar.ax.set_yticklabels(
        {
            "en": ["monotone", "oscillatory", "not settled"],
            "ru": ["монотонно", "колебательно", "не установилось"],
        }[language]
    )
    save_figure(fig, "gain_stability", language)


def spatial_heterogeneity(language: str) -> None:
    x = np.linspace(0.0, 1.0, 81)
    time = np.linspace(0.0, 5.0, 181)
    target = np.where(x < 0.5, -0.10, 0.22)
    law = VolumetricGrowthLawParameters(
        rate=0.28,
        target=0.0,
        scale=1.0,
        measure="mean_mandel",
        response_limit=2.0,
    )
    result = simulate_spatial_growth_field(
        time, x, 1.08 * np.eye(3), np.ones_like(x), target, law, MATERIAL
    )
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.8))
    for index in [0, 40, 120, -1]:
        axes[0].plot(x, result["Jg"][index], label=f"t={time[index]:.1f}")
    axes[0].set_xlabel(tr("position", language))
    axes[0].set_ylabel(tr("jg", language))
    axes[0].legend()
    axes[1].plot(x, target, color=INK, linestyle="--", label=tr("target", language))
    axes[1].plot(x, result["stimulus"][-1], color=BLUE, label={"en": "Final stimulus", "ru": "Конечный стимул"}[language])
    axes[1].set_xlabel(tr("position", language))
    axes[1].set_ylabel(tr("stimulus", language))
    axes[1].legend()
    fig.suptitle(title("spatial_heterogeneity", language))
    fig.tight_layout()
    save_figure(fig, "spatial_heterogeneity", language)


def regularization(language: str) -> None:
    x = np.linspace(0.0, 1.0, 81)
    time = np.linspace(0.0, 4.0, 181)
    target = 0.22 * np.sin(10.0 * np.pi * x) + 0.08 * (x > 0.55)
    law = VolumetricGrowthLawParameters(
        rate=0.28,
        target=0.0,
        scale=1.0,
        measure="mean_mandel",
        response_limit=2.0,
    )
    diffusivities = [0.0, 1.0e-4, 4.0e-4]
    labels = {
        "en": ["Local", "Weak regularization", "Strong regularization"],
        "ru": ["Локально", "Слабая регуляризация", "Сильная регуляризация"],
    }[language]
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.8))
    for diffusivity, label in zip(diffusivities, labels):
        result = simulate_spatial_growth_field(
            time,
            x,
            1.07 * np.eye(3),
            np.ones_like(x),
            target,
            law,
            MATERIAL,
            diffusivity,
        )
        axes[0].plot(x, result["Jg"][-1], label=label)
        gradient = np.gradient(np.log(result["Jg"][-1]), x)
        axes[1].plot(x, gradient, label=label)
    axes[0].set_xlabel(tr("position", language))
    axes[0].set_ylabel(tr("jg", language))
    axes[1].set_xlabel(tr("position", language))
    axes[1].set_ylabel({"en": "Gradient of ln Jg", "ru": "Градиент ln Jg"}[language])
    for ax in axes:
        ax.legend()
    fig.suptitle(title("regularization", language))
    fig.tight_layout()
    save_figure(fig, "regularization", language)


def identifiability(language: str) -> None:
    deformation = 1.10 * np.eye(3)
    time = np.linspace(0.0, 8.0, 81)
    true_law = _law(deformation, rate=0.22, target=0.08, scale=1.0)
    synthetic = simulate_prescribed_deformation(time, deformation, material=MATERIAL, law=true_law)["Jg"]
    gains = np.linspace(0.08, 0.40, 14)
    targets = np.linspace(-0.10, 0.24, 14)
    rmse = np.empty((targets.size, gains.size))
    for i, target_value in enumerate(targets):
        for j, gain in enumerate(gains):
            law = _law(deformation, rate=gain, target=target_value, scale=1.0)
            prediction = simulate_prescribed_deformation(time, deformation, material=MATERIAL, law=law)["Jg"]
            rmse[i, j] = np.sqrt(np.mean((prediction - synthetic) ** 2))
    fig, ax = plt.subplots(figsize=(8.2, 6.2))
    image = ax.contourf(gains, targets, np.log10(rmse + 1.0e-6), levels=35, cmap="viridis")
    ax.plot([0.22], [0.08], marker="*", markersize=14, color="white", markeredgecolor=INK)
    ax.set_xlabel(tr("gain", language))
    ax.set_ylabel(tr("target", language))
    ax.set_title(title("identifiability", language))
    fig.colorbar(image, ax=ax, label={"en": "log10 RMSE", "ru": "log10 RMSE"}[language])
    save_figure(fig, "identifiability", language)


def benchmark_summary(language: str) -> None:
    rows = []
    jg_error = abs(np.linalg.det(isotropic_growth_tensor(1.7)) - 1.7)
    free = evaluate_growth_stimulus(isotropic_growth_tensor(1.4), 1.4, "mean_mandel", MATERIAL)
    free_stress = float(np.linalg.norm(free["cauchy"]))
    deformation = 1.10 * np.eye(3)
    result = simulate_prescribed_deformation(
        np.linspace(0.0, 20.0, 401), deformation, material=MATERIAL, law=_law(deformation, rate=0.24)
    )
    relaxation = abs(result["mean_mandel"][-1]) / abs(result["mean_mandel"][0])
    positivity = update_volume_ratio_exponential(1.0, -5.0, 1.0, 1.0e-8, 10.0)
    uniaxial = np.diag([1.25, 1.0, 1.0])
    uni = simulate_prescribed_deformation(
        np.linspace(0.0, 25.0, 501), uniaxial, material=MATERIAL, law=_law(uniaxial, rate=0.24)
    )
    deviatoric_remaining = float(uni["von_mises"][-1])
    rows.extend(
        [
            ("det(Fg)=Jg", jg_error, 1.0e-12, jg_error < 1.0e-12),
            ("free-growth stress", free_stress, 1.0e-10, free_stress < 1.0e-10),
            ("mean-stress relaxation ratio", relaxation, 0.03, relaxation < 0.03),
            ("positive exponential update", positivity, 0.0, positivity > 0.0),
            ("deviatoric stress retained", deviatoric_remaining, 0.1, deviatoric_remaining > 0.1),
        ]
    )
    DATA_DIRECTORY.mkdir(parents=True, exist_ok=True)
    csv_path = DATA_DIRECTORY / "volumetric_growth_benchmark.csv"
    with csv_path.open("w", encoding="utf-8") as stream:
        stream.write("test,value,tolerance_or_threshold,passed\n")
        for name, value, tolerance, passed in rows:
            stream.write(f"{name},{value:.12g},{tolerance:.12g},{passed}\n")
    labels_en = [row[0] for row in rows]
    translations = {
        "det(Fg)=Jg": "det(Fg)=Jg",
        "free-growth stress": "напряжение при свободном росте",
        "mean-stress relaxation ratio": "доля остаточного среднего напряжения",
        "positive exponential update": "положительность экспоненциального обновления",
        "deviatoric stress retained": "сохранение девиаторного напряжения",
    }
    labels = labels_en if language == "en" else [translations[label] for label in labels_en]
    values = [min(max(row[1] / max(abs(row[2]), 1.0e-12), 1.0e-6), 1.0e6) for row in rows]
    passed = [row[3] for row in rows]
    fig, ax = plt.subplots(figsize=(10.5, 5.2))
    y = np.arange(len(rows))
    bars = ax.barh(y, np.log10(values), color=[LIME if ok else "#E05A5A" for ok in passed])
    ax.set_yticks(y, labels)
    ax.axvline(0.0, color=INK, linewidth=1.0)
    ax.set_xlabel({"en": "log10(value / criterion)", "ru": "log10(значение / критерий)"}[language])
    ax.set_title(title("benchmark_summary", language))
    for bar, ok in zip(bars, passed):
        ax.text(bar.get_width(), bar.get_y() + bar.get_height() / 2, (" PASS" if ok else " FAIL") if language == "en" else (" ПРОЙДЕНО" if ok else " НЕ ПРОЙДЕНО"), va="center")
    save_figure(fig, "benchmark_summary", language)


def relaxation_animation(language: str) -> None:
    apply_tutorial_style()
    time = np.linspace(0.0, 16.0, 161)
    deformation = 1.11 * np.eye(3)
    result = simulate_prescribed_deformation(time, deformation, material=MATERIAL, law=_law(deformation, rate=0.22))
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.4))
    line_jg, = axes[0].plot([], [], color=BLUE, linewidth=2.5)
    marker_jg, = axes[0].plot([], [], "o", color=LIME)
    line_stress, = axes[1].plot([], [], color=CYAN, linewidth=2.5)
    marker_stress, = axes[1].plot([], [], "o", color=INK)
    axes[0].set_xlim(time[0], time[-1])
    axes[0].set_ylim(0.95, 1.45)
    axes[1].set_xlim(time[0], time[-1])
    margin = 0.08 * (np.ptp(result["mean_mandel"]) + 1.0e-6)
    axes[1].set_ylim(np.min(result["mean_mandel"]) - margin, np.max(result["mean_mandel"]) + margin)
    axes[0].set_xlabel(tr("time", language))
    axes[0].set_ylabel(tr("jg", language))
    axes[1].set_xlabel(tr("time", language))
    axes[1].set_ylabel({"en": "Mean Mandel stress", "ru": "Среднее напряжение Манделя"}[language])
    fig.suptitle(title("fixed_deformation_relaxation", language))

    def update(frame: int):
        line_jg.set_data(time[: frame + 1], result["Jg"][: frame + 1])
        marker_jg.set_data([time[frame]], [result["Jg"][frame]])
        line_stress.set_data(time[: frame + 1], result["mean_mandel"][: frame + 1])
        marker_stress.set_data([time[frame]], [result["mean_mandel"][frame]])
        return line_jg, marker_jg, line_stress, marker_stress

    movie = animation.FuncAnimation(fig, update, frames=range(0, time.size, 10), interval=110, blit=True)
    ANIMATION_DIRECTORY.mkdir(parents=True, exist_ok=True)
    suffix = "" if language == "en" else "_ru"
    path = ANIMATION_DIRECTORY / f"volumetric_relaxation{suffix}.gif"
    movie.save(path, writer=animation.PillowWriter(fps=8), dpi=70)
    plt.close(fig)


SCENARIOS = {
    "feedback_architecture": feedback_architecture,
    "stimulus_measures": stimulus_measures,
    "homeostatic_surface": homeostatic_surface,
    "fixed_deformation_relaxation": fixed_deformation_relaxation,
    "boundary_control": boundary_control,
    "load_protocols": load_protocols,
    "growth_resorption": growth_resorption,
    "dead_zone_saturation": dead_zone_saturation,
    "hydrostatic_deviatoric": hydrostatic_deviatoric,
    "mass_density": mass_density,
    "time_integration": time_integration,
    "gain_stability": gain_stability,
    "spatial_heterogeneity": spatial_heterogeneity,
    "regularization": regularization,
    "identifiability": identifiability,
    "benchmark_summary": benchmark_summary,
    "relaxation_animation": relaxation_animation,
}


def run(name: str) -> None:
    function = SCENARIOS[name]
    for language in ("en", "ru"):
        function(language)


def run_all() -> None:
    for name in SCENARIOS:
        run(name)


if __name__ == "__main__":
    run_all()
