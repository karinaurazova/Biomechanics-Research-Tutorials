"""Visualization helpers for Tutorial 02."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation, PillowWriter

from biomechanics_tutorials.collagen_dispersion import (
    axial_von_mises_density,
    dispersion_index,
    order_parameter,
    orientation_grid,
    sample_axial_von_mises,
)
from biomechanics_tutorials.localization import tr
from biomechanics_tutorials.plotting import PALETTE, apply_tutorial_style


def _prepare_output(output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)


def save_distribution_gallery(
    concentrations: tuple[float, ...],
    mean_angle: float,
    output: Path,
    *,
    language: str = "en",
) -> None:
    """Save a localized distribution gallery."""
    apply_tutorial_style()
    _prepare_output(output)
    theta = orientation_grid(1001)
    fig, axes = plt.subplots(2, 2, figsize=(11, 8), sharex=True)
    axes_flat = axes.ravel()
    line_styles = ["-", "--", "-.", ":"]
    for index, (axis, beta) in enumerate(zip(axes_flat, concentrations, strict=True)):
        density = axial_von_mises_density(theta, mean_angle, beta)
        axis.plot(
            np.rad2deg(theta),
            density,
            linewidth=2.5,
            linestyle=line_styles[index],
        )
        samples = sample_axial_von_mises(45, mean_angle, beta, seed=100 + index)
        for sample in samples:
            axis.plot(
                [np.rad2deg(sample), np.rad2deg(sample)],
                [0.0, 0.04 * density.max()],
                linewidth=0.8,
                alpha=0.35,
                color=PALETTE["slate"],
            )
        axis.axvline(np.rad2deg(mean_angle), linewidth=1.2, linestyle="--")
        order = float(order_parameter(beta))
        dispersion = float(dispersion_index(beta))
        axis.set_title(rf"$\beta={beta:g}$, $S={order:.3f}$, $D={dispersion:.3f}$")
        axis.set_xlim(-90, 90)
        axis.set_ylim(bottom=0)
    for axis in axes[-1, :]:
        axis.set_xlabel(tr("axial_orientation_deg", language))
    for axis in axes[:, 0]:
        axis.set_ylabel(tr("probability_density", language))
    fig.suptitle(tr("distribution_gallery_title", language), fontsize=16)
    fig.tight_layout()
    fig.savefig(output, dpi=220)
    plt.close(fig)


def save_tensor_verification(
    concentrations: np.ndarray,
    analytical_eigenvalues: np.ndarray,
    numerical_eigenvalues: np.ndarray,
    errors: np.ndarray,
    output: Path,
    *,
    language: str = "en",
) -> None:
    """Save localized analytical-versus-numerical tensor checks."""
    apply_tutorial_style()
    _prepare_output(output)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    axes[0].plot(
        concentrations,
        analytical_eigenvalues[:, 0],
        label=tr("analytical_major", language),
        linewidth=2.4,
    )
    axes[0].plot(
        concentrations,
        numerical_eigenvalues[:, 0],
        "o",
        fillstyle="none",
        markevery=max(1, len(concentrations) // 12),
        label=tr("quadrature_major", language),
    )
    axes[0].plot(
        concentrations,
        analytical_eigenvalues[:, 1],
        linestyle="--",
        linewidth=2.4,
        label=tr("analytical_minor", language),
    )
    axes[0].plot(
        concentrations,
        numerical_eigenvalues[:, 1],
        "s",
        fillstyle="none",
        markevery=max(1, len(concentrations) // 12),
        label=tr("quadrature_minor", language),
    )
    axes[0].set_xlabel(tr("concentration_beta", language))
    axes[0].set_ylabel(tr("orientation_tensor_eigenvalue", language))
    axes[0].set_ylim(0, 1.02)
    axes[0].legend()
    axes[0].set_title(tr("tensor_verification_title", language))

    axes[1].semilogy(concentrations, errors, linewidth=2.4)
    axes[1].set_xlabel(tr("concentration_beta", language))
    axes[1].set_ylabel(tr("maximum_component_error", language))
    axes[1].set_title(tr("quadrature_error_title", language))
    fig.tight_layout()
    fig.savefig(output, dpi=220)
    plt.close(fig)


def save_response_curves(
    stretches: np.ndarray,
    curves: dict[float, np.ndarray],
    mean_angle: float,
    output: Path,
    *,
    title_key: str,
    language: str = "en",
) -> None:
    """Save localized stress-stretch curves for one mean orientation."""
    apply_tutorial_style()
    _prepare_output(output)
    fig, axis = plt.subplots(figsize=(8.5, 5.2))
    line_styles = ["-", "--", "-.", ":", (0, (5, 1))]
    for index, (beta, stress) in enumerate(curves.items()):
        axis.plot(
            stretches,
            stress,
            linewidth=2.5,
            linestyle=line_styles[index % len(line_styles)],
            label=rf"$\beta={beta:g}$",
        )
    axis.set_xlabel(tr("uniaxial_stretch", language))
    axis.set_ylabel(tr("nominal_stress_dimensionless", language))
    axis.set_title(
        f"{tr(title_key, language)}\n"
        f"{tr('mean_fiber_angle', language, angle=np.rad2deg(mean_angle))}"
    )
    axis.legend(title=tr("concentration", language))
    fig.tight_layout()
    fig.savefig(output, dpi=220)
    plt.close(fig)


def save_anisotropy_map(
    mean_angles: np.ndarray,
    concentrations: np.ndarray,
    stress_map: np.ndarray,
    stretch: float,
    output: Path,
    *,
    language: str = "en",
) -> None:
    """Save a localized map of stress over mean angle and concentration."""
    apply_tutorial_style()
    _prepare_output(output)
    fig, axis = plt.subplots(figsize=(9.5, 5.7))
    image = axis.imshow(
        stress_map,
        origin="lower",
        aspect="auto",
        extent=[
            np.rad2deg(mean_angles[0]),
            np.rad2deg(mean_angles[-1]),
            concentrations[0],
            concentrations[-1],
        ],
        cmap="viridis",
    )
    contours = axis.contour(
        np.rad2deg(mean_angles),
        concentrations,
        stress_map,
        levels=7,
        colors="white",
        linewidths=0.8,
        alpha=0.75,
    )
    axis.clabel(contours, inline=True, fontsize=8, fmt="%.2f")
    axis.set_xlabel(tr("mean_axial_orientation", language))
    axis.set_ylabel(tr("concentration_beta", language))
    axis.set_title(tr("joint_effect_title", language, stretch=stretch))
    colorbar = fig.colorbar(image, ax=axis)
    colorbar.set_label(tr("nominal_stress_dimensionless", language))
    fig.tight_layout()
    fig.savefig(output, dpi=220)
    plt.close(fig)


def save_quadrature_convergence(
    points: np.ndarray,
    errors: np.ndarray,
    output: Path,
    *,
    language: str = "en",
) -> None:
    """Save a localized angular-integration convergence plot."""
    apply_tutorial_style()
    _prepare_output(output)
    fig, axis = plt.subplots(figsize=(8.2, 5.0))
    axis.loglog(points, errors, "o-", linewidth=2.3, markersize=6)
    axis.set_xlabel(tr("angular_quadrature_points", language))
    axis.set_ylabel(tr("maximum_stress_error", language))
    axis.set_title(tr("convergence_title", language))
    for x_value, y_value in zip(points, errors, strict=True):
        axis.annotate(
            f"{y_value:.1e}",
            (x_value, y_value),
            xytext=(4, 5),
            textcoords="offset points",
            fontsize=8,
        )
    fig.tight_layout()
    fig.savefig(output, dpi=220)
    plt.close(fig)


def save_dispersion_animation(
    output: Path,
    *,
    mean_angle: float = np.deg2rad(20.0),
    maximum_concentration: float = 12.0,
    frames: int = 55,
    fibers: int = 90,
    language: str = "en",
) -> None:
    """Save a localized synthetic dispersion animation."""
    apply_tutorial_style()
    _prepare_output(output)
    fig, (axis_fibers, axis_density) = plt.subplots(1, 2, figsize=(10.5, 4.8))
    theta_grid = orientation_grid(801)
    generator = np.random.default_rng(21)
    uniforms = generator.random(fibers)
    columns = 10
    rows = int(np.ceil(fibers / columns))
    grid_x, grid_y = np.meshgrid(
        np.linspace(-0.78, 0.78, columns),
        np.linspace(-0.72, 0.72, rows),
    )
    centers = np.column_stack((grid_x.ravel(), grid_y.ravel()))[:fibers]
    centers += generator.normal(scale=0.025, size=centers.shape)

    axis_fibers.set_xlim(-1.05, 1.05)
    axis_fibers.set_ylim(-1.05, 1.05)
    axis_fibers.set_aspect("equal")
    axis_fibers.set_xticks([])
    axis_fibers.set_yticks([])
    axis_fibers.set_title(tr("synthetic_fiber_population", language))
    segments = [
        axis_fibers.plot(
            [],
            [],
            linewidth=1.5,
            alpha=0.62,
            color=PALETTE["cyan"],
        )[0]
        for _ in range(fibers)
    ]
    mean_line = axis_fibers.plot(
        [],
        [],
        linewidth=3.0,
        linestyle="--",
        label=tr("mean_axis", language),
    )[0]
    axis_fibers.legend(loc="lower right")

    density_line = axis_density.plot([], [], linewidth=2.6)[0]
    axis_density.set_xlim(-90, 90)
    axis_density.set_xlabel(tr("axial_orientation_deg", language))
    axis_density.set_ylabel(tr("probability_density", language))
    axis_density.set_title(tr("evolving_concentration", language))
    annotation = axis_density.text(
        0.03,
        0.95,
        "",
        transform=axis_density.transAxes,
        va="top",
    )

    def deterministic_samples(beta: float) -> np.ndarray:
        if beta == 0:
            doubled = 2.0 * np.pi * uniforms - np.pi
        else:
            dense = np.linspace(-np.pi, np.pi, 5001)
            density = np.exp(beta * np.cos(dense))
            cumulative = np.cumsum(density)
            cumulative = (cumulative - cumulative[0]) / (
                cumulative[-1] - cumulative[0]
            )
            doubled = np.interp(uniforms, cumulative, dense)
        values = mean_angle + 0.5 * doubled
        return (values + np.pi / 2.0) % np.pi - np.pi / 2.0

    def update(frame: int):
        beta = maximum_concentration * frame / max(frames - 1, 1)
        samples = deterministic_samples(beta)
        for line, angle, center in zip(segments, samples, centers, strict=True):
            center_x, center_y = center
            half = 0.075
            dx = half * np.cos(angle)
            dy = half * np.sin(angle)
            line.set_data(
                [center_x - dx, center_x + dx],
                [center_y - dy, center_y + dy],
            )
        dx = 0.78 * np.cos(mean_angle)
        dy = 0.78 * np.sin(mean_angle)
        mean_line.set_data([-dx, dx], [-dy, dy])
        density = axial_von_mises_density(theta_grid, mean_angle, beta)
        density_line.set_data(np.rad2deg(theta_grid), density)
        axis_density.set_ylim(0, max(0.45, density.max() * 1.12))
        annotation.set_text(
            rf"$\beta={beta:.2f}$   $S={float(order_parameter(beta)):.3f}$"
        )
        return [*segments, mean_line, density_line, annotation]

    animation = FuncAnimation(fig, update, frames=frames, interval=90, blit=False)
    fig.suptitle(tr("dispersion_animation_title", language), fontsize=15)
    fig.tight_layout()
    animation.save(output, writer=PillowWriter(fps=10), dpi=110)
    plt.close(fig)


def save_baseline_overview(
    theta: np.ndarray,
    density: np.ndarray,
    stretches: np.ndarray,
    stress: np.ndarray,
    mean_angle: float,
    concentration: float,
    output: Path,
    *,
    language: str = "en",
) -> None:
    """Save the localized baseline density and mechanical response."""
    apply_tutorial_style()
    _prepare_output(output)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    axes[0].plot(np.rad2deg(theta), density, linewidth=2.6)
    axes[0].axvline(
        np.rad2deg(mean_angle),
        linestyle="--",
        linewidth=1.5,
        label=tr("mean_axis", language),
    )
    axes[0].set_xlabel(tr("axial_orientation_deg", language))
    axes[0].set_ylabel(tr("probability_density", language))
    axes[0].set_title(
        tr(
            "orientation_distribution_title",
            language,
            angle=np.rad2deg(mean_angle),
            beta=concentration,
        )
    )
    axes[0].legend()

    axes[1].plot(stretches, stress, linewidth=2.6)
    axes[1].set_xlabel(tr("uniaxial_stretch", language))
    axes[1].set_ylabel(tr("nominal_stress_dimensionless", language))
    axes[1].set_title(tr("tension_only_response", language))
    fig.suptitle(tr("t2_baseline_title", language), fontsize=16)
    fig.tight_layout()
    fig.savefig(output, dpi=220)
    plt.close(fig)
