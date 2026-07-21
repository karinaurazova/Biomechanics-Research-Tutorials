"""Figure and animation scenarios for Tutorial 07."""

from __future__ import annotations

import csv
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

from biomechanics_tutorials.growth_kinematics import (
    GrowthLawParameters,
    GrowthMaterialParameters,
    commutator_norm,
    compose_growth_increments,
    elastic_cauchy_stress,
    elastic_energy_density,
    finite_difference_first_piola,
    growth_tensor_isotropic,
    growth_tensor_orthotropic,
    growth_tensor_transversely_isotropic,
    incompatibility_norm_2d,
    jacobian_bookkeeping,
    material_basis,
    multiplicative_decomposition,
    push_forward_direction,
    reduced_strip_equilibrium,
    rotation_matrix,
    simulate_stress_driven_growth,
    total_first_piola,
    total_reference_energy,
)
from biomechanics_tutorials.plotting import PALETTE, apply_tutorial_style

from common import ANIMATION_DIRECTORY, DATA_DIRECTORY, save_figure, title, tr


def _transformed_circle(matrix: np.ndarray, count: int = 241) -> np.ndarray:
    angle = np.linspace(0.0, 2.0 * np.pi, count)
    points = np.vstack((np.cos(angle), np.sin(angle), np.zeros_like(angle)))
    return matrix @ points


def kinematics_schematic(language: str) -> None:
    apply_tutorial_style()
    fig, ax = plt.subplots(figsize=(11.5, 4.5))
    ax.axis("off")
    boxes = [
        (0.04, "Reference\nconfiguration" if language == "en" else "Отсчётная\nконфигурация"),
        (0.38, "Local grown\nconfiguration" if language == "en" else "Локальная выросшая\nконфигурация"),
        (0.72, "Current compatible\nconfiguration" if language == "en" else "Текущая совместная\nконфигурация"),
    ]
    for x, label in boxes:
        patch = FancyBboxPatch(
            (x, 0.35), 0.23, 0.28, boxstyle="round,pad=0.03", facecolor="#FFFFFF",
            edgecolor=PALETTE["blue"], linewidth=2.0,
        )
        ax.add_patch(patch)
        ax.text(x + 0.115, 0.49, label, ha="center", va="center", fontsize=12)
    arrows = [
        (0.27, 0.38, r"$\mathbf{F}_g$", "local growth" if language == "en" else "локальный рост"),
        (0.61, 0.72, r"$\mathbf{F}_e$", "elastic accommodation" if language == "en" else "упругая аккомодация"),
        (0.27, 0.72, r"$\mathbf{F}=\mathbf{F}_e\mathbf{F}_g$", "observable deformation" if language == "en" else "наблюдаемая деформация"),
    ]
    for start, end, symbol, caption in arrows:
        y = 0.49 if end - start < 0.4 else 0.19
        arrow = FancyArrowPatch((start, y), (end, y), arrowstyle="-|>", mutation_scale=18,
                                linewidth=2.0, color=PALETTE["ink"])
        ax.add_patch(arrow)
        ax.text((start + end) / 2, y + 0.055, symbol, ha="center", fontsize=14)
        ax.text((start + end) / 2, y - 0.07, caption, ha="center", fontsize=9)
    ax.text(
        0.5, 0.83,
        "Fg may be locally stress-free but globally incompatible" if language == "en"
        else "Fg может быть локально ненапряжённым, но глобально несовместным",
        ha="center", fontsize=12, color=PALETTE["slate"],
    )
    fig.suptitle(title("kinematics_schematic", language))
    save_figure(fig, "kinematics_schematic", language)


def growth_tensor_atlas(language: str) -> None:
    apply_tutorial_style()
    tensors = [
        ("Isotropic" if language == "en" else "Изотропный", growth_tensor_isotropic(linear_growth=1.18)),
        ("Fiber growth" if language == "en" else "Рост вдоль волокна", growth_tensor_transversely_isotropic(1.35, 1.0)),
        ("Transverse growth" if language == "en" else "Поперечный рост", growth_tensor_transversely_isotropic(1.0, 1.22)),
        ("Orthotropic" if language == "en" else "Ортотропный", growth_tensor_orthotropic([1.30, 1.10, 0.92], material_basis([1, 1, 0], [0, 0, 1]))),
    ]
    fig, axes = plt.subplots(1, 4, figsize=(13.5, 3.6), sharex=True, sharey=True)
    for ax, (label, tensor) in zip(axes, tensors, strict=True):
        original = _transformed_circle(np.eye(3))
        grown = _transformed_circle(tensor)
        ax.plot(original[0], original[1], linestyle="--", color=PALETTE["slate"], label="reference")
        ax.plot(grown[0], grown[1], color=PALETTE["blue"], linewidth=2.2)
        ax.set_title(label)
        ax.set_aspect("equal")
        ax.set_xlim(-1.55, 1.55)
        ax.set_ylim(-1.55, 1.55)
        ax.text(0.02, 0.03, f"Jg={np.linalg.det(tensor):.2f}", transform=ax.transAxes)
    fig.suptitle(title("growth_tensor_atlas", language))
    fig.tight_layout()
    save_figure(fig, "growth_tensor_atlas", language)


def determinant_bookkeeping(language: str) -> None:
    apply_tutorial_style()
    linear = np.linspace(0.82, 1.32, 101)
    j = []
    je = []
    jg = []
    for value in linear:
        growth = growth_tensor_isotropic(linear_growth=value)
        total = np.diag([1.18, 0.96, 0.92])
        values = jacobian_bookkeeping(total, growth)
        j.append(values["J"])
        je.append(values["Je"])
        jg.append(values["Jg"])
    fig, ax = plt.subplots(figsize=(7.3, 4.7))
    ax.plot(linear, j, label="J", linewidth=2.2)
    ax.plot(linear, je, label="Je", linewidth=2.2)
    ax.plot(linear, jg, label="Jg", linewidth=2.2)
    ax.plot(linear, np.asarray(je) * np.asarray(jg), linestyle="--", label="Je Jg")
    ax.set_xlabel(tr("growth_stretch", language))
    ax.set_ylabel("volume ratio" if language == "en" else "объёмный коэффициент")
    ax.legend(ncol=2)
    ax.set_title(title("determinant_bookkeeping", language))
    fig.tight_layout()
    save_figure(fig, "determinant_bookkeeping", language)


def free_constrained_growth(language: str) -> None:
    apply_tutorial_style()
    stretches = np.linspace(0.82, 1.28, 161)
    free_energy = []
    constrained_energy = []
    constrained_stress = []
    for value in stretches:
        growth = growth_tensor_isotropic(linear_growth=value)
        free_elastic, _ = multiplicative_decomposition(growth, growth)
        constrained_elastic, _ = multiplicative_decomposition(np.eye(3), growth)
        free_energy.append(elastic_energy_density(free_elastic))
        constrained_energy.append(total_reference_energy(np.eye(3), growth))
        constrained_stress.append(np.trace(elastic_cauchy_stress(constrained_elastic)) / 3.0)
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.2))
    axes[0].plot(stretches, free_energy, label="free" if language == "en" else "свободный")
    axes[0].plot(stretches, constrained_energy, label="constrained" if language == "en" else "стеснённый")
    axes[0].set_xlabel(tr("growth_stretch", language))
    axes[0].set_ylabel(tr("energy", language))
    axes[0].legend()
    axes[1].plot(stretches, constrained_stress)
    axes[1].axhline(0.0, color=PALETTE["slate"], linewidth=1.0)
    axes[1].set_xlabel(tr("growth_stretch", language))
    axes[1].set_ylabel("mean Cauchy stress" if language == "en" else "среднее напряжение Коши")
    fig.suptitle(title("free_constrained_growth", language))
    fig.tight_layout()
    save_figure(fig, "free_constrained_growth", language)


def frame_indifference(language: str) -> None:
    apply_tutorial_style()
    angles = np.linspace(0.0, 360.0, 181)
    total = np.array([[1.22, 0.16, 0.0], [0.0, 0.94, 0.03], [0.0, 0.0, 0.91]])
    growth = np.diag([1.08, 0.98, 1.02])
    values = [total_reference_energy(rotation_matrix([0.2, 0.7, 0.3], np.deg2rad(a)) @ total, growth) for a in angles]
    baseline = values[0]
    fig, ax = plt.subplots(figsize=(7.4, 4.5))
    ax.plot(angles, np.asarray(values) - baseline)
    ax.set_xlabel(tr("angle", language))
    ax.set_ylabel("energy change" if language == "en" else "изменение энергии")
    ax.ticklabel_format(axis="y", style="sci", scilimits=(-12, -12))
    ax.set_title(title("frame_indifference", language))
    fig.tight_layout()
    save_figure(fig, "frame_indifference", language)


def decomposition_nonuniqueness(language: str) -> None:
    apply_tutorial_style()
    total = np.diag([1.25, 0.94, 0.90])
    growth_x = np.linspace(0.85, 1.35, 151)
    energy = []
    elastic_x = []
    for value in growth_x:
        growth = np.diag([value, 1.0, 1.0])
        elastic, _ = multiplicative_decomposition(total, growth)
        elastic_x.append(elastic[0, 0])
        energy.append(total_reference_energy(total, growth))
    fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.2))
    axes[0].plot(growth_x, elastic_x)
    axes[0].set_xlabel(tr("growth_stretch", language))
    axes[0].set_ylabel(tr("elastic_stretch", language))
    axes[1].plot(growth_x, energy)
    axes[1].set_xlabel(tr("growth_stretch", language))
    axes[1].set_ylabel(tr("energy", language))
    fig.suptitle(title("decomposition_nonuniqueness", language))
    fig.tight_layout()
    save_figure(fig, "decomposition_nonuniqueness", language)


def _relaxation_result(rate: float = 0.10, target: float = 0.0, mode: str = "diagonal"):
    time = np.linspace(0.0, 35.0, 1401)
    stretch = 1.35
    total = np.diag([stretch, 1.0 / np.sqrt(stretch), 1.0 / np.sqrt(stretch)])
    law = GrowthLawParameters(rate=rate, target_mandel=target, mode=mode, response_limit=0.16)
    return simulate_stress_driven_growth(time, total, law=law)


def stress_relaxation(language: str) -> None:
    apply_tutorial_style()
    result = _relaxation_result()
    time = result["time"]
    fig, axes = plt.subplots(1, 3, figsize=(14.0, 4.0))
    axes[0].plot(time, result["Fg"][:, 0, 0], label="g_f")
    axes[0].plot(time, result["Fg"][:, 1, 1], label="g_s")
    axes[0].plot(time, result["Fg"][:, 2, 2], label="g_n")
    axes[0].set_xlabel(tr("time", language))
    axes[0].set_ylabel(tr("growth_stretch", language))
    axes[0].legend()
    axes[1].plot(time, result["mandel"][:, 0, 0], label="Mff")
    axes[1].plot(time, result["mandel"][:, 1, 1], label="Mss")
    axes[1].set_xlabel(tr("time", language))
    axes[1].set_ylabel(tr("mandel", language))
    axes[1].legend()
    axes[2].semilogy(time, np.maximum(result["energy"], 1.0e-12))
    axes[2].set_xlabel(tr("time", language))
    axes[2].set_ylabel(tr("energy", language))
    fig.suptitle(title("stress_relaxation", language))
    fig.tight_layout()
    save_figure(fig, "stress_relaxation", language)


def growth_law_sweep(language: str) -> None:
    apply_tutorial_style()
    rates = [0.03, 0.07, 0.14]
    targets = [0.0, 0.08]
    fig, axes = plt.subplots(1, 2, figsize=(11.4, 4.2))
    for rate in rates:
        result = _relaxation_result(rate=rate)
        axes[0].plot(result["time"], result["mandel"][:, 0, 0], label=f"k={rate}")
    for target in targets:
        result = _relaxation_result(rate=0.09, target=target)
        axes[1].plot(result["time"], result["mandel"][:, 0, 0], label=f"M*= {target}")
    axes[0].set_xlabel(tr("time", language))
    axes[0].set_ylabel("Mff")
    axes[0].legend()
    axes[1].set_xlabel(tr("time", language))
    axes[1].set_ylabel("Mff")
    axes[1].legend()
    fig.suptitle(title("growth_law_sweep", language))
    fig.tight_layout()
    save_figure(fig, "growth_law_sweep", language)


def anisotropic_growth(language: str) -> None:
    apply_tutorial_style()
    time = np.linspace(0.0, 28.0, 1101)
    total = np.diag([1.28, 1.10, 1.0 / (1.28 * 1.10)])
    modes = ["isotropic", "diagonal", "symmetric"]
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.0))
    for mode in modes:
        result = simulate_stress_driven_growth(
            time, total,
            law=GrowthLawParameters(rate=0.09, mode=mode, response_limit=0.14),
        )
        axes[0].plot(time, result["Fg"][:, 0, 0], label=mode)
        axes[1].plot(time, result["Fg"][:, 1, 1], label=mode)
        axes[2].plot(time, result["energy"], label=mode)
    for ax, ylabel in zip(axes, ["Fg11", "Fg22", tr("energy", language)], strict=True):
        ax.set_xlabel(tr("time", language))
        ax.set_ylabel(ylabel)
        ax.legend()
    fig.suptitle(title("anisotropic_growth", language))
    fig.tight_layout()
    save_figure(fig, "anisotropic_growth", language)


def noncommutative_paths(language: str) -> None:
    apply_tutorial_style()
    angles = np.linspace(0.0, 90.0, 91)
    difference = []
    commutator = []
    first = growth_tensor_orthotropic([1.22, 0.94, 1.0])
    for angle in angles:
        q = rotation_matrix([0.0, 0.0, 1.0], np.deg2rad(angle))
        second = growth_tensor_orthotropic([1.16, 0.91, 1.0], q)
        ab = compose_growth_increments([first, second])
        ba = compose_growth_increments([second, first])
        difference.append(np.linalg.norm(ab - ba))
        commutator.append(commutator_norm(first, second))
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    ax.plot(angles, difference, label="||Fg_BA - Fg_AB||")
    ax.plot(angles, commutator, linestyle="--", label=tr("commutator", language))
    ax.set_xlabel(tr("angle", language))
    ax.set_ylabel("path difference" if language == "en" else "различие путей")
    ax.legend()
    ax.set_title(title("noncommutative_paths", language))
    fig.tight_layout()
    save_figure(fig, "noncommutative_paths", language)


def incompatibility_map(language: str) -> None:
    apply_tutorial_style()
    y, x = np.mgrid[-1.0:1.0:101j, -1.0:1.0:101j]
    theta = 1.0 + 0.22 * np.exp(-3.5 * (x**2 + y**2)) + 0.05 * x
    field = np.zeros(theta.shape + (2, 2))
    field[..., 0, 0] = theta
    field[..., 1, 1] = theta
    incompatibility = incompatibility_norm_2d(
        field, x[0, 1] - x[0, 0], y[1, 0] - y[0, 0]
    )
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.2))
    image0 = axes[0].imshow(theta, origin="lower", extent=(-1, 1, -1, 1), cmap="viridis")
    axes[0].set_title(tr("growth_stretch", language))
    fig.colorbar(image0, ax=axes[0], shrink=0.82)
    image1 = axes[1].imshow(incompatibility, origin="lower", extent=(-1, 1, -1, 1), cmap="magma")
    axes[1].set_title(tr("incompatibility", language))
    fig.colorbar(image1, ax=axes[1], shrink=0.82)
    for ax in axes:
        ax.set_xlabel("x")
        ax.set_ylabel("y")
    fig.suptitle(title("incompatibility_map", language))
    fig.tight_layout()
    save_figure(fig, "incompatibility_map", language)


def differential_growth_strip(language: str) -> None:
    apply_tutorial_style()
    z = np.linspace(-0.5, 0.5, 401)
    gradients = [0.0, 0.12, 0.24, 0.36]
    fig, axes = plt.subplots(1, 3, figsize=(13.4, 4.1))
    curvatures = []
    for gradient in gradients:
        growth = 1.0 + gradient * z
        result = reduced_strip_equilibrium(z, growth)
        curvatures.append(result["curvature"])
        axes[0].plot(growth, z, label=f"α={gradient:.2f}")
        axes[1].plot(result["nominal_stress"], z, label=f"α={gradient:.2f}")
    axes[2].plot(gradients, curvatures, marker="o")
    axes[0].set_xlabel(tr("growth_stretch", language))
    axes[0].set_ylabel(tr("position", language))
    axes[1].set_xlabel(tr("stress", language))
    axes[1].set_ylabel(tr("position", language))
    axes[2].set_xlabel("growth gradient" if language == "en" else "градиент роста")
    axes[2].set_ylabel(tr("curvature", language))
    axes[0].legend()
    axes[1].legend()
    fig.suptitle(title("differential_growth_strip", language))
    fig.tight_layout()
    save_figure(fig, "differential_growth_strip", language)


def direction_pushforward(language: str) -> None:
    apply_tutorial_style()
    angles = np.linspace(-80.0, 80.0, 161)
    growth = growth_tensor_orthotropic([1.30, 0.92, 1.0], material_basis([1, 1, 0], [0, 0, 1]))
    elastic = np.array([[1.08, 0.22, 0.0], [0.0, 0.96, 0.0], [0.0, 0.0, 1.0]])
    total = elastic @ growth
    grown_angles = []
    total_angles = []
    for angle in angles:
        direction = np.array([np.cos(np.deg2rad(angle)), np.sin(np.deg2rad(angle)), 0.0])
        grown = push_forward_direction(growth, direction)
        current = push_forward_direction(total, direction)
        grown_angles.append(np.rad2deg(np.arctan2(grown[1], grown[0])))
        total_angles.append(np.rad2deg(np.arctan2(current[1], current[0])))
    fig, ax = plt.subplots(figsize=(7.5, 4.7))
    ax.plot(angles, angles, linestyle=":", color=PALETTE["slate"], label="identity")
    ax.plot(angles, grown_angles, label="Fg")
    ax.plot(angles, total_angles, label="F=Fe Fg")
    ax.set_xlabel("reference angle" if language == "en" else "отсчётный угол")
    ax.set_ylabel("current angle" if language == "en" else "текущий угол")
    ax.legend()
    ax.set_title(title("direction_pushforward", language))
    fig.tight_layout()
    save_figure(fig, "direction_pushforward", language)


def _benchmark_rows() -> list[dict[str, str | float]]:
    material = GrowthMaterialParameters(1.3, 20.0)
    total = np.array([[1.18, 0.08, 0.0], [0.0, 0.96, 0.0], [0.0, 0.0, 0.92]])
    growth = np.diag([1.08, 0.98, 1.02])
    bookkeeping = jacobian_bookkeeping(total, growth)
    analytical = total_first_piola(total, growth, material)
    numerical = finite_difference_first_piola(total, growth, material)
    rotation = rotation_matrix([0.2, 0.7, 0.4], 0.75)
    frame_error = abs(total_reference_energy(rotation @ total, growth, material) - total_reference_energy(total, growth, material))
    z = np.linspace(-0.5, 0.5, 401)
    strip = reduced_strip_equilibrium(z, 1.0 + 0.25 * z)
    constant_field = np.zeros((31, 31, 2, 2))
    constant_field[...] = np.diag([1.1, 0.95])
    return [
        {"test": "determinant_product", "value": abs(bookkeeping["error"]), "tolerance": 1e-12},
        {"test": "stress_derivative", "value": float(np.max(np.abs(analytical - numerical))), "tolerance": 5e-5},
        {"test": "frame_indifference", "value": frame_error, "tolerance": 1e-11},
        {"test": "strip_force_residual", "value": abs(float(strip["force_residual"])), "tolerance": 1e-6},
        {"test": "strip_moment_residual", "value": abs(float(strip["moment_residual"])), "tolerance": 1e-6},
        {"test": "compatible_field_curl", "value": float(np.max(incompatibility_norm_2d(constant_field))), "tolerance": 1e-12},
    ]


def benchmark_summary(language: str) -> None:
    apply_tutorial_style()
    rows = _benchmark_rows()
    DATA_DIRECTORY.mkdir(parents=True, exist_ok=True)
    csv_path = DATA_DIRECTORY / "growth_kinematics_benchmark.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=["test", "value", "tolerance", "passed"])
        writer.writeheader()
        for row in rows:
            writer.writerow({**row, "passed": float(row["value"]) <= float(row["tolerance"])})
    translations = {
        "determinant_product": "баланс определителей",
        "stress_derivative": "производная энергии",
        "frame_indifference": "объективность",
        "strip_force_residual": "невязка силы в полосе",
        "strip_moment_residual": "невязка момента в полосе",
        "compatible_field_curl": "ротор совместного поля",
    }
    labels = [str(row["test"]) if language == "en" else translations[str(row["test"])] for row in rows]
    ratios = [max(float(row["value"]) / float(row["tolerance"]), 1.0e-6) for row in rows]
    fig, ax = plt.subplots(figsize=(9.0, 4.8))
    positions = np.arange(len(rows))
    ax.barh(positions, ratios)
    ax.axvline(1.0, color=PALETTE["ink"], linestyle="--", label="tolerance" if language == "en" else "допуск")
    ax.set_yticks(positions, labels)
    ax.set_xscale("log")
    ax.set_xlabel("error / tolerance" if language == "en" else "ошибка / допуск")
    ax.legend()
    ax.set_title(title("benchmark_summary", language))
    fig.tight_layout()
    save_figure(fig, "benchmark_summary", language)


def relaxation_animation(language: str) -> None:
    apply_tutorial_style()
    result = _relaxation_result(rate=0.11)
    indices = np.linspace(0, result["time"].size - 1, 70, dtype=int)
    fig, axes = plt.subplots(1, 2, figsize=(9.5, 4.2))
    time = result["time"]
    axes[0].plot(time, result["mandel"][:, 0, 0], color=PALETTE["blue"])
    marker0, = axes[0].plot([], [], "o", color=PALETTE["lime"], markersize=8)
    axes[0].set_xlabel(tr("time", language))
    axes[0].set_ylabel("Mff")
    axes[1].plot(time, result["Fg"][:, 0, 0], color=PALETTE["cyan"])
    marker1, = axes[1].plot([], [], "o", color=PALETTE["lime"], markersize=8)
    axes[1].set_xlabel(tr("time", language))
    axes[1].set_ylabel("Fg11")
    fig.suptitle(title("stress_relaxation", language))

    def update(frame: int):
        index = indices[frame]
        marker0.set_data([time[index]], [result["mandel"][index, 0, 0]])
        marker1.set_data([time[index]], [result["Fg"][index, 0, 0]])
        return marker0, marker1

    animation = FuncAnimation(fig, update, frames=len(indices), interval=80, blit=True)
    suffix = "" if language == "en" else "_ru"
    path = ANIMATION_DIRECTORY / f"stress_relaxation{suffix}.gif"
    path.parent.mkdir(parents=True, exist_ok=True)
    animation.save(path, writer=PillowWriter(fps=12))
    plt.close(fig)
