from __future__ import annotations

import json
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np


def _find_repository_root(start: Path) -> Path:
    current = start.resolve()
    for candidate in [current, *current.parents]:
        if (candidate / "src" / "biomechanics_tutorials").exists():
            return candidate
    raise RuntimeError("Could not locate repository root containing src/biomechanics_tutorials.")


REPOSITORY_ROOT = _find_repository_root(Path(__file__))
SOURCE_DIRECTORY = REPOSITORY_ROOT / "src"
if str(SOURCE_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIRECTORY))

from biomechanics_tutorials.rve_homogenization import (  # noqa: E402
    convergence_study,
    directional_young_modulus,
    element_field_to_grid,
    export_rve_dataset,
    homogenize_rve,
    save_csv,
    stiffness_summary,
)

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
FIGURES = HERE / "figures"
DATA.mkdir(exist_ok=True)
FIGURES.mkdir(exist_ok=True)


def labels(language: str) -> dict[str, str]:
    if language == "ru":
        return {
            "micro": "Синтетический RVE: структурные поля",
            "theta": "Ориентация волокон, град",
            "rho": "Плотность волокон",
            "pore": "Поры",
            "conn": "Связность",
            "stiffness": "Эффективные матрицы жёсткости",
            "periodic": "Периодическая RVE-задача",
            "disp": "Модуль перемещения",
            "sxx": "Напряжение sigma_xx",
            "energy": "Плотность энергии",
            "bounds": "Сравнение оценок жёсткости",
            "conv": "Сходимость RVE",
            "dir": "Направленная жёсткость",
            "angle": "Угол, град",
            "young": "Направленный модуль Юнга",
            "value": "Значение",
            "method": "Метод",
            "resolution": "Разрешение RVE, nx=ny",
        }
    return {
        "micro": "Synthetic RVE: structural fields",
        "theta": "Fiber orientation, deg",
        "rho": "Fiber density",
        "pore": "Pores",
        "conn": "Connectivity",
        "stiffness": "Effective stiffness matrices",
        "periodic": "Periodic RVE solution",
        "disp": "Displacement magnitude",
        "sxx": "Stress sigma_xx",
        "energy": "Energy density",
        "bounds": "Stiffness estimate comparison",
        "conv": "RVE convergence",
        "dir": "Directional stiffness",
        "angle": "Angle, deg",
        "young": "Directional Young modulus",
        "value": "Value",
        "method": "Method",
        "resolution": "RVE resolution, nx=ny",
    }


def _imshow(ax, image, title, cmap="viridis"):
    im = ax.imshow(image, origin="lower", aspect="auto", cmap=cmap)
    ax.set_title(title, fontsize=11)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)


def plot_microstructure(result, language: str, suffix: str) -> None:
    lab = labels(language)
    m = result.microstructure
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), constrained_layout=True)
    _imshow(axes[0, 0], np.rad2deg(m.theta), lab["theta"], cmap="twilight")
    _imshow(axes[0, 1], m.rho_f, lab["rho"])
    _imshow(axes[1, 0], m.pore, lab["pore"], cmap="gray")
    _imshow(axes[1, 1], m.connectivity, lab["conn"])
    fig.suptitle(lab["micro"], fontsize=15)
    fig.savefig(FIGURES / f"rve_microstructure_fields{suffix}.png", dpi=180)
    plt.close(fig)


def plot_stiffness_matrices(result, language: str, suffix: str) -> None:
    lab = labels(language)
    mats = [("Voigt", result.voigt_stiffness), ("Periodic", result.periodic_stiffness), ("Reuss", result.reuss_stiffness)]
    vmax = max(float(np.max(np.abs(M))) for _, M in mats)
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.5), constrained_layout=True)
    for ax, (title, M) in zip(axes, mats):
        im = ax.imshow(M, vmin=-0.15 * vmax, vmax=vmax, cmap="viridis")
        ax.set_title(title)
        ax.set_xticks([0, 1, 2])
        ax.set_yticks([0, 1, 2])
        ax.set_xticklabels(["xx", "yy", "xy"])
        ax.set_yticklabels(["xx", "yy", "xy"])
        for i in range(3):
            for j in range(3):
                ax.text(j, i, f"{M[i, j]:.1f}", ha="center", va="center", fontsize=9)
        plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.suptitle(lab["stiffness"], fontsize=15)
    fig.savefig(FIGURES / f"effective_stiffness_matrices{suffix}.png", dpi=180)
    plt.close(fig)


def plot_periodic_solution(result, language: str, suffix: str) -> None:
    lab = labels(language)
    mesh = result.mesh
    case = result.cases[0]
    disp = np.linalg.norm(case.displacement, axis=1).reshape(mesh.ny + 1, mesh.nx + 1)
    sxx = element_field_to_grid(mesh, case.element_stress[:, 0])
    energy = element_field_to_grid(mesh, case.element_energy)
    strain = element_field_to_grid(mesh, case.element_strain[:, 0])
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), constrained_layout=True)
    _imshow(axes[0, 0], disp, lab["disp"])
    _imshow(axes[0, 1], strain, "exx" if language == "en" else "Деформация exx")
    _imshow(axes[1, 0], sxx, lab["sxx"], cmap="coolwarm")
    _imshow(axes[1, 1], energy, lab["energy"])
    fig.suptitle(lab["periodic"], fontsize=15)
    fig.savefig(FIGURES / f"periodic_solution_fields{suffix}.png", dpi=180)
    plt.close(fig)


def plot_bounds(result, language: str, suffix: str) -> None:
    lab = labels(language)
    rows = [
        stiffness_summary(result.voigt_stiffness, "Voigt"),
        stiffness_summary(result.periodic_stiffness, "Periodic"),
        stiffness_summary(result.reuss_stiffness, "Reuss"),
    ]
    methods = [r["method"] for r in rows]
    x = np.arange(len(methods))
    width = 0.22
    fig, ax = plt.subplots(figsize=(11, 7), constrained_layout=True)
    ax.bar(x - width, [r["C11"] for r in rows], width, label="C11")
    ax.bar(x, [r["C22"] for r in rows], width, label="C22")
    ax.bar(x + width, [r["C66"] for r in rows], width, label="C66")
    ax.set_xticks(x)
    ax.set_xticklabels(methods)
    ax.set_ylabel(lab["value"])
    ax.set_xlabel(lab["method"])
    ax.set_title(lab["bounds"])
    ax.grid(True, axis="y", alpha=0.25)
    ax.legend(loc="best")
    fig.savefig(FIGURES / f"bounds_comparison{suffix}.png", dpi=180)
    plt.close(fig)


def plot_directional_stiffness(result, language: str, suffix: str) -> None:
    lab = labels(language)
    fig, ax = plt.subplots(figsize=(11, 7), constrained_layout=True)
    for name, C in [("Voigt", result.voigt_stiffness), ("Periodic", result.periodic_stiffness), ("Reuss", result.reuss_stiffness)]:
        angles, E = directional_young_modulus(C)
        ax.plot(np.rad2deg(angles), E, label=name)
    ax.set_xlabel(lab["angle"])
    ax.set_ylabel(lab["young"])
    ax.set_title(lab["dir"])
    ax.grid(True, alpha=0.25)
    ax.legend(loc="best")
    fig.savefig(FIGURES / f"directional_stiffness{suffix}.png", dpi=180)
    plt.close(fig)


def plot_convergence(rows, language: str, suffix: str) -> None:
    lab = labels(language)
    n = [row["nx"] for row in rows]
    fig, ax = plt.subplots(figsize=(11, 7), constrained_layout=True)
    ax.plot(n, [row["periodic_C11"] for row in rows], marker="o", label="C11")
    ax.plot(n, [row["periodic_C22"] for row in rows], marker="o", label="C22")
    ax.plot(n, [row["periodic_C66"] for row in rows], marker="o", label="C66")
    ax.plot(n, [row["periodic_anisotropy_ratio"] for row in rows], marker="o", label="anisotropy" if language == "en" else "анизотропия")
    ax.set_xlabel(lab["resolution"])
    ax.set_ylabel(lab["value"])
    ax.set_title(lab["conv"])
    ax.grid(True, alpha=0.25)
    ax.legend(loc="best")
    fig.savefig(FIGURES / f"rve_convergence{suffix}.png", dpi=180)
    plt.close(fig)


def main() -> None:
    result = homogenize_rve(nx=14, ny=14, seed=22)
    convergence = convergence_study((6, 8, 10, 12, 14), seed=22)

    stiffness_rows = [
        stiffness_summary(result.voigt_stiffness, "Voigt"),
        stiffness_summary(result.periodic_stiffness, "Periodic"),
        stiffness_summary(result.reuss_stiffness, "Reuss"),
    ]
    case_rows = []
    for case in result.cases:
        case_rows.append({
            "case": case.name,
            "macro_exx": float(case.macro_strain[0]),
            "macro_eyy": float(case.macro_strain[1]),
            "macro_gxy": float(case.macro_strain[2]),
            "avg_sxx": float(case.average_stress[0]),
            "avg_syy": float(case.average_stress[1]),
            "avg_sxy": float(case.average_stress[2]),
            "hill_mandel_error": float(case.hill_mandel_error),
            "reduced_residual_norm": float(case.reduced_residual_norm),
        })

    save_csv(DATA / "stiffness_summary.csv", stiffness_rows)
    save_csv(DATA / "periodic_case_summary.csv", case_rows)
    save_csv(DATA / "convergence_study.csv", convergence)
    export_rve_dataset(result, DATA / "rve_homogenization_dataset.npz")

    summary = {
        "tutorial": 22,
        "title": "RVE Homogenization",
        "n_nodes": result.mesh.n_nodes,
        "n_elements": result.mesh.n_elements,
        "fiber_volume_fraction": result.metrics["fiber_volume_fraction"],
        "pore_fraction": result.metrics["pore_fraction"],
        "periodic_C11": float(result.periodic_stiffness[0, 0]),
        "periodic_C22": float(result.periodic_stiffness[1, 1]),
        "periodic_C66": float(result.periodic_stiffness[2, 2]),
        "periodic_anisotropy_ratio": result.metrics["periodic_anisotropy_ratio"],
        "max_hill_mandel_error": result.metrics["max_hill_mandel_error"],
        "max_reduced_residual_norm": result.metrics["max_reduced_residual_norm"],
    }
    (DATA / "benchmark_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    for language, suffix in [("en", ""), ("ru", "_ru")]:
        plot_microstructure(result, language, suffix)
        plot_stiffness_matrices(result, language, suffix)
        plot_periodic_solution(result, language, suffix)
        plot_bounds(result, language, suffix)
        plot_directional_stiffness(result, language, suffix)
        plot_convergence(convergence, language, suffix)

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
