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

from biomechanics_tutorials.finite_element_growth import (  # noqa: E402
    compute_identifiability_table,
    element_field_grid,
    element_to_node_average,
    fiber_stress,
    nodal_field_grid,
    run_scenarios,
    save_csv,
    scenario_summary_rows,
)

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
FIGURES = HERE / "figures"
DATA.mkdir(exist_ok=True)
FIGURES.mkdir(exist_ok=True)


def _labels(language: str) -> dict[str, str]:
    if language == "ru":
        return {
            "mesh": "Сетка и начальное поле роста",
            "solution": "Равновесное решение",
            "history": "История stress-feedback",
            "scenario": "Сравнение сценариев",
            "iso": "Изотропный рост",
            "fiber": "Волоконный рост",
            "disp": "Модуль перемещения",
            "trace": "Trace stress",
            "fiber_stress": "Fiber stress",
            "energy": "Плотность энергии",
            "step": "Шаг",
            "value": "Значение",
            "stress": "Напряжение",
            "growth": "Рост",
            "scenario_x": "Сценарий",
            "parameter": "Показатель",
        }
    return {
        "mesh": "Mesh and initial growth field",
        "solution": "Equilibrium solution",
        "history": "Stress-feedback history",
        "scenario": "Scenario comparison",
        "iso": "Isotropic growth",
        "fiber": "Fiber growth",
        "disp": "Displacement magnitude",
        "trace": "Trace stress",
        "fiber_stress": "Fiber stress",
        "energy": "Energy density",
        "step": "Step",
        "value": "Value",
        "stress": "Stress",
        "growth": "Growth",
        "scenario_x": "Scenario",
        "parameter": "Metric",
    }


def _imshow(ax, grid, title, extent, cmap="viridis"):
    im = ax.imshow(grid, origin="lower", extent=extent, aspect="auto", cmap=cmap)
    ax.set_title(title, fontsize=11)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)


def plot_initial_fields(history, language: str, suffix: str):
    labels = _labels(language)
    mesh = history.mesh
    state = history.states[0]
    extent = [0, mesh.length, 0, mesh.height]
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), constrained_layout=True)
    for ax, val, title in [
        (axes[0, 0], state.isotropic, labels["iso"]),
        (axes[0, 1], state.fiber, labels["fiber"]),
        (axes[1, 0], np.rad2deg(state.theta), "Fiber angle, deg" if language == "en" else "Угол волокон, град"),
        (axes[1, 1], np.linalg.norm(history.equilibrium[0].growth_strain, axis=1), "Growth-strain magnitude" if language == "en" else "Модуль growth strain"),
    ]:
        _imshow(ax, element_field_grid(mesh, val), title, extent)
    fig.suptitle(labels["mesh"], fontsize=15)
    fig.savefig(FIGURES / f"initial_growth_fields{suffix}.png", dpi=180)
    plt.close(fig)


def plot_solution_fields(history, language: str, suffix: str):
    labels = _labels(language)
    mesh = history.mesh
    result = history.equilibrium[-1]
    state = history.states[-1]
    extent = [0, mesh.length, 0, mesh.height]
    displacement = np.linalg.norm(result.displacement, axis=1)
    trace = result.stress[:, 0] + result.stress[:, 1]
    ff = fiber_stress(result.stress, state.theta)
    energy = result.energy_density
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), constrained_layout=True)
    _imshow(axes[0, 0], nodal_field_grid(mesh, displacement), labels["disp"], extent)
    _imshow(axes[0, 1], element_field_grid(mesh, trace), labels["trace"], extent, cmap="coolwarm")
    _imshow(axes[1, 0], element_field_grid(mesh, ff), labels["fiber_stress"], extent, cmap="coolwarm")
    _imshow(axes[1, 1], element_field_grid(mesh, energy), labels["energy"], extent)
    fig.suptitle(labels["solution"], fontsize=15)
    fig.savefig(FIGURES / f"equilibrium_solution_fields{suffix}.png", dpi=180)
    plt.close(fig)


def plot_history(history, language: str, suffix: str):
    labels = _labels(language)
    steps = [row["step"] for row in history.metrics]
    fig, ax = plt.subplots(figsize=(11, 7), constrained_layout=True)
    ax.plot(steps, [row["mean_trace_stress"] for row in history.metrics], marker="o", label=labels["trace"])
    ax.plot(steps, [row["mean_fiber_stress"] for row in history.metrics], marker="o", label=labels["fiber_stress"])
    ax.plot(steps, [row["mean_energy_density"] for row in history.metrics], marker="o", label=labels["energy"])
    ax.plot(steps, [row["mean_growth_magnitude"] for row in history.metrics], marker="o", label=labels["growth"])
    ax.set_xlabel(labels["step"])
    ax.set_ylabel(labels["value"])
    ax.set_title(labels["history"])
    ax.grid(True, alpha=0.25)
    ax.legend(loc="best")
    fig.savefig(FIGURES / f"stress_feedback_history{suffix}.png", dpi=180)
    plt.close(fig)


def plot_scenario_comparison(rows, language: str, suffix: str):
    labels = _labels(language)
    names = [str(row["scenario"]).replace("_", "\n") for row in rows]
    x = np.arange(len(names))
    width = 0.28
    fig, ax = plt.subplots(figsize=(11, 7), constrained_layout=True)
    ax.bar(x - width, [row["final_mean_trace_stress"] for row in rows], width, label=labels["trace"])
    ax.bar(x, [row["final_mean_fiber_stress"] for row in rows], width, label=labels["fiber_stress"])
    ax.bar(x + width, [row["final_mean_energy_density"] for row in rows], width, label=labels["energy"])
    ax.set_xticks(x)
    ax.set_xticklabels(names)
    ax.set_ylabel(labels["value"])
    ax.set_title(labels["scenario"])
    ax.grid(True, axis="y", alpha=0.25)
    ax.legend(loc="best")
    fig.savefig(FIGURES / f"scenario_comparison{suffix}.png", dpi=180)
    plt.close(fig)


def main() -> None:
    scenarios = run_scenarios()
    scenario_rows = scenario_summary_rows(scenarios)
    save_csv(DATA / "scenario_summary.csv", scenario_rows)
    baseline = next(item.history for item in scenarios if item.name == "stress_feedback")
    save_csv(DATA / "time_history_stress_feedback.csv", baseline.metrics)
    save_csv(DATA / "identifiability_diagnostics.csv", compute_identifiability_table(baseline))
    np.savez_compressed(
        DATA / "finite_element_growth_dataset.npz",
        nodes=baseline.mesh.nodes,
        elements=baseline.mesh.elements,
        final_displacement=baseline.equilibrium[-1].displacement,
        final_stress=baseline.equilibrium[-1].stress,
        final_growth_strain=baseline.equilibrium[-1].growth_strain,
        final_elastic_strain=baseline.equilibrium[-1].elastic_strain,
        final_isotropic_growth=baseline.states[-1].isotropic,
        final_fiber_growth=baseline.states[-1].fiber,
        theta=baseline.states[-1].theta,
    )
    summary = {
        "tutorial": 21,
        "title": "Finite-Element Growth Model",
        "n_nodes": baseline.mesh.n_nodes,
        "n_elements": baseline.mesh.n_elements,
        "n_dofs": baseline.mesh.n_dofs,
        "final_residual_norm": baseline.metrics[-1]["residual_norm"],
        "final_mean_trace_stress": baseline.metrics[-1]["mean_trace_stress"],
        "final_mean_fiber_stress": baseline.metrics[-1]["mean_fiber_stress"],
    }
    (DATA / "benchmark_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    for language, suffix in [("en", ""), ("ru", "_ru")]:
        plot_initial_fields(baseline, language, suffix)
        plot_solution_fields(baseline, language, suffix)
        plot_history(baseline, language, suffix)
        plot_scenario_comparison(scenario_rows, language, suffix)

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
