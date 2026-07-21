"""Localized result generation for Tutorial 14."""

from __future__ import annotations

from functools import lru_cache
import csv

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np

from common import ANIMATION_DIRECTORY, DATA_DIRECTORY, save_figure, t
from biomechanics_tutorials.synthetic_fibrous_tissue import (
    generate_fiber_volume,
    rasterize_network,
    tissue_preset,
)
from biomechanics_tutorials.synthetic_microscopy import (
    ArtifactParameters,
    OpticalParameters,
    SEMParameters,
    export_multimodal_dataset,
    focus_series,
    global_ssim,
    height_from_mask,
    psnr,
    resample_stack,
    simulate_brightfield,
    simulate_confocal_stack,
    simulate_fib_sem_stack,
    simulate_fluorescence,
    simulate_sem,
    simulate_shg,
)


def _pair(stem, builder):
    for language in ("en", "ru"):
        save_figure(builder(language), stem, language)


@lru_cache(maxsize=1)
def _base2d():
    network = tissue_preset("skin", seed=14)
    raster = rasterize_network(network, (256, 256), blur_sigma=0.35)
    amplitude = raster.mask.astype(float) * (0.45 + 0.55 * np.clip(raster.coherence, 0, 1))
    orientation = np.where(raster.mask, raster.orientation, np.nan)
    thickness = raster.thickness / max(np.max(raster.thickness), 1.0)
    return network, raster, amplitude, orientation, thickness


@lru_cache(maxsize=1)
def _base3d():
    return generate_fiber_volume((34, 96, 96), n_fibers=28, angular_noise=0.38, radius=1.5, seed=14)


def modality_taxonomy():
    def build(language):
        fig, axes = plt.subplots(2, 3, figsize=(12.5, 7.5))
        cards = [
            (
                "Bright-field",
                "Светлое поле",
                "Transmission + absorption",
                "Пропускание + поглощение",
            ),
            (
                "Fluorescence",
                "Флуоресценция",
                "PSF + photon/read noise",
                "ФРТ + фотонный/считывающий шум",
            ),
            (
                "Confocal",
                "Конфокальная",
                "3-D PSF + optical sectioning",
                "3D ФРТ + оптическое сечение",
            ),
            (
                "SHG-like",
                "SHG-подобная",
                "Orientation-sensitive collagen contrast",
                "Ориентационно-зависимый контраст коллагена",
            ),
            ("SEM-like", "СЭМ-подобная", "Topography + composition", "Топография + состав"),
            (
                "FIB-SEM-like",
                "FIB-SEM-подобная",
                "Serial sections + drift/curtaining",
                "Серийные срезы + дрейф/полосы",
            ),
        ]
        for ax, (en1, ru1, en2, ru2) in zip(axes.flat, cards):
            ax.axis("off")
            ax.text(
                0.5,
                0.62,
                t(language, en1, ru1),
                ha="center",
                va="center",
                fontsize=15,
                weight="bold",
            )
            ax.text(
                0.5, 0.35, t(language, en2, ru2), ha="center", va="center", fontsize=10, wrap=True
            )
            ax.add_patch(plt.Rectangle((0.05, 0.08), 0.9, 0.82, fill=False, lw=1.4))
        fig.suptitle(
            t(
                language,
                "Synthetic image formation: one structure, multiple virtual instruments",
                "Синтетическое формирование изображений: одна структура, несколько виртуальных приборов",
            )
        )
        return fig

    _pair("modality_taxonomy", build)


def ground_truth_channels():
    _, raster, amplitude, orientation, thickness = _base2d()

    def build(language):
        fig, axes = plt.subplots(1, 4, figsize=(14, 3.8))
        arrays = [raster.mask, amplitude, np.rad2deg(orientation), thickness]
        titles = [
            t(language, "Binary mask", "Бинарная маска"),
            t(language, "Emitter amplitude", "Амплитуда излучателя"),
            t(language, "Axial orientation", "Осевая ориентация"),
            t(language, "Relative thickness", "Относительная толщина"),
        ]
        cmaps = ["gray", "magma", "twilight", "viridis"]
        for ax, arr, title, cmap in zip(axes, arrays, titles, cmaps):
            im = ax.imshow(arr, cmap=cmap)
            ax.set_title(title)
            ax.axis("off")
            if cmap in {"twilight", "viridis"}:
                fig.colorbar(im, ax=ax, shrink=0.72)
        fig.suptitle(
            t(
                language,
                "Ground truth is richer than any single image",
                "Ground truth содержит больше информации, чем одно изображение",
            )
        )
        return fig

    _pair("ground_truth_channels", build)


def brightfield_formation():
    _, _, _, _, thickness = _base2d()
    result = simulate_brightfield(
        thickness, absorption=2.7, phase_edge_gain=0.18, illumination_gradient=0.25, seed=2
    )

    def build(language):
        fig, axes = plt.subplots(1, 3, figsize=(11.5, 3.7))
        for ax, arr, title in zip(
            axes,
            [thickness, result.expectation, result.image],
            [
                t(language, "Thickness ground truth", "Истинная толщина"),
                t(language, "Noise-free expectation", "Ожидаемое изображение без шума"),
                t(language, "Observed image", "Наблюдаемое изображение"),
            ],
        ):
            ax.imshow(arr, cmap="gray")
            ax.set_title(title)
            ax.axis("off")
        fig.suptitle(
            t(
                language,
                "Bright-field-like transmission with absorption and edge contrast",
                "Светлопольное пропускание с поглощением и краевым контрастом",
            )
        )
        return fig

    _pair("brightfield_formation", build)


def fluorescence_psf():
    _, _, amplitude, _, _ = _base2d()
    sigmas = [0.5, 1.3, 2.8]
    results = [
        simulate_fluorescence(
            amplitude, OpticalParameters(sigma_xy=s, gain=400, read_noise=0.8), seed=3
        )
        for s in sigmas
    ]

    def build(language):
        fig, axes = plt.subplots(1, 4, figsize=(14, 3.7))
        axes[0].imshow(amplitude, cmap="magma")
        axes[0].set_title(t(language, "Ground truth emitters", "Истинные излучатели"))
        axes[0].axis("off")
        for ax, res, s in zip(axes[1:], results, sigmas):
            ax.imshow(res.image, cmap="magma")
            ax.set_title(f"σ={s}")
            ax.axis("off")
        fig.suptitle(
            t(
                language,
                "Point-spread width controls resolvable fiber separation",
                "Ширина ФРТ определяет разрешимое разделение волокон",
            )
        )
        return fig

    _pair("fluorescence_psf", build)


def photon_budget():
    _, _, amplitude, _, _ = _base2d()
    gains = [30, 100, 400, 1600]
    results = [
        simulate_fluorescence(amplitude, OpticalParameters(gain=g, read_noise=1.5), seed=7)
        for g in gains
    ]
    metrics = [psnr(r.expectation, r.image) for r in results]

    def build(language):
        fig, axes = plt.subplots(1, 5, figsize=(15, 3.4))
        for ax, res, g, m in zip(axes[:4], results, gains, metrics):
            ax.imshow(res.image, cmap="magma")
            ax.set_title(f"gain={g}\nPSNR={m:.1f} dB")
            ax.axis("off")
        axes[4].plot(gains, metrics, marker="o")
        axes[4].set_xscale("log")
        axes[4].set_xlabel(t(language, "Photon gain", "Фотонный коэффициент"))
        axes[4].set_ylabel("PSNR, dB")
        axes[4].set_title(t(language, "Noise trend", "Тренд шума"))
        fig.suptitle(
            t(
                language,
                "Photon budget changes the reliability of faint structures",
                "Фотонный бюджет меняет надёжность слабых структур",
            )
        )
        return fig

    _pair("photon_budget", build)


def confocal_sections():
    vol = _base3d().volume.astype(float)
    res = simulate_confocal_stack(
        vol, OpticalParameters(sigma_xy=1.0, sigma_z=2.1, gain=500, read_noise=0.8), seed=8
    )
    indices = [8, 17, 26]

    def build(language):
        fig, axes = plt.subplots(2, 3, figsize=(10.5, 6.7))
        for j, i in enumerate(indices):
            axes[0, j].imshow(vol[i], cmap="gray")
            axes[0, j].set_title(t(language, f"Ground truth z={i}", f"Истина z={i}"))
            axes[0, j].axis("off")
            axes[1, j].imshow(res.image[i], cmap="magma")
            axes[1, j].set_title(t(language, f"Confocal-like z={i}", f"Конфокальное z={i}"))
            axes[1, j].axis("off")
        fig.suptitle(
            t(
                language,
                "Optical sectioning does not remove the axial PSF",
                "Оптическое сечение не устраняет осевую ФРТ",
            )
        )
        return fig

    _pair("confocal_sections", build)


def axial_resolution():
    vol = np.zeros((41, 64, 64))
    vol[15, 32, 32] = 1
    vol[25, 32, 32] = 1
    sigmas = [1.0, 2.5, 5.0]
    profiles = []
    for s in sigmas:
        res = simulate_confocal_stack(
            vol, OpticalParameters(sigma_xy=0.8, sigma_z=s, gain=5000, read_noise=0), seed=1
        )
        profiles.append(res.expectation[:, 32, 32])

    def build(language):
        fig, ax = plt.subplots(figsize=(8, 4.7))
        for p, s in zip(profiles, sigmas):
            ax.plot(np.arange(41), p, label=f"σz={s}")
        ax.axvline(15, ls="--", lw=1)
        ax.axvline(25, ls="--", lw=1)
        ax.set_xlabel("z")
        ax.set_ylabel(t(language, "Normalized intensity", "Нормированная интенсивность"))
        ax.legend()
        ax.set_title(
            t(
                language,
                "Two planes merge when axial blur is too broad",
                "Два слоя сливаются при слишком широкой осевой ФРТ",
            )
        )
        return fig

    _pair("axial_resolution", build)


def shg_polarization():
    _, raster, amplitude, orientation, _ = _base2d()
    angles = np.deg2rad([0, 30, 60, 90])
    results = [
        simulate_shg(amplitude, orientation, polarization_angle=a, gain=600, seed=4) for a in angles
    ]

    def build(language):
        fig, axes = plt.subplots(1, 4, figsize=(13, 3.6))
        for ax, res, a in zip(axes, results, np.rad2deg(angles)):
            ax.imshow(res.image, cmap="inferno")
            ax.set_title(f"{a:.0f}°")
            ax.axis("off")
        fig.suptitle(
            t(
                language,
                "SHG-like intensity depends on fiber orientation and input polarization",
                "SHG-подобная интенсивность зависит от ориентации волокон и поляризации",
            )
        )
        return fig

    _pair("shg_polarization", build)


def sem_topography():
    _, raster, _, _, _ = _base2d()
    height = height_from_mask(raster.mask, sigma=1.7)
    sem = simulate_sem(
        height,
        parameters=SEMParameters(topography_gain=1, edge_gain=0.25, composition_gain=0),
        seed=2,
    )

    def build(language):
        fig, axes = plt.subplots(1, 3, figsize=(11, 3.8))
        for ax, arr, title, cmap in zip(
            axes,
            [raster.mask, height, sem.image],
            [
                t(language, "Structure mask", "Маска структуры"),
                t(language, "Synthetic relief", "Синтетический рельеф"),
                t(language, "SEM-like image", "СЭМ-подобное изображение"),
            ],
            ["gray", "terrain", "gray"],
        ):
            ax.imshow(arr, cmap=cmap)
            ax.set_title(title)
            ax.axis("off")
        fig.suptitle(
            t(
                language,
                "Topographic contrast is generated from surface normals and edges",
                "Топографический контраст формируется нормалями поверхности и краями",
            )
        )
        return fig

    _pair("sem_topography", build)


def sem_detector_direction():
    _, raster, _, _, _ = _base2d()
    height = height_from_mask(raster.mask)
    angles = [0, 90, 180, 270]
    imgs = [
        simulate_sem(
            height, parameters=SEMParameters(detector_azimuth_deg=a, noise_std=0.01), seed=3
        ).expectation
        for a in angles
    ]

    def build(language):
        fig, axes = plt.subplots(1, 4, figsize=(13, 3.5))
        for ax, img, a in zip(axes, imgs, angles):
            ax.imshow(img, cmap="gray")
            ax.set_title(t(language, f"Detector {a}°", f"Детектор {a}°"))
            ax.axis("off")
        fig.suptitle(
            t(
                language,
                "Detector direction reverses topographic shading",
                "Направление детектора меняет топографическое затенение",
            )
        )
        return fig

    _pair("sem_detector_direction", build)


def sem_composition():
    _, raster, _, _, _ = _base2d()
    height = height_from_mask(raster.mask)
    comp = np.where(raster.family == 0, 0.25, np.where(raster.family == 1, 0.85, 0.0))
    topo = simulate_sem(height, comp, SEMParameters(composition_gain=0, noise_std=0.01), seed=1)
    mixed = simulate_sem(
        height,
        comp,
        SEMParameters(composition_gain=0.9, topography_gain=0.45, noise_std=0.01),
        seed=1,
    )

    def build(language):
        fig, axes = plt.subplots(1, 3, figsize=(11, 3.7))
        for ax, arr, title in zip(
            axes,
            [comp, topo.image, mixed.image],
            [
                t(language, "Composition ground truth", "Истинный состав"),
                t(language, "Topography-dominated", "Топографический контраст"),
                t(language, "Mixed contrast", "Смешанный контраст"),
            ],
        ):
            ax.imshow(arr, cmap="gray")
            ax.set_title(title)
            ax.axis("off")
        fig.suptitle(
            t(
                language,
                "Composition and topography can be confounded in one grayscale image",
                "Состав и топография могут смешиваться в одном полутоновом изображении",
            )
        )
        return fig

    _pair("sem_composition", build)


def fib_sem_stack():
    vol = _base3d().volume.astype(float)
    res = simulate_fib_sem_stack(vol, noise_std=0.018, seed=5)
    indices = [6, 16, 26]

    def build(language):
        fig, axes = plt.subplots(2, 3, figsize=(10.5, 6.6))
        for j, i in enumerate(indices):
            axes[0, j].imshow(vol[i], cmap="gray")
            axes[0, j].set_title(t(language, f"Ground truth slice {i}", f"Истинный срез {i}"))
            axes[0, j].axis("off")
            axes[1, j].imshow(res.image[i], cmap="gray")
            axes[1, j].set_title(t(language, f"FIB-SEM-like {i}", f"FIB-SEM-подобный {i}"))
            axes[1, j].axis("off")
        fig.suptitle(
            t(
                language,
                "Serial-section imaging produces a registered 3-D observation stack",
                "Серийная визуализация создаёт наблюдаемый 3D-стек",
            )
        )
        return fig

    _pair("fib_sem_stack", build)


def drift_curtaining():
    vol = _base3d().volume.astype(float)
    clean = simulate_fib_sem_stack(vol, seed=2)
    bad = simulate_fib_sem_stack(
        vol,
        drift_per_slice=(0.08, 0.18),
        curtaining_strength=0.18,
        missing_slice_probability=0.04,
        seed=2,
    )
    z = 20

    def build(language):
        fig, axes = plt.subplots(1, 3, figsize=(11, 3.7))
        arrays = [clean.image[z], bad.image[z], np.abs(clean.image[z] - bad.image[z])]
        titles = [
            t(language, "Clean synthetic slice", "Чистый синтетический срез"),
            t(language, "Drift + curtaining", "Дрейф + полосчатость"),
            t(language, "Absolute difference", "Абсолютная разность"),
        ]
        for ax, arr, title in zip(axes, arrays, titles):
            ax.imshow(arr, cmap="gray")
            ax.set_title(title)
            ax.axis("off")
        fig.suptitle(
            t(
                language,
                "Acquisition artifacts change topology before segmentation begins",
                "Артефакты меняют топологию ещё до сегментации",
            )
        )
        return fig

    _pair("drift_curtaining", build)


def voxel_anisotropy():
    vol = _base3d().volume.astype(float)
    anis = resample_stack(vol, (3, 1, 1), (1, 1, 1), order=1)

    def build(language):
        fig, axes = plt.subplots(1, 3, figsize=(11, 3.8))
        axes[0].imshow(np.max(vol, axis=0), cmap="gray")
        axes[0].set_title(t(language, "Original projection", "Исходная проекция"))
        axes[0].axis("off")
        axes[1].imshow(np.max(anis, axis=0), cmap="gray")
        axes[1].set_title(t(language, "Resampled projection", "Проекция после ресэмплинга"))
        axes[1].axis("off")
        axes[2].plot(np.mean(vol, axis=(1, 2)), label=t(language, "Original", "Исходный"))
        axes[2].plot(
            np.linspace(0, len(vol) - 1, len(anis)),
            np.mean(anis, axis=(1, 2)),
            label=t(language, "Resampled", "Ресэмплинг"),
        )
        axes[2].set_xlabel("z")
        axes[2].set_ylabel(t(language, "Occupied fraction", "Доля структуры"))
        axes[2].legend()
        fig.suptitle(
            t(
                language,
                "Anisotropic voxels change apparent continuity and scale",
                "Анизотропные воксели меняют видимую непрерывность и масштаб",
            )
        )
        return fig

    _pair("voxel_anisotropy", build)


def artifact_gallery():
    _, _, amp, _, _ = _base2d()
    base = simulate_fluorescence(amp, seed=9)
    pars = [
        ArtifactParameters(),
        ArtifactParameters(vignette_strength=0.55),
        ArtifactParameters(stripe_strength=0.18),
        ArtifactParameters(drift_pixels=7),
        ArtifactParameters(dead_pixel_fraction=0.025),
        ArtifactParameters(line_jitter=1.2, saturation_fraction=0.03),
    ]
    labels = [
        ("Reference", "Эталон"),
        ("Vignetting", "Виньетирование"),
        ("Stripes", "Полосы"),
        ("Drift", "Дрейф"),
        ("Dead pixels", "Мёртвые пиксели"),
        ("Jitter + saturation", "Дрожание + насыщение"),
    ]
    from biomechanics_tutorials.synthetic_microscopy import apply_artifacts

    imgs = [apply_artifacts(base.image, p, seed=10 + i) for i, p in enumerate(pars)]

    def build(language):
        fig, axes = plt.subplots(2, 3, figsize=(10.5, 7))
        for ax, img, (en, ru) in zip(axes.flat, imgs, labels):
            ax.imshow(img, cmap="magma")
            ax.set_title(t(language, en, ru))
            ax.axis("off")
        fig.suptitle(
            t(
                language,
                "Artifact library for domain-shift and robustness tests",
                "Библиотека артефактов для проверки устойчивости и domain shift",
            )
        )
        return fig

    _pair("artifact_gallery", build)


def domain_shift():
    _, _, amp, _, _ = _base2d()
    conditions = []
    for blur, gain, bg in [(0.6, 800, 0.01), (1.2, 250, 0.03), (2.2, 80, 0.08), (1.0, 120, 0.15)]:
        conditions.append(
            simulate_fluorescence(
                amp,
                OpticalParameters(sigma_xy=blur, gain=gain, background=bg, read_noise=2),
                illumination_gradient=0.3,
                seed=int(gain),
            ).image
        )

    def build(language):
        fig, axes = plt.subplots(1, 4, figsize=(13, 3.5))
        titles = [
            t(language, "High SNR", "Высокий SNR"),
            t(language, "Nominal", "Номинальный"),
            t(language, "Blurred low count", "Размытый слабый сигнал"),
            t(language, "Background shift", "Сдвиг фона"),
        ]
        for ax, img, title in zip(axes, conditions, titles):
            ax.imshow(img, cmap="magma")
            ax.set_title(title)
            ax.axis("off")
        fig.suptitle(
            t(
                language,
                "The same ground truth can generate different acquisition domains",
                "Одна ground truth создаёт разные домены наблюдения",
            )
        )
        return fig

    _pair("domain_shift", build)


def multimodal_registration():
    _, raster, amp, orientation, thickness = _base2d()
    fl = simulate_fluorescence(amp, seed=1).image
    bf = simulate_brightfield(thickness, seed=1).image
    shg = simulate_shg(amp, orientation, polarization_angle=0.4, seed=1).image
    sem = simulate_sem(height_from_mask(raster.mask), seed=1).image

    def build(language):
        fig, axes = plt.subplots(1, 4, figsize=(13, 3.5))
        for ax, img, title, cmap in zip(
            axes,
            [bf, fl, shg, sem],
            [
                t(language, "Bright-field", "Светлое поле"),
                t(language, "Fluorescence", "Флуоресценция"),
                "SHG-like" if language == "en" else "SHG-подобная",
                t(language, "SEM-like", "СЭМ-подобная"),
            ],
            ["gray", "magma", "inferno", "gray"],
        ):
            ax.imshow(img, cmap=cmap)
            ax.set_title(title)
            ax.axis("off")
        fig.suptitle(
            t(
                language,
                "Registered modalities share geometry but not intensity semantics",
                "Совмещённые модальности имеют общую геометрию, но разный смысл интенсивности",
            )
        )
        return fig

    _pair("multimodal_registration", build)


def calibration_targets():
    n = 256
    yy, xx = np.indices((n, n))
    beads = np.zeros((n, n))
    for y, x in [(40, 40), (60, 180), (135, 85), (190, 190), (205, 45)]:
        beads[y, x] = 1
    bars = ((xx // 8) % 2).astype(float)
    wedge = np.clip(xx / (n - 1), 0, 1)
    result = simulate_fluorescence(
        beads, OpticalParameters(sigma_xy=2.1, gain=1500, read_noise=0.5), seed=2
    )

    def build(language):
        fig, axes = plt.subplots(1, 4, figsize=(13, 3.5))
        arrays = [beads, result.image, bars, wedge]
        titles = [
            t(language, "Point emitters", "Точечные излучатели"),
            t(language, "Measured PSF target", "Мишень для оценки ФРТ"),
            t(language, "Resolution bars", "Штриховая мира"),
            t(language, "Intensity wedge", "Клин интенсивности"),
        ]
        for ax, img, title in zip(axes, arrays, titles):
            ax.imshow(img, cmap="gray")
            ax.set_title(title)
            ax.axis("off")
        fig.suptitle(
            t(
                language,
                "Synthetic calibration targets separate instrument checks from tissue complexity",
                "Синтетические калибровочные мишени отделяют проверку прибора от сложности ткани",
            )
        )
        return fig

    _pair("calibration_targets", build)


def quality_metrics():
    _, _, amp, _, _ = _base2d()
    sigmas = np.linspace(0.4, 3.2, 9)
    p = []
    s = []
    for sigma in sigmas:
        r = simulate_fluorescence(
            amp, OpticalParameters(sigma_xy=float(sigma), gain=1000, read_noise=0.3), seed=3
        )
        p.append(psnr(amp, r.image))
        s.append(global_ssim(amp, r.image))

    def build(language):
        fig, ax1 = plt.subplots(figsize=(8.2, 4.7))
        ax2 = ax1.twinx()
        ax1.plot(sigmas, p, marker="o", label="PSNR")
        ax2.plot(sigmas, s, marker="s", ls="--", label="SSIM")
        ax1.set_xlabel(t(language, "PSF width σ", "Ширина ФРТ σ"))
        ax1.set_ylabel("PSNR, dB")
        ax2.set_ylabel("SSIM")
        ax1.set_title(
            t(
                language,
                "Image metrics depend on what is chosen as the reference",
                "Метрики изображения зависят от выбранного эталона",
            )
        )
        return fig

    _pair("quality_metrics", build)


def dataset_schema():
    _, raster, amp, orientation, thickness = _base2d()
    fl = simulate_fluorescence(amp, seed=14)
    bf = simulate_brightfield(thickness, seed=14)
    sem = simulate_sem(height_from_mask(raster.mask), seed=14)
    path = export_multimodal_dataset(
        DATA_DIRECTORY / "example_multimodal_dataset.npz",
        ground_truth={"mask": raster.mask, "orientation": orientation, "thickness": thickness},
        modalities={"fluorescence": fl.image, "brightfield": bf.image, "sem_like": sem.image},
        metadata={"seed": 14, "tutorial": 14},
    )
    with np.load(path, allow_pickle=False) as archive:
        keys = sorted(archive.files)

    def build(language):
        fig, ax = plt.subplots(figsize=(9, 5.2))
        ax.axis("off")
        rows = []
        for key in keys:
            with np.load(path, allow_pickle=False) as archive:
                arr = archive[key]
            shape = "scalar" if arr.ndim == 0 else " × ".join(map(str, arr.shape))
            rows.append([key, shape, str(arr.dtype)])
        table = ax.table(
            cellText=rows,
            colLabels=[
                t(language, "Array", "Массив"),
                t(language, "Shape", "Размерность"),
                t(language, "Type", "Тип"),
            ],
            loc="center",
            cellLoc="left",
        )
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 1.35)
        ax.set_title(
            t(
                language,
                "Synchronized multimodal dataset schema",
                "Схема синхронизированного мультимодального датасета",
            )
        )
        return fig

    _pair("dataset_schema", build)


def uncertainty_sweep():
    _, _, amp, _, _ = _base2d()
    sigmas = [0.6, 1.4, 2.2]
    gains = [50, 200, 800]
    values = np.zeros((len(sigmas), len(gains)))
    for i, sigma in enumerate(sigmas):
        for j, gain in enumerate(gains):
            r = simulate_fluorescence(
                amp, OpticalParameters(sigma_xy=sigma, gain=gain, read_noise=1), seed=20 + i * 5 + j
            )
            values[i, j] = global_ssim(r.expectation, r.image)

    def build(language):
        fig, ax = plt.subplots(figsize=(6.7, 5))
        im = ax.imshow(values, vmin=0, vmax=1, cmap="viridis")
        ax.set_xticks(range(len(gains)), gains)
        ax.set_yticks(range(len(sigmas)), sigmas)
        ax.set_xlabel(t(language, "Photon gain", "Фотонный коэффициент"))
        ax.set_ylabel(t(language, "PSF width", "Ширина ФРТ"))
        ax.set_title(
            t(
                language,
                "Observation uncertainty depends on optics and detector noise",
                "Неопределённость наблюдения зависит от оптики и шума детектора",
            )
        )
        fig.colorbar(im, ax=ax, label="SSIM")
        return fig

    _pair("uncertainty_sweep", build)


def benchmark_summary():
    _, raster, amp, orientation, thickness = _base2d()
    fluorescence = simulate_fluorescence(
        amp, OpticalParameters(sigma_xy=1.1, gain=900, read_noise=0.5), seed=12
    )
    brightfield = simulate_brightfield(thickness, noise_std=0.005, seed=12)
    sem = simulate_sem(
        height_from_mask(raster.mask), parameters=SEMParameters(noise_std=0.01), seed=12
    )
    vol = _base3d().volume.astype(float)
    fib = simulate_fib_sem_stack(vol, noise_std=0.008, seed=12)
    rows = [
        ("fluorescence_psnr", psnr(fluorescence.expectation, fluorescence.image), 25.0, "min"),
        (
            "fluorescence_ssim",
            global_ssim(fluorescence.expectation, fluorescence.image),
            0.85,
            "min",
        ),
        ("brightfield_ssim", global_ssim(brightfield.expectation, brightfield.image), 0.90, "min"),
        ("sem_ssim", global_ssim(sem.expectation, sem.image), 0.82, "min"),
        ("fib_sem_ssim", global_ssim(fib.expectation, fib.image), 0.60, "min"),
        ("dataset_mask_fraction", float(np.mean(raster.mask)), 0.01, "min"),
    ]
    csv_path = DATA_DIRECTORY / "synthetic_microscopy_benchmark.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["metric", "value", "threshold", "rule", "passed"])
        for name, value, thr, rule in rows:
            w.writerow([name, value, thr, rule, value >= thr])

    def build(language):
        fig, ax = plt.subplots(figsize=(10, 5.2))
        names = [r[0].replace("_", " ") for r in rows]
        ratios = [min(r[1] / r[2], 2.0) for r in rows]
        ax.barh(names, ratios)
        ax.axvline(1, ls="--", lw=1.2)
        ax.set_xlabel(t(language, "Value / acceptance threshold", "Значение / порог приёмки"))
        ax.set_title(
            t(
                language,
                "Verification-oriented synthetic benchmark",
                "Синтетический benchmark для верификации",
            )
        )
        return fig

    _pair("benchmark_summary", build)


def focus_animation():
    _, _, amp, _, _ = _base2d()
    defocus = np.concatenate([np.linspace(0, 4, 15), np.linspace(4, 0, 15)])
    frames = focus_series(amp, defocus)
    for language in ("en", "ru"):
        fig, ax = plt.subplots(figsize=(5.2, 5.2))
        im = ax.imshow(frames[0], cmap="magma", animated=True)
        ax.axis("off")
        title = ax.set_title("Defocus 0.0" if language == "en" else "Расфокусировка 0.0")

        def update(i):
            im.set_array(frames[i])
            title.set_text(
                (
                    f"Defocus {defocus[i]:.1f}"
                    if language == "en"
                    else f"Расфокусировка {defocus[i]:.1f}"
                )
            )
            return im, title

        ani = animation.FuncAnimation(fig, update, frames=len(frames), interval=100, blit=False)
        suffix = "" if language == "en" else "_ru"
        ani.save(ANIMATION_DIRECTORY / f"focus_sweep{suffix}.gif", writer="pillow", fps=10, dpi=85)
        plt.close(fig)


def fib_sem_animation():
    vol = _base3d().volume.astype(float)
    stack = simulate_fib_sem_stack(
        vol, drift_per_slice=(0.03, 0.06), curtaining_strength=0.08, seed=6
    ).image
    for language in ("en", "ru"):
        fig, ax = plt.subplots(figsize=(5.2, 5.2))
        im = ax.imshow(stack[0], cmap="gray", animated=True)
        ax.axis("off")
        title = ax.set_title("Serial section 0" if language == "en" else "Серийный срез 0")

        def update(i):
            im.set_array(stack[i])
            title.set_text((f"Serial section {i}" if language == "en" else f"Серийный срез {i}"))
            return im, title

        ani = animation.FuncAnimation(fig, update, frames=len(stack), interval=90, blit=False)
        suffix = "" if language == "en" else "_ru"
        ani.save(
            ANIMATION_DIRECTORY / f"fib_sem_serial_sections{suffix}.gif",
            writer="pillow",
            fps=11,
            dpi=85,
        )
        plt.close(fig)


SCENARIOS = {
    "modality taxonomy": modality_taxonomy,
    "ground-truth channels": ground_truth_channels,
    "bright-field formation": brightfield_formation,
    "fluorescence PSF": fluorescence_psf,
    "photon budget": photon_budget,
    "confocal sections": confocal_sections,
    "axial resolution": axial_resolution,
    "SHG polarization": shg_polarization,
    "SEM topography": sem_topography,
    "SEM detector direction": sem_detector_direction,
    "SEM composition": sem_composition,
    "FIB-SEM stack": fib_sem_stack,
    "drift and curtaining": drift_curtaining,
    "voxel anisotropy": voxel_anisotropy,
    "artifact gallery": artifact_gallery,
    "domain shift": domain_shift,
    "multimodal registration": multimodal_registration,
    "calibration targets": calibration_targets,
    "quality metrics": quality_metrics,
    "dataset schema": dataset_schema,
    "uncertainty sweep": uncertainty_sweep,
    "benchmark summary": benchmark_summary,
    "focus animation": focus_animation,
    "FIB-SEM animation": fib_sem_animation,
}
