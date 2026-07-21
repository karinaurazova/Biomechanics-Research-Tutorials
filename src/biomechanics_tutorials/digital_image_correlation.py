"""Synthetic two-dimensional digital image correlation utilities.

The module is intentionally transparent and educational. It implements a
reproducible synthetic image generator, exact displacement fields, image
warping, local subset correlation, subpixel peak refinement, optional affine
subset refinement, strain recovery, verification metrics, and dataset export.
It is not intended to replace production DIC software such as Ncorr,
OpenCorr, or dedicated stereo-DIC systems.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Literal, Mapping

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy.interpolate import griddata
from scipy.ndimage import gaussian_filter, map_coordinates
from scipy.optimize import least_squares

FloatArray = NDArray[np.float64]


@dataclass(frozen=True)
class SpeckleParameters:
    """Parameters for a synthetic grayscale speckle pattern."""

    density: float = 0.035
    radius_mean: float = 1.8
    radius_std: float = 0.45
    contrast: float = 0.92
    background: float = 0.08
    blur_sigma: float = 0.55
    seed: int = 0

    def __post_init__(self) -> None:
        if not 0.0 < self.density < 0.5:
            raise ValueError("density must be between 0 and 0.5")
        if self.radius_mean <= 0.0 or self.radius_std < 0.0:
            raise ValueError("invalid speckle radii")
        if not 0.0 < self.contrast <= 1.0:
            raise ValueError("contrast must be in (0, 1]")
        if not 0.0 <= self.background < 1.0:
            raise ValueError("background must be in [0, 1)")
        if self.blur_sigma < 0.0:
            raise ValueError("blur_sigma must be non-negative")


@dataclass(frozen=True)
class DICParameters:
    """Parameters for a local translation-based subset DIC analysis."""

    subset_radius: int = 9
    step: int = 12
    search_radius: int = 6
    subpixel: bool = True
    strain_smoothing_sigma: float = 1.0
    interpolation_order: int = 3

    def __post_init__(self) -> None:
        if self.subset_radius < 3:
            raise ValueError("subset_radius must be at least 3 pixels")
        if self.step < 1:
            raise ValueError("step must be positive")
        if self.search_radius < 1:
            raise ValueError("search_radius must be positive")
        if self.strain_smoothing_sigma < 0.0:
            raise ValueError("strain_smoothing_sigma must be non-negative")
        if self.interpolation_order not in {0, 1, 2, 3, 4, 5}:
            raise ValueError("interpolation_order must be between 0 and 5")


@dataclass
class DICGridResult:
    """Sparse DIC output on a regular grid of subset centers."""

    x: FloatArray
    y: FloatArray
    u: FloatArray
    v: FloatArray
    correlation: FloatArray
    valid: NDArray[np.bool_]
    metadata: dict[str, object]


@dataclass
class StrainFields:
    """Small- and finite-strain measures on a dense grid."""

    du_dx: FloatArray
    du_dy: FloatArray
    dv_dx: FloatArray
    dv_dy: FloatArray
    small_exx: FloatArray
    small_eyy: FloatArray
    small_exy: FloatArray
    green_exx: FloatArray
    green_eyy: FloatArray
    green_exy: FloatArray
    jacobian: FloatArray


def _normalize_image(image: ArrayLike) -> FloatArray:
    array = np.asarray(image, dtype=float)
    finite = np.isfinite(array)
    if not np.any(finite):
        raise ValueError("image contains no finite values")
    low = float(np.nanmin(array))
    high = float(np.nanmax(array))
    if high - low < 1.0e-12:
        return np.zeros_like(array, dtype=float)
    return np.clip((array - low) / (high - low), 0.0, 1.0)


def generate_speckle_pattern(
    shape: tuple[int, int],
    parameters: SpeckleParameters | None = None,
) -> FloatArray:
    """Generate a reproducible grayscale pattern from random Gaussian speckles.

    Individual speckles have variable radii. The returned pattern is normalized
    to ``[0, 1]`` and has dark speckles on a bright background.
    """

    params = parameters or SpeckleParameters()
    height, width = map(int, shape)
    if height < 16 or width < 16:
        raise ValueError("shape must be at least 16 x 16")
    rng = np.random.default_rng(params.seed)
    yy, xx = np.indices((height, width), dtype=float)
    count = max(1, int(params.density * height * width))
    centers_x = rng.uniform(0.0, width - 1.0, count)
    centers_y = rng.uniform(0.0, height - 1.0, count)
    radii = np.clip(
        rng.normal(params.radius_mean, params.radius_std, count),
        0.35,
        4.0 * params.radius_mean,
    )
    amplitudes = rng.uniform(0.65, 1.0, count)
    dark = np.zeros((height, width), dtype=float)
    # Chunking avoids a large H x W x N allocation.
    for start in range(0, count, 96):
        stop = min(start + 96, count)
        dx = xx[..., None] - centers_x[start:stop]
        dy = yy[..., None] - centers_y[start:stop]
        rr = radii[start:stop]
        contribution = amplitudes[start:stop] * np.exp(
            -0.5 * (dx * dx + dy * dy) / np.maximum(rr * rr, 1.0e-12)
        )
        dark = np.maximum(dark, np.max(contribution, axis=-1))
    if params.blur_sigma > 0.0:
        dark = gaussian_filter(dark, params.blur_sigma, mode="reflect")
    pattern = 1.0 - params.contrast * _normalize_image(dark)
    pattern = params.background + (1.0 - params.background) * pattern
    return np.clip(pattern, 0.0, 1.0)


def generate_natural_texture(shape: tuple[int, int], seed: int = 0) -> FloatArray:
    """Generate a multiscale natural-texture surrogate for marker-free DIC."""

    rng = np.random.default_rng(seed)
    texture = np.zeros(shape, dtype=float)
    for sigma, weight in [(0.8, 0.35), (2.0, 0.30), (5.0, 0.22), (11.0, 0.13)]:
        texture += weight * gaussian_filter(rng.normal(size=shape), sigma, mode="reflect")
    yy, xx = np.indices(shape, dtype=float)
    texture += 0.12 * np.sin(0.035 * xx + 0.024 * yy)
    return _normalize_image(texture)


def displacement_field(
    shape: tuple[int, int],
    kind: Literal[
        "translation",
        "uniaxial",
        "biaxial",
        "shear",
        "rotation",
        "bending",
        "heterogeneous",
        "localization",
    ] = "translation",
    amplitude: float = 3.0,
) -> tuple[FloatArray, FloatArray]:
    """Return exact pixel displacement fields for synthetic verification.

    Coordinates are centered and normalized by image size for all deformation
    modes except translation. ``u`` acts along image columns and ``v`` along
    image rows.
    """

    height, width = map(int, shape)
    yy, xx = np.indices((height, width), dtype=float)
    cx = 0.5 * (width - 1)
    cy = 0.5 * (height - 1)
    xn = (xx - cx) / max(width - 1, 1)
    yn = (yy - cy) / max(height - 1, 1)
    if kind == "translation":
        u = np.full(shape, amplitude, dtype=float)
        v = np.full(shape, -0.55 * amplitude, dtype=float)
    elif kind == "uniaxial":
        u = amplitude * xn
        v = -0.30 * amplitude * yn
    elif kind == "biaxial":
        u = amplitude * xn
        v = 0.72 * amplitude * yn
    elif kind == "shear":
        u = amplitude * yn
        v = np.zeros(shape, dtype=float)
    elif kind == "rotation":
        angle = amplitude / max(height, width)
        u = -angle * (yy - cy)
        v = angle * (xx - cx)
    elif kind == "bending":
        u = 0.45 * amplitude * yn
        v = amplitude * (xn * xn - np.mean(xn * xn))
    elif kind == "heterogeneous":
        u = amplitude * (0.55 * xn + 0.22 * np.sin(2.0 * np.pi * yn))
        v = amplitude * (-0.25 * yn + 0.16 * np.sin(2.0 * np.pi * xn))
    elif kind == "localization":
        width_band = 0.09
        transition = np.tanh(xn / width_band)
        u = 0.5 * amplitude * transition
        v = 0.12 * amplitude * np.sin(2.0 * np.pi * yn) * np.exp(-(xn / 0.22) ** 2)
    else:
        raise ValueError(f"unknown displacement-field kind: {kind}")
    return np.asarray(u, dtype=float), np.asarray(v, dtype=float)


def _sample_field(field: FloatArray, y: FloatArray, x: FloatArray) -> FloatArray:
    return map_coordinates(field, [y, x], order=1, mode="nearest", prefilter=False)


def inverse_deformation_coordinates(
    u: ArrayLike,
    v: ArrayLike,
    iterations: int = 8,
) -> tuple[FloatArray, FloatArray]:
    """Approximate the inverse map for a displacement field by fixed-point iteration."""

    u_field = np.asarray(u, dtype=float)
    v_field = np.asarray(v, dtype=float)
    if u_field.shape != v_field.shape or u_field.ndim != 2:
        raise ValueError("u and v must be equal-shaped two-dimensional arrays")
    yy, xx = np.indices(u_field.shape, dtype=float)
    x_ref = xx.copy()
    y_ref = yy.copy()
    for _ in range(max(1, int(iterations))):
        u_sample = _sample_field(u_field, y_ref, x_ref)
        v_sample = _sample_field(v_field, y_ref, x_ref)
        x_ref = xx - u_sample
        y_ref = yy - v_sample
    return x_ref, y_ref


def warp_image(
    reference: ArrayLike,
    u: ArrayLike,
    v: ArrayLike,
    interpolation_order: int = 3,
    intensity_gain: float = 1.0,
    intensity_offset: float = 0.0,
    noise_std: float = 0.0,
    blur_sigma: float = 0.0,
    seed: int = 0,
) -> FloatArray:
    """Generate a deformed image by inverse warping the reference image."""

    image = np.asarray(reference, dtype=float)
    u_field = np.asarray(u, dtype=float)
    v_field = np.asarray(v, dtype=float)
    if image.shape != u_field.shape or image.shape != v_field.shape:
        raise ValueError("reference, u, and v must have equal shape")
    if interpolation_order not in {0, 1, 2, 3, 4, 5}:
        raise ValueError("interpolation_order must be between 0 and 5")
    if noise_std < 0.0 or blur_sigma < 0.0:
        raise ValueError("noise_std and blur_sigma must be non-negative")
    x_ref, y_ref = inverse_deformation_coordinates(u_field, v_field)
    deformed = map_coordinates(
        image,
        [y_ref, x_ref],
        order=interpolation_order,
        mode="reflect",
        prefilter=interpolation_order > 1,
    )
    if blur_sigma > 0.0:
        deformed = gaussian_filter(deformed, blur_sigma, mode="reflect")
    deformed = intensity_gain * deformed + intensity_offset
    if noise_std > 0.0:
        rng = np.random.default_rng(seed)
        deformed += rng.normal(0.0, noise_std, size=deformed.shape)
    return np.clip(deformed, 0.0, 1.0)


def zncc(reference_subset: ArrayLike, deformed_subset: ArrayLike) -> float:
    """Zero-normalized cross-correlation coefficient."""

    first = np.asarray(reference_subset, dtype=float)
    second = np.asarray(deformed_subset, dtype=float)
    if first.shape != second.shape:
        raise ValueError("subsets must have equal shape")
    a = first - np.mean(first)
    b = second - np.mean(second)
    denominator = float(np.sqrt(np.sum(a * a) * np.sum(b * b)))
    if denominator < 1.0e-14:
        return float("nan")
    return float(np.sum(a * b) / denominator)


def znssd(reference_subset: ArrayLike, deformed_subset: ArrayLike) -> float:
    """Zero-normalized sum of squared differences."""

    first = np.asarray(reference_subset, dtype=float)
    second = np.asarray(deformed_subset, dtype=float)
    if first.shape != second.shape:
        raise ValueError("subsets must have equal shape")
    a = first - np.mean(first)
    b = second - np.mean(second)
    norm_a = float(np.linalg.norm(a))
    norm_b = float(np.linalg.norm(b))
    if norm_a < 1.0e-14 or norm_b < 1.0e-14:
        return float("nan")
    residual = a / norm_a - b / norm_b
    return float(np.sum(residual * residual))


def _extract_integer_patch(image: FloatArray, cy: int, cx: int, radius: int) -> FloatArray:
    return image[cy - radius : cy + radius + 1, cx - radius : cx + radius + 1]


def correlation_surface(
    reference: ArrayLike,
    deformed: ArrayLike,
    center_y: int,
    center_x: int,
    subset_radius: int,
    search_radius: int,
) -> tuple[FloatArray, NDArray[np.int64], NDArray[np.int64]]:
    """Compute an integer-shift ZNCC surface for one subset."""

    ref = np.asarray(reference, dtype=float)
    deformed_array = np.asarray(deformed, dtype=float)
    if ref.shape != deformed_array.shape or ref.ndim != 2:
        raise ValueError("images must be equal-shaped two-dimensional arrays")
    margin = subset_radius + search_radius
    if not (margin <= center_y < ref.shape[0] - margin):
        raise ValueError("subset center is too close to the vertical boundary")
    if not (margin <= center_x < ref.shape[1] - margin):
        raise ValueError("subset center is too close to the horizontal boundary")
    reference_patch = _extract_integer_patch(ref, center_y, center_x, subset_radius)
    shifts = np.arange(-search_radius, search_radius + 1, dtype=int)
    scores = np.empty((shifts.size, shifts.size), dtype=float)
    for iy, dv in enumerate(shifts):
        for ix, du in enumerate(shifts):
            candidate = _extract_integer_patch(
                deformed_array,
                center_y + int(dv),
                center_x + int(du),
                subset_radius,
            )
            scores[iy, ix] = zncc(reference_patch, candidate)
    return scores, shifts.copy(), shifts.copy()


def quadratic_subpixel_peak(values_minus: float, values_center: float, values_plus: float) -> float:
    """Return the offset of a parabolic peak relative to the center sample."""

    denominator = values_minus - 2.0 * values_center + values_plus
    if abs(denominator) < 1.0e-14:
        return 0.0
    offset = 0.5 * (values_minus - values_plus) / denominator
    return float(np.clip(offset, -1.0, 1.0))


def estimate_subset_displacement(
    reference: ArrayLike,
    deformed: ArrayLike,
    center_y: int,
    center_x: int,
    subset_radius: int = 9,
    search_radius: int = 6,
    subpixel: bool = True,
) -> tuple[float, float, float]:
    """Estimate local translation and return ``(u, v, peak_zncc)``."""

    scores, u_shifts, v_shifts = correlation_surface(
        reference,
        deformed,
        center_y,
        center_x,
        subset_radius,
        search_radius,
    )
    if not np.any(np.isfinite(scores)):
        return float("nan"), float("nan"), float("nan")
    iy, ix = np.unravel_index(np.nanargmax(scores), scores.shape)
    u = float(u_shifts[ix])
    v = float(v_shifts[iy])
    if subpixel and 0 < ix < scores.shape[1] - 1:
        u += quadratic_subpixel_peak(scores[iy, ix - 1], scores[iy, ix], scores[iy, ix + 1])
    if subpixel and 0 < iy < scores.shape[0] - 1:
        v += quadratic_subpixel_peak(scores[iy - 1, ix], scores[iy, ix], scores[iy + 1, ix])
    return u, v, float(scores[iy, ix])


def _sample_affine_subset(
    image: FloatArray,
    center_y: float,
    center_x: float,
    subset_radius: int,
    parameters: FloatArray,
) -> FloatArray:
    """Sample an affine-warped subset from the deformed image."""

    u0, v0, du_dx, du_dy, dv_dx, dv_dy = parameters
    local = np.arange(-subset_radius, subset_radius + 1, dtype=float)
    dy, dx = np.meshgrid(local, local, indexing="ij")
    x = center_x + dx + u0 + du_dx * dx + du_dy * dy
    y = center_y + dy + v0 + dv_dx * dx + dv_dy * dy
    return map_coordinates(image, [y, x], order=3, mode="reflect", prefilter=True)


def refine_affine_subset(
    reference: ArrayLike,
    deformed: ArrayLike,
    center_y: int,
    center_x: int,
    initial_u: float = 0.0,
    initial_v: float = 0.0,
    subset_radius: int = 9,
    max_nfev: int = 80,
) -> tuple[FloatArray, float]:
    """Refine a six-parameter affine subset shape with nonlinear least squares.

    Parameters are ``[u, v, du/dx, du/dy, dv/dx, dv/dy]``. The residual uses
    zero-mean, unit-norm subsets to reduce sensitivity to gain and offset.
    """

    ref = np.asarray(reference, dtype=float)
    deformed_array = np.asarray(deformed, dtype=float)
    patch = _extract_integer_patch(ref, center_y, center_x, subset_radius)
    patch_zero = patch - np.mean(patch)
    patch_norm = np.linalg.norm(patch_zero)
    if patch_norm < 1.0e-12:
        raise ValueError("reference subset lacks texture")
    target = patch_zero / patch_norm

    def residual(parameters: FloatArray) -> FloatArray:
        candidate = _sample_affine_subset(
            deformed_array,
            float(center_y),
            float(center_x),
            subset_radius,
            parameters,
        )
        candidate -= np.mean(candidate)
        norm = np.linalg.norm(candidate)
        if norm < 1.0e-12:
            return np.full(target.size, 10.0)
        return (target - candidate / norm).ravel()

    initial = np.array([initial_u, initial_v, 0.0, 0.0, 0.0, 0.0], dtype=float)
    result = least_squares(residual, initial, max_nfev=max_nfev, method="trf")
    score = 1.0 - 0.5 * float(np.sum(result.fun * result.fun))
    return np.asarray(result.x, dtype=float), score


def run_subset_dic(
    reference: ArrayLike,
    deformed: ArrayLike,
    parameters: DICParameters | None = None,
    correlation_threshold: float = 0.55,
) -> DICGridResult:
    """Run translation-based subset DIC on a regular grid."""

    params = parameters or DICParameters()
    ref = np.asarray(reference, dtype=float)
    deformed_array = np.asarray(deformed, dtype=float)
    if ref.shape != deformed_array.shape or ref.ndim != 2:
        raise ValueError("images must be equal-shaped two-dimensional arrays")
    margin = params.subset_radius + params.search_radius + 1
    ys = np.arange(margin, ref.shape[0] - margin, params.step, dtype=int)
    xs = np.arange(margin, ref.shape[1] - margin, params.step, dtype=int)
    grid_x, grid_y = np.meshgrid(xs.astype(float), ys.astype(float))
    u = np.full_like(grid_x, np.nan, dtype=float)
    v = np.full_like(grid_y, np.nan, dtype=float)
    correlation = np.full_like(grid_x, np.nan, dtype=float)
    for row, cy in enumerate(ys):
        for col, cx in enumerate(xs):
            local_u, local_v, score = estimate_subset_displacement(
                ref,
                deformed_array,
                int(cy),
                int(cx),
                subset_radius=params.subset_radius,
                search_radius=params.search_radius,
                subpixel=params.subpixel,
            )
            u[row, col] = local_u
            v[row, col] = local_v
            correlation[row, col] = score
    valid = np.isfinite(correlation) & (correlation >= correlation_threshold)
    u[~valid] = np.nan
    v[~valid] = np.nan
    return DICGridResult(
        x=grid_x,
        y=grid_y,
        u=u,
        v=v,
        correlation=correlation,
        valid=valid,
        metadata={
            "synthetic": True,
            "experimental_validation": False,
            "algorithm": "translation-subset-zncc-quadratic-subpixel",
            **asdict(params),
            "correlation_threshold": float(correlation_threshold),
        },
    )


def interpolate_sparse_field(
    result: DICGridResult,
    shape: tuple[int, int],
    method: Literal["linear", "nearest", "cubic"] = "linear",
) -> tuple[FloatArray, FloatArray]:
    """Interpolate sparse DIC displacement samples onto a dense image grid."""

    yy, xx = np.indices(shape, dtype=float)
    valid = result.valid & np.isfinite(result.u) & np.isfinite(result.v)
    if np.count_nonzero(valid) < 3:
        raise ValueError("not enough valid DIC points for interpolation")
    points = np.column_stack([result.x[valid], result.y[valid]])
    dense_u = griddata(points, result.u[valid], (xx, yy), method=method)
    dense_v = griddata(points, result.v[valid], (xx, yy), method=method)
    # Fill convex-hull gaps conservatively with nearest-neighbor values.
    nearest_u = griddata(points, result.u[valid], (xx, yy), method="nearest")
    nearest_v = griddata(points, result.v[valid], (xx, yy), method="nearest")
    dense_u = np.where(np.isfinite(dense_u), dense_u, nearest_u)
    dense_v = np.where(np.isfinite(dense_v), dense_v, nearest_v)
    return np.asarray(dense_u, dtype=float), np.asarray(dense_v, dtype=float)


def strain_fields(
    u: ArrayLike,
    v: ArrayLike,
    pixel_size: float = 1.0,
    smoothing_sigma: float = 0.0,
) -> StrainFields:
    """Compute displacement gradients, infinitesimal strain, and Green strain."""

    u_field = np.asarray(u, dtype=float)
    v_field = np.asarray(v, dtype=float)
    if u_field.shape != v_field.shape or u_field.ndim != 2:
        raise ValueError("u and v must be equal-shaped two-dimensional arrays")
    if pixel_size <= 0.0 or smoothing_sigma < 0.0:
        raise ValueError("invalid pixel_size or smoothing_sigma")
    if smoothing_sigma > 0.0:
        u_field = gaussian_filter(u_field, smoothing_sigma, mode="nearest")
        v_field = gaussian_filter(v_field, smoothing_sigma, mode="nearest")
    du_dy, du_dx = np.gradient(u_field, pixel_size, pixel_size, edge_order=2)
    dv_dy, dv_dx = np.gradient(v_field, pixel_size, pixel_size, edge_order=2)
    small_exx = du_dx
    small_eyy = dv_dy
    small_exy = 0.5 * (du_dy + dv_dx)
    f11 = 1.0 + du_dx
    f12 = du_dy
    f21 = dv_dx
    f22 = 1.0 + dv_dy
    green_exx = 0.5 * (f11 * f11 + f21 * f21 - 1.0)
    green_eyy = 0.5 * (f12 * f12 + f22 * f22 - 1.0)
    green_exy = 0.5 * (f11 * f12 + f21 * f22)
    jacobian = f11 * f22 - f12 * f21
    return StrainFields(
        du_dx=du_dx,
        du_dy=du_dy,
        dv_dx=dv_dx,
        dv_dy=dv_dy,
        small_exx=small_exx,
        small_eyy=small_eyy,
        small_exy=small_exy,
        green_exx=green_exx,
        green_eyy=green_eyy,
        green_exy=green_exy,
        jacobian=jacobian,
    )


def principal_strains_2d(
    exx: ArrayLike,
    eyy: ArrayLike,
    exy: ArrayLike,
) -> tuple[FloatArray, FloatArray, FloatArray]:
    """Return maximum/minimum principal strains and principal-axis angle."""

    exx_array = np.asarray(exx, dtype=float)
    eyy_array = np.asarray(eyy, dtype=float)
    exy_array = np.asarray(exy, dtype=float)
    mean = 0.5 * (exx_array + eyy_array)
    radius = np.sqrt((0.5 * (exx_array - eyy_array)) ** 2 + exy_array**2)
    maximum = mean + radius
    minimum = mean - radius
    angle = 0.5 * np.arctan2(2.0 * exy_array, exx_array - eyy_array)
    return maximum, minimum, angle


def forward_backward_error(
    forward: DICGridResult,
    backward: DICGridResult,
) -> FloatArray:
    """Approximate forward-backward consistency on equal DIC grids."""

    if forward.x.shape != backward.x.shape or not np.allclose(forward.x, backward.x):
        raise ValueError("forward and backward grids must match")
    return np.sqrt((forward.u + backward.u) ** 2 + (forward.v + backward.v) ** 2)


def virtual_extensometer(
    u: ArrayLike,
    v: ArrayLike,
    point_a: tuple[float, float],
    point_b: tuple[float, float],
) -> float:
    """Compute engineering strain between two tracked image points."""

    u_field = np.asarray(u, dtype=float)
    v_field = np.asarray(v, dtype=float)
    a = np.asarray(point_a, dtype=float)
    b = np.asarray(point_b, dtype=float)
    original = float(np.linalg.norm(b - a))
    if original <= 0.0:
        raise ValueError("extensometer points must be distinct")
    ua = _sample_field(u_field, np.array([a[1]]), np.array([a[0]]))[0]
    va = _sample_field(v_field, np.array([a[1]]), np.array([a[0]]))[0]
    ub = _sample_field(u_field, np.array([b[1]]), np.array([b[0]]))[0]
    vb = _sample_field(v_field, np.array([b[1]]), np.array([b[0]]))[0]
    deformed_a = a + np.array([ua, va])
    deformed_b = b + np.array([ub, vb])
    return float(np.linalg.norm(deformed_b - deformed_a) / original - 1.0)


def dic_metrics(
    estimated_u: ArrayLike,
    estimated_v: ArrayLike,
    truth_u: ArrayLike,
    truth_v: ArrayLike,
    mask: ArrayLike | None = None,
) -> dict[str, float]:
    """Return displacement error metrics for a common grid."""

    eu = np.asarray(estimated_u, dtype=float)
    ev = np.asarray(estimated_v, dtype=float)
    tu = np.asarray(truth_u, dtype=float)
    tv = np.asarray(truth_v, dtype=float)
    if not (eu.shape == ev.shape == tu.shape == tv.shape):
        raise ValueError("all displacement fields must have equal shape")
    valid = np.isfinite(eu) & np.isfinite(ev) & np.isfinite(tu) & np.isfinite(tv)
    if mask is not None:
        valid &= np.asarray(mask, dtype=bool)
    if not np.any(valid):
        raise ValueError("no valid samples")
    du = eu[valid] - tu[valid]
    dv = ev[valid] - tv[valid]
    magnitude = np.sqrt(du * du + dv * dv)
    return {
        "u_bias": float(np.mean(du)),
        "v_bias": float(np.mean(dv)),
        "vector_mae": float(np.mean(magnitude)),
        "vector_rmse": float(np.sqrt(np.mean(magnitude * magnitude))),
        "p95_vector_error": float(np.percentile(magnitude, 95.0)),
        "coverage": float(np.mean(valid)),
    }


def sample_truth_on_dic_grid(
    field: ArrayLike,
    result: DICGridResult,
) -> FloatArray:
    """Sample a dense ground-truth field at DIC subset centers."""

    array = np.asarray(field, dtype=float)
    return map_coordinates(array, [result.y, result.x], order=1, mode="nearest")


def export_dic_dataset(
    path: str | Path,
    reference: ArrayLike,
    deformed: ArrayLike,
    u: ArrayLike,
    v: ArrayLike,
    metadata: Mapping[str, object] | None = None,
) -> Path:
    """Export a compressed synthetic DIC dataset with embedded JSON metadata."""

    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "synthetic": True,
        "experimental_validation": False,
        "schema": "bmrt.synthetic-dic.v1",
        **dict(metadata or {}),
    }
    np.savez_compressed(
        destination,
        reference=np.asarray(reference, dtype=float),
        deformed=np.asarray(deformed, dtype=float),
        u=np.asarray(u, dtype=float),
        v=np.asarray(v, dtype=float),
        metadata_json=np.array(json.dumps(payload, sort_keys=True)),
    )
    return destination


def read_dic_metadata(path: str | Path) -> dict[str, object]:
    """Read JSON provenance from an exported synthetic DIC dataset."""

    with np.load(Path(path), allow_pickle=False) as data:
        return json.loads(str(data["metadata_json"].item()))
