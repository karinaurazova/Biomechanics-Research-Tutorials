"""Rendering scenarios for Tutorial 09."""

from __future__ import annotations

import csv
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import numpy as np

from biomechanics_tutorials.fiber_family_remodeling import (
    FiberFamily,
    FiberMaterialParameters,
    ODFRemodelingParameters,
    RecruitmentParameters,
    ReorientationParameters,
    TurnoverParameters,
    angular_integrated_energy,
    axial_angle_difference,
    axial_grid,
    axial_order_parameter,
    axial_von_mises_density,
    compare_approach_state_count,
    discrete_family_energy,
    fiber_stretch,
    planar_structure_tensor_energy,
    recruited_fraction,
    recruitment_tension,
    simulate_cohort_turnover,
    simulate_discrete_reorientation,
    simulate_odf_remodeling,
    simulate_two_family_mass_remodeling,
)
from biomechanics_tutorials.plotting import apply_tutorial_style

from common import ANIMATION_DIRECTORY, DATA_DIRECTORY, colors, save_figure, title, tr

BLUE, CYAN, LIME, INK, SLATE, RED = colors()


def _uniaxial(stretch: float, angle: float = 0.0) -> np.ndarray:
    base = np.diag([stretch, 1.0 / np.sqrt(stretch)])
    c = np.cos(angle)
    s = np.sin(angle)
    rotation = np.array([[c, -s], [s, c]])
    return rotation @ base @ rotation.T


def _finite_difference_nominal_stress(
    energy_function,
    stretches: np.ndarray,
    step: float = 1.0e-5,
) -> np.ndarray:
    values = []
    for stretch in stretches:
        plus = energy_function(_uniaxial(stretch + step))
        minus = energy_function(_uniaxial(stretch - step))
        values.append((plus - minus) / (2.0 * step))
    return np.asarray(values)


def render_modeling_taxonomy(language: str) -> None:
    labels = {
        "en": [
            "Direct family\nrotation",
            "Structure-tensor\nclosure",
            "Continuous ODF\nevolution",
            "Cohort turnover\nmixture",
        ],
        "ru": [
            "Прямая ротация\nсемейства",
            "Замыкание через\nструктурный тензор",
            "Эволюция\nнепрерывного ODF",
            "Когортная\nсмесь turnover",
        ],
    }[language]
    state_counts = compare_approach_state_count(181, 100)
    counts = list(state_counts.values())
    biological = {
        "en": [
            "existing fibers rotate",
            "mean + dispersion",
            "redistribution in angle space",
            "deposition + survival",
        ],
        "ru": [
            "существующие волокна вращаются",
            "среднее + дисперсия",
            "перераспределение по углам",
            "отложение + выживание",
        ],
    }[language]
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.2))
    axes[0].bar(np.arange(4), counts, color=[BLUE, CYAN, LIME, RED])
    axes[0].set_yscale("log")
    axes[0].set_xticks(np.arange(4), labels)
    axes[0].set_ylabel("Internal state variables" if language == "en" else "Число внутренних переменных")
    axes[0].set_title("Computational state size" if language == "en" else "Размер вычислительного состояния")
    axes[1].axis("off")
    y_positions = np.linspace(0.85, 0.2, 4)
    for y, label, mechanism, color in zip(y_positions, labels, biological, [BLUE, CYAN, LIME, RED]):
        axes[1].text(0.02, y, label.replace("\n", " "), weight="bold", color=color, fontsize=12)
        axes[1].text(0.53, y, mechanism, fontsize=11)
        axes[1].annotate("", xy=(0.49, y + 0.01), xytext=(0.33, y + 0.01), arrowprops={"arrowstyle": "->", "color": SLATE})
    axes[1].set_title("Biological statement" if language == "en" else "Биологическое утверждение")
    fig.suptitle(title("modeling_taxonomy", language), fontsize=16, weight="bold")
    fig.tight_layout()
    save_figure(fig, "modeling_taxonomy", language)


def render_discrete_reorientation(language: str) -> None:
    time = np.linspace(0.0, 8.0, 401)
    target = np.deg2rad(30.0)
    rates = [0.25, 0.6, 1.2]
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.8))
    for rate, color in zip(rates, [CYAN, BLUE, RED]):
        result = simulate_discrete_reorientation(
            time,
            np.deg2rad(-50.0),
            target,
            ReorientationParameters(rate=rate),
        )
        axes[0].plot(time, np.rad2deg(result["angle"]), label=f"k={rate:g}", color=color)
        axes[1].plot(time, np.rad2deg(np.abs(result["error"])), label=f"k={rate:g}", color=color)
    axes[0].axhline(np.rad2deg(target), color=INK, linestyle="--", label="target" if language == "en" else "цель")
    axes[0].set_xlabel(tr("time", language))
    axes[0].set_ylabel(tr("angle", language))
    axes[0].legend()
    axes[1].set_xlabel(tr("time", language))
    axes[1].set_ylabel("Absolute axial mismatch, deg" if language == "en" else "Абсолютное осевое рассогласование, град")
    axes[1].set_yscale("log")
    axes[1].legend()
    fig.suptitle(title("discrete_reorientation", language), fontsize=16, weight="bold")
    fig.tight_layout()
    save_figure(fig, "discrete_reorientation", language)


def render_cue_degeneracy(language: str) -> None:
    ratios = np.linspace(0.5, 1.5, 301)
    noise_levels = [0.0, 0.005, 0.02]
    rng = np.random.default_rng(42)
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.8))
    for noise, color in zip(noise_levels, [INK, CYAN, RED]):
        angles = []
        gaps = []
        for ratio in ratios:
            tensor = np.array([[1.0, 0.0], [0.0, ratio]])
            perturbation = noise * rng.normal(size=(2, 2))
            perturbation = 0.5 * (perturbation + perturbation.T)
            values, vectors = np.linalg.eigh(tensor + perturbation)
            vector = vectors[:, np.argmax(values)]
            angles.append(np.rad2deg(np.arctan2(vector[1], vector[0])))
            gaps.append(values[-1] - values[0])
        axes[0].plot(ratios, angles, color=color, label=f"noise={noise:g}")
        axes[1].plot(ratios, gaps, color=color, label=f"noise={noise:g}")
    axes[0].axvline(1.0, color=SLATE, linestyle="--")
    axes[1].axvline(1.0, color=SLATE, linestyle="--")
    axes[0].set_xlabel("Principal-value ratio" if language == "en" else "Отношение главных значений")
    axes[0].set_ylabel("Selected principal angle, deg" if language == "en" else "Выбранный главный угол, град")
    axes[1].set_xlabel("Principal-value ratio" if language == "en" else "Отношение главных значений")
    axes[1].set_ylabel("Eigenvalue gap" if language == "en" else "Разность собственных значений")
    axes[0].legend()
    axes[1].legend()
    fig.suptitle(title("cue_degeneracy", language), fontsize=16, weight="bold")
    fig.tight_layout()
    save_figure(fig, "cue_degeneracy", language)


def render_loading_switch(language: str) -> None:
    time = np.linspace(0.0, 15.0, 751)
    def target(t: float) -> float:
        if t < 5.0:
            return np.deg2rad(-30.0)
        if t < 10.0:
            return np.deg2rad(50.0)
        return np.deg2rad(5.0)

    result = simulate_discrete_reorientation(
        time,
        np.deg2rad(-70.0),
        target,
        ReorientationParameters(rate=0.7),
    )
    reversed_result = simulate_discrete_reorientation(
        time,
        np.deg2rad(-70.0),
        lambda t: target(15.0 - t),
        ReorientationParameters(rate=0.7),
    )
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.8))
    axes[0].plot(time, np.rad2deg(result["target"]), color=INK, linestyle="--", label="cue" if language == "en" else "стимул")
    axes[0].plot(time, np.rad2deg(result["angle"]), color=BLUE, label="family" if language == "en" else "семейство")
    axes[0].set_xlabel(tr("time", language))
    axes[0].set_ylabel(tr("angle", language))
    axes[0].legend()
    axes[1].plot(time, np.rad2deg(result["angle"]), color=BLUE, label="forward protocol" if language == "en" else "прямой протокол")
    axes[1].plot(time, np.rad2deg(reversed_result["angle"]), color=RED, label="reversed protocol" if language == "en" else "обратный протокол")
    axes[1].set_xlabel(tr("time", language))
    axes[1].set_ylabel(tr("angle", language))
    axes[1].legend()
    fig.suptitle(title("loading_switch", language), fontsize=16, weight="bold")
    fig.tight_layout()
    save_figure(fig, "loading_switch", language)


def _odf_reference_result() -> dict[str, np.ndarray]:
    theta = axial_grid(181)
    initial = axial_von_mises_density(theta, np.deg2rad(-45.0), 5.0)
    time = np.linspace(0.0, 6.0, 241)
    return simulate_odf_remodeling(
        time,
        theta,
        initial,
        np.deg2rad(35.0),
        ODFRemodelingParameters(alignment_rate=1.0, rotational_diffusivity=0.015),
    )


def render_odf_evolution(language: str) -> None:
    result = _odf_reference_result()
    theta_deg = np.rad2deg(result["theta"])
    indices = [0, 40, 100, 240]
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.8))
    for index, color in zip(indices, [SLATE, CYAN, BLUE, RED]):
        axes[0].plot(theta_deg, result["density"][index], color=color, label=f"t={result['time'][index]:.1f}")
    axes[0].set_xlabel(tr("angle", language))
    axes[0].set_ylabel(tr("density", language))
    axes[0].legend()
    axes[1].plot(result["time"], np.rad2deg(result["mean_angle"]), color=BLUE, label="mean angle" if language == "en" else "средний угол")
    axes[1].plot(result["time"], np.rad2deg(result["target"]), color=INK, linestyle="--", label="target" if language == "en" else "цель")
    ax2 = axes[1].twinx()
    ax2.plot(result["time"], result["order_parameter"], color=RED, label="order" if language == "en" else "порядок")
    axes[1].set_xlabel(tr("time", language))
    axes[1].set_ylabel(tr("angle", language))
    ax2.set_ylabel(tr("order", language))
    lines = axes[1].lines + ax2.lines
    axes[1].legend(lines, [line.get_label() for line in lines], loc="center right")
    fig.suptitle(title("odf_evolution", language), fontsize=16, weight="bold")
    fig.tight_layout()
    save_figure(fig, "odf_evolution", language)


def render_alignment_diffusion_map(language: str) -> None:
    theta = axial_grid(91)
    initial = axial_von_mises_density(theta, np.deg2rad(-35.0), 4.0)
    time = np.linspace(0.0, 3.0, 121)
    alignment_values = np.linspace(0.1, 1.5, 15)
    diffusion_values = np.linspace(0.0, 0.08, 15)
    order = np.zeros((diffusion_values.size, alignment_values.size))
    error = np.zeros_like(order)
    target = np.deg2rad(25.0)
    for row, diffusivity in enumerate(diffusion_values):
        for col, alignment in enumerate(alignment_values):
            result = simulate_odf_remodeling(
                time,
                theta,
                initial,
                target,
                ODFRemodelingParameters(alignment_rate=alignment, rotational_diffusivity=diffusivity),
            )
            order[row, col] = result["order_parameter"][-1]
            error[row, col] = np.rad2deg(abs(axial_angle_difference(target, result["mean_angle"][-1])))
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    im0 = axes[0].imshow(order, origin="lower", aspect="auto", extent=[alignment_values[0], alignment_values[-1], diffusion_values[0], diffusion_values[-1]], vmin=0.0, vmax=1.0)
    im1 = axes[1].imshow(error, origin="lower", aspect="auto", extent=[alignment_values[0], alignment_values[-1], diffusion_values[0], diffusion_values[-1]])
    for axis in axes:
        axis.set_xlabel(tr("alignment", language))
        axis.set_ylabel(tr("diffusion", language))
    axes[0].set_title(tr("order", language))
    axes[1].set_title("Final mean-angle error, deg" if language == "en" else "Финальная ошибка среднего угла, град")
    fig.colorbar(im0, ax=axes[0])
    fig.colorbar(im1, ax=axes[1])
    fig.suptitle(title("alignment_diffusion_map", language), fontsize=16, weight="bold")
    fig.tight_layout()
    save_figure(fig, "alignment_diffusion_map", language)


def render_dispersion_metrics(language: str) -> None:
    theta = axial_grid(361)
    unimodal = axial_von_mises_density(theta, 0.0, 4.0)
    bimodal = 0.5 * axial_von_mises_density(theta, np.deg2rad(-30.0), 16.0) + 0.5 * axial_von_mises_density(theta, np.deg2rad(30.0), 16.0)
    broad = axial_von_mises_density(theta, 0.0, 1.2)
    densities = [unimodal, bimodal, broad]
    names = {
        "en": ["unimodal", "bimodal", "broad"],
        "ru": ["одномодальное", "двухмодальное", "широкое"],
    }[language]
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.8))
    for density, name, color in zip(densities, names, [BLUE, RED, CYAN]):
        axes[0].plot(np.rad2deg(theta), density, label=name, color=color)
    order = [axial_order_parameter(theta, density) for density in densities]
    entropy = []
    delta = np.pi / theta.size
    for density in densities:
        rho = np.maximum(density, 1.0e-14)
        entropy.append(float(-np.sum(rho * np.log(rho)) * delta))
    axes[0].set_xlabel(tr("angle", language))
    axes[0].set_ylabel(tr("density", language))
    axes[0].legend()
    x = np.arange(3)
    axes[1].bar(x - 0.18, order, width=0.36, color=BLUE, label=tr("order", language))
    axes[1].bar(x + 0.18, entropy, width=0.36, color=RED, label="entropy" if language == "en" else "энтропия")
    axes[1].set_xticks(x, names)
    axes[1].legend()
    fig.suptitle(title("dispersion_metrics", language), fontsize=16, weight="bold")
    fig.tight_layout()
    save_figure(fig, "dispersion_metrics", language)


def render_discrete_continuous(language: str) -> None:
    theta = axial_grid(1441)
    density = axial_von_mises_density(theta, np.deg2rad(25.0), 6.0)
    stretches = np.linspace(1.0, 1.22, 61)
    material = FiberMaterialParameters(k1=2.5, k2=7.0)
    reference = np.array([angular_integrated_energy(_uniaxial(lam), theta, density, material) for lam in stretches])
    counts = [2, 4, 8, 16, 32, 64]
    errors = []
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.8))
    axes[0].plot(stretches, reference, color=INK, linewidth=2.5, label="angular integration" if language == "en" else "угловое интегрирование")
    for count, color in zip([4, 8, 16, 32], [CYAN, LIME, BLUE, RED]):
        sample_angles = np.linspace(-0.5 * np.pi, 0.5 * np.pi, count, endpoint=False)
        sample_density = axial_von_mises_density(sample_angles, np.deg2rad(25.0), 6.0)
        weights = sample_density * np.pi / count
        values = []
        for lam in stretches:
            families = [FiberFamily(angle=angle, mass_fraction=weight) for angle, weight in zip(sample_angles, weights)]
            values.append(discrete_family_energy(_uniaxial(lam), families, material))
        values = np.asarray(values)
        axes[0].plot(stretches, values, color=color, label=f"N={count}")
    for count in counts:
        sample_angles = np.linspace(-0.5 * np.pi, 0.5 * np.pi, count, endpoint=False)
        sample_density = axial_von_mises_density(sample_angles, np.deg2rad(25.0), 6.0)
        weights = sample_density * np.pi / count
        values = np.array([
            discrete_family_energy(
                _uniaxial(lam),
                [FiberFamily(angle=angle, mass_fraction=weight) for angle, weight in zip(sample_angles, weights)],
                material,
            )
            for lam in stretches
        ])
        errors.append(np.linalg.norm(values - reference) / np.linalg.norm(reference))
    axes[0].set_xlabel(tr("stretch", language))
    axes[0].set_ylabel(tr("energy", language))
    axes[0].legend()
    axes[1].loglog(counts, errors, marker="o", color=BLUE)
    axes[1].set_xlabel("Number of discrete families" if language == "en" else "Число дискретных семейств")
    axes[1].set_ylabel("Relative curve error" if language == "en" else "Относительная ошибка кривой")
    fig.suptitle(title("discrete_continuous", language), fontsize=16, weight="bold")
    fig.tight_layout()
    save_figure(fig, "discrete_continuous", language)


def render_lanir_goh_comparison(language: str) -> None:
    theta = axial_grid(1441)
    stretches = np.linspace(1.0, 1.22, 61)
    material = FiberMaterialParameters(k1=2.0, k2=6.0)
    concentrations = [1.0, 4.0, 16.0]
    dispersions = [0.40, 0.18, 0.04]
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.8))
    mismatch = []
    for concentration, dispersion, color in zip(concentrations, dispersions, [CYAN, BLUE, RED]):
        density = axial_von_mises_density(theta, 0.0, concentration)
        lanir = np.array([angular_integrated_energy(_uniaxial(lam), theta, density, material) for lam in stretches])
        closure = np.array([planar_structure_tensor_energy(_uniaxial(lam), 0.0, dispersion, material) for lam in stretches])
        axes[0].plot(stretches, lanir, color=color, label=f"AI κ={concentration:g}")
        axes[0].plot(stretches, closure, color=color, linestyle="--", label=f"GST d={dispersion:g}")
        mismatch.append(np.linalg.norm(lanir - closure) / max(np.linalg.norm(lanir), 1.0e-12))
    axes[0].set_xlabel(tr("stretch", language))
    axes[0].set_ylabel(tr("energy", language))
    axes[0].legend(ncol=2, fontsize=9)
    axes[1].bar(np.arange(3), mismatch, color=[CYAN, BLUE, RED])
    axes[1].set_xticks(np.arange(3), ["broad", "moderate", "aligned"] if language == "en" else ["широкое", "умеренное", "выровненное"])
    axes[1].set_ylabel("Relative closure mismatch" if language == "en" else "Относительное расхождение замыкания")
    fig.suptitle(title("lanir_goh_comparison", language), fontsize=16, weight="bold")
    fig.tight_layout()
    save_figure(fig, "lanir_goh_comparison", language)


def render_two_family_response(language: str) -> None:
    stretches = np.linspace(1.0, 1.25, 71)
    family_angles = [15.0, 35.0, 55.0]
    loading_angles = [0.0, 45.0, 90.0]
    material = FiberMaterialParameters(k1=2.0, k2=6.0)
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.4), sharey=True)
    for axis, loading_angle in zip(axes, loading_angles):
        for angle, color in zip(family_angles, [CYAN, BLUE, RED]):
            families = [
                FiberFamily(angle=np.deg2rad(angle), mass_fraction=0.5),
                FiberFamily(angle=np.deg2rad(-angle), mass_fraction=0.5),
            ]
            energy = np.array([
                discrete_family_energy(_uniaxial(lam, np.deg2rad(loading_angle)), families, material)
                for lam in stretches
            ])
            axis.plot(stretches, energy, color=color, label=f"±{angle:.0f}°")
        axis.set_title(("load " if language == "en" else "нагрузка ") + f"{loading_angle:.0f}°")
        axis.set_xlabel(tr("stretch", language))
    axes[0].set_ylabel(tr("energy", language))
    axes[-1].legend()
    fig.suptitle(title("two_family_response", language), fontsize=16, weight="bold")
    fig.tight_layout()
    save_figure(fig, "two_family_response", language)


def render_recruitment_crimp(language: str) -> None:
    stretch = np.linspace(0.95, 1.22, 180)
    parameter_sets = [
        RecruitmentParameters(mean=1.04, standard_deviation=0.012),
        RecruitmentParameters(mean=1.07, standard_deviation=0.025),
        RecruitmentParameters(mean=1.10, standard_deviation=0.04),
    ]
    names = {
        "en": ["early/narrow", "intermediate", "late/broad"],
        "ru": ["раннее/узкое", "среднее", "позднее/широкое"],
    }[language]
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.8))
    for params, name, color in zip(parameter_sets, names, [CYAN, BLUE, RED]):
        axes[0].plot(stretch, recruited_fraction(stretch, params), color=color, label=name)
        axes[1].plot(stretch, recruitment_tension(stretch, params), color=color, label=name)
    axes[0].set_xlabel(tr("stretch", language))
    axes[0].set_ylabel("Recruited fraction" if language == "en" else "Доля рекрутированных волокон")
    axes[1].set_xlabel(tr("stretch", language))
    axes[1].set_ylabel("Tension proxy" if language == "en" else "Прокси натяжения")
    axes[0].legend()
    axes[1].legend()
    fig.suptitle(title("recruitment_crimp", language), fontsize=16, weight="bold")
    fig.tight_layout()
    save_figure(fig, "recruitment_crimp", language)


def _turnover_result(half_life: float = 5.0) -> dict:
    time = np.linspace(0.0, 24.0, 241)
    return simulate_cohort_turnover(
        time,
        stress_protocol=lambda t: 1.0 if t < 4.0 else 1.35,
        deposition_angle_protocol=lambda t: np.deg2rad(-20.0) if t < 6.0 else np.deg2rad(55.0),
        parameters=TurnoverParameters(
            half_life=half_life,
            basal_production=0.18,
            stress_gain=0.8,
            target_stress=1.0,
            deposition_stretch=1.08,
        ),
        initial_angle=np.deg2rad(-20.0),
    )


def render_turnover_replacement(language: str) -> None:
    result = _turnover_result()
    fig, axes = plt.subplots(2, 2, figsize=(12.5, 8.2), sharex=True)
    axes[0, 0].plot(result["time"], result["stress"], color=INK)
    axes[0, 0].axhline(1.0, color=SLATE, linestyle="--")
    axes[0, 0].set_ylabel("Stress cue" if language == "en" else "Стимул напряжения")
    axes[0, 1].plot(result["time"], result["mass"], color=BLUE)
    axes[0, 1].set_ylabel(tr("mass", language))
    axes[1, 0].plot(result["time"], np.rad2deg(result["mean_angle"]), color=RED)
    axes[1, 0].set_ylabel(tr("angle", language))
    axes[1, 1].plot(result["time"], result["mean_age"], color=CYAN)
    axes[1, 1].set_ylabel(tr("age", language))
    for axis in axes[-1]:
        axis.set_xlabel(tr("time", language))
    fig.suptitle(title("turnover_replacement", language), fontsize=16, weight="bold")
    fig.tight_layout()
    save_figure(fig, "turnover_replacement", language)


def render_direct_vs_turnover(language: str) -> None:
    time = np.linspace(0.0, 24.0, 241)
    target_angle = np.deg2rad(55.0)
    direct = simulate_discrete_reorientation(
        time,
        np.deg2rad(-20.0),
        lambda t: np.deg2rad(-20.0) if t < 6.0 else target_angle,
        ReorientationParameters(rate=0.23),
    )
    turnover_fast = _turnover_result(half_life=3.0)
    turnover_slow = _turnover_result(half_life=9.0)
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.8))
    axes[0].plot(time, np.rad2deg(direct["angle"]), color=BLUE, label="direct rotation" if language == "en" else "прямая ротация")
    axes[0].plot(time, np.rad2deg(turnover_fast["mean_angle"]), color=RED, label="turnover t½=3")
    axes[0].plot(time, np.rad2deg(turnover_slow["mean_angle"]), color=CYAN, label="turnover t½=9")
    axes[0].axhline(np.rad2deg(target_angle), color=INK, linestyle="--")
    axes[0].set_xlabel(tr("time", language))
    axes[0].set_ylabel(tr("angle", language))
    axes[0].legend()
    axes[1].plot(time, turnover_fast["mass"], color=RED, label="turnover t½=3")
    axes[1].plot(time, turnover_slow["mass"], color=CYAN, label="turnover t½=9")
    axes[1].axhline(1.0, color=INK, linestyle="--", label="direct rotation mass" if language == "en" else "масса при прямой ротации")
    axes[1].set_xlabel(tr("time", language))
    axes[1].set_ylabel(tr("mass", language))
    axes[1].legend()
    fig.suptitle(title("direct_vs_turnover", language), fontsize=16, weight="bold")
    fig.tight_layout()
    save_figure(fig, "direct_vs_turnover", language)


def render_deposition_stretch(language: str) -> None:
    stretches = np.linspace(0.9, 1.18, 140)
    deposition = [0.96, 1.0, 1.08, 1.15]
    material = FiberMaterialParameters(k1=2.0, k2=5.0)
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.8))
    reference_energy = []
    for value, color in zip(deposition, [SLATE, CYAN, BLUE, RED]):
        families = [FiberFamily(angle=0.0, deposition_stretch=value)]
        energy = np.array([discrete_family_energy(_uniaxial(lam), families, material) for lam in stretches])
        stress = np.gradient(energy, stretches)
        axes[0].plot(stretches, energy, color=color, label=f"G_h={value:g}")
        axes[1].plot(stretches, stress, color=color, label=f"G_h={value:g}")
        reference_energy.append(discrete_family_energy(np.eye(2), families, material))
    axes[0].set_xlabel(tr("stretch", language))
    axes[0].set_ylabel(tr("energy", language))
    axes[1].set_xlabel(tr("stretch", language))
    axes[1].set_ylabel("Nominal-stress proxy" if language == "en" else "Прокси номинального напряжения")
    axes[0].legend()
    axes[1].legend()
    fig.suptitle(title("deposition_stretch", language), fontsize=16, weight="bold")
    fig.tight_layout()
    save_figure(fig, "deposition_stretch", language)


def render_family_competition(language: str) -> None:
    time = np.linspace(0.0, 12.0, 241)
    def deformation(t: float) -> np.ndarray:
        if t < 6.0:
            return _uniaxial(1.18, 0.0)
        return _uniaxial(1.18, 0.5 * np.pi)

    result = simulate_two_family_mass_remodeling(
        time,
        deformation,
        initial_masses=(0.5, 0.5),
        family_angles=(0.0, 0.5 * np.pi),
        target_tension=0.3,
        adaptation_rate=0.45,
        removal_rate=0.12,
    )
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.8))
    axes[0].plot(time, result["tension"][:, 0], color=BLUE, label="family 0°" if language == "en" else "семейство 0°")
    axes[0].plot(time, result["tension"][:, 1], color=RED, label="family 90°" if language == "en" else "семейство 90°")
    axes[0].set_xlabel(tr("time", language))
    axes[0].set_ylabel("Family tension proxy" if language == "en" else "Прокси натяжения семейства")
    axes[0].legend()
    axes[1].plot(time, result["mass_fraction"][:, 0], color=BLUE, label="family 0°" if language == "en" else "семейство 0°")
    axes[1].plot(time, result["mass_fraction"][:, 1], color=RED, label="family 90°" if language == "en" else "семейство 90°")
    axes[1].axvline(6.0, color=INK, linestyle="--")
    axes[1].set_xlabel(tr("time", language))
    axes[1].set_ylabel(tr("fraction", language))
    axes[1].legend()
    fig.suptitle(title("family_competition", language), fontsize=16, weight="bold")
    fig.tight_layout()
    save_figure(fig, "family_competition", language)


def render_identifiability(language: str) -> None:
    stretches = np.linspace(1.0, 1.18, 31)
    theta = axial_grid(241)
    material = FiberMaterialParameters(k1=2.0, k2=5.0)
    true_angle = np.deg2rad(25.0)
    true_concentration = 7.0
    true_mass = 1.0
    delta = np.pi / theta.size

    # Precompute the directional energy matrix for every loading level and
    # orientation.  Candidate distributions then require only matrix-vector
    # products, making the identifiability sweep fast and deterministic.
    energy_matrix = np.empty((stretches.size, theta.size), dtype=float)
    for row, lam in enumerate(stretches):
        F = _uniaxial(lam)
        directional_stretch = np.array([fiber_stretch(F, angle) for angle in theta])
        effective = directional_stretch / material.slack_stretch
        strain_measure = np.maximum(effective**2 - 1.0, 0.0)
        energy_matrix[row] = material.k1 / (2.0 * material.k2) * (
            np.exp(material.k2 * strain_measure**2) - 1.0
        )

    true_density = axial_von_mises_density(theta, true_angle, true_concentration)
    target = true_mass * (energy_matrix @ (true_density * delta))
    angles = np.deg2rad(np.linspace(5.0, 45.0, 35))
    concentrations = np.linspace(2.0, 14.0, 35)
    error = np.empty((concentrations.size, angles.size))
    best_mass = np.empty_like(error)
    for row, concentration in enumerate(concentrations):
        for col, angle in enumerate(angles):
            density = axial_von_mises_density(theta, angle, concentration)
            basis = energy_matrix @ (density * delta)
            mass = float(np.dot(target, basis) / max(np.dot(basis, basis), 1.0e-14))
            best_mass[row, col] = mass
            residual = mass * basis - target
            error[row, col] = np.linalg.norm(residual) / np.linalg.norm(target)
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    extent = [
        np.rad2deg(angles[0]),
        np.rad2deg(angles[-1]),
        concentrations[0],
        concentrations[-1],
    ]
    im0 = axes[0].imshow(error, origin="lower", aspect="auto", extent=extent)
    im1 = axes[1].imshow(best_mass, origin="lower", aspect="auto", extent=extent)
    axes[0].scatter([25.0], [true_concentration], marker="x", s=100, color="white")
    for axis in axes:
        axis.set_xlabel("Mean angle, deg" if language == "en" else "Средний угол, град")
        axis.set_ylabel(tr("concentration", language))
    axes[0].set_title("Relative fitting error" if language == "en" else "Относительная ошибка подгонки")
    axes[1].set_title("Best compensating mass" if language == "en" else "Лучшая компенсирующая масса")
    fig.colorbar(im0, ax=axes[0])
    fig.colorbar(im1, ax=axes[1])
    fig.suptitle(title("identifiability", language), fontsize=16, weight="bold")
    fig.tight_layout()
    save_figure(fig, "identifiability", language)


def render_biology_model_map(language: str) -> None:
    mechanisms = {
        "en": [
            "cell traction and contact guidance",
            "fibril rotation / sliding",
            "cross-link maturation",
            "collagen synthesis",
            "enzymatic degradation",
            "crimp and recruitment",
        ],
        "ru": [
            "клеточная тяга и контактное направление",
            "ротация / скольжение фибрилл",
            "созревание поперечных сшивок",
            "синтез коллагена",
            "ферментативная деградация",
            "извитость и рекрутирование",
        ],
    }[language]
    variables = {
        "en": ["target cue", "orientation / ODF", "stiffness + survival", "production rate", "survival function", "slack-stretch distribution"],
        "ru": ["целевой стимул", "ориентация / ODF", "жёсткость + выживание", "скорость синтеза", "функция выживания", "распределение слабин"],
    }[language]
    scales = {
        "en": ["cell", "fibril", "cross-link", "molecular", "molecular", "fiber bundle"],
        "ru": ["клетка", "фибрилла", "сшивка", "молекулярный", "молекулярный", "пучок волокон"],
    }[language]
    fig, axis = plt.subplots(figsize=(13, 6.4))
    axis.axis("off")
    columns = [0.05, 0.42, 0.77]
    headers = {
        "en": ["Biological mechanism", "Model variable", "Scale"],
        "ru": ["Биологический механизм", "Переменная модели", "Масштаб"],
    }[language]
    for x, header in zip(columns, headers):
        axis.text(x, 0.94, header, weight="bold", fontsize=13, color=INK)
    y_positions = np.linspace(0.82, 0.12, len(mechanisms))
    for index, (mechanism, variable, scale, y) in enumerate(zip(mechanisms, variables, scales, y_positions)):
        color = [BLUE, CYAN, LIME, RED, SLATE, "#8B5CF6"][index]
        axis.text(columns[0], y, mechanism, color=color, fontsize=11)
        axis.text(columns[1], y, variable, fontsize=11)
        axis.text(columns[2], y, scale, fontsize=11)
        axis.annotate("", xy=(columns[1] - 0.02, y + 0.01), xytext=(columns[0] + 0.28, y + 0.01), arrowprops={"arrowstyle": "->", "color": SLATE})
        axis.annotate("", xy=(columns[2] - 0.02, y + 0.01), xytext=(columns[1] + 0.25, y + 0.01), arrowprops={"arrowstyle": "->", "color": SLATE})
    axis.set_title(title("biology_model_map", language), fontsize=16, weight="bold")
    fig.tight_layout()
    save_figure(fig, "biology_model_map", language)


def _benchmark_rows() -> list[dict[str, str | float | bool]]:
    rows: list[dict[str, str | float | bool]] = []
    theta = axial_grid(721)
    density = axial_von_mises_density(theta, np.deg2rad(20.0), 8.0)
    normalization_error = abs(np.sum(density) * np.pi / theta.size - 1.0)
    rows.append({"test": "ODF normalization", "metric": normalization_error, "tolerance": 1.0e-5, "passed": normalization_error < 1.0e-5})
    angle = np.rad2deg(np.arctan2(0.0, 1.0))
    rows.append({"test": "principal cue", "metric": abs(angle), "tolerance": 1.0e-12, "passed": abs(angle) < 1.0e-12})
    time = np.linspace(0.0, 6.0, 301)
    direct = simulate_discrete_reorientation(time, np.deg2rad(-45.0), np.deg2rad(25.0), ReorientationParameters(rate=1.0))
    direct_error = np.rad2deg(abs(direct["error"][-1]))
    rows.append({"test": "direct alignment", "metric": direct_error, "tolerance": 1.0, "passed": direct_error < 1.0})
    odf = simulate_odf_remodeling(
        np.linspace(0.0, 4.0, 161),
        axial_grid(121),
        axial_von_mises_density(axial_grid(121), np.deg2rad(-35.0), 6.0),
        np.deg2rad(25.0),
        ODFRemodelingParameters(alignment_rate=1.0, rotational_diffusivity=0.01),
    )
    odf_error = np.rad2deg(abs(axial_angle_difference(np.deg2rad(25.0), odf["mean_angle"][-1])))
    rows.append({"test": "ODF alignment", "metric": odf_error, "tolerance": 5.0, "passed": odf_error < 5.0})
    survival_error = abs(0.5 - np.exp(-np.log(2.0)))
    rows.append({"test": "half-life survival", "metric": survival_error, "tolerance": 1.0e-12, "passed": survival_error < 1.0e-12})
    stretch = np.linspace(0.95, 1.2, 100)
    monotonic_violation = float(max(0.0, -np.min(np.diff(recruitment_tension(stretch)))))
    rows.append({"test": "recruitment monotonicity", "metric": monotonic_violation, "tolerance": 1.0e-10, "passed": monotonic_violation < 1.0e-10})
    return rows


def render_benchmark_summary(language: str) -> None:
    rows = _benchmark_rows()
    DATA_DIRECTORY.mkdir(parents=True, exist_ok=True)
    csv_path = DATA_DIRECTORY / "fiber_remodeling_benchmark.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=["test", "metric", "tolerance", "passed"])
        writer.writeheader()
        writer.writerows(rows)
    label_translations = {
        "ODF normalization": "нормировка ODF",
        "principal cue": "главное направление",
        "direct alignment": "прямое выравнивание",
        "ODF alignment": "выравнивание ODF",
        "half-life survival": "выживание за период полураспада",
        "recruitment monotonicity": "монотонность рекрутирования",
    }
    labels = [
        label_translations.get(str(row["test"]), str(row["test"]))
        if language == "ru"
        else str(row["test"])
        for row in rows
    ]
    normalized = [float(row["metric"]) / max(float(row["tolerance"]), 1.0e-16) for row in rows]
    plot_values = [max(value, 1.0e-12) for value in normalized]
    passed = [bool(row["passed"]) for row in rows]
    fig, axis = plt.subplots(figsize=(11.5, 5.6))
    bars = axis.barh(
        np.arange(len(rows)),
        plot_values,
        color=[BLUE if value else RED for value in passed],
    )
    axis.axvline(1.0, color=INK, linestyle="--", label="tolerance" if language == "en" else "допуск")
    axis.set_yticks(np.arange(len(rows)), labels)
    axis.set_xscale("log")
    axis.set_xlim(1.0e-12, 3.0)
    axis.set_xlabel("Metric / tolerance" if language == "en" else "Метрика / допуск")
    axis.legend()
    for bar, passed_value, exact_value in zip(bars, passed, normalized):
        label = "PASS" if passed_value else "FAIL"
        if exact_value == 0.0:
            label += " (0)"
        axis.text(
            min(max(bar.get_width() * 1.25, 2.0e-12), 2.2),
            bar.get_y() + 0.5 * bar.get_height(),
            label,
            va="center",
        )
    axis.set_title(title("benchmark_summary", language), fontsize=16, weight="bold")
    fig.tight_layout()
    save_figure(fig, "benchmark_summary", language)


def render_odf_animation(language: str) -> None:
    result = _odf_reference_result()
    theta_deg = np.rad2deg(result["theta"])
    indices = np.linspace(0, result["time"].size - 1, 32, dtype=int)
    apply_tutorial_style()
    fig, axis = plt.subplots(figsize=(8, 4.8))
    line, = axis.plot(theta_deg, result["density"][0], color=BLUE, linewidth=2.5)
    target_line = axis.axvline(np.rad2deg(result["target"][0]), color=RED, linestyle="--")
    axis.set_xlim(-90.0, 90.0)
    axis.set_ylim(0.0, 1.1 * np.max(result["density"]))
    axis.set_xlabel(tr("angle", language))
    axis.set_ylabel(tr("density", language))
    time_text = axis.text(0.02, 0.92, "", transform=axis.transAxes)
    axis.set_title(title("odf_evolution", language))

    def update(frame: int):
        index = indices[frame]
        line.set_ydata(result["density"][index])
        x = np.rad2deg(result["target"][index])
        target_line.set_xdata([x, x])
        time_text.set_text(f"t={result['time'][index]:.2f}")
        return line, target_line, time_text

    animation = FuncAnimation(fig, update, frames=len(indices), interval=100, blit=False)
    ANIMATION_DIRECTORY.mkdir(parents=True, exist_ok=True)
    suffix = "" if language == "en" else "_ru"
    path = ANIMATION_DIRECTORY / f"odf_remodeling{suffix}.gif"
    animation.save(path, writer=PillowWriter(fps=10), dpi=100)
    plt.close(fig)


SCENARIOS = {
    "modeling_taxonomy": render_modeling_taxonomy,
    "discrete_reorientation": render_discrete_reorientation,
    "cue_degeneracy": render_cue_degeneracy,
    "loading_switch": render_loading_switch,
    "odf_evolution": render_odf_evolution,
    "alignment_diffusion_map": render_alignment_diffusion_map,
    "dispersion_metrics": render_dispersion_metrics,
    "discrete_continuous": render_discrete_continuous,
    "lanir_goh_comparison": render_lanir_goh_comparison,
    "two_family_response": render_two_family_response,
    "recruitment_crimp": render_recruitment_crimp,
    "turnover_replacement": render_turnover_replacement,
    "direct_vs_turnover": render_direct_vs_turnover,
    "deposition_stretch": render_deposition_stretch,
    "family_competition": render_family_competition,
    "identifiability": render_identifiability,
    "biology_model_map": render_biology_model_map,
    "benchmark_summary": render_benchmark_summary,
    "odf_animation": render_odf_animation,
}


def render_scenario(name: str) -> None:
    if name not in SCENARIOS:
        raise KeyError(f"Unknown Tutorial 09 scenario: {name}")
    for language in ("en", "ru"):
        SCENARIOS[name](language)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("scenario", choices=sorted(SCENARIOS))
    arguments = parser.parse_args()
    render_scenario(arguments.scenario)
