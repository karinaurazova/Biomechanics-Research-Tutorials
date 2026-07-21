"""Reproducible figures, datasets, benchmarks, and animations for Tutorial 16."""

from __future__ import annotations


import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np

from common import ANIMATION_DIRECTORY, DATA_DIRECTORY, save_figure, t
from biomechanics_tutorials.digital_image_correlation import (
    DICParameters,
    SpeckleParameters,
    correlation_surface,
    dic_metrics,
    displacement_field,
    estimate_subset_displacement,
    export_dic_dataset,
    forward_backward_error,
    generate_natural_texture,
    generate_speckle_pattern,
    refine_affine_subset,
    run_subset_dic,
    sample_truth_on_dic_grid,
    strain_fields,
    warp_image,
)


def _base_pair(seed: int = 4, shape: tuple[int, int] = (128, 144)):
    ref = generate_speckle_pattern(shape, SpeckleParameters(seed=seed, density=0.03))
    u, v = displacement_field(shape, "heterogeneous", amplitude=4.0)
    deformed = warp_image(ref, u, v, interpolation_order=3)
    return ref, deformed, u, v


def _imshow(ax, array, title, cmap="gray", vmin=None, vmax=None):
    image = ax.imshow(array, cmap=cmap, origin="upper", vmin=vmin, vmax=vmax)
    ax.set_title(title)
    ax.set_xticks([])
    ax.set_yticks([])
    return image


def _paired(stem: str, builder):
    for language in ("en", "ru"):
        fig = builder(language)
        save_figure(fig, stem, language)


def modeling_taxonomy():
    def builder(language):
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        cards = [
            (
                "Forward image model",
                "Прямая модель изображения",
                "speckles → warp → camera artifacts",
                "спеклы → деформация → артефакты камеры",
            ),
            (
                "Subset matching",
                "Сопоставление подобластей",
                "ZNCC / ZNSSD, search and subpixel peak",
                "ZNCC / ZNSSD, поиск и субпиксельный максимум",
            ),
            (
                "Kinematics",
                "Кинематика",
                "displacements → gradients → strain tensors",
                "перемещения → градиенты → тензоры деформации",
            ),
            (
                "Verification",
                "Верификация",
                "ground truth, uncertainty and failure modes",
                "ground truth, неопределённость и режимы отказа",
            ),
        ]
        for ax, (en_title, ru_title, en_body, ru_body) in zip(axes.ravel(), cards):
            ax.axis("off")
            ax.text(
                0.5,
                0.72,
                t(language, en_title, ru_title),
                ha="center",
                va="center",
                fontsize=14,
                weight="bold",
                transform=ax.transAxes,
            )
            ax.text(
                0.5,
                0.40,
                t(language, en_body, ru_body),
                ha="center",
                va="center",
                fontsize=11,
                wrap=True,
                transform=ax.transAxes,
            )
        fig.suptitle(
            t(
                language,
                "Synthetic DIC as a forward–inverse measurement pipeline",
                "Синтетический DIC как прямая и обратная измерительная цепочка",
            )
        )
        return fig

    _paired("modeling_taxonomy", builder)


def speckle_gallery():
    patterns = [
        generate_speckle_pattern(
            (120, 120), SpeckleParameters(seed=1, density=0.018, radius_mean=1.2)
        ),
        generate_speckle_pattern(
            (120, 120), SpeckleParameters(seed=1, density=0.035, radius_mean=1.8)
        ),
        generate_speckle_pattern(
            (120, 120), SpeckleParameters(seed=1, density=0.055, radius_mean=2.6)
        ),
        generate_natural_texture((120, 120), seed=2),
    ]

    def builder(language):
        fig, axes = plt.subplots(1, 4, figsize=(14, 3.6))
        titles = [
            ("Fine sparse", "Мелкий редкий"),
            ("Balanced", "Сбалансированный"),
            ("Coarse dense", "Крупный плотный"),
            ("Natural texture", "Естественная текстура"),
        ]
        for ax, image, title in zip(axes, patterns, titles):
            _imshow(ax, image, t(language, *title))
        fig.suptitle(
            t(
                language,
                "Reference texture controls correlation information",
                "Текстура исходного изображения определяет информативность корреляции",
            )
        )
        return fig

    _paired("speckle_gallery", builder)


def exact_displacement_fields():
    fields = ["translation", "uniaxial", "shear", "bending", "heterogeneous", "localization"]

    def builder(language):
        fig, axes = plt.subplots(2, 3, figsize=(13, 8))
        labels = {
            "translation": ("Translation", "Перенос"),
            "uniaxial": ("Uniaxial", "Одноосное"),
            "shear": ("Simple shear", "Простой сдвиг"),
            "bending": ("Bending-like", "Изгибное"),
            "heterogeneous": ("Heterogeneous", "Неоднородное"),
            "localization": ("Localization", "Локализация"),
        }
        for ax, kind in zip(axes.ravel(), fields):
            u, v = displacement_field((80, 96), kind, amplitude=4.0)
            magnitude = np.hypot(u, v)
            im = ax.imshow(magnitude, cmap="viridis")
            stride = 8
            yy, xx = np.indices(magnitude.shape)
            ax.quiver(
                xx[::stride, ::stride],
                yy[::stride, ::stride],
                u[::stride, ::stride],
                v[::stride, ::stride],
                color="white",
                scale=45,
            )
            ax.set_title(t(language, *labels[kind]))
            ax.set_xticks([])
            ax.set_yticks([])
            fig.colorbar(im, ax=ax, shrink=0.72)
        fig.suptitle(
            t(
                language,
                "Exact displacement fields used as ground truth",
                "Точные поля перемещений, используемые как ground truth",
            )
        )
        return fig

    _paired("exact_displacement_fields", builder)


def reference_deformed_pair():
    ref, deformed, u, v = _base_pair()

    def builder(language):
        fig, axes = plt.subplots(1, 4, figsize=(14, 3.8))
        _imshow(axes[0], ref, t(language, "Reference image", "Исходное изображение"))
        _imshow(axes[1], deformed, t(language, "Deformed image", "Деформированное изображение"))
        im2 = _imshow(
            axes[2], u, t(language, "Ground-truth u [px]", "Ground-truth u [пикс.]"), "coolwarm"
        )
        im3 = _imshow(
            axes[3], v, t(language, "Ground-truth v [px]", "Ground-truth v [пикс.]"), "coolwarm"
        )
        fig.colorbar(im2, ax=axes[2], shrink=0.75)
        fig.colorbar(im3, ax=axes[3], shrink=0.75)
        fig.suptitle(
            t(
                language,
                "Image formation by inverse warping",
                "Формирование изображения обратным отображением",
            )
        )
        return fig

    _paired("reference_deformed_pair", builder)


def correlation_surface_figure():
    ref = generate_speckle_pattern((112, 112), SpeckleParameters(seed=8))
    u = np.full_like(ref, 2.4)
    v = np.full_like(ref, -1.6)
    deformed = warp_image(ref, u, v)
    scores, us, vs = correlation_surface(ref, deformed, 56, 56, 13, 5)
    est = estimate_subset_displacement(ref, deformed, 56, 56, 13, 5, True)

    def builder(language):
        fig, axes = plt.subplots(1, 3, figsize=(12, 4))
        _imshow(axes[0], ref[43:70, 43:70], t(language, "Reference subset", "Исходная подобласть"))
        _imshow(
            axes[1],
            deformed[41:68, 45:72],
            t(language, "Matched deformed region", "Сопоставленная область"),
        )
        im = axes[2].imshow(
            scores, extent=[us[0] - 0.5, us[-1] + 0.5, vs[-1] + 0.5, vs[0] - 0.5], cmap="viridis"
        )
        axes[2].scatter(
            [est[0]],
            [est[1]],
            marker="x",
            s=90,
            label=t(language, "subpixel peak", "субпиксельный максимум"),
        )
        axes[2].set_xlabel(t(language, "horizontal shift u [px]", "горизонтальный сдвиг u [пикс.]"))
        axes[2].set_ylabel(t(language, "vertical shift v [px]", "вертикальный сдвиг v [пикс.]"))
        axes[2].legend()
        fig.colorbar(im, ax=axes[2], label="ZNCC")
        fig.suptitle(
            t(
                language,
                "Correlation surface converts texture similarity into displacement",
                "Корреляционная поверхность преобразует сходство текстуры в перемещение",
            )
        )
        return fig

    _paired("correlation_surface", builder)


def subpixel_peak():
    ref = generate_speckle_pattern((112, 112), SpeckleParameters(seed=12))
    truth = np.array([2.4, -1.6])
    deformed = warp_image(ref, np.full_like(ref, truth[0]), np.full_like(ref, truth[1]))
    scores, us, vs = correlation_surface(ref, deformed, 56, 56, 13, 5)
    est = estimate_subset_displacement(ref, deformed, 56, 56, 13, 5, True)
    iy, ix = np.unravel_index(np.argmax(scores), scores.shape)

    def builder(language):
        fig, axes = plt.subplots(1, 2, figsize=(10, 4))
        axes[0].plot(us, scores[iy], "o-")
        axes[0].axvline(truth[0], ls="--", label=t(language, "truth", "истина"))
        axes[0].axvline(est[0], ls=":", label=t(language, "estimate", "оценка"))
        axes[0].set_xlabel("u [px]")
        axes[0].set_ylabel("ZNCC")
        axes[0].legend()
        axes[0].set_title(t(language, "Horizontal peak", "Горизонтальный максимум"))
        axes[1].plot(vs, scores[:, ix], "o-")
        axes[1].axvline(truth[1], ls="--", label=t(language, "truth", "истина"))
        axes[1].axvline(est[1], ls=":", label=t(language, "estimate", "оценка"))
        axes[1].set_xlabel("v [px]")
        axes[1].set_ylabel("ZNCC")
        axes[1].legend()
        axes[1].set_title(t(language, "Vertical peak", "Вертикальный максимум"))
        fig.suptitle(
            t(
                language,
                "Quadratic interpolation resolves subpixel displacement",
                "Квадратичная интерполяция восстанавливает субпиксельное перемещение",
            )
        )
        return fig

    _paired("subpixel_peak", builder)


def affine_subset():
    ref = generate_speckle_pattern((120, 120), SpeckleParameters(seed=21))
    yy, xx = np.indices(ref.shape, dtype=float)
    u = 1.2 + 0.018 * (xx - 60) + 0.011 * (yy - 60)
    v = -0.8 - 0.007 * (xx - 60) - 0.012 * (yy - 60)
    deformed = warp_image(ref, u, v)
    p, score = refine_affine_subset(ref, deformed, 60, 60, 1.2, -0.8, 16)
    truth = np.array([1.2, -0.8, 0.018, 0.011, -0.007, -0.012])

    def builder(language):
        fig, axes = plt.subplots(1, 2, figsize=(11, 4.4))
        names = ["u", "v", "du/dx", "du/dy", "dv/dx", "dv/dy"]
        x = np.arange(6)
        w = 0.36
        axes[0].bar(x - w / 2, truth, w, label=t(language, "truth", "истина"))
        axes[0].bar(x + w / 2, p, w, label=t(language, "estimate", "оценка"))
        axes[0].set_xticks(x, names, rotation=24)
        axes[0].legend()
        axes[0].set_title(t(language, "Affine subset parameters", "Параметры аффинной подобласти"))
        residual = np.array(
            [
                p[0] - truth[0],
                p[1] - truth[1],
                p[2] - truth[2],
                p[3] - truth[3],
                p[4] - truth[4],
                p[5] - truth[5],
            ]
        )
        axes[1].bar(names, np.abs(residual))
        axes[1].set_yscale("log")
        axes[1].tick_params(axis="x", rotation=24)
        axes[1].set_ylabel(t(language, "absolute error", "абсолютная ошибка"))
        axes[1].set_title(
            t(language, f"Normalized score = {score:.4f}", f"Нормированный score = {score:.4f}")
        )
        fig.suptitle(
            t(
                language,
                "Affine refinement separates translation and local deformation",
                "Аффинное уточнение разделяет перенос и локальную деформацию",
            )
        )
        return fig

    _paired("affine_subset", builder)


def translation_verification():
    ref = generate_speckle_pattern((128, 144), SpeckleParameters(seed=10))
    u = np.full_like(ref, 2.75)
    v = np.full_like(ref, 1.35)
    deformed = warp_image(ref, u, v)
    result = run_subset_dic(
        ref, deformed, DICParameters(subset_radius=11, step=18, search_radius=5), 0.65
    )
    tu = sample_truth_on_dic_grid(u, result)
    tv = sample_truth_on_dic_grid(v, result)
    err = np.hypot(result.u - tu, result.v - tv)

    def builder(language):
        fig, axes = plt.subplots(1, 3, figsize=(13, 4))
        im = axes[0].imshow(result.u, cmap="coolwarm", vmin=2.5, vmax=3.0)
        axes[0].set_title(t(language, "Recovered u [px]", "Восстановленное u [пикс.]"))
        fig.colorbar(im, ax=axes[0])
        im = axes[1].imshow(result.v, cmap="coolwarm", vmin=1.1, vmax=1.6)
        axes[1].set_title(t(language, "Recovered v [px]", "Восстановленное v [пикс.]"))
        fig.colorbar(im, ax=axes[1])
        im = axes[2].imshow(err, cmap="magma")
        axes[2].set_title(t(language, "Vector error [px]", "Векторная ошибка [пикс.]"))
        fig.colorbar(im, ax=axes[2])
        fig.suptitle(
            t(
                language,
                "Rigid translation is the first verification case",
                "Жёсткий перенос — первый верификационный случай",
            )
        )
        return fig

    _paired("translation_verification", builder)


def uniaxial_strain_recovery():
    shape = (132, 148)
    ref = generate_speckle_pattern(shape, SpeckleParameters(seed=30, density=0.04))
    yy, xx = np.indices(shape, dtype=float)
    u = 0.035 * (xx - 74)
    v = -0.012 * (yy - 66)
    deformed = warp_image(ref, u, v)
    result = run_subset_dic(
        ref, deformed, DICParameters(subset_radius=12, step=14, search_radius=5), 0.55
    )
    # Fit affine gradients directly on sparse grid for robust educational recovery.
    valid = result.valid
    A = np.column_stack([np.ones(np.count_nonzero(valid)), result.x[valid], result.y[valid]])
    cu = np.linalg.lstsq(A, result.u[valid], rcond=None)[0]
    cv = np.linalg.lstsq(A, result.v[valid], rcond=None)[0]
    estimates = np.array([cu[1], cv[2], 0.5 * (cu[2] + cv[1])])
    truth = np.array([0.035, -0.012, 0.0])

    def builder(language):
        fig, axes = plt.subplots(1, 3, figsize=(13, 4))
        axes[0].quiver(result.x, result.y, result.u, result.v, result.correlation, cmap="viridis")
        axes[0].invert_yaxis()
        axes[0].set_aspect("equal")
        axes[0].set_title(t(language, "Sparse displacement field", "Разреженное поле перемещений"))
        labels = ["εxx", "εyy", "εxy"]
        x = np.arange(3)
        w = 0.36
        axes[1].bar(x - w / 2, truth, w, label=t(language, "truth", "истина"))
        axes[1].bar(x + w / 2, estimates, w, label=t(language, "DIC estimate", "оценка DIC"))
        axes[1].set_xticks(x, labels)
        axes[1].legend()
        axes[1].set_title(t(language, "Global affine strain", "Глобальная аффинная деформация"))
        axes[2].scatter(sample_truth_on_dic_grid(u, result)[valid], result.u[valid], s=22)
        lim = [np.nanmin(result.u), np.nanmax(result.u)]
        axes[2].plot(lim, lim, "--")
        axes[2].set_xlabel(t(language, "true u [px]", "истинное u [пикс.]"))
        axes[2].set_ylabel(t(language, "estimated u [px]", "оценённое u [пикс.]"))
        axes[2].set_title(t(language, "Pointwise displacement", "Поточечное перемещение"))
        fig.suptitle(
            t(
                language,
                "Strain follows from spatial derivatives, not from displacement magnitude",
                "Деформация определяется пространственными производными, а не величиной перемещения",
            )
        )
        return fig

    _paired("uniaxial_strain_recovery", builder)


def shear_rotation():
    shape = (110, 126)
    yy, xx = np.indices(shape, dtype=float)
    results = []
    for kind in ["shear", "rotation"]:
        u, v = displacement_field(shape, kind, amplitude=5.0)
        s = strain_fields(u, v)
        results.append((u, v, s))

    def builder(language):
        fig, axes = plt.subplots(2, 3, figsize=(12, 7))
        row_titles = [("Simple shear", "Простой сдвиг"), ("Rigid rotation", "Жёсткое вращение")]
        for row, (u, v, s) in enumerate(results):
            _imshow(axes[row, 0], u, t(language, "u field", "поле u"), "coolwarm")
            _imshow(
                axes[row, 1],
                s.small_exy,
                t(language, "small shear strain εxy", "малая сдвиговая деформация εxy"),
                "coolwarm",
            )
            _imshow(
                axes[row, 2],
                s.green_exx + s.green_eyy,
                t(language, "Green-strain trace", "след деформации Грина"),
                "coolwarm",
            )
            axes[row, 0].set_ylabel(t(language, *row_titles[row]))
        fig.suptitle(
            t(
                language,
                "Objective interpretation requires separating strain from rigid motion",
                "Объективная интерпретация требует отделять деформацию от жёсткого движения",
            )
        )
        return fig

    _paired("shear_rotation", builder)


def bending_field():
    shape = (128, 144)
    ref = generate_speckle_pattern(shape, SpeckleParameters(seed=40))
    u, v = displacement_field(shape, "bending", 5.0)
    deformed = warp_image(ref, u, v)
    s = strain_fields(u, v)

    def builder(language):
        fig, axes = plt.subplots(1, 4, figsize=(14, 4))
        _imshow(axes[0], deformed, t(language, "Deformed image", "Деформированное изображение"))
        _imshow(
            axes[1],
            v,
            t(language, "Vertical displacement v", "Вертикальное перемещение v"),
            "coolwarm",
        )
        _imshow(axes[2], s.small_exx, t(language, "εxx", "εxx"), "coolwarm")
        _imshow(axes[3], s.small_exy, t(language, "εxy", "εxy"), "coolwarm")
        fig.suptitle(
            t(
                language,
                "Bending combines displacement curvature and strain gradients",
                "Изгиб сочетает кривизну перемещений и градиенты деформации",
            )
        )
        return fig

    _paired("bending_field", builder)


def heterogeneous_field():
    ref, deformed, u, v = _base_pair(44)
    result = run_subset_dic(
        ref, deformed, DICParameters(subset_radius=11, step=14, search_radius=6), 0.5
    )
    tu = sample_truth_on_dic_grid(u, result)
    tv = sample_truth_on_dic_grid(v, result)

    def builder(language):
        fig, axes = plt.subplots(2, 3, figsize=(13, 8))
        arrays = [tu, result.u, result.u - tu, tv, result.v, result.v - tv]
        titles = [
            ("true u", "истинное u"),
            ("DIC u", "DIC u"),
            ("u error", "ошибка u"),
            ("true v", "истинное v"),
            ("DIC v", "DIC v"),
            ("v error", "ошибка v"),
        ]
        for ax, a, title in zip(axes.ravel(), arrays, titles):
            im = ax.imshow(a, cmap="coolwarm")
            ax.set_title(t(language, *title))
            fig.colorbar(im, ax=ax, shrink=0.72)
        fig.suptitle(
            t(
                language,
                "Local translation DIC approximates smoothly heterogeneous motion",
                "Локальный трансляционный DIC приближает плавно неоднородное движение",
            )
        )
        return fig

    _paired("heterogeneous_field", builder)


def _translation_error_for(ref, noise=0.0, subset=9, step=18, radius=1.8, order=3):
    if radius != 1.8:
        ref = generate_speckle_pattern(
            ref.shape, SpeckleParameters(seed=51, radius_mean=radius, density=0.035)
        )
    u = np.full_like(ref, 2.4)
    v = np.full_like(ref, -1.3)
    deformed = warp_image(ref, u, v, interpolation_order=order, noise_std=noise, seed=9)
    res = run_subset_dic(
        ref, deformed, DICParameters(subset_radius=subset, step=step, search_radius=5), 0.20
    )
    tu = sample_truth_on_dic_grid(u, res)
    tv = sample_truth_on_dic_grid(v, res)
    if not np.any(res.valid):
        return float("nan"), 0.0
    return dic_metrics(res.u, res.v, tu, tv, res.valid)["vector_rmse"], np.mean(res.valid)


def subset_size_sweep():
    ref = generate_speckle_pattern((120, 128), SpeckleParameters(seed=51))
    values = np.array([5, 7, 9, 11, 13, 15])
    errors = []
    cover = []
    for value in values:
        e, c = _translation_error_for(ref, noise=0.012, subset=int(value), step=18)
        errors.append(e)
        cover.append(c)

    def builder(language):
        fig, ax1 = plt.subplots(figsize=(8, 5))
        ax1.plot(2 * values + 1, errors, "o-", label=t(language, "RMSE", "СКО"))
        ax1.set_xlabel(t(language, "subset width [px]", "ширина подобласти [пикс.]"))
        ax1.set_ylabel(t(language, "displacement RMSE [px]", "СКО перемещения [пикс.]"))
        ax2 = ax1.twinx()
        ax2.plot(2 * values + 1, cover, "s--", label=t(language, "coverage", "покрытие"))
        ax2.set_ylabel(t(language, "valid fraction", "доля валидных точек"))
        fig.suptitle(
            t(
                language,
                "Subset size trades spatial resolution for robustness",
                "Размер подобласти задаёт компромисс разрешения и устойчивости",
            )
        )
        return fig

    _paired("subset_size_sweep", builder)


def step_size_sweep():
    ref = generate_speckle_pattern((120, 128), SpeckleParameters(seed=52))
    values = np.array([6, 8, 10, 14, 18, 24])
    points = []
    runtime_proxy = []
    for step in values:
        res = run_subset_dic(
            ref,
            warp_image(ref, np.full_like(ref, 2.0), np.full_like(ref, -1.0)),
            DICParameters(subset_radius=9, step=int(step), search_radius=4),
            0.5,
        )
        points.append(np.count_nonzero(res.valid))
        runtime_proxy.append(res.u.size * (2 * 4 + 1) ** 2)

    def builder(language):
        fig, axes = plt.subplots(1, 2, figsize=(10, 4))
        axes[0].plot(values, points, "o-")
        axes[0].set_xlabel(t(language, "step [px]", "шаг [пикс.]"))
        axes[0].set_ylabel(t(language, "valid subsets", "валидные подобласти"))
        axes[0].set_title(t(language, "Sampling density", "Плотность выборки"))
        axes[1].plot(values, runtime_proxy, "s-")
        axes[1].set_yscale("log")
        axes[1].set_xlabel(t(language, "step [px]", "шаг [пикс.]"))
        axes[1].set_ylabel(t(language, "relative work", "относительная работа"))
        axes[1].set_title(
            t(language, "Computational cost proxy", "Оценка вычислительной стоимости")
        )
        fig.suptitle(
            t(
                language,
                "Step size controls field density, not subset information",
                "Шаг определяет плотность поля, а не информативность подобласти",
            )
        )
        return fig

    _paired("step_size_sweep", builder)


def speckle_size_sweep():
    base = np.zeros((112, 120))
    values = np.array([0.8, 1.2, 1.8, 2.5, 3.4])
    errors = []
    for r in values:
        errors.append(
            _translation_error_for(base, noise=0.01, radius=float(r), subset=9, step=18)[0]
        )

    def builder(language):
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(values, errors, "o-")
        ax.set_xlabel(t(language, "mean speckle radius [px]", "средний радиус спекла [пикс.]"))
        ax.set_ylabel(t(language, "displacement RMSE [px]", "СКО перемещения [пикс.]"))
        ax.set_title(
            t(
                language,
                "Speckle scale must be compatible with subset scale",
                "Масштаб спеклов должен соответствовать масштабу подобласти",
            )
        )
        return fig

    _paired("speckle_size_sweep", builder)


def noise_sweep():
    ref = generate_speckle_pattern((112, 120), SpeckleParameters(seed=53))
    values = np.array([0, 0.005, 0.01, 0.02, 0.04, 0.07])
    errors = []
    cover = []
    for n in values:
        e, c = _translation_error_for(ref, noise=float(n), subset=10, step=18)
        errors.append(e)
        cover.append(c)

    def builder(language):
        fig, axes = plt.subplots(1, 2, figsize=(10, 4))
        axes[0].plot(values, errors, "o-")
        axes[0].set_xlabel(t(language, "noise standard deviation", "стандартное отклонение шума"))
        axes[0].set_ylabel(t(language, "RMSE [px]", "СКО [пикс.]"))
        axes[0].set_title(t(language, "Accuracy", "Точность"))
        axes[1].plot(values, cover, "s-")
        axes[1].set_xlabel(t(language, "noise standard deviation", "стандартное отклонение шума"))
        axes[1].set_ylabel(t(language, "valid fraction", "доля валидных точек"))
        axes[1].set_title(t(language, "Coverage", "Покрытие"))
        fig.suptitle(
            t(
                language,
                "Noise affects both displacement error and measurement availability",
                "Шум влияет и на ошибку, и на доступность измерений",
            )
        )
        return fig

    _paired("noise_sweep", builder)


def interpolation_order():
    ref = generate_speckle_pattern((112, 120), SpeckleParameters(seed=54))
    orders = np.arange(0, 6)
    errors = []
    for order in orders:
        errors.append(_translation_error_for(ref, noise=0, subset=10, step=18, order=int(order))[0])

    def builder(language):
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar(orders, errors)
        ax.set_xlabel(
            t(language, "warping interpolation order", "порядок интерполяции при деформировании")
        )
        ax.set_ylabel(
            t(
                language,
                "recovered displacement RMSE [px]",
                "СКО восстановленного перемещения [пикс.]",
            )
        )
        ax.set_title(
            t(
                language,
                "Synthetic benchmark depends on the image interpolation model",
                "Синтетический benchmark зависит от модели интерполяции изображения",
            )
        )
        return fig

    _paired("interpolation_order", builder)


def strain_smoothing():
    shape = (128, 140)
    yy, xx = np.indices(shape, dtype=float)
    u = 0.025 * xx + 0.004 * np.sin(xx / 8)
    v = -0.01 * yy
    rng = np.random.default_rng(2)
    noisy_u = u + rng.normal(0, 0.08, shape)
    noisy_v = v + rng.normal(0, 0.08, shape)
    sigmas = [0, 0.6, 1.2, 2.0]

    def builder(language):
        fig, axes = plt.subplots(1, 4, figsize=(14, 3.8))
        for ax, sigma in zip(axes, sigmas):
            e = strain_fields(noisy_u, noisy_v, smoothing_sigma=sigma).small_exx
            im = ax.imshow(e, cmap="coolwarm", vmin=0.005, vmax=0.045)
            ax.set_title(t(language, f"σ = {sigma}", f"σ = {sigma}"))
            ax.set_xticks([])
            ax.set_yticks([])
        fig.colorbar(im, ax=axes.ravel().tolist(), shrink=0.75, label="εxx")
        fig.suptitle(
            t(
                language,
                "Differentiation amplifies noise; smoothing introduces spatial bias",
                "Дифференцирование усиливает шум, а сглаживание создаёт пространственное смещение",
            )
        )
        return fig

    _paired("strain_smoothing", builder)


def forward_backward():
    ref = generate_speckle_pattern((120, 128), SpeckleParameters(seed=61))
    u = np.full_like(ref, 2.2)
    v = np.full_like(ref, -1.1)
    deformed = warp_image(ref, u, v, noise_std=0.015, seed=5)
    p = DICParameters(subset_radius=10, step=16, search_radius=5)
    f = run_subset_dic(ref, deformed, p, 0.45)
    b = run_subset_dic(deformed, ref, p, 0.45)
    error = forward_backward_error(f, b)

    def builder(language):
        fig, axes = plt.subplots(1, 3, figsize=(12, 4))
        im = axes[0].imshow(f.correlation, cmap="viridis", vmin=0.5, vmax=1)
        axes[0].set_title(t(language, "Forward ZNCC", "Прямой ZNCC"))
        fig.colorbar(im, ax=axes[0])
        im = axes[1].imshow(b.correlation, cmap="viridis", vmin=0.5, vmax=1)
        axes[1].set_title(t(language, "Backward ZNCC", "Обратный ZNCC"))
        fig.colorbar(im, ax=axes[1])
        im = axes[2].imshow(error, cmap="magma")
        axes[2].set_title(
            t(language, "Forward–backward error [px]", "Прямо-обратная ошибка [пикс.]")
        )
        fig.colorbar(im, ax=axes[2])
        fig.suptitle(
            t(
                language,
                "Consistency is a diagnostic, not a proof of accuracy",
                "Согласованность — диагностический признак, а не доказательство точности",
            )
        )
        return fig

    _paired("forward_backward", builder)


def illumination_change():
    ref = generate_speckle_pattern((120, 128), SpeckleParameters(seed=63))
    u = np.full_like(ref, 2.0)
    v = np.full_like(ref, -1.0)
    deformed = warp_image(ref, u, v, intensity_gain=0.72, intensity_offset=0.16)
    res = run_subset_dic(
        ref, deformed, DICParameters(subset_radius=10, step=16, search_radius=4), 0.45
    )

    def builder(language):
        fig, axes = plt.subplots(1, 3, figsize=(12, 4))
        _imshow(axes[0], ref, t(language, "Reference", "Исходное"))
        _imshow(axes[1], deformed, t(language, "Gain and offset changed", "Изменены gain и offset"))
        im = axes[2].imshow(res.correlation, cmap="viridis", vmin=0.5, vmax=1)
        axes[2].set_title(t(language, "ZNCC remains normalized", "ZNCC сохраняет нормировку"))
        fig.colorbar(im, ax=axes[2])
        fig.suptitle(
            t(
                language,
                "Zero normalization reduces sensitivity to linear intensity changes",
                "Нулевая нормировка снижает чувствительность к линейным изменениям интенсивности",
            )
        )
        return fig

    _paired("illumination_change", builder)


def boundary_effects():
    ref = generate_speckle_pattern((120, 128), SpeckleParameters(seed=64))
    yy, xx = np.indices(ref.shape, dtype=float)
    u = 4.5 * (xx / (ref.shape[1] - 1))
    v = np.zeros_like(u)
    deformed = warp_image(ref, u, v)
    res = run_subset_dic(
        ref, deformed, DICParameters(subset_radius=10, step=12, search_radius=5), 0.4
    )
    err = np.abs(res.u - sample_truth_on_dic_grid(u, res))

    def builder(language):
        fig, axes = plt.subplots(1, 3, figsize=(12, 4))
        _imshow(axes[0], deformed, t(language, "Deformed image", "Деформированное изображение"))
        im = axes[1].imshow(res.correlation, cmap="viridis", vmin=0.4, vmax=1)
        axes[1].set_title(t(language, "Correlation quality", "Качество корреляции"))
        fig.colorbar(im, ax=axes[1])
        im = axes[2].imshow(err, cmap="magma")
        axes[2].set_title(t(language, "Absolute u error", "Абсолютная ошибка u"))
        fig.colorbar(im, ax=axes[2])
        fig.suptitle(
            t(
                language,
                "Finite subsets and search windows create unavoidable boundary losses",
                "Конечные подобласти и окна поиска создают неизбежные потери у границ",
            )
        )
        return fig

    _paired("boundary_effects", builder)


def discontinuity_failure():
    ref = generate_speckle_pattern((128, 144), SpeckleParameters(seed=66))
    u, v = displacement_field(ref.shape, "localization", 5.5)
    deformed = warp_image(ref, u, v)  # create an intensity discontinuity mimicking crack opening
    deformed[:, 70:74] = 1.0
    res = run_subset_dic(
        ref, deformed, DICParameters(subset_radius=10, step=12, search_radius=6), 0.35
    )
    err = np.abs(res.u - sample_truth_on_dic_grid(u, res))

    def builder(language):
        fig, axes = plt.subplots(1, 4, figsize=(14, 4))
        _imshow(
            axes[0], deformed, t(language, "Image with discontinuity", "Изображение с разрывом")
        )
        im = axes[1].imshow(res.u, cmap="coolwarm")
        axes[1].set_title(t(language, "Recovered u", "Восстановленное u"))
        fig.colorbar(im, ax=axes[1])
        im = axes[2].imshow(res.correlation, cmap="viridis", vmin=0.3, vmax=1)
        axes[2].set_title(t(language, "ZNCC", "ZNCC"))
        fig.colorbar(im, ax=axes[2])
        im = axes[3].imshow(err, cmap="magma")
        axes[3].set_title(t(language, "u error", "ошибка u"))
        fig.colorbar(im, ax=axes[3])
        fig.suptitle(
            t(
                language,
                "A smooth subset model fails when displacement is discontinuous inside the subset",
                "Гладкая модель подобласти нарушается при разрыве перемещений внутри подобласти",
            )
        )
        return fig

    _paired("discontinuity_failure", builder)


def natural_texture():
    ref = generate_natural_texture((128, 144), seed=68)
    u = np.full_like(ref, 1.8)
    v = np.full_like(ref, -1.2)
    deformed = warp_image(ref, u, v, noise_std=0.008, seed=3)
    res = run_subset_dic(
        ref, deformed, DICParameters(subset_radius=12, step=16, search_radius=4), 0.35
    )
    err = np.hypot(res.u - 1.8, res.v + 1.2)

    def builder(language):
        fig, axes = plt.subplots(1, 4, figsize=(14, 4))
        _imshow(
            axes[0], ref, t(language, "Natural-texture surrogate", "Суррогат естественной текстуры")
        )
        _imshow(axes[1], deformed, t(language, "Deformed", "Деформированное"))
        im = axes[2].imshow(res.correlation, cmap="viridis", vmin=0.3, vmax=1)
        axes[2].set_title(t(language, "Correlation", "Корреляция"))
        fig.colorbar(im, ax=axes[2])
        im = axes[3].imshow(err, cmap="magma")
        axes[3].set_title(t(language, "Vector error [px]", "Векторная ошибка [пикс.]"))
        fig.colorbar(im, ax=axes[3])
        fig.suptitle(
            t(
                language,
                "Marker-free analysis is possible only where natural texture is informative",
                "Безмаркерный анализ возможен только при информативной естественной текстуре",
            )
        )
        return fig

    _paired("natural_texture", builder)


def dataset_schema():
    ref, deformed, u, v = _base_pair(71, (96, 112))
    path = export_dic_dataset(
        DATA_DIRECTORY / "example_dic_dataset.npz",
        ref,
        deformed,
        u,
        v,
        {"seed": 71, "pixel_size_um": 8.0, "loading_mode": "synthetic heterogeneous"},
    )
    schema = [
        ("reference", "2D grayscale image", "2D полутоновое изображение"),
        ("deformed", "2D grayscale image", "2D полутоновое изображение"),
        ("u, v", "ground-truth displacement [px]", "ground-truth перемещение [пикс.]"),
        ("metadata_json", "provenance and units", "происхождение и единицы"),
    ]

    def builder(language):
        fig, ax = plt.subplots(figsize=(10, 5.2))
        ax.axis("off")
        cell_text = [[name, t(language, en, ru)] for name, en, ru in schema]
        table = ax.table(
            cellText=cell_text,
            colLabels=[t(language, "Field", "Поле"), t(language, "Meaning", "Смысл")],
            loc="center",
            cellLoc="left",
        )
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 1.8)
        ax.set_title(
            t(language, "Synthetic DIC dataset schema", "Схема синтетического DIC-датасета")
        )
        ax.text(
            0.5,
            0.08,
            t(language, f"Saved: {path.name}", f"Сохранено: {path.name}"),
            ha="center",
            transform=ax.transAxes,
        )
        return fig

    _paired("dataset_schema", builder)


def _benchmark_rows():
    rows = []
    ref = generate_speckle_pattern((128, 136), SpeckleParameters(seed=80))
    u = np.full_like(ref, 2.6)
    v = np.full_like(ref, -1.4)
    deformed = warp_image(ref, u, v)
    res = run_subset_dic(
        ref, deformed, DICParameters(subset_radius=11, step=17, search_radius=5), 0.6
    )
    tu = sample_truth_on_dic_grid(u, res)
    tv = sample_truth_on_dic_grid(v, res)
    metrics = dic_metrics(res.u, res.v, tu, tv, res.valid)
    rows.append(
        ("translation_vector_rmse", metrics["vector_rmse"], 0.25, metrics["vector_rmse"] < 0.25)
    )
    yy, xx = np.indices((80, 90), dtype=float)
    af_u = 0.025 * xx + 0.01 * yy
    af_v = -0.008 * xx + 0.018 * yy
    s = strain_fields(af_u, af_v)
    exx_err = abs(float(np.median(s.small_exx)) - 0.025)
    rows.append(("analytic_exx_error", exx_err, 1e-10, exx_err < 1e-10))
    p, score = refine_affine_subset(
        ref,
        warp_image(
            ref,
            0.016 * (np.indices(ref.shape)[1] - 68) + 1.0,
            -0.01 * (np.indices(ref.shape)[0] - 64) - 0.5,
        ),
        64,
        68,
        1.0,
        -0.5,
        14,
    )
    aff_err = abs(p[2] - 0.016)
    rows.append(("affine_du_dx_error", aff_err, 0.012, aff_err < 0.012))
    b = run_subset_dic(
        deformed, ref, DICParameters(subset_radius=11, step=17, search_radius=5), 0.6
    )
    fb = float(np.nanmedian(forward_backward_error(res, b)))
    rows.append(("forward_backward_median", fb, 0.35, fb < 0.35))
    noisy = warp_image(ref, u, v, noise_std=0.05, seed=1)
    noisy_res = run_subset_dic(
        ref, noisy, DICParameters(subset_radius=11, step=17, search_radius=5), 0.35
    )
    noisy_m = dic_metrics(
        noisy_res.u,
        noisy_res.v,
        sample_truth_on_dic_grid(u, noisy_res),
        sample_truth_on_dic_grid(v, noisy_res),
        noisy_res.valid,
    )
    degrade = noisy_m["vector_rmse"] > metrics["vector_rmse"]
    rows.append(
        (
            "noise_increases_error",
            float(noisy_m["vector_rmse"] - metrics["vector_rmse"]),
            0.0,
            degrade,
        )
    )
    rows.append(("affine_normalized_score", score, 0.9, score > 0.9))
    return rows


def benchmark_summary():
    rows = _benchmark_rows()
    path = DATA_DIRECTORY / "digital_image_correlation_benchmark.csv"
    path.write_text(
        "metric,value,threshold,passed\n"
        + "\n".join(f"{n},{v:.10g},{th:.10g},{str(p).lower()}" for n, v, th, p in rows)
        + "\n",
        encoding="utf-8",
    )

    def builder(language):
        fig, ax = plt.subplots(figsize=(10, 5.4))
        labels = [r[0].replace("_", " ") for r in rows]
        values = [max(abs(r[1] / r[2]) if r[2] != 0 else abs(r[1]), 1e-8) for r in rows]
        colors = ["#2a9d8f" if r[3] else "#d62828" for r in rows]
        ax.barh(labels, values, color=colors)
        ax.axvline(1, ls="--")
        ax.set_xscale("log")
        ax.set_xlabel(
            t(
                language,
                "normalized value (criterion at 1)",
                "нормированное значение (критерий при 1)",
            )
        )
        ax.set_title(
            t(
                language,
                "Synthetic DIC verification benchmark",
                "Верификационный benchmark синтетического DIC",
            )
        )
        return fig

    _paired("benchmark_summary", builder)


def dic_animation():
    ref = generate_speckle_pattern((96, 112), SpeckleParameters(seed=90, density=0.04))
    frames = []
    displacements = []
    for amp in np.linspace(0, 4.5, 13):
        u, v = displacement_field(ref.shape, "bending", float(amp))
        frames.append(warp_image(ref, u, v))
        displacements.append(np.hypot(u, v))
    for language in ("en", "ru"):
        fig, axes = plt.subplots(1, 2, figsize=(8, 4))
        im0 = axes[0].imshow(frames[0], cmap="gray", vmin=0, vmax=1)
        im1 = axes[1].imshow(
            displacements[0], cmap="viridis", vmin=0, vmax=np.max(displacements[-1])
        )
        axes[0].set_title(
            t(language, "Synthetic image sequence", "Синтетическая последовательность")
        )
        axes[1].set_title(
            t(language, "Exact displacement magnitude", "Точная величина перемещения")
        )
        [ax.set_axis_off() for ax in axes]

        def update(i):
            im0.set_data(frames[i])
            im1.set_data(displacements[i])
            fig.suptitle(t(language, f"Load step {i:02d}", f"Шаг нагружения {i:02d}"))
            return im0, im1

        anim = animation.FuncAnimation(fig, update, frames=len(frames), interval=180, blit=False)
        suffix = "" if language == "en" else "_ru"
        anim.save(
            ANIMATION_DIRECTORY / f"dic_sequence{suffix}.gif", writer="pillow", fps=5, dpi=100
        )
        plt.close(fig)


SCENARIOS = {
    "modeling taxonomy": modeling_taxonomy,
    "speckle gallery": speckle_gallery,
    "exact displacement fields": exact_displacement_fields,
    "reference and deformed pair": reference_deformed_pair,
    "correlation surface": correlation_surface_figure,
    "subpixel peak": subpixel_peak,
    "affine subset": affine_subset,
    "translation verification": translation_verification,
    "uniaxial strain recovery": uniaxial_strain_recovery,
    "shear and rotation": shear_rotation,
    "bending field": bending_field,
    "heterogeneous field": heterogeneous_field,
    "subset-size sweep": subset_size_sweep,
    "step-size sweep": step_size_sweep,
    "speckle-size sweep": speckle_size_sweep,
    "noise sweep": noise_sweep,
    "interpolation order": interpolation_order,
    "strain smoothing": strain_smoothing,
    "forward-backward consistency": forward_backward,
    "illumination change": illumination_change,
    "boundary effects": boundary_effects,
    "discontinuity failure": discontinuity_failure,
    "natural texture": natural_texture,
    "dataset schema": dataset_schema,
    "benchmark summary": benchmark_summary,
    "DIC animation": dic_animation,
}
