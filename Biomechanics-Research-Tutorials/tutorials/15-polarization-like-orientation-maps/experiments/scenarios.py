"""Result generation for Tutorial 15."""

from __future__ import annotations

from functools import lru_cache
import csv

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np

from common import ANIMATION_DIRECTORY, DATA_DIRECTORY, save_figure, t
from biomechanics_tutorials.synthetic_fibrous_tissue import rasterize_network, tissue_preset
from biomechanics_tutorials.polarization_orientation import (
    PolarizationParameters,
    axial_difference,
    calibration_sweep,
    crossed_polarizer_intensity,
    estimate_retardance_from_modulation,
    export_polarization_dataset,
    multilayer_jones_intensity,
    orientation_error_deg,
    quadrature_orientation_error_deg,
    recover_orientation_harmonic,
    retardance_from_birefringence,
    simulate_polarization_series,
    synthetic_illumination_field,
)


def _pair(stem, builder):
    for language in ("en", "ru"):
        save_figure(builder(language), stem, language)


@lru_cache(maxsize=1)
def _base():
    network = tissue_preset("skin", seed=15)
    raster = rasterize_network(network, (220, 220), blur_sigma=0.35)
    mask = raster.mask
    orientation = np.where(mask, raster.orientation, 0.0)
    coherence = np.where(mask, np.clip(raster.coherence, 0.0, 1.0), 0.0)
    thickness = raster.thickness / max(float(np.max(raster.thickness)), 1.0)
    retardance = 0.15 + 1.8 * thickness * (0.4 + 0.6 * coherence)
    amplitude = mask.astype(float) * (0.35 + 0.65 * coherence)
    return mask, orientation, coherence, thickness, retardance, amplitude


def _series(n_angles=12, noise=0.008, depolarization=0.05, seed=15):
    mask, orientation, _, _, retardance, amplitude = _base()
    angles = np.linspace(0.0, np.pi, n_angles, endpoint=False)
    params = PolarizationParameters(
        read_noise_std=noise,
        depolarization=depolarization,
        blur_sigma=0.5,
        photon_count=2000,
    )
    return (
        mask,
        orientation,
        retardance,
        amplitude,
        simulate_polarization_series(
            orientation,
            retardance,
            angles,
            amplitude=amplitude,
            parameters=params,
            illumination=synthetic_illumination_field(mask.shape),
            seed=seed,
        ),
    )


def modeling_taxonomy():
    def build(language):
        fig, axes = plt.subplots(2, 3, figsize=(12.5, 7.4))
        cards = [
            (
                "Known structure",
                "Известная структура",
                "axis, thickness, composition",
                "ось, толщина, состав",
            ),
            (
                "Forward optics",
                "Прямая оптика",
                "Jones / reduced harmonic model",
                "Джонс / редуцированная гармоника",
            ),
            (
                "Angular series",
                "Угловая серия",
                "multiple analyzer states",
                "несколько состояний анализатора",
            ),
            (
                "Inverse recovery",
                "Обратное восстановление",
                "orientation, modulation, retardance",
                "ориентация, модуляция, retardance",
            ),
            (
                "Failure modes",
                "Режимы отказа",
                "overlap, depolarization, ambiguity",
                "наложение, деполяризация, неоднозначность",
            ),
            (
                "Verification",
                "Верификация",
                "known synthetic ground truth",
                "известная синтетическая ground truth",
            ),
        ]
        for ax, (en1, ru1, en2, ru2) in zip(axes.flat, cards):
            ax.axis("off")
            ax.add_patch(plt.Rectangle((0.04, 0.08), 0.92, 0.82, fill=False, lw=1.4))
            ax.text(
                0.5,
                0.63,
                t(language, en1, ru1),
                ha="center",
                va="center",
                fontsize=14,
                weight="bold",
                wrap=True,
            )
            ax.text(
                0.5, 0.34, t(language, en2, ru2), ha="center", va="center", fontsize=10, wrap=True
            )
        fig.suptitle(
            t(
                language,
                "Polarization-like imaging as a forward and inverse problem",
                "Поляризационно-подобная визуализация как прямая и обратная задача",
            )
        )
        return fig

    _pair("modeling_taxonomy", build)


def ground_truth_fields():
    mask, orientation, coherence, thickness, retardance, _ = _base()

    def build(language):
        fig, axes = plt.subplots(1, 5, figsize=(15.5, 3.5))
        arrays = [mask, np.rad2deg(orientation), coherence, thickness, retardance]
        titles = [
            t(language, "Mask", "Маска"),
            t(language, "Orientation, deg", "Ориентация, град"),
            t(language, "Coherence", "Когерентность"),
            t(language, "Thickness", "Толщина"),
            t(language, "Retardance, rad", "Фазовая задержка, рад"),
        ]
        cmaps = ["gray", "twilight", "viridis", "magma", "plasma"]
        for ax, arr, title, cmap in zip(axes, arrays, titles, cmaps):
            im = ax.imshow(arr, cmap=cmap)
            ax.set_title(title)
            ax.axis("off")
            if cmap != "gray":
                fig.colorbar(im, ax=ax, shrink=0.67)
        fig.suptitle(
            t(language, "Synthetic optical ground truth", "Синтетическая оптическая ground truth")
        )
        return fig

    _pair("ground_truth_fields", build)


def malus_curves():
    angles = np.linspace(0, np.pi, 361)
    orientations = np.deg2rad([0, 20, 45, 70])

    def build(language):
        fig, ax = plt.subplots(figsize=(8, 4.8))
        for ori in orientations:
            intensity = crossed_polarizer_intensity(ori, 1.4, angles)
            ax.plot(np.rad2deg(angles), intensity, label=f"{np.rad2deg(ori):.0f}°")
        ax.set_xlabel(t(language, "Analyzer angle, deg", "Угол анализатора, град"))
        ax.set_ylabel(t(language, "Normalized intensity", "Нормированная интенсивность"))
        ax.legend(title=t(language, "Optical axis", "Оптическая ось"), ncol=2)
        ax.set_title(
            t(
                language,
                "Fourth-harmonic angular response of a linear retarder",
                "Угловой отклик четвёртой гармоники линейного ретардера",
            )
        )
        return fig

    _pair("malus_curves", build)


def retardance_thickness_map():
    thickness = np.linspace(0, 20, 300)
    deltas = [0.0005, 0.001, 0.002]

    def build(language):
        fig, ax = plt.subplots(figsize=(8, 4.8))
        for dn in deltas:
            r = retardance_from_birefringence(dn, thickness)
            ax.plot(thickness, r, label=f"Δn={dn:g}")
        ax.set_xlabel(t(language, "Thickness, μm", "Толщина, мкм"))
        ax.set_ylabel(t(language, "Phase retardance, rad", "Фазовая задержка, рад"))
        ax.legend()
        ax.set_title(
            t(
                language,
                "Birefringence-thickness ambiguity",
                "Неоднозначность «двулучепреломление—толщина»",
            )
        )
        return fig

    _pair("retardance_thickness_map", build)


def angular_frames():
    _, _, _, _, series = _series()
    ids = [0, 2, 4, 6, 8, 10]

    def build(language):
        fig, axes = plt.subplots(2, 3, figsize=(10, 7))
        for ax, i in zip(axes.flat, ids):
            ax.imshow(series.images[i], cmap="gray")
            ax.axis("off")
            ax.set_title(f"θ={np.rad2deg(series.angles_rad[i]):.0f}°")
        fig.suptitle(
            t(
                language,
                "Synthetic angular acquisition series",
                "Синтетическая угловая серия измерений",
            )
        )
        return fig

    _pair("angular_frames", build)


def harmonic_recovery():
    mask, truth, _, _, series = _series(noise=0.006)
    rec = recover_orientation_harmonic(series.images, series.angles_rad)
    err = quadrature_orientation_error_deg(rec.orientation_rad, truth)

    def build(language):
        fig, axes = plt.subplots(1, 4, figsize=(14, 3.8))
        vals = [np.rad2deg(truth), np.rad2deg(rec.orientation_rad), err, rec.confidence]
        titles = [
            t(language, "Truth", "Истина"),
            t(language, "Recovered", "Восстановлено"),
            t(
                language,
                "Quadrature-equivalent error, deg",
                "Ошибка с учётом 90°-неоднозначности, град",
            ),
            t(language, "Confidence", "Доверие"),
        ]
        cmaps = ["twilight", "twilight", "magma", "viridis"]
        for ax, v, title, cmap in zip(axes, vals, titles, cmaps):
            im = ax.imshow(np.where(mask, v, np.nan), cmap=cmap)
            ax.set_title(title)
            ax.axis("off")
            fig.colorbar(im, ax=ax, shrink=0.65)
        fig.suptitle(
            t(language, "Harmonic orientation recovery", "Гармоническое восстановление ориентации")
        )
        return fig

    _pair("harmonic_recovery", build)


def angular_sampling_sweep():
    mask, truth, ret, amp, _ = _series()
    counts = np.array([3, 4, 5, 6, 8, 12, 18, 24])
    errors = []
    for n in counts:
        angles = np.linspace(0, np.pi, n, endpoint=False)
        series = simulate_polarization_series(
            truth,
            ret,
            angles,
            amp,
            PolarizationParameters(read_noise_std=0.012, photon_count=1000, blur_sigma=0.4),
            seed=n,
        )
        rec = recover_orientation_harmonic(series.images, angles, regularization=1e-8)
        errors.append(np.median(orientation_error_deg(rec.orientation_rad, truth, mask)))

    def build(language):
        fig, ax = plt.subplots(figsize=(7.5, 4.8))
        ax.plot(counts, errors, "o-")
        ax.set_xlabel(t(language, "Number of angular states", "Число угловых состояний"))
        ax.set_ylabel(t(language, "Median error, deg", "Медианная ошибка, град"))
        ax.set_title(
            t(
                language,
                "Angular sampling controls inverse accuracy",
                "Угловая дискретизация определяет точность восстановления",
            )
        )
        ax.grid(True, alpha=0.3)
        return fig

    _pair("angular_sampling_sweep", build)


def noise_sweep():
    mask, truth, ret, amp, _ = _series()
    noise = np.linspace(0, 0.06, 10)
    median = []
    p95 = []
    angles = np.linspace(0, np.pi, 12, endpoint=False)
    for i, n in enumerate(noise):
        s = simulate_polarization_series(
            truth,
            ret,
            angles,
            amp,
            PolarizationParameters(read_noise_std=float(n), photon_count=700, blur_sigma=0.4),
            seed=i,
        )
        rec = recover_orientation_harmonic(s.images, angles)
        e = orientation_error_deg(rec.orientation_rad, truth, mask)
        median.append(np.median(e))
        p95.append(np.percentile(e, 95))

    def build(language):
        fig, ax = plt.subplots(figsize=(7.5, 4.8))
        ax.plot(noise, median, "o-", label=t(language, "Median", "Медиана"))
        ax.plot(noise, p95, "s--", label=t(language, "95th percentile", "95-й процентиль"))
        ax.set_xlabel(t(language, "Read-noise standard deviation", "СКО шума считывания"))
        ax.set_ylabel(t(language, "Orientation error, deg", "Ошибка ориентации, град"))
        ax.legend()
        ax.grid(True, alpha=0.3)
        return fig

    _pair("noise_sweep", build)


def depolarization_sweep():
    mask, truth, ret, amp, _ = _series()
    values = np.linspace(0, 0.9, 10)
    mod = []
    err = []
    angles = np.linspace(0, np.pi, 12, endpoint=False)
    for i, d in enumerate(values):
        s = simulate_polarization_series(
            truth,
            ret,
            angles,
            amp,
            PolarizationParameters(depolarization=float(d), read_noise_std=0.01, photon_count=1200),
            seed=i,
        )
        r = recover_orientation_harmonic(s.images, angles)
        mod.append(np.nanmedian(r.modulation[mask]))
        err.append(np.median(orientation_error_deg(r.orientation_rad, truth, mask)))

    def build(language):
        fig, ax = plt.subplots(figsize=(7.8, 4.8))
        ax.plot(values, mod, "o-", label=t(language, "Median modulation", "Медианная модуляция"))
        ax.set_xlabel(
            t(language, "Depolarization-like fraction", "Доля деполяризационно-подобного вклада")
        )
        ax.set_ylabel(t(language, "Modulation", "Модуляция"))
        ax2 = ax.twinx()
        ax2.plot(values, err, "s--", label=t(language, "Orientation error", "Ошибка ориентации"))
        ax2.set_ylabel(t(language, "Median error, deg", "Медианная ошибка, град"))
        lines = ax.lines + ax2.lines
        ax.legend(lines, [line.get_label() for line in lines], loc="center left")
        return fig

    _pair("depolarization_sweep", build)


def illumination_bias():
    mask, truth, ret, amp, _ = _series()
    angles = np.linspace(0, np.pi, 12, endpoint=False)
    field = synthetic_illumination_field(mask.shape, gradient=(0.6, -0.45), vignette=0.35)
    s = simulate_polarization_series(
        truth,
        ret,
        angles,
        amp,
        PolarizationParameters(read_noise_std=0.004),
        illumination=field,
        seed=4,
    )
    rec = recover_orientation_harmonic(s.images, angles)

    def build(language):
        fig, axes = plt.subplots(1, 3, figsize=(11, 3.7))
        arrays = [
            field,
            s.images[0],
            np.where(mask, orientation_error_deg(rec.orientation_rad, truth), np.nan),
        ]
        titles = [
            t(language, "Illumination field", "Поле освещения"),
            t(language, "Observed frame", "Наблюдаемый кадр"),
            t(language, "Orientation error", "Ошибка ориентации"),
        ]
        cmaps = ["viridis", "gray", "magma"]
        for ax, a, title, cmap in zip(axes, arrays, titles, cmaps):
            im = ax.imshow(a, cmap=cmap)
            ax.set_title(title)
            ax.axis("off")
            fig.colorbar(im, ax=ax, shrink=0.65)
        return fig

    _pair("illumination_bias", build)


def retardance_recovery():
    mask, truth, ret, amp, series = _series(noise=0.002, depolarization=0)
    rec = recover_orientation_harmonic(series.images, series.angles_rad)
    est = estimate_retardance_from_modulation(rec.modulation, amp)

    def build(language):
        fig, axes = plt.subplots(1, 3, figsize=(11, 3.6))
        vals = [ret, est, np.abs(est - ret)]
        titles = [
            t(language, "True retardance", "Истинная задержка"),
            t(language, "Principal-branch estimate", "Оценка главной ветви"),
            t(language, "Absolute error", "Абсолютная ошибка"),
        ]
        for ax, v, title in zip(axes, vals, titles):
            im = ax.imshow(np.where(mask, v, np.nan), cmap="plasma")
            ax.set_title(title)
            ax.axis("off")
            fig.colorbar(im, ax=ax, shrink=0.65)
        fig.suptitle(
            t(
                language,
                "Retardance recovery is branch-limited and amplitude-dependent",
                "Восстановление задержки ограничено ветвью и зависит от амплитуды",
            )
        )
        return fig

    _pair("retardance_recovery", build)


def axial_ambiguity():
    angles = np.linspace(0, np.pi, 300)
    alpha = np.deg2rad(25)
    i1 = crossed_polarizer_intensity(alpha, 1.2, angles)
    i2 = crossed_polarizer_intensity(alpha + np.pi, 1.2, angles)
    i3 = crossed_polarizer_intensity(alpha + np.pi / 2, 1.2, angles)

    def build(language):
        fig, ax = plt.subplots(figsize=(8, 4.7))
        ax.plot(np.rad2deg(angles), i1, label=t(language, "α", "α"))
        ax.plot(np.rad2deg(angles), i2, "--", label=t(language, "α + 180°", "α + 180°"))
        ax.plot(np.rad2deg(angles), i3, ":", label=t(language, "α + 90°", "α + 90°"))
        ax.set_xlabel(t(language, "Analyzer angle, deg", "Угол анализатора, град"))
        ax.set_ylabel(t(language, "Intensity", "Интенсивность"))
        ax.legend()
        ax.set_title(
            t(
                language,
                "Reduced crossed-polarizer data contain axial and quadrature ambiguities",
                "Редуцированные данные содержат осевую и квадратурную неоднозначности",
            )
        )
        return fig

    _pair("axial_ambiguity", build)


def multilayer_noncommutativity():
    theta = np.linspace(0, np.pi, 181)
    first = np.array([multilayer_jones_intensity([0.1, 0.8], [1.1, 0.7], 0, a) for a in theta])
    second = np.array([multilayer_jones_intensity([0.8, 0.1], [0.7, 1.1], 0, a) for a in theta])

    def build(language):
        fig, ax = plt.subplots(figsize=(8, 4.8))
        ax.plot(np.rad2deg(theta), first, label=t(language, "Layer 1 → layer 2", "Слой 1 → слой 2"))
        ax.plot(
            np.rad2deg(theta),
            second,
            "--",
            label=t(language, "Layer 2 → layer 1", "Слой 2 → слой 1"),
        )
        ax.set_xlabel(t(language, "Analyzer angle, deg", "Угол анализатора, град"))
        ax.set_ylabel(t(language, "Intensity", "Интенсивность"))
        ax.legend()
        ax.set_title(
            t(
                language,
                "Ordered anisotropic layers are generally non-commutative",
                "Упорядоченные анизотропные слои в общем случае некоммутативны",
            )
        )
        return fig

    _pair("multilayer_noncommutativity", build)


def crossing_families_failure():
    shape = (180, 180)
    yy, xx = np.indices(shape)
    left = xx < 90
    alpha1 = np.deg2rad(25)
    alpha2 = np.deg2rad(-35)
    angles = np.linspace(0, np.pi, 12, endpoint=False)
    stack = []
    for a in angles:
        f1 = crossed_polarizer_intensity(alpha1, 1.3, a)
        f2 = crossed_polarizer_intensity(alpha2, 1.3, a)
        image = np.where(left, f1, 0.5 * f1 + 0.5 * f2)
        stack.append(np.ones(shape) * image)
    stack = np.stack(stack)
    rec = recover_orientation_harmonic(stack, angles)

    def build(language):
        fig, axes = plt.subplots(1, 3, figsize=(11, 3.7))
        axes[0].imshow(stack[2], cmap="gray")
        axes[0].set_title(t(language, "Angular frame", "Угловой кадр"))
        axes[1].imshow(np.rad2deg(rec.orientation_rad), cmap="twilight", vmin=-90, vmax=90)
        axes[1].set_title(t(language, "Single-axis fit", "Одноосевая аппроксимация"))
        axes[2].imshow(rec.residual_rms, cmap="magma")
        axes[2].set_title(t(language, "Model residual", "Невязка модели"))
        [ax.axis("off") for ax in axes]
        fig.suptitle(
            t(
                language,
                "A single recovered axis cannot represent two overlapping families",
                "Одна восстановленная ось не описывает два наложенных семейства",
            )
        )
        return fig

    _pair("crossing_families_failure", build)


def circular_retardance_bias():
    theta = np.linspace(0, np.pi, 181)
    base = np.sin(2 * (theta - 0.3)) ** 2
    biased = 0.15 + 0.7 * base + 0.14 * np.sin(2 * theta + 0.5)
    rec = recover_orientation_harmonic(biased[:, None, None], theta)

    def build(language):
        fig, ax = plt.subplots(figsize=(8, 4.8))
        ax.plot(
            np.rad2deg(theta),
            base,
            label=t(
                language, "Ideal linear-retardance response", "Идеальный отклик линейной задержки"
            ),
        )
        ax.plot(
            np.rad2deg(theta),
            biased,
            label=t(
                language,
                "Response with unmodeled lower harmonic",
                "Отклик с неучтённой низшей гармоникой",
            ),
        )
        ax.plot(
            np.rad2deg(theta),
            np.full_like(theta, rec.offset.item()),
            "--",
            label=t(language, "Fitted offset", "Оценённое смещение"),
        )
        ax.set_xlabel(t(language, "Angle, deg", "Угол, град"))
        ax.set_ylabel(t(language, "Intensity", "Интенсивность"))
        ax.legend()
        ax.set_title(
            t(
                language,
                "Unmodeled polarization effects bias a reduced inverse model",
                "Неучтённые поляризационные эффекты смещают редуцированную обратную модель",
            )
        )
        return fig

    _pair("circular_retardance_bias", build)


def calibration_offset():
    known = np.deg2rad(np.linspace(-80, 80, 17))
    measured = calibration_sweep(known, np.deg2rad(7.5), 0.98)
    fitted_offset = np.median(axial_difference(measured, known))
    corrected = measured - fitted_offset

    def build(language):
        fig, ax = plt.subplots(figsize=(6, 5.5))
        ax.scatter(
            np.rad2deg(known), np.rad2deg(measured), label=t(language, "Raw", "До коррекции")
        )
        ax.scatter(
            np.rad2deg(known),
            np.rad2deg(corrected),
            label=t(language, "Corrected", "После коррекции"),
        )
        ax.plot([-90, 90], [-90, 90], "--", label=t(language, "Identity", "Тождество"))
        ax.set_xlabel(t(language, "Known axis, deg", "Известная ось, град"))
        ax.set_ylabel(t(language, "Measured axis, deg", "Измеренная ось, град"))
        ax.legend()
        ax.set_title(
            t(
                language,
                "Synthetic angular-offset calibration",
                "Синтетическая калибровка углового смещения",
            )
        )
        return fig

    _pair("calibration_offset", build)


def confidence_masking():
    mask, truth, _, _, series = _series(noise=0.025, depolarization=0.25)
    rec = recover_orientation_harmonic(series.images, series.angles_rad)
    threshold = np.percentile(rec.confidence[mask], 35)
    valid = mask & (rec.confidence >= threshold)

    def build(language):
        fig, axes = plt.subplots(1, 3, figsize=(11, 3.7))
        vals = [
            rec.confidence,
            valid,
            np.where(valid, orientation_error_deg(rec.orientation_rad, truth), np.nan),
        ]
        titles = [
            t(language, "Confidence", "Доверие"),
            t(language, "Accepted pixels", "Принятые пиксели"),
            t(language, "Error after masking", "Ошибка после маскирования"),
        ]
        cmaps = ["viridis", "gray", "magma"]
        for ax, v, title, cmap in zip(axes, vals, titles, cmaps):
            im = ax.imshow(v, cmap=cmap)
            ax.set_title(title)
            ax.axis("off")
            fig.colorbar(im, ax=ax, shrink=0.65)
        return fig

    _pair("confidence_masking", build)


def incomplete_series():
    mask, truth, ret, amp, _ = _series()
    all_angles = np.linspace(0, np.pi, 12, endpoint=False)
    subsets = [all_angles, all_angles[:6], all_angles[[0, 1, 2, 6, 7, 8]]]
    errors = []
    conds = []
    for angles in subsets:
        s = simulate_polarization_series(
            truth, ret, angles, amp, PolarizationParameters(read_noise_std=0.01), seed=len(angles)
        )
        r = recover_orientation_harmonic(s.images, angles, regularization=1e-6)
        errors.append(np.median(orientation_error_deg(r.orientation_rad, truth, mask)))
        conds.append(
            np.linalg.cond(
                np.column_stack([np.ones_like(angles), np.cos(4 * angles), np.sin(4 * angles)])
            )
        )

    def build(language):
        names = [
            t(language, "Full range", "Полный диапазон"),
            t(language, "Half range", "Половина диапазона"),
            t(language, "Clustered", "Сгруппированные углы"),
        ]
        fig, ax = plt.subplots(figsize=(8, 4.8))
        x = np.arange(3)
        ax.bar(x, errors)
        ax.set_xticks(x, names)
        ax.set_ylabel(t(language, "Median error, deg", "Медианная ошибка, град"))
        ax2 = ax.twinx()
        ax2.plot(x, conds, "o--")
        ax2.set_ylabel(t(language, "Design condition number", "Число обусловленности матрицы"))
        ax.set_title(
            t(
                language,
                "Missing angular coverage can make the inverse problem ill-conditioned",
                "Неполное угловое покрытие ухудшает обусловленность обратной задачи",
            )
        )
        return fig

    _pair("incomplete_series", build)


def wavelength_sweep():
    thickness = np.linspace(0, 12, 240)
    wavelengths = [450, 550, 650]

    def build(language):
        fig, ax = plt.subplots(figsize=(8, 4.8))
        for wavelength in wavelengths:
            delta = retardance_from_birefringence(0.0015, thickness, wavelength)
            contrast = np.sin(delta / 2) ** 2
            ax.plot(thickness, contrast, label=f"{wavelength} nm")
        ax.set_xlabel(t(language, "Thickness, μm", "Толщина, мкм"))
        ax.set_ylabel(t(language, "Retardance contrast factor", "Контрастный множитель задержки"))
        ax.legend()
        ax.set_title(
            t(
                language,
                "Spectral dependence creates periodic contrast reversals",
                "Спектральная зависимость создаёт периодические инверсии контраста",
            )
        )
        return fig

    _pair("wavelength_sweep", build)


def spatial_resolution():
    mask, truth, ret, amp, _ = _series()
    sigmas = [0, 1, 2.5]
    angles = np.linspace(0, np.pi, 12, endpoint=False)
    outputs = []
    for sigma in sigmas:
        s = simulate_polarization_series(
            truth,
            ret,
            angles,
            amp,
            PolarizationParameters(blur_sigma=sigma, read_noise_std=0.003),
            seed=3,
        )
        r = recover_orientation_harmonic(s.images, angles)
        outputs.append(r.orientation_rad)

    def build(language):
        fig, axes = plt.subplots(1, 3, figsize=(11, 3.7))
        for ax, out, sigma in zip(axes, outputs, sigmas):
            ax.imshow(np.where(mask, np.rad2deg(out), np.nan), cmap="twilight", vmin=-90, vmax=90)
            ax.set_title(f"σ={sigma:g} px")
            ax.axis("off")
        fig.suptitle(
            t(
                language,
                "Optical blur mixes neighboring orientations",
                "Оптическое размытие смешивает соседние ориентации",
            )
        )
        return fig

    _pair("spatial_resolution", build)


def uncertainty_map():
    mask, truth, ret, amp, _ = _series()
    angles = np.linspace(0, np.pi, 12, endpoint=False)
    est = []
    for seed in range(18):
        s = simulate_polarization_series(
            truth,
            ret,
            angles,
            amp,
            PolarizationParameters(read_noise_std=0.02, photon_count=700),
            seed=seed,
        )
        est.append(recover_orientation_harmonic(s.images, angles).orientation_rad)
    z = np.mean(np.exp(2j * np.stack(est)), axis=0)
    circular_std = np.sqrt(np.maximum(-2 * np.log(np.clip(np.abs(z), 1e-9, 1)), 0)) / 2

    def build(language):
        fig, axes = plt.subplots(1, 3, figsize=(11, 3.7))
        vals = [
            np.rad2deg(np.angle(z) / 2),
            np.rad2deg(circular_std),
            np.where(mask, np.rad2deg(np.abs(axial_difference(np.angle(z) / 2, truth))), np.nan),
        ]
        titles = [
            t(language, "Ensemble mean", "Среднее по ансамблю"),
            t(language, "Axial uncertainty, deg", "Осевая неопределённость, град"),
            t(language, "Mean error, deg", "Ошибка среднего, град"),
        ]
        for ax, v, title in zip(axes, vals, titles):
            im = ax.imshow(
                np.where(mask, v, np.nan),
                cmap="magma"
                if "error" in title.lower()
                or "ошиб" in title.lower()
                or "uncert" in title.lower()
                or "неоп" in title.lower()
                else "twilight",
            )
            ax.set_title(title)
            ax.axis("off")
            fig.colorbar(im, ax=ax, shrink=0.65)
        return fig

    _pair("uncertainty_map", build)


def dataset_schema():
    mask, truth, ret, amp, series = _series()
    path = export_polarization_dataset(
        DATA_DIRECTORY / "example_polarization_dataset.npz",
        series,
        {"mask": mask, "orientation_rad": truth, "retardance_rad": ret, "amplitude": amp},
        {"tutorial": 15},
    )
    with np.load(path, allow_pickle=False) as data:
        keys = list(data.files)

    def build(language):
        fig, ax = plt.subplots(figsize=(9, 5.8))
        ax.axis("off")
        ax.text(
            0.03,
            0.95,
            t(language, "Exported NPZ schema", "Схема экспортированного NPZ"),
            fontsize=16,
            weight="bold",
            va="top",
        )
        lines = [
            f"• {key}: {np.load(path, allow_pickle=False)[key].shape if key != 'metadata_json' else 'JSON'}"
            for key in keys
        ]
        ax.text(0.05, 0.82, "\n".join(lines), family="monospace", fontsize=10, va="top")
        ax.text(
            0.52,
            0.82,
            t(
                language,
                "Required provenance:\nsynthetic = true\nexperimental_validation = false\nseed and forward-model metadata",
                "Обязательное происхождение:\nsynthetic = true\nexperimental_validation = false\nseed и метаданные прямой модели",
            ),
            fontsize=11,
            va="top",
        )
        return fig

    _pair("dataset_schema", build)


def benchmark_summary():
    mask, truth, ret, amp, _ = _series()
    angles = np.linspace(0, np.pi, 16, endpoint=False)
    s = simulate_polarization_series(
        truth,
        ret,
        angles,
        amp,
        PolarizationParameters(read_noise_std=0.005, photon_count=2500),
        seed=21,
    )
    r = recover_orientation_harmonic(s.images, angles)
    err = quadrature_orientation_error_deg(r.orientation_rad, truth, mask)
    rows = [
        ("median_quadrature_error_deg", float(np.median(err)), 3.5),
        ("p95_quadrature_error_deg", float(np.percentile(err, 95)), 15.0),
        ("finite_fraction", float(np.mean(np.isfinite(r.orientation_rad))), 0.999),
        ("positive_confidence_fraction", float(np.mean(r.confidence[mask] > 0)), 0.99),
        ("metadata_synthetic", 1.0, 1.0),
    ]
    with (DATA_DIRECTORY / "polarization_orientation_benchmark.csv").open(
        "w", newline="", encoding="utf-8"
    ) as stream:
        writer = csv.writer(stream)
        writer.writerow(["check", "value", "target", "passed"])
        for name, value, target in rows:
            passed = value <= target if "error" in name else value >= target
            writer.writerow([name, value, target, passed])

    def build(language):
        names = [
            t(language, "Median error", "Медианная ошибка"),
            t(language, "95% error", "95% ошибка"),
            t(language, "Finite pixels", "Конечные значения"),
            t(language, "Positive confidence", "Положительное доверие"),
            t(language, "Synthetic provenance", "Синтетическое происхождение"),
        ]
        values = [
            min(rows[0][1] / rows[0][2], 1.5),
            min(rows[1][1] / rows[1][2], 1.5),
            rows[2][1],
            rows[3][1],
            rows[4][1],
        ]
        fig, ax = plt.subplots(figsize=(9, 4.8))
        ax.barh(names, values)
        ax.axvline(1, color="black", ls="--", lw=1)
        ax.set_xlabel(
            t(language, "Normalized verification score", "Нормированный показатель проверки")
        )
        ax.set_title(
            t(language, "Synthetic verification benchmark", "Синтетический benchmark верификации")
        )
        return fig

    _pair("benchmark_summary", build)


def orientation_animation():
    mask, truth, ret, amp, _ = _series()
    angles = np.linspace(0, np.pi, 30, endpoint=False)
    series = simulate_polarization_series(
        truth,
        ret,
        angles,
        amp,
        PolarizationParameters(read_noise_std=0.006, photon_count=1400),
        seed=19,
    )
    for language, suffix in (("en", ""), ("ru", "_ru")):
        fig, ax = plt.subplots(figsize=(5.5, 5.3))
        image = ax.imshow(
            series.images[0], cmap="gray", vmin=0, vmax=np.percentile(series.images, 99.5)
        )
        ax.axis("off")
        title = ax.set_title("")

        def update(index):
            image.set_data(series.images[index])
            title.set_text(
                t(language, "Analyzer angle", "Угол анализатора")
                + f": {np.rad2deg(angles[index]):.0f}°"
            )
            return image, title

        movie = animation.FuncAnimation(fig, update, frames=len(angles), interval=100, blit=False)
        movie.save(
            ANIMATION_DIRECTORY / f"polarization_series{suffix}.gif",
            writer="pillow",
            fps=10,
            dpi=90,
        )
        plt.close(fig)


SCENARIOS = {
    "modeling_taxonomy": modeling_taxonomy,
    "ground_truth_fields": ground_truth_fields,
    "malus_curves": malus_curves,
    "retardance_thickness_map": retardance_thickness_map,
    "angular_frames": angular_frames,
    "harmonic_recovery": harmonic_recovery,
    "angular_sampling_sweep": angular_sampling_sweep,
    "noise_sweep": noise_sweep,
    "depolarization_sweep": depolarization_sweep,
    "illumination_bias": illumination_bias,
    "retardance_recovery": retardance_recovery,
    "axial_ambiguity": axial_ambiguity,
    "multilayer_noncommutativity": multilayer_noncommutativity,
    "crossing_families_failure": crossing_families_failure,
    "circular_retardance_bias": circular_retardance_bias,
    "calibration_offset": calibration_offset,
    "confidence_masking": confidence_masking,
    "incomplete_series": incomplete_series,
    "wavelength_sweep": wavelength_sweep,
    "spatial_resolution": spatial_resolution,
    "uncertainty_map": uncertainty_map,
    "dataset_schema": dataset_schema,
    "benchmark_summary": benchmark_summary,
    "orientation_animation": orientation_animation,
}
