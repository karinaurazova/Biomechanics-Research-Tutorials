"""Synthetic fibrous images and 2-D structure-tensor orientation analysis."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.ndimage import gaussian_filter


@dataclass(frozen=True)
class StructureTensorParameters:
    """Scales used to estimate image gradients and average their products."""

    gradient_sigma: float = 1.0
    integration_sigma: float = 3.0

    def validate(self) -> None:
        if self.gradient_sigma <= 0:
            raise ValueError("gradient_sigma must be positive")
        if self.integration_sigma < 0:
            raise ValueError("integration_sigma must be nonnegative")


def wrap_axial_radians(angle: np.ndarray | float) -> np.ndarray:
    """Wrap axial angles to [-pi/2, pi/2)."""

    values = np.asarray(angle, dtype=float)
    return (values + np.pi / 2.0) % np.pi - np.pi / 2.0


def axial_angle_difference(
    first: np.ndarray | float,
    second: np.ndarray | float,
) -> np.ndarray:
    """Return the signed shortest difference between two axial directions."""

    return 0.5 * np.arctan2(
        np.sin(2.0 * (np.asarray(first) - np.asarray(second))),
        np.cos(2.0 * (np.asarray(first) - np.asarray(second))),
    )


def weighted_axial_mean(
    angles: np.ndarray,
    weights: np.ndarray | None = None,
) -> tuple[float, float]:
    """Return axial mean direction and resultant length/order parameter."""

    angles = np.asarray(angles, dtype=float)
    if weights is None:
        weights = np.ones_like(angles)
    weights = np.asarray(weights, dtype=float)
    valid = np.isfinite(angles) & np.isfinite(weights) & (weights > 0)
    if not np.any(valid):
        return float("nan"), 0.0
    doubled = 2.0 * angles[valid]
    total_weight = np.sum(weights[valid])
    c = np.sum(weights[valid] * np.cos(doubled)) / total_weight
    s = np.sum(weights[valid] * np.sin(doubled)) / total_weight
    return float(0.5 * np.arctan2(s, c)), float(np.hypot(c, s))


def _coordinate_grid(shape: tuple[int, int]) -> tuple[np.ndarray, np.ndarray]:
    rows, columns = shape
    y, x = np.mgrid[0:rows, 0:columns]
    x = x - 0.5 * (columns - 1)
    y = y - 0.5 * (rows - 1)
    return x, y


def _periodic_ridges(phase: np.ndarray, spacing: float, width: float) -> np.ndarray:
    if spacing <= 0 or width <= 0:
        raise ValueError("spacing and width must be positive")
    distance = (phase + 0.5 * spacing) % spacing - 0.5 * spacing
    return np.exp(-0.5 * (distance / width) ** 2)


def _finish_image(
    ridges: np.ndarray,
    contrast: float,
    background: float,
    noise_std: float,
    seed: int,
    illumination: np.ndarray | None = None,
) -> np.ndarray:
    image = background + contrast * ridges
    if illumination is not None:
        image = image * illumination
    if noise_std > 0:
        image = image + np.random.default_rng(seed).normal(0.0, noise_std, image.shape)
    return np.clip(image, 0.0, 1.0)


def synthetic_parallel_fibers(
    shape: tuple[int, int] = (192, 192),
    angle_degrees: float = 25.0,
    spacing: float = 16.0,
    width: float = 2.4,
    contrast: float = 0.8,
    background: float = 0.1,
    noise_std: float = 0.0,
    seed: int = 0,
    illumination_gradient: float = 0.0,
) -> tuple[np.ndarray, np.ndarray]:
    """Create parallel bright ridges and their exact axial orientation field."""

    x, y = _coordinate_grid(shape)
    theta = np.deg2rad(angle_degrees)
    normal_coordinate = -np.sin(theta) * x + np.cos(theta) * y
    ridges = _periodic_ridges(normal_coordinate, spacing, width)
    illumination = None
    if illumination_gradient != 0:
        normalized_x = x / max(np.max(np.abs(x)), 1.0)
        illumination = 1.0 + illumination_gradient * normalized_x
    image = _finish_image(
        ridges,
        contrast,
        background,
        noise_std,
        seed,
        illumination,
    )
    truth = np.full(shape, wrap_axial_radians(theta), dtype=float)
    return image, truth


def synthetic_curved_fibers(
    shape: tuple[int, int] = (192, 256),
    amplitude: float = 18.0,
    wavelength: float = 150.0,
    spacing: float = 17.0,
    width: float = 2.3,
    noise_std: float = 0.02,
    seed: int = 1,
) -> tuple[np.ndarray, np.ndarray]:
    """Create sinusoidally curved parallel fibers with an analytical tangent field."""

    x, y = _coordinate_grid(shape)
    wave_number = 2.0 * np.pi / wavelength
    phase = y - amplitude * np.sin(wave_number * x)
    ridges = _periodic_ridges(phase, spacing, width)
    slope = amplitude * wave_number * np.cos(wave_number * x)
    truth = wrap_axial_radians(np.arctan(slope))
    image = _finish_image(ridges, 0.82, 0.08, noise_std, seed)
    return image, truth


def synthetic_fan_fibers(
    shape: tuple[int, int] = (192, 192),
    rays: int = 18,
    width_radians: float = 0.035,
    noise_std: float = 0.015,
    seed: int = 2,
) -> tuple[np.ndarray, np.ndarray]:
    """Create a radial fan of fibers around an off-image virtual origin."""

    rows, columns = shape
    y, x = np.mgrid[0:rows, 0:columns]
    origin_x = 0.5 * (columns - 1)
    origin_y = 1.3 * rows
    dx = x - origin_x
    dy = y - origin_y
    polar = np.arctan2(dy, dx)
    angular_spacing = np.pi / rays
    distance = (polar + 0.5 * angular_spacing) % angular_spacing - 0.5 * angular_spacing
    ridges = np.exp(-0.5 * (distance / width_radians) ** 2)
    truth = wrap_axial_radians(polar)
    image = _finish_image(ridges, 0.8, 0.08, noise_std, seed)
    return image, truth


def synthetic_piecewise_fibers(
    shape: tuple[int, int] = (192, 256),
    left_angle_degrees: float = -30.0,
    right_angle_degrees: float = 35.0,
    transition_width: float = 0.0,
    noise_std: float = 0.02,
    seed: int = 3,
) -> tuple[np.ndarray, np.ndarray]:
    """Create two orientation domains separated by a vertical transition."""

    left, left_truth = synthetic_parallel_fibers(
        shape, left_angle_degrees, noise_std=0.0, seed=seed
    )
    right, right_truth = synthetic_parallel_fibers(
        shape, right_angle_degrees, noise_std=0.0, seed=seed
    )
    columns = shape[1]
    coordinate = np.arange(columns) - 0.5 * (columns - 1)
    if transition_width <= 0:
        blend = (coordinate >= 0).astype(float)
    else:
        blend = 0.5 * (1.0 + np.tanh(coordinate / transition_width))
    blend = np.broadcast_to(blend, shape)
    image = (1.0 - blend) * left + blend * right
    truth = np.where(blend < 0.5, left_truth, right_truth)
    if noise_std > 0:
        image = image + np.random.default_rng(seed).normal(0.0, noise_std, shape)
    return np.clip(image, 0.0, 1.0), truth


def synthetic_crossing_fibers(
    shape: tuple[int, int] = (192, 192),
    angle_a_degrees: float = -40.0,
    angle_b_degrees: float = 40.0,
    noise_std: float = 0.015,
    seed: int = 4,
) -> tuple[np.ndarray, tuple[float, float]]:
    """Create two superposed fiber families; no unique single-angle truth exists."""

    first, _ = synthetic_parallel_fibers(
        shape, angle_a_degrees, spacing=18.0, width=2.1, contrast=0.55, background=0.02
    )
    second, _ = synthetic_parallel_fibers(
        shape, angle_b_degrees, spacing=18.0, width=2.1, contrast=0.55, background=0.02
    )
    image = np.clip(first + second, 0.0, 1.0)
    if noise_std > 0:
        image = image + np.random.default_rng(seed).normal(0.0, noise_std, shape)
    return np.clip(image, 0.0, 1.0), (
        float(wrap_axial_radians(np.deg2rad(angle_a_degrees))),
        float(wrap_axial_radians(np.deg2rad(angle_b_degrees))),
    )


def structure_tensor_orientation(
    image: np.ndarray,
    parameters: StructureTensorParameters | None = None,
) -> dict[str, np.ndarray]:
    """Estimate local fiber orientation, coherence, energy, and tensor entries."""

    if parameters is None:
        parameters = StructureTensorParameters()
    parameters.validate()
    image = np.asarray(image, dtype=float)
    if image.ndim != 2:
        raise ValueError("image must be a two-dimensional array")

    sigma_g = parameters.gradient_sigma
    sigma_i = parameters.integration_sigma
    gradient_x = gaussian_filter(image, sigma_g, order=(0, 1), mode="reflect")
    gradient_y = gaussian_filter(image, sigma_g, order=(1, 0), mode="reflect")
    jxx = gaussian_filter(gradient_x * gradient_x, sigma_i, mode="reflect")
    jxy = gaussian_filter(gradient_x * gradient_y, sigma_i, mode="reflect")
    jyy = gaussian_filter(gradient_y * gradient_y, sigma_i, mode="reflect")

    discriminant = np.sqrt(np.maximum((jxx - jyy) ** 2 + 4.0 * jxy**2, 0.0))
    lambda_max = 0.5 * (jxx + jyy + discriminant)
    lambda_min = 0.5 * (jxx + jyy - discriminant)
    gradient_angle = 0.5 * np.arctan2(2.0 * jxy, jxx - jyy)
    fiber_angle = wrap_axial_radians(gradient_angle + np.pi / 2.0)
    energy = lambda_max + lambda_min
    coherence = (lambda_max - lambda_min) / np.maximum(energy, np.finfo(float).eps)

    return {
        "orientation": fiber_angle,
        "coherence": np.clip(coherence, 0.0, 1.0),
        "energy": energy,
        "lambda_max": lambda_max,
        "lambda_min": lambda_min,
        "jxx": jxx,
        "jxy": jxy,
        "jyy": jyy,
        "gradient_x": gradient_x,
        "gradient_y": gradient_y,
    }


def confidence_mask(
    result: dict[str, np.ndarray],
    coherence_threshold: float = 0.35,
    energy_quantile: float = 0.15,
    border: int = 0,
) -> np.ndarray:
    """Create a mask from local coherence, signal energy, and optional border exclusion."""

    if not 0.0 <= coherence_threshold <= 1.0:
        raise ValueError("coherence_threshold must lie in [0, 1]")
    if not 0.0 <= energy_quantile < 1.0:
        raise ValueError("energy_quantile must lie in [0, 1)")
    energy = result["energy"]
    positive = energy[energy > 0]
    threshold = np.quantile(positive, energy_quantile) if positive.size else np.inf
    mask = (result["coherence"] >= coherence_threshold) & (energy >= threshold)
    if border > 0:
        mask[:border] = False
        mask[-border:] = False
        mask[:, :border] = False
        mask[:, -border:] = False
    return mask


def orientation_error_metrics(
    estimate: np.ndarray,
    truth: np.ndarray,
    mask: np.ndarray | None = None,
) -> dict[str, float]:
    """Return axial MAE, RMSE, median, P95, bias, and coverage in degrees."""

    estimate = np.asarray(estimate, dtype=float)
    truth = np.asarray(truth, dtype=float)
    if estimate.shape != truth.shape:
        raise ValueError("estimate and truth must have the same shape")
    if mask is None:
        mask = np.ones(estimate.shape, dtype=bool)
    valid = np.asarray(mask, dtype=bool) & np.isfinite(estimate) & np.isfinite(truth)
    if not np.any(valid):
        return {
            "mae_deg": float("nan"),
            "rmse_deg": float("nan"),
            "median_deg": float("nan"),
            "p95_deg": float("nan"),
            "bias_deg": float("nan"),
            "coverage": 0.0,
        }
    error_deg = np.rad2deg(axial_angle_difference(estimate[valid], truth[valid]))
    absolute = np.abs(error_deg)
    return {
        "mae_deg": float(np.mean(absolute)),
        "rmse_deg": float(np.sqrt(np.mean(error_deg**2))),
        "median_deg": float(np.median(absolute)),
        "p95_deg": float(np.percentile(absolute, 95.0)),
        "bias_deg": float(np.mean(error_deg)),
        "coverage": float(np.mean(valid)),
    }


def orientation_histogram(
    angles: np.ndarray,
    weights: np.ndarray | None = None,
    bins: int = 36,
) -> tuple[np.ndarray, np.ndarray]:
    """Return a normalized axial histogram over [-90, 90) degrees."""

    angles = np.rad2deg(wrap_axial_radians(np.asarray(angles, dtype=float)))
    if weights is not None:
        weights = np.asarray(weights, dtype=float)
    density, edges = np.histogram(
        angles[np.isfinite(angles)],
        bins=bins,
        range=(-90.0, 90.0),
        weights=None if weights is None else weights[np.isfinite(angles)],
        density=True,
    )
    centers = 0.5 * (edges[:-1] + edges[1:])
    return centers, density
