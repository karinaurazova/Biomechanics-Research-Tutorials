"""Generate the core Tutorial 18 benchmark tables and figures."""

from __future__ import annotations

import csv

import matplotlib.pyplot as plt
import numpy as np

from common import DATA, FIGURES
from biomechanics_tutorials.orientation_distributions import (
    benchmark_modalities,
    build_synthetic_orientation_dataset,
    concentration_sweep,
    format_benchmark_csv,
)
from biomechanics_tutorials.plotting import apply_tutorial_style

apply_tutorial_style()

LABELS = {
    "en": {
        "ground_truth": "Ground truth",
        "sem_like_gradient": "SEM-like gradient",
        "polarization_like_map": "Polarization-like map",
        "segmented_mask": "Segmented mask",
        "mask": "Ground-truth mask",
        "sem": "SEM-like image",
        "pol": "Polarization orientation",
        "seg": "Segmentation-derived mask",
        "angle": "Orientation angle, degrees",
        "density": "ODF density",
        "concentration": "Concentration / alignment",
        "metric": "Metric value",
        "resultant": "Resultant length R",
        "kappa": "von-Mises kappa",
        "js": "JS divergence to ground truth",
        "stiffness": "Toy stiffness index",
        "overview_title": "The same architecture viewed through four synthetic modalities",
        "odf_title": "Orientation distribution functions recovered from each modality",
        "metric_title": "Concentration and error metrics",
        "sweep_title": "Changing structural order changes recovered concentration",
        "stiff_title": "Why concentration errors matter for image-informed mechanics",
    },
    "ru": {
        "ground_truth": "Точная структура",
        "sem_like_gradient": "СЭМ-подобный градиент",
        "polarization_like_map": "Поляризационная карта",
        "segmented_mask": "Маска после сегментации",
        "mask": "Истинная маска",
        "sem": "СЭМ-подобное изображение",
        "pol": "Поляризационная ориентация",
        "seg": "Маска сегментации",
        "angle": "Угол ориентации, градусы",
        "density": "Плотность ODF",
        "concentration": "Концентрация / выравнивание",
        "metric": "Значение метрики",
        "resultant": "Длина результирующего вектора R",
        "kappa": "Параметр фон Мизеса kappa",
        "js": "JS-дивергенция к точной структуре",
        "stiffness": "Учебный индекс жёсткости",
        "overview_title": "Одна архитектура в четырёх синтетических модальностях",
        "odf_title": "Распределения ориентаций, восстановленные из разных модальностей",
        "metric_title": "Параметры концентрации и ошибки",
        "sweep_title": "Изменение структурного порядка меняет восстановленную концентрацию",
        "stiff_title": "Почему ошибки концентрации важны для image-informed механики",
    },
}


def save_dataset_and_tables(dataset, results, centers, densities) -> None:
    np.savez_compressed(
        DATA / "orientation_distribution_dataset.npz",
        mask=dataset.mask,
        family_id=dataset.family_id,
        true_orientation=dataset.true_orientation,
        sem_like_image=dataset.sem_like_image,
        polarization_orientation=dataset.polarization_orientation,
        polarization_confidence=dataset.polarization_confidence,
        segmented_mask=dataset.segmented_mask,
        segmented_orientation=dataset.segmented_orientation,
        sem_orientation=dataset.sem_orientation,
        sem_confidence=dataset.sem_confidence,
        odf_centers=centers,
        **{f"odf_{name}": value for name, value in densities.items()},
    )
    (DATA / "orientation_benchmark.csv").write_text(format_benchmark_csv(results), encoding="utf-8")
    rows = concentration_sweep()
    with (DATA / "concentration_sweep.csv").open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def figure_overview(dataset, lang: str) -> None:
    lab = LABELS[lang]
    fig, axes = plt.subplots(2, 2, figsize=(12.5, 9.0), dpi=150)
    axes = axes.ravel()
    images = [
        (dataset.mask.astype(float), lab["mask"], "gray"),
        (dataset.sem_like_image, lab["sem"], "gray"),
        (np.rad2deg(dataset.polarization_orientation), lab["pol"], "hsv"),
        (dataset.segmented_mask.astype(float), lab["seg"], "gray"),
    ]
    for axis, (image, title, cmap) in zip(axes, images):
        im = axis.imshow(image, cmap=cmap, interpolation="nearest")
        axis.set_title(title)
        axis.set_xticks([])
        axis.set_yticks([])
        if cmap == "hsv":
            cb = fig.colorbar(im, ax=axis, fraction=0.046, pad=0.04)
            cb.set_label(lab["angle"])
    fig.suptitle(lab["overview_title"])
    fig.savefig(FIGURES / f"modality_overview{'_ru' if lang == 'ru' else ''}.png")
    plt.close(fig)


def figure_odf(centers, densities, lang: str) -> None:
    lab = LABELS[lang]
    fig, ax = plt.subplots(figsize=(11.0, 7.4), dpi=150)
    degrees = np.rad2deg(centers)
    for name, density in densities.items():
        ax.plot(degrees, density, linewidth=2.2, label=lab[name])
    ax.set_xlabel(lab["angle"])
    ax.set_ylabel(lab["density"])
    ax.set_title(lab["odf_title"])
    ax.legend(loc="upper right")
    fig.savefig(FIGURES / f"odf_comparison{'_ru' if lang == 'ru' else ''}.png")
    plt.close(fig)


def figure_metrics(results, lang: str) -> None:
    lab = LABELS[lang]
    names = [name for name in results if name != "ground_truth"]
    x = np.arange(len(names))
    width = 0.23
    fig, ax = plt.subplots(figsize=(12.4, 7.6), dpi=150)
    ax.bar(x - width, [results[n]["resultant_length"] for n in names], width, label=lab["resultant"])
    ax.bar(x, [results[n]["js_to_ground_truth"] for n in names], width, label=lab["js"])
    ax.bar(x + width, [results[n]["orientation_mae_deg"] / 90.0 for n in names], width, label="MAE / 90°")
    ax.set_xticks(x)
    ax.set_xticklabels([lab[n] for n in names])
    ax.set_ylabel(lab["metric"])
    ax.set_title(lab["metric_title"])
    ax.legend(loc="upper left")
    fig.savefig(FIGURES / f"metrics_summary{'_ru' if lang == 'ru' else ''}.png")
    plt.close(fig)


def figure_sweep(lang: str) -> None:
    lab = LABELS[lang]
    rows = concentration_sweep()
    modalities = ["ground_truth", "sem_like_gradient", "polarization_like_map", "segmented_mask"]
    fig, ax = plt.subplots(figsize=(11.5, 7.5), dpi=150)
    for modality in modalities:
        subset = [row for row in rows if row["modality"] == modality]
        x = [row["target_concentration"] for row in subset]
        y = [row["resultant_length"] for row in subset]
        ax.plot(x, y, marker="o", linewidth=2.1, label=lab[modality])
    ax.set_xlabel("Target concentration" if lang == "en" else "Заданная концентрация")
    ax.set_ylabel(lab["resultant"])
    ax.set_title(lab["sweep_title"])
    ax.legend(loc="lower right")
    fig.savefig(FIGURES / f"concentration_sweep{'_ru' if lang == 'ru' else ''}.png")
    plt.close(fig)


def figure_stiffness(results, lang: str) -> None:
    lab = LABELS[lang]
    names = list(results)
    fig, ax = plt.subplots(figsize=(11.2, 7.2), dpi=150)
    values = [results[n]["stiffness_index"] for n in names]
    ax.bar(np.arange(len(names)), values)
    ax.set_xticks(np.arange(len(names)))
    ax.set_xticklabels([lab[n] for n in names])
    ax.set_ylabel(lab["stiffness"])
    ax.set_title(lab["stiff_title"])
    for i, n in enumerate(names):
        err = results[n]["stiffness_error_percent"]
        ax.text(i, values[i] + 0.05, f"{err:+.1f}%", ha="center", va="bottom", fontsize=9)
    fig.savefig(FIGURES / f"biomechanics_link{'_ru' if lang == 'ru' else ''}.png")
    plt.close(fig)


def main() -> None:
    dataset = build_synthetic_orientation_dataset()
    results, centers, densities = benchmark_modalities(dataset)
    save_dataset_and_tables(dataset, results, centers, densities)
    for lang in ("en", "ru"):
        figure_overview(dataset, lang)
        figure_odf(centers, densities, lang)
        figure_metrics(results, lang)
        figure_sweep(lang)
        figure_stiffness(results, lang)
    print("Tutorial 18 orientation benchmark regenerated successfully.")


if __name__ == "__main__":
    main()
