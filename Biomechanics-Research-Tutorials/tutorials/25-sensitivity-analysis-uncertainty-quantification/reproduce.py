#!/usr/bin/env python3
"""Reproduce Tutorial 25 outputs."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import imageio.v2 as imageio

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from biomechanics_tutorials.sensitivity_uncertainty import (  # noqa: E402
    PARAMETERS, OUTPUT_NAMES, evaluate_tissue_model, nominal_parameter_vector,
    run_full_uq, sample_parameters, tornado_analysis
)

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
FIG = HERE / "figures"
ANI = HERE / "animations"
for d in [DATA, FIG, ANI]:
    d.mkdir(parents=True, exist_ok=True)


def labels_ru():
    return {
        "matrix_modulus": "Модуль матрикса",
        "fibre_gain": "Усиление волокон",
        "fibre_fraction": "Доля волокон",
        "orientation_deg": "Ориентация",
        "concentration": "Концентрация",
        "connectivity": "Связность",
        "load_scale": "Масштаб нагрузки",
        "boundary_compliance": "Податливость границы",
        "peak_stress": "Пиковое напряжение",
        "strain_energy": "Энергия деформации",
        "anisotropy_ratio": "Анизотропия",
    }


def parameter_names():
    return [p.name for p in PARAMETERS]


def save_csv(path: Path, rows: list[dict]):
    pd.DataFrame(rows).to_csv(path, index=False)


def plot_pipeline(path: Path, ru: bool = False):
    fig, ax = plt.subplots(figsize=(12.5, 4.2))
    ax.axis("off")
    if ru:
        boxes = ["Неопределённые\nпараметры", "Прямая\nмодель", "Распределения\nотклика", "Sensitivity\nindices", "Решение:\nчто важно?"]
        title = "Схема uncertainty quantification"
    else:
        boxes = ["Uncertain\nparameters", "Forward\nmodel", "Output\ndistributions", "Sensitivity\nindices", "Decision:\nwhat matters?"]
        title = "Uncertainty-quantification workflow"
    xs = np.linspace(0.08, 0.92, len(boxes))
    for x, b in zip(xs, boxes):
        ax.add_patch(plt.Rectangle((x-0.085, 0.40), 0.17, 0.28, fill=False, lw=2))
        ax.text(x, 0.54, b, ha="center", va="center", fontsize=11)
    for x0, x1 in zip(xs[:-1], xs[1:]):
        ax.annotate("", xy=(x1-0.10, 0.54), xytext=(x0+0.10, 0.54), arrowprops=dict(arrowstyle="->", lw=1.8))
    ax.text(0.5, 0.84, title, ha="center", fontsize=15, fontweight="bold")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def plot_parameter_distributions(samples, path: Path, ru: bool = False):
    names = parameter_names()
    lr = labels_ru()
    fig, axes = plt.subplots(2, 4, figsize=(14, 7))
    for ax, j, p in zip(axes.ravel(), range(len(PARAMETERS)), PARAMETERS):
        ax.hist(samples[:, j], bins=28, alpha=0.85)
        ax.axvline(p.nominal, lw=2, ls="--")
        ax.set_title(lr.get(p.name, p.name) if ru else p.name)
        ax.set_xlabel(p.unit)
        ax.set_ylabel("частота" if ru else "count")
    fig.suptitle("Распределения входных параметров" if ru else "Input parameter distributions", fontsize=15)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def plot_output_distributions(outputs, path: Path, ru: bool = False):
    names = ["peak_stress", "strain_energy", "anisotropy_ratio", "growth_stimulus"]
    lr = labels_ru()
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    for ax, name in zip(axes.ravel(), names):
        y = outputs[name]
        ax.hist(y, bins=36, alpha=0.85)
        ax.axvline(np.mean(y), lw=2, ls="--")
        ax.axvline(np.quantile(y, 0.05), lw=1.6, ls=":")
        ax.axvline(np.quantile(y, 0.95), lw=1.6, ls=":")
        ax.set_title(lr.get(name, name) if ru else name)
        ax.set_ylabel("частота" if ru else "count")
    fig.suptitle("Распределения механического отклика" if ru else "Output uncertainty distributions", fontsize=15)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def plot_sobol(sobol_peak, sobol_energy, path: Path, ru: bool = False):
    names = parameter_names()
    lr = labels_ru()
    labels = [lr.get(n, n) if ru else n for n in names]
    s_peak = [sobol_peak[n]["ST"] for n in names]
    s_energy = [sobol_energy[n]["ST"] for n in names]
    y = np.arange(len(names))
    fig, ax = plt.subplots(figsize=(11.5, 7))
    ax.barh(y - 0.18, s_peak, height=0.35, label="Пиковое напряжение" if ru else "peak stress")
    ax.barh(y + 0.18, s_energy, height=0.35, label="Энергия" if ru else "strain energy")
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.set_xlabel("total Sobol index" if not ru else "полный индекс Соболя")
    ax.set_title("Глобальная чувствительность" if ru else "Global sensitivity analysis")
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def plot_morris(morris, path: Path, ru: bool = False):
    names = parameter_names()
    lr = labels_ru()
    fig, ax = plt.subplots(figsize=(8, 7))
    for n in names:
        x = morris[n]["mu_star"]
        y = morris[n]["sigma"]
        ax.scatter(x, y, s=80)
        ax.text(x, y, "  " + (lr.get(n, n) if ru else n), va="center", fontsize=9)
    ax.set_xlabel("μ*" if not ru else "μ* (средний модуль эффекта)")
    ax.set_ylabel("σ" if not ru else "σ (нелинейность / взаимодействия)")
    ax.set_title("Morris screening" if not ru else "Morris screening: важность и взаимодействия")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def plot_tornado(tornado, path: Path, ru: bool = False):
    rows = []
    for name, d in tornado.items():
        rows.append((name, d["signed_change_low"], d["signed_change_high"], d["range"]))
    rows.sort(key=lambda t: t[3], reverse=True)
    names = [r[0] for r in rows]
    lr = labels_ru()
    labels = [lr.get(n, n) if ru else n for n in names]
    lows = np.array([r[1] for r in rows])
    highs = np.array([r[2] for r in rows])
    y = np.arange(len(names))
    fig, ax = plt.subplots(figsize=(11, 7))
    ax.barh(y, highs, height=0.35, label="верхняя граница" if ru else "upper bound")
    ax.barh(y, lows, height=0.35, label="нижняя граница" if ru else "lower bound")
    ax.axvline(0, lw=1)
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    ax.set_xlabel("изменение peak stress" if ru else "change in peak stress")
    ax.set_title("Tornado plot" if not ru else "Tornado plot: one-at-a-time чувствительность")
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def plot_uncertainty_propagation(samples, outputs, path: Path, ru: bool = False):
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.8))
    sc = axes[0].scatter(samples[:, 2], outputs["peak_stress"], c=samples[:, 3], s=8, alpha=0.6)
    axes[0].set_xlabel("fibre_fraction" if not ru else "доля волокон")
    axes[0].set_ylabel("peak_stress" if not ru else "пиковое напряжение")
    axes[0].set_title("Structure → stress" if not ru else "Структура → напряжение")
    fig.colorbar(sc, ax=axes[0], label="orientation_deg" if not ru else "ориентация, град")
    axes[1].scatter(outputs["anisotropy_ratio"], outputs["strain_energy"], s=8, alpha=0.55)
    axes[1].set_xlabel("anisotropy_ratio" if not ru else "анизотропия")
    axes[1].set_ylabel("strain_energy" if not ru else "энергия")
    axes[1].set_title("Mechanical readouts" if not ru else "Механические признаки")
    axes[2].scatter(outputs["peak_stress"], outputs["growth_stimulus"], s=8, alpha=0.55)
    axes[2].axhline(0, lw=1, ls="--")
    axes[2].set_xlabel("peak_stress" if not ru else "пиковое напряжение")
    axes[2].set_ylabel("growth_stimulus" if not ru else "стимул роста")
    axes[2].set_title("Stress → remodeling cue" if not ru else "Напряжение → стимул")
    fig.suptitle("Uncertainty propagation" if not ru else "Распространение неопределённости", fontsize=15)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def plot_posterior(samples, weights, path: Path, ru: bool = False):
    names = ["matrix_modulus", "fibre_gain", "fibre_fraction", "orientation_deg"]
    idx = [parameter_names().index(n) for n in names]
    lr = labels_ru()
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    for ax, j, n in zip(axes.ravel(), idx, names):
        ax.hist(samples[:, j], bins=28, alpha=0.45, density=True, label="prior")
        ax.hist(samples[:, j], bins=28, weights=weights, alpha=0.65, density=True, label="posterior")
        ax.set_title(lr.get(n, n) if ru else n)
        ax.legend()
    fig.suptitle("Prior-to-posterior update" if not ru else "Обновление prior → posterior", fontsize=15)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def plot_reliability(outputs, path: Path, ru: bool = False):
    limits = np.linspace(np.quantile(outputs["peak_stress"], 0.02), np.quantile(outputs["peak_stress"], 0.98), 80)
    p_fail = [np.mean(outputs["peak_stress"] > lim) for lim in limits]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(limits, p_fail, lw=2)
    ax.set_xlabel("stress limit" if not ru else "предельное напряжение")
    ax.set_ylabel("P(peak stress > limit)" if not ru else "P(пиковое напряжение > предел)")
    ax.set_title("Reliability curve" if not ru else "Кривая надёжности")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def plot_convergence(conv, path: Path, ru: bool = False):
    fig, ax = plt.subplots(figsize=(8, 5))
    n = conv["n"]
    ax.plot(n, conv["mean"], marker="o", label="mean" if not ru else "среднее")
    ax.fill_between(n, conv["q05"], conv["q95"], alpha=0.25, label="5–95%")
    ax.set_xscale("log")
    ax.set_xlabel("Monte Carlo samples" if not ru else "число Monte Carlo samples")
    ax.set_ylabel("peak_stress" if not ru else "пиковое напряжение")
    ax.set_title("Monte Carlo convergence" if not ru else "Сходимость Monte Carlo")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def make_gifs(samples, outputs, conv):
    frames = []
    checkpoints = np.unique(np.geomspace(24, len(outputs["peak_stress"]), 22).astype(int))
    for n in checkpoints:
        fig, ax = plt.subplots(figsize=(6.8, 4.6))
        y = outputs["peak_stress"][:n]
        ax.hist(y, bins=32, alpha=0.85, range=(np.min(outputs["peak_stress"]), np.max(outputs["peak_stress"])))
        ax.axvline(np.mean(y), lw=2, ls="--")
        ax.set_title(f"Monte Carlo convergence: n={n}")
        ax.set_xlabel("peak_stress")
        ax.set_ylabel("count")
        fig.tight_layout()
        tmp = ANI / f"_mc_{n}.png"
        fig.savefig(tmp, dpi=110)
        plt.close(fig)
        frames.append(imageio.imread(tmp))
        tmp.unlink(missing_ok=True)
    imageio.mimsave(ANI / "monte_carlo_convergence.gif", frames, duration=0.18)

    frames = []
    order = np.argsort(samples[:, 2])
    chunks = np.array_split(order, 22)
    selected = []
    for c in chunks:
        selected.extend(list(c))
        idx = np.array(selected, dtype=int)
        fig, ax = plt.subplots(figsize=(6.8, 4.6))
        ax.scatter(samples[idx, 2], outputs["peak_stress"][idx], c=samples[idx, 5], s=14, alpha=0.75)
        ax.set_xlim(np.min(samples[:, 2]), np.max(samples[:, 2]))
        ax.set_ylim(np.min(outputs["peak_stress"]), np.max(outputs["peak_stress"]))
        ax.set_title("Propagation: fibre fraction and connectivity")
        ax.set_xlabel("fibre_fraction")
        ax.set_ylabel("peak_stress")
        fig.tight_layout()
        tmp = ANI / f"_prop_{len(selected)}.png"
        fig.savefig(tmp, dpi=110)
        plt.close(fig)
        frames.append(imageio.imread(tmp))
        tmp.unlink(missing_ok=True)
    imageio.mimsave(ANI / "uncertainty_propagation_sweep.gif", frames, duration=0.18)


def main():
    result = run_full_uq(seed=25, n_mc=4096, n_sobol=1536)
    samples = result["samples"]
    outputs = result["outputs"]
    weights = result["likelihood"]["weights"]
    np.savez_compressed(DATA / "sensitivity_uq_dataset.npz", samples=samples, **{k: v for k, v in outputs.items() if isinstance(v, np.ndarray)}, weights=weights)

    # Tables
    save_csv(DATA / "parameter_ranges.csv", [dict(name=p.name, nominal=p.nominal, lower=p.lower, upper=p.upper, unit=p.unit, description=p.description) for p in PARAMETERS])
    save_csv(DATA / "monte_carlo_summary.csv", [dict(output=k, **v) for k, v in result["monte_carlo_summary"].items()])
    save_csv(DATA / "sobol_indices.csv", [dict(output="peak_stress", parameter=k, **v) for k, v in result["sobol_peak_stress"].items()] + [dict(output="strain_energy", parameter=k, **v) for k, v in result["sobol_strain_energy"].items()])
    save_csv(DATA / "morris_indices.csv", [dict(output="peak_stress", parameter=k, **v) for k, v in result["morris_peak_stress"].items()])
    save_csv(DATA / "tornado_summary.csv", [dict(parameter=k, **v) for k, v in result["tornado_peak_stress"].items()])
    save_csv(DATA / "posterior_summary.csv", [dict(parameter=k, **v) for k, v in result["posterior_summary"].items()])
    save_csv(DATA / "reliability_summary.csv", [result["reliability"]])
    save_csv(DATA / "convergence_trace.csv", [dict(n=int(n), mean=m, q05=q5, q95=q95) for n, m, q5, q95 in zip(result["convergence"]["n"], result["convergence"]["mean"], result["convergence"]["q05"], result["convergence"]["q95"])])
    (DATA / "benchmark_summary.json").write_text(json.dumps({
        "tutorial": 25,
        "name": "Sensitivity Analysis and Uncertainty Quantification",
        "n_parameters": len(PARAMETERS),
        "n_monte_carlo": int(samples.shape[0]),
        "probability_any_failure": result["reliability"]["p_any_failure"],
        "posterior_effective_sample_size": float(result["likelihood"]["effective_sample_size"][0]),
    }, indent=2), encoding="utf-8")

    plot_pipeline(FIG / "uq_pipeline.png", ru=False)
    plot_pipeline(FIG / "uq_pipeline_ru.png", ru=True)
    plot_parameter_distributions(samples, FIG / "parameter_distributions.png", ru=False)
    plot_parameter_distributions(samples, FIG / "parameter_distributions_ru.png", ru=True)
    plot_output_distributions(outputs, FIG / "output_distributions.png", ru=False)
    plot_output_distributions(outputs, FIG / "output_distributions_ru.png", ru=True)
    plot_sobol(result["sobol_peak_stress"], result["sobol_strain_energy"], FIG / "sobol_indices.png", ru=False)
    plot_sobol(result["sobol_peak_stress"], result["sobol_strain_energy"], FIG / "sobol_indices_ru.png", ru=True)
    plot_morris(result["morris_peak_stress"], FIG / "morris_screening.png", ru=False)
    plot_morris(result["morris_peak_stress"], FIG / "morris_screening_ru.png", ru=True)
    plot_tornado(result["tornado_peak_stress"], FIG / "tornado_peak_stress.png", ru=False)
    plot_tornado(result["tornado_peak_stress"], FIG / "tornado_peak_stress_ru.png", ru=True)
    plot_uncertainty_propagation(samples, outputs, FIG / "uncertainty_propagation.png", ru=False)
    plot_uncertainty_propagation(samples, outputs, FIG / "uncertainty_propagation_ru.png", ru=True)
    plot_posterior(samples, weights, FIG / "posterior_update.png", ru=False)
    plot_posterior(samples, weights, FIG / "posterior_update_ru.png", ru=True)
    plot_reliability(outputs, FIG / "reliability_curve.png", ru=False)
    plot_reliability(outputs, FIG / "reliability_curve_ru.png", ru=True)
    plot_convergence(result["convergence"], FIG / "monte_carlo_convergence.png", ru=False)
    plot_convergence(result["convergence"], FIG / "monte_carlo_convergence_ru.png", ru=True)
    make_gifs(samples, outputs, result["convergence"])
    print("Tutorial 25 reproduced:", HERE)


if __name__ == "__main__":
    main()
