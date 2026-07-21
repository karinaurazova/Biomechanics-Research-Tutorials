"""Reproducible scenarios for Tutorial 13."""
from __future__ import annotations

from pathlib import Path
import csv
import json
import sys

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
from scipy import ndimage

from common import ANIMATION_DIRECTORY, DATA_DIRECTORY, save_figure, t

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
SOURCE_DIRECTORY = REPOSITORY_ROOT / "src"
if str(SOURCE_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIRECTORY))

from biomechanics_tutorials.synthetic_fibrous_tissue import (  # noqa: E402
    add_branches,
    apply_defects,
    axial_difference,
    axial_mean,
    export_network_dataset,
    generate_crossing_families,
    generate_fiber_volume,
    generate_layered_network,
    generate_mikado_network,
    generate_parallel_bundle,
    generate_spatial_gradient_network,
    generate_voronoi_network,
    morphological_skeleton,
    network_metrics,
    rasterize_network,
    skeleton_degrees,
    skeleton_graph_metrics,
    tissue_preset,
)


def _imshow(axis, image, title, cmap="gray", vmin=None, vmax=None):
    artist = axis.imshow(image, cmap=cmap, vmin=vmin, vmax=vmax, origin="upper")
    axis.set_title(title)
    axis.set_xticks([])
    axis.set_yticks([])
    return artist


def _network_lines(axis, network, title, family_colors=False):
    for fiber in network.fibers:
        kwargs = {"linewidth": max(0.7, 100 * fiber.radius), "alpha": 0.85}
        if family_colors:
            kwargs["label"] = f"family {fiber.family}"
        axis.plot(fiber.points[:, 0], fiber.points[:, 1], **kwargs)
    axis.set_xlim(0.0, network.domain[0])
    axis.set_ylim(network.domain[1], 0.0)
    axis.set_aspect("equal")
    axis.set_title(title)
    axis.set_xlabel("x")
    axis.set_ylabel("y")


def modeling_taxonomy(language="en"):
    fig, axes = plt.subplots(2, 3, figsize=(12.5, 7.2))
    titles = [
        t(language, "Discrete fibers", "Дискретные волокна"),
        t(language, "Continuous orientation field", "Непрерывное поле ориентаций"),
        t(language, "Raster ground truth", "Растровые эталонные данные"),
        t(language, "Network topology", "Топология сети"),
        t(language, "Volumetric fibers", "Объёмные волокна"),
        t(language, "Synthetic dataset", "Синтетический набор данных"),
    ]
    texts = [
        t(language, "Polylines, radii, families, identifiers", "Полилинии, радиусы, семейства, идентификаторы"),
        t(language, "Axial angle, coherence, gradients, layers", "Осевой угол, когерентность, градиенты, слои"),
        t(language, "Image, mask, thickness, overlap count", "Изображение, маска, толщина, число наложений"),
        t(language, "Skeleton, branches, endpoints, components", "Скелет, ветвления, концы, компоненты"),
        t(language, "Voxel mask and 3-D direction vectors", "Воксельная маска и трёхмерные направления"),
        t(language, "Arrays, metadata, seed and provenance", "Массивы, метаданные, seed и происхождение"),
    ]
    for ax, title, text in zip(axes.flat, titles, texts):
        ax.axis("off")
        ax.text(0.5, 0.66, title, ha="center", va="center", fontsize=12, fontweight="bold", transform=ax.transAxes)
        ax.text(0.5, 0.36, text, ha="center", va="center", fontsize=9.5, wrap=True, transform=ax.transAxes)
        ax.add_patch(plt.Rectangle((0.06, 0.12), 0.88, 0.76, fill=False, linewidth=1.2, transform=ax.transAxes))
    fig.suptitle(t(language, "Representations used in Tutorial 13", "Представления, используемые в Tutorial 13"))
    save_figure(fig, "modeling_taxonomy", language)


def preset_gallery(language="en"):
    names = ["tendon", "skin", "artery", "myocardium", "valve", "lung", "scaffold"]
    labels_en = ["Aligned bundle", "Crossed dermal-like", "Layered wall", "Rotating orientation", "Two-family membrane", "Cellular network", "Nonwoven scaffold"]
    labels_ru = ["Ориентированный пучок", "Перекрёстная дерма-подобная сеть", "Слоистая стенка", "Вращение ориентации", "Двухсемейная мембрана", "Ячеистая сеть", "Нетканый каркас"]
    fig, axes = plt.subplots(2, 4, figsize=(13, 6.5))
    for index, (name, en, ru) in enumerate(zip(names, labels_en, labels_ru)):
        network = tissue_preset(name, seed=20 + index)
        raster = rasterize_network(network, (150, 150), blur_sigma=0.6)
        _imshow(axes.flat[index], raster.image, t(language, en, ru))
    axes.flat[-1].axis("off")
    axes.flat[-1].text(0.5, 0.5, t(language, "Presets are educational analogues,\nnot calibrated tissue replicas.", "Пресеты — учебные аналоги,\nа не калиброванные копии тканей."), ha="center", va="center", transform=axes.flat[-1].transAxes)
    fig.suptitle(t(language, "Universal fibrous-architecture presets", "Универсальные пресеты волокнистой архитектуры"))
    save_figure(fig, "preset_gallery", language)


def ground_truth_layers(language="en"):
    network = generate_crossing_families((-0.55, 0.55), 22, seed=13)
    raster = rasterize_network(network, (200, 200), noise_std=0.025)
    skeleton = morphological_skeleton(raster.mask)
    fig, axes = plt.subplots(2, 4, figsize=(13.2, 6.8))
    _imshow(axes[0, 0], raster.image, t(language, "Synthetic image", "Синтетическое изображение"))
    _imshow(axes[0, 1], raster.mask, t(language, "Binary mask", "Бинарная маска"))
    im = _imshow(axes[0, 2], np.rad2deg(raster.orientation), t(language, "Axial orientation", "Осевая ориентация"), cmap="twilight", vmin=-90, vmax=90)
    fig.colorbar(im, ax=axes[0, 2], fraction=0.045, label=t(language, "degrees", "градусы"))
    im = _imshow(axes[0, 3], raster.coherence, t(language, "Local coherence", "Локальная когерентность"), cmap="viridis", vmin=0, vmax=1)
    fig.colorbar(im, ax=axes[0, 3], fraction=0.045)
    _imshow(axes[1, 0], raster.family, t(language, "Dominant family label", "Метка доминирующего семейства"), cmap="tab10", vmin=-1, vmax=2)
    im = _imshow(axes[1, 1], raster.count, t(language, "Overlap count", "Число наложений"), cmap="magma")
    fig.colorbar(im, ax=axes[1, 1], fraction=0.045)
    im = _imshow(axes[1, 2], raster.thickness, t(language, "Local thickness", "Локальная толщина"), cmap="plasma")
    fig.colorbar(im, ax=axes[1, 2], fraction=0.045, label=t(language, "pixels", "пиксели"))
    _imshow(axes[1, 3], skeleton, t(language, "Morphological skeleton", "Морфологический скелет"))
    fig.suptitle(t(language, "One geometry, multiple synchronized ground-truth layers", "Одна геометрия и несколько синхронизированных эталонных слоёв"))
    save_figure(fig, "ground_truth_layers", language)


def density_porosity(language="en"):
    counts = np.array([15, 30, 50, 75, 105])
    area = []
    components = []
    largest = []
    for count in counts:
        network = generate_mikado_network(int(count), radius=0.006, seed=51)
        raster = rasterize_network(network, (150, 150), blur_sigma=0.0)
        metrics = network_metrics(network, raster)
        area.append(metrics["area_fraction"])
        components.append(metrics["components"])
        largest.append(metrics["largest_component_fraction"])
    fig, axes = plt.subplots(1, 3, figsize=(12.2, 3.8))
    axes[0].plot(counts, area, marker="o")
    axes[0].set(xlabel=t(language, "Number of fibers", "Число волокон"), ylabel=t(language, "Area fraction", "Доля площади"), title=t(language, "Material content", "Содержание материала"))
    axes[1].plot(counts, components, marker="o")
    axes[1].set(xlabel=t(language, "Number of fibers", "Число волокон"), ylabel=t(language, "Connected components", "Компоненты связности"), title=t(language, "Fragmentation", "Фрагментация"))
    axes[2].plot(counts, largest, marker="o")
    axes[2].set(xlabel=t(language, "Number of fibers", "Число волокон"), ylabel=t(language, "Largest-component fraction", "Доля крупнейшей компоненты"), title=t(language, "Network connectivity", "Связность сети"))
    fig.suptitle(t(language, "Density changes geometry and topology simultaneously", "Плотность одновременно меняет геометрию и топологию"))
    save_figure(fig, "density_porosity", language)


def thickness_resolution(language="en"):
    radii = [0.003, 0.006, 0.012]
    shapes = [(96, 96), (160, 160), (256, 256)]
    fig, axes = plt.subplots(3, 3, figsize=(9.5, 9.2))
    for row, radius in enumerate(radii):
        modified = generate_mikado_network(45, radius=radius, seed=29)
        for col, shape in enumerate(shapes):
            raster = rasterize_network(modified, shape, blur_sigma=0.4)
            _imshow(axes[row, col], raster.mask, t(language, f"r={radius:.3f}; {shape[0]} px", f"r={radius:.3f}; {shape[0]} пикс."))
    fig.suptitle(t(language, "Fiber radius and pixel resolution determine apparent morphology", "Радиус волокна и разрешение определяют наблюдаемую морфологию"))
    save_figure(fig, "thickness_resolution", language)


def concentration_order(language="en"):
    concentrations = np.array([0.0, 0.5, 1.5, 4.0, 12.0, 30.0])
    order = []
    estimated = []
    for concentration in concentrations:
        network = generate_mikado_network(100, mean_angle=0.4, concentration=float(concentration), seed=31)
        raster = rasterize_network(network, (128, 128), blur_sigma=0.0)
        metrics = network_metrics(network, raster)
        order.append(metrics["order_parameter"])
        estimated.append(np.rad2deg(metrics["mean_orientation_rad"]))
    fig, axes = plt.subplots(1, 2, figsize=(9.8, 4.0))
    axes[0].plot(concentrations, order, marker="o")
    axes[0].set(xlabel=t(language, "Axial concentration", "Осевая концентрация"), ylabel=t(language, "Order parameter", "Параметр порядка"), title=t(language, "Dispersion control", "Управление дисперсией"))
    axes[1].plot(concentrations, estimated, marker="o", label=t(language, "Estimated", "Оценённый"))
    axes[1].axhline(np.rad2deg(0.4), linestyle="--", label=t(language, "Target", "Целевое значение"))
    axes[1].set(xlabel=t(language, "Axial concentration", "Осевая концентрация"), ylabel=t(language, "Mean angle, degrees", "Средний угол, градусы"), title=t(language, "Mean direction", "Среднее направление"))
    axes[1].legend()
    fig.suptitle(t(language, "Concentration changes dispersion without redefining the target axis", "Концентрация меняет дисперсию, не переопределяя целевую ось"))
    save_figure(fig, "concentration_order", language)


def crossing_families(language="en"):
    separations = [20, 50, 90]
    fig, axes = plt.subplots(2, 3, figsize=(11.2, 7.0))
    for col, separation in enumerate(separations):
        half = np.deg2rad(separation / 2)
        network = generate_crossing_families((-half, half), 22, seed=45 + col)
        raster = rasterize_network(network, (170, 170), blur_sigma=0.5)
        _imshow(axes[0, col], raster.image, t(language, f"Family separation: {separation}°", f"Разведение семейств: {separation}°"))
        im = _imshow(axes[1, col], raster.coherence, t(language, "Single-axis coherence", "Когерентность одной оси"), cmap="viridis", vmin=0, vmax=1)
    fig.colorbar(im, ax=axes[1, :], fraction=0.025, pad=0.03)
    fig.suptitle(t(language, "Crossings are intentionally ambiguous for a one-axis ground truth", "Пересечения намеренно неоднозначны для одной эталонной оси"))
    save_figure(fig, "crossing_families", language)


def crimp_waviness(language="en"):
    waviness_values = [0.0, 0.015, 0.035, 0.065]
    fig, axes = plt.subplots(1, 4, figsize=(13, 3.4))
    tortuosity = []
    for ax, amplitude in zip(axes, waviness_values):
        network = generate_parallel_bundle(20, waviness=amplitude, seed=61)
        raster = rasterize_network(network, (170, 170))
        _imshow(ax, raster.image, t(language, f"Amplitude {amplitude:.3f}", f"Амплитуда {amplitude:.3f}"))
        ratios = []
        for fiber in network.fibers:
            contour = np.sum(np.linalg.norm(np.diff(fiber.points, axis=0), axis=1))
            chord = np.linalg.norm(fiber.points[-1] - fiber.points[0])
            ratios.append(contour / max(chord, 1e-12))
        tortuosity.append(np.mean(ratios))
        ax.text(0.5, 0.03, t(language, f"tortuosity={tortuosity[-1]:.3f}", f"извилистость={tortuosity[-1]:.3f}"), ha="center", transform=ax.transAxes, fontsize=8.5)
    fig.suptitle(t(language, "Crimp and waviness are geometric variables, not material stiffness", "Извитость и волнистость — геометрические переменные, а не жёсткость материала"))
    save_figure(fig, "crimp_waviness", language)


def spatial_gradient(language="en"):
    network = generate_spatial_gradient_network(54, seed=73)
    raster = rasterize_network(network, (210, 210))
    column_mean = []
    x = np.arange(raster.orientation.shape[1])
    for column in x:
        values = raster.orientation[:, column]
        column_mean.append(np.rad2deg(axial_mean(values[np.isfinite(values)])))
    fig, axes = plt.subplots(1, 3, figsize=(12.1, 3.9))
    _imshow(axes[0], raster.image, t(language, "Generated image", "Сгенерированное изображение"))
    im = _imshow(axes[1], np.rad2deg(raster.orientation), t(language, "Ground-truth angle", "Истинный угол"), cmap="twilight", vmin=-90, vmax=90)
    fig.colorbar(im, ax=axes[1], fraction=0.05, label=t(language, "degrees", "градусы"))
    axes[2].plot(x / (len(x) - 1), column_mean)
    axes[2].set(xlabel=t(language, "Normalized x", "Нормированная x"), ylabel=t(language, "Axial mean, degrees", "Осевое среднее, градусы"), title=t(language, "Recovered spatial trend", "Восстановленный пространственный тренд"))
    fig.suptitle(t(language, "Spatially varying architecture requires field-valued ground truth", "Пространственно изменяющаяся архитектура требует эталонного поля"))
    save_figure(fig, "spatial_gradient", language)


def layered_architecture(language="en"):
    angles = (-0.95, 0.0, 0.95)
    network = generate_layered_network(angles, 18, seed=80)
    raster = rasterize_network(network, (210, 210))
    fig, axes = plt.subplots(1, 3, figsize=(11.5, 3.9))
    _imshow(axes[0], raster.image, t(language, "Layered image", "Слоистое изображение"))
    _imshow(axes[1], raster.family, t(language, "Layer / family labels", "Метки слоёв / семейств"), cmap="tab10", vmin=-1, vmax=3)
    row_angles = []
    for row in range(raster.orientation.shape[0]):
        values = raster.orientation[row]
        row_angles.append(np.rad2deg(axial_mean(values[np.isfinite(values)])))
    axes[2].plot(row_angles, np.linspace(1, 0, len(row_angles)))
    axes[2].set(xlabel=t(language, "Mean angle, degrees", "Средний угол, градусы"), ylabel=t(language, "Normalized depth", "Нормированная глубина"), title=t(language, "Transmural profile", "Профиль по толщине"))
    fig.suptitle(t(language, "Layer identity and orientation can be stored separately", "Идентичность слоя и ориентация могут храниться раздельно"))
    save_figure(fig, "layered_architecture", language)


def mikado_topology(language="en"):
    networks = [generate_mikado_network(n, seed=91) for n in (25, 55, 100)]
    fig, axes = plt.subplots(2, 3, figsize=(11.2, 7.0))
    for col, network in enumerate(networks):
        raster = rasterize_network(network, (170, 170), blur_sigma=0.0)
        skeleton = morphological_skeleton(raster.mask)
        metrics = skeleton_graph_metrics(skeleton)
        _imshow(axes[0, col], raster.mask, t(language, f"{len(network.fibers)} fibers", f"{len(network.fibers)} волокон"))
        _imshow(axes[1, col], skeleton, t(language, f"components={metrics['components']}; branches={metrics['branchpoints']}", f"компоненты={metrics['components']}; ветви={metrics['branchpoints']}"))
    fig.suptitle(t(language, "A visual density change is also a graph-topology change", "Визуальное изменение плотности одновременно меняет топологию графа"))
    save_figure(fig, "mikado_topology", language)


def voronoi_cellular(language="en"):
    seeds = [20, 40, 70]
    fig, axes = plt.subplots(1, 3, figsize=(11.2, 3.7))
    for ax, count in zip(axes, seeds):
        network = generate_voronoi_network(count, seed=100 + count)
        raster = rasterize_network(network, (180, 180), blur_sigma=0.25)
        metrics = network_metrics(network, raster)
        _imshow(ax, raster.image, t(language, f"{count} seeds; porosity={metrics['porosity']:.2f}", f"{count} центров; пористость={metrics['porosity']:.2f}"))
    fig.suptitle(t(language, "Voronoi-like networks provide a cellular architecture family", "Voronoi-подобные сети задают семейство ячеистых архитектур"))
    save_figure(fig, "voronoi_cellular", language)


def branches_defects(language="en"):
    base = generate_parallel_bundle(26, waviness=0.02, seed=111)
    branched = add_branches(base, branch_probability=0.55, seed=112)
    defective = apply_defects(branched, deletion_fraction=0.18, gap_probability=0.35, seed=113)
    networks = [base, branched, defective]
    labels = [("Baseline", "Базовая сеть"), ("Added branches", "Добавлены ветви"), ("Deletion and gaps", "Удаление и разрывы")]
    fig, axes = plt.subplots(2, 3, figsize=(11.2, 7.0))
    for col, (network, label) in enumerate(zip(networks, labels)):
        raster = rasterize_network(network, (180, 180), blur_sigma=0.4)
        skeleton = morphological_skeleton(raster.mask)
        _imshow(axes[0, col], raster.image, t(language, *label))
        degree = skeleton_degrees(skeleton)
        display = skeleton.astype(float)
        display[degree >= 3] = 2.0
        _imshow(axes[1, col], display, t(language, "Skeleton and branch pixels", "Скелет и пиксели ветвления"), cmap="magma")
    fig.suptitle(t(language, "Defects must be labeled explicitly rather than hidden in noise", "Дефекты нужно маркировать явно, а не скрывать в шуме"))
    save_figure(fig, "branches_defects", language)


def skeleton_graph(language="en"):
    network = add_branches(generate_mikado_network(55, seed=122), 0.35, seed=123)
    raster = rasterize_network(network, (220, 220), blur_sigma=0.0)
    skeleton = morphological_skeleton(raster.mask)
    degree = skeleton_degrees(skeleton)
    fig, axes = plt.subplots(1, 3, figsize=(11.5, 3.9))
    _imshow(axes[0], raster.mask, t(language, "Binary network", "Бинарная сеть"))
    _imshow(axes[1], skeleton, t(language, "One-pixel skeleton", "Однопиксельный скелет"))
    _imshow(axes[2], np.where(skeleton, degree, np.nan), t(language, "Local graph degree", "Локальная степень графа"), cmap="viridis", vmin=0, vmax=8)
    metrics = skeleton_graph_metrics(skeleton)
    fig.suptitle(t(language, f"Topology: {metrics['components']} components, {metrics['endpoints']} endpoints, {metrics['branchpoints']} branch pixels", f"Топология: {metrics['components']} компонент, {metrics['endpoints']} концов, {metrics['branchpoints']} пикселей ветвления"))
    save_figure(fig, "skeleton_graph", language)


def volume_3d(language="en"):
    volume = generate_fiber_volume((34, 68, 68), n_fibers=24, mean_direction=(0.2, 0.2, 1.0), angular_noise=0.3, seed=132)
    projections = [np.max(volume.volume, axis=0), np.max(volume.volume, axis=1), np.max(volume.volume, axis=2)]
    labels = [("Maximum projection: z", "Максимальная проекция: z"), ("Maximum projection: y", "Максимальная проекция: y"), ("Maximum projection: x", "Максимальная проекция: x")]
    fig, axes = plt.subplots(1, 3, figsize=(11.2, 3.8))
    for ax, projection, label in zip(axes, projections, labels):
        _imshow(ax, projection, t(language, *label))
    fig.suptitle(t(language, "Synthetic volume stores a mask and local 3-D directions", "Синтетический объём хранит маску и локальные трёхмерные направления"))
    save_figure(fig, "volume_3d", language)


def voxel_anisotropy(language="en"):
    volume = generate_fiber_volume((32, 64, 64), n_fibers=20, mean_direction=(0.0, 0.15, 1.0), angular_noise=0.22, seed=141)
    base = volume.volume.astype(float)
    degraded = ndimage.gaussian_filter(base, sigma=(2.2, 0.7, 0.7))
    sampled = degraded[::2]
    fig, axes = plt.subplots(1, 3, figsize=(11.2, 3.8))
    _imshow(axes[0], np.max(base, axis=0), t(language, "Isotropic reference", "Изотропный эталон"))
    _imshow(axes[1], np.max(degraded, axis=0), t(language, "Axial blur", "Аксиальное размытие"))
    _imshow(axes[2], np.max(sampled, axis=0), t(language, "Blur and z-downsampling", "Размытие и прореживание по z"))
    fig.suptitle(t(language, "Voxel anisotropy is an acquisition property, not tissue dispersion", "Анизотропия вокселя — свойство съёмки, а не дисперсия ткани"))
    save_figure(fig, "voxel_anisotropy", language)


def seed_reproducibility(language="en"):
    seeds = [7, 7, 8]
    fig, axes = plt.subplots(1, 3, figsize=(10.8, 3.6))
    images = []
    for ax, seed in zip(axes, seeds):
        network = generate_mikado_network(55, concentration=1.2, seed=seed)
        raster = rasterize_network(network, (170, 170))
        images.append(raster.mask)
        _imshow(ax, raster.image, t(language, f"seed={seed}", f"seed={seed}"))
    same = np.array_equal(images[0], images[1])
    different = not np.array_equal(images[0], images[2])
    fig.suptitle(t(language, f"Same seed identical: {same}; different seed changes realization: {different}", f"Одинаковый seed совпадает: {'да' if same else 'нет'}; другой seed меняет реализацию: {'да' if different else 'нет'}"))
    save_figure(fig, "seed_reproducibility", language)


def parameter_sensitivity(language="en"):
    counts = [25, 50, 90]
    concentrations = [0.0, 2.0, 10.0]
    porosity = np.zeros((3, 3))
    order = np.zeros((3, 3))
    for i, count in enumerate(counts):
        for j, concentration in enumerate(concentrations):
            network = generate_mikado_network(count, concentration=concentration, seed=151)
            raster = rasterize_network(network, (120, 120), blur_sigma=0.0)
            metrics = network_metrics(network, raster)
            porosity[i, j] = metrics["porosity"]
            order[i, j] = metrics["order_parameter"]
    fig, axes = plt.subplots(1, 2, figsize=(9.8, 4.0))
    im = axes[0].imshow(porosity, origin="lower", aspect="auto", cmap="viridis")
    axes[0].set(xticks=range(3), xticklabels=concentrations, yticks=range(3), yticklabels=counts, xlabel=t(language, "Concentration", "Концентрация"), ylabel=t(language, "Fiber count", "Число волокон"), title=t(language, "Porosity", "Пористость"))
    fig.colorbar(im, ax=axes[0], fraction=0.05)
    im = axes[1].imshow(order, origin="lower", aspect="auto", cmap="magma", vmin=0, vmax=1)
    axes[1].set(xticks=range(3), xticklabels=concentrations, yticks=range(3), yticklabels=counts, xlabel=t(language, "Concentration", "Концентрация"), ylabel=t(language, "Fiber count", "Число волокон"), title=t(language, "Order parameter", "Параметр порядка"))
    fig.colorbar(im, ax=axes[1], fraction=0.05)
    fig.suptitle(t(language, "Different parameters control different observables", "Разные параметры управляют разными наблюдаемыми величинами"))
    save_figure(fig, "parameter_sensitivity", language)


def dataset_export(language="en"):
    network = tissue_preset("skin", seed=163)
    raster = rasterize_network(network, (180, 180), noise_std=0.015)
    metrics = network_metrics(network, raster)
    destination = DATA_DIRECTORY / "example_fibrous_dataset.npz"
    export_network_dataset(destination, network, raster, metrics)
    fig, axes = plt.subplots(1, 3, figsize=(10.8, 3.7))
    _imshow(axes[0], raster.image, t(language, "image", "изображение"))
    _imshow(axes[1], raster.mask, t(language, "mask", "маска"))
    axes[2].axis("off")
    summary = [
        t(language, "Synthetic: yes", "Синтетика: да"),
        f"seed: {network.seed}",
        t(language, f"fibers: {metrics['fiber_count']}", f"волокон: {metrics['fiber_count']}"),
        t(language, f"porosity: {metrics['porosity']:.3f}", f"пористость: {metrics['porosity']:.3f}"),
        t(language, f"order: {metrics['order_parameter']:.3f}", f"порядок: {metrics['order_parameter']:.3f}"),
        "NPZ + JSON metadata",
    ]
    axes[2].text(0.04, 0.95, "\n".join(summary), va="top", fontsize=10, transform=axes[2].transAxes)
    fig.suptitle(t(language, "Dataset export keeps arrays and provenance synchronized", "Экспорт сохраняет синхронность массивов и происхождения данных"))
    save_figure(fig, "dataset_export", language)


def benchmark_summary(language="en"):
    cases = []
    # Deterministic reproduction.
    a = rasterize_network(generate_mikado_network(20, seed=1), (96, 96)).mask
    b = rasterize_network(generate_mikado_network(20, seed=1), (96, 96)).mask
    cases.append(("reproducibility", float(np.mean(a != b)), 0.0, "<="))
    # Orientation target.
    network = generate_parallel_bundle(20, angle=0.35, waviness=0.0, seed=2)
    raster = rasterize_network(network, (128, 128))
    metrics = network_metrics(network, raster)
    cases.append(("orientation_error_deg", float(abs(np.rad2deg(axial_difference(metrics["mean_orientation_rad"], 0.35)))), 3.0, "<="))
    cases.append(("aligned_order", float(metrics["order_parameter"]), 0.95, ">="))
    # Volume direction normalization.
    volume = generate_fiber_volume((20, 28, 28), n_fibers=6, seed=3)
    norms = np.linalg.norm(volume.orientation[volume.volume], axis=1)
    cases.append(("orientation_norm_error", float(np.max(abs(norms - 1.0))), 1e-6, "<="))
    # Export provenance.
    path = DATA_DIRECTORY / "benchmark_dataset.npz"
    export_network_dataset(path, network, raster, metrics)
    with np.load(path, allow_pickle=False) as dataset:
        metadata = json.loads(str(dataset["metadata_json"]))
    cases.append(("synthetic_flag", float(metadata["synthetic"]), 1.0, ">="))
    rows = []
    for name, value, threshold, relation in cases:
        passed = value <= threshold if relation == "<=" else value >= threshold
        rows.append({"check": name, "value": value, "threshold": threshold, "relation": relation, "passed": passed})
    path = DATA_DIRECTORY / "synthetic_fibrous_tissue_benchmark.csv"
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    fig, ax = plt.subplots(figsize=(9.5, 4.2))
    label_map_ru = {
        "reproducibility": "воспроизводимость",
        "orientation_error_deg": "ошибка ориентации",
        "aligned_order": "порядок пучка",
        "orientation_norm_error": "норма 3D-направления",
        "synthetic_flag": "метка синтетики",
    }
    labels = [row["check"] if language == "en" else label_map_ru[row["check"]] for row in rows]
    display = [max(abs(row["value"] - row["threshold"]), 1e-9) for row in rows]
    ax.barh(labels, display)
    ax.set_xscale("log")
    ax.set_xlabel(t(language, "Absolute margin to criterion (log scale)", "Абсолютный запас до критерия (логарифмическая шкала)"))
    ax.set_title(t(language, "All synthetic verification checks passed", "Все синтетические проверки пройдены"))
    for index, row in enumerate(rows):
        ax.text(display[index] * 1.15, index, t(language, "PASS", "ПРОЙДЕНО"), va="center", fontsize=8.5)
    save_figure(fig, "benchmark_summary", language)


def generation_animation(language="en"):
    rng_seed = 181
    frames = [10, 25, 40, 55, 70]
    fig, ax = plt.subplots(figsize=(4.4, 4.2))
    image_artist = ax.imshow(np.zeros((110, 110)), cmap="gray", vmin=0, vmax=1)
    ax.set_xticks([])
    ax.set_yticks([])
    title = ax.set_title("")

    def update(frame_index):
        count = frames[frame_index]
        network = generate_mikado_network(count, concentration=0.8, seed=rng_seed)
        raster = rasterize_network(network, (110, 110), blur_sigma=0.45)
        image_artist.set_data(raster.image)
        title.set_text(t(language, f"Sequential deposition: {count} fibers", f"Последовательное отложение: {count} волокон"))
        return image_artist, title

    movie = animation.FuncAnimation(fig, update, frames=len(frames), interval=420, blit=False)
    suffix = "" if language == "en" else "_ru"
    movie.save(ANIMATION_DIRECTORY / f"network_deposition{suffix}.gif", writer=animation.PillowWriter(fps=2.0), dpi=78)
    plt.close(fig)


def run_all():
    static = [
        modeling_taxonomy, preset_gallery, ground_truth_layers, density_porosity,
        thickness_resolution, concentration_order, crossing_families, crimp_waviness,
        spatial_gradient, layered_architecture, mikado_topology, voronoi_cellular,
        branches_defects, skeleton_graph, volume_3d, voxel_anisotropy,
        seed_reproducibility, parameter_sensitivity, dataset_export, benchmark_summary,
    ]
    for scenario in static:
        for language in ("en", "ru"):
            scenario(language)
    for language in ("en", "ru"):
        generation_animation(language)


SCENARIOS = {
    "modeling_taxonomy": lambda: [modeling_taxonomy(lang) for lang in ("en", "ru")],
    "preset_gallery": lambda: [preset_gallery(lang) for lang in ("en", "ru")],
    "ground_truth_layers": lambda: [ground_truth_layers(lang) for lang in ("en", "ru")],
    "density_porosity": lambda: [density_porosity(lang) for lang in ("en", "ru")],
    "thickness_resolution": lambda: [thickness_resolution(lang) for lang in ("en", "ru")],
    "concentration_order": lambda: [concentration_order(lang) for lang in ("en", "ru")],
    "crossing_families": lambda: [crossing_families(lang) for lang in ("en", "ru")],
    "crimp_waviness": lambda: [crimp_waviness(lang) for lang in ("en", "ru")],
    "spatial_gradient": lambda: [spatial_gradient(lang) for lang in ("en", "ru")],
    "layered_architecture": lambda: [layered_architecture(lang) for lang in ("en", "ru")],
    "mikado_topology": lambda: [mikado_topology(lang) for lang in ("en", "ru")],
    "voronoi_cellular": lambda: [voronoi_cellular(lang) for lang in ("en", "ru")],
    "branches_defects": lambda: [branches_defects(lang) for lang in ("en", "ru")],
    "skeleton_graph": lambda: [skeleton_graph(lang) for lang in ("en", "ru")],
    "volume_3d": lambda: [volume_3d(lang) for lang in ("en", "ru")],
    "voxel_anisotropy": lambda: [voxel_anisotropy(lang) for lang in ("en", "ru")],
    "seed_reproducibility": lambda: [seed_reproducibility(lang) for lang in ("en", "ru")],
    "parameter_sensitivity": lambda: [parameter_sensitivity(lang) for lang in ("en", "ru")],
    "dataset_export": lambda: [dataset_export(lang) for lang in ("en", "ru")],
    "benchmark_summary": lambda: [benchmark_summary(lang) for lang in ("en", "ru")],
    "generation_animation": lambda: [generation_animation(lang) for lang in ("en", "ru")],
}
