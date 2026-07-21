"""Synthetic microscopy and SEM-like image formation with explicit ground truth.

The module provides deterministic educational simulators for wide-field,
confocal-like, bright-field, SHG-like, SEM-like, and FIB-SEM-like images.
They are deliberately lightweight and verification-oriented.  In particular,
the SEM routines are phenomenological image-formation models rather than a
Monte-Carlo electron--solid interaction solver.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy import ndimage

FloatArray = NDArray[np.float64]
BoolArray = NDArray[np.bool_]


@dataclass(frozen=True)
class OpticalParameters:
    """Parameters for a Gaussian-PSF optical imaging approximation."""

    sigma_xy: float = 1.2
    sigma_z: float = 2.5
    gain: float = 250.0
    background: float = 0.02
    read_noise: float = 1.5
    offset: float = 0.0
    saturation: float = 1.0


@dataclass(frozen=True)
class SEMParameters:
    """Parameters for a fast SEM-like topography/composition renderer."""

    detector_azimuth_deg: float = 35.0
    detector_elevation_deg: float = 35.0
    topography_gain: float = 0.85
    edge_gain: float = 0.35
    composition_gain: float = 0.35
    charging_strength: float = 0.0
    blur_sigma: float = 0.8
    noise_std: float = 0.025


@dataclass(frozen=True)
class ArtifactParameters:
    """Common acquisition artifacts for domain-shift experiments."""

    vignette_strength: float = 0.0
    stripe_strength: float = 0.0
    drift_pixels: float = 0.0
    dead_pixel_fraction: float = 0.0
    saturation_fraction: float = 0.0
    line_jitter: float = 0.0


@dataclass(frozen=True)
class SyntheticImageResult:
    """Image, noise-free expectation, and provenance metadata."""

    image: FloatArray
    expectation: FloatArray
    metadata: dict[str, Any]


def normalize01(values: ArrayLike, *, robust: bool = False) -> FloatArray:
    """Normalize an array to ``[0, 1]`` while preserving finite values."""
    array = np.asarray(values, dtype=float)
    finite = array[np.isfinite(array)]
    if finite.size == 0:
        return np.zeros_like(array, dtype=float)
    if robust:
        low, high = np.percentile(finite, [1.0, 99.0])
    else:
        low, high = float(np.min(finite)), float(np.max(finite))
    if high <= low + 1e-15:
        return np.zeros_like(array, dtype=float)
    result = (array - low) / (high - low)
    return np.clip(np.nan_to_num(result, nan=0.0, posinf=1.0, neginf=0.0), 0.0, 1.0)


def gaussian_psf_blur(image: ArrayLike, sigma: float | tuple[float, ...]) -> FloatArray:
    """Apply a normalized Gaussian point-spread approximation."""
    if np.isscalar(sigma) and float(sigma) < 0.0:
        raise ValueError("sigma must be non-negative")
    return ndimage.gaussian_filter(np.asarray(image, dtype=float), sigma=sigma, mode="reflect")


def poisson_gaussian_noise(
    expectation: ArrayLike,
    *,
    gain: float = 250.0,
    read_noise: float = 1.5,
    offset: float = 0.0,
    seed: int = 0,
) -> FloatArray:
    """Apply signal-dependent Poisson noise and additive Gaussian read noise."""
    if gain <= 0.0:
        raise ValueError("gain must be positive")
    if read_noise < 0.0:
        raise ValueError("read_noise must be non-negative")
    expected = np.clip(np.asarray(expectation, dtype=float), 0.0, None)
    rng = np.random.default_rng(seed)
    photons = rng.poisson(expected * gain).astype(float)
    detector = photons + rng.normal(offset, read_noise, expected.shape)
    return np.clip(detector / gain, 0.0, None)


def apply_artifacts(
    image: ArrayLike,
    parameters: ArtifactParameters,
    *,
    seed: int = 0,
) -> FloatArray:
    """Apply deterministic acquisition artifacts to a two-dimensional image."""
    result = np.asarray(image, dtype=float).copy()
    if result.ndim != 2:
        raise ValueError("artifact model expects a 2-D image")
    rng = np.random.default_rng(seed)
    rows, cols = result.shape
    yy, xx = np.mgrid[-1.0 : 1.0 : complex(rows), -1.0 : 1.0 : complex(cols)]

    if parameters.vignette_strength:
        radius2 = xx**2 + yy**2
        result *= np.clip(1.0 - parameters.vignette_strength * radius2, 0.0, 1.0)

    if parameters.stripe_strength:
        phase = rng.uniform(0.0, 2.0 * np.pi)
        stripe = 1.0 + parameters.stripe_strength * np.sin(2.0 * np.pi * xx * 8.0 + phase)
        result *= stripe

    if parameters.drift_pixels:
        shifted = np.empty_like(result)
        for row in range(rows):
            shift = parameters.drift_pixels * row / max(rows - 1, 1)
            shifted[row] = ndimage.shift(result[row], shift, order=1, mode="nearest")
        result = shifted

    if parameters.line_jitter:
        shifted = np.empty_like(result)
        shifts = rng.normal(0.0, parameters.line_jitter, rows)
        for row, shift in enumerate(shifts):
            shifted[row] = ndimage.shift(result[row], shift, order=1, mode="nearest")
        result = shifted

    if parameters.dead_pixel_fraction:
        count = int(np.floor(result.size * parameters.dead_pixel_fraction))
        if count > 0:
            indices = rng.choice(result.size, count, replace=False)
            result.flat[indices] = 0.0

    if parameters.saturation_fraction:
        threshold = float(np.quantile(result, max(0.0, 1.0 - parameters.saturation_fraction)))
        result = np.minimum(result, threshold)

    return normalize01(result, robust=True)


def simulate_fluorescence(
    fluorophore: ArrayLike,
    parameters: OpticalParameters = OpticalParameters(),
    *,
    bleaching: float = 0.0,
    illumination_gradient: float = 0.0,
    artifacts: ArtifactParameters | None = None,
    seed: int = 0,
) -> SyntheticImageResult:
    """Generate a wide-field fluorescence-like image."""
    signal = np.clip(np.asarray(fluorophore, dtype=float), 0.0, None)
    if signal.ndim != 2:
        raise ValueError("wide-field simulation expects a 2-D field")
    rows, cols = signal.shape
    yy, xx = np.mgrid[0.0 : 1.0 : complex(rows), 0.0 : 1.0 : complex(cols)]
    illumination = np.clip(1.0 + illumination_gradient * (xx - 0.5), 0.0, None)
    bleach_profile = np.exp(-max(bleaching, 0.0) * yy)
    expectation = gaussian_psf_blur(signal * illumination * bleach_profile, parameters.sigma_xy)
    expectation = normalize01(expectation)
    expectation = np.clip(expectation + parameters.background, 0.0, parameters.saturation)
    noisy = poisson_gaussian_noise(
        expectation,
        gain=parameters.gain,
        read_noise=parameters.read_noise,
        offset=parameters.offset,
        seed=seed,
    )
    image = normalize01(noisy, robust=True)
    if artifacts is not None:
        image = apply_artifacts(image, artifacts, seed=seed + 101)
    return SyntheticImageResult(
        image=image,
        expectation=normalize01(expectation),
        metadata={
            "modality": "widefield-fluorescence-like",
            "synthetic": True,
            "parameters": asdict(parameters),
            "bleaching": float(bleaching),
            "illumination_gradient": float(illumination_gradient),
            "seed": int(seed),
        },
    )


def simulate_brightfield(
    thickness: ArrayLike,
    *,
    absorption: float = 2.0,
    phase_edge_gain: float = 0.2,
    blur_sigma: float = 1.0,
    illumination_gradient: float = 0.0,
    noise_std: float = 0.01,
    seed: int = 0,
) -> SyntheticImageResult:
    """Generate a transmission bright-field-like image using Beer--Lambert attenuation."""
    field = np.clip(np.asarray(thickness, dtype=float), 0.0, None)
    if field.ndim != 2:
        raise ValueError("bright-field simulation expects a 2-D field")
    rows, cols = field.shape
    _, xx = np.mgrid[0.0 : 1.0 : complex(rows), 0.0 : 1.0 : complex(cols)]
    illumination = np.clip(1.0 + illumination_gradient * (xx - 0.5), 0.05, None)
    transmission = illumination * np.exp(-absorption * normalize01(field))
    edge = ndimage.gaussian_gradient_magnitude(field, sigma=max(blur_sigma, 0.2))
    expectation = gaussian_psf_blur(transmission + phase_edge_gain * normalize01(edge), blur_sigma)
    rng = np.random.default_rng(seed)
    image = expectation + rng.normal(0.0, noise_std, field.shape)
    return SyntheticImageResult(
        image=normalize01(image, robust=True),
        expectation=normalize01(expectation),
        metadata={
            "modality": "brightfield-like",
            "synthetic": True,
            "absorption": float(absorption),
            "phase_edge_gain": float(phase_edge_gain),
            "blur_sigma": float(blur_sigma),
            "seed": int(seed),
        },
    )


def simulate_confocal_stack(
    fluorophore_volume: ArrayLike,
    parameters: OpticalParameters = OpticalParameters(),
    *,
    pinhole_rejection: float = 0.45,
    seed: int = 0,
) -> SyntheticImageResult:
    """Generate a confocal-like stack with anisotropic PSF and out-of-focus rejection."""
    volume = np.clip(np.asarray(fluorophore_volume, dtype=float), 0.0, None)
    if volume.ndim != 3:
        raise ValueError("confocal simulation expects a 3-D volume")
    blurred = gaussian_psf_blur(
        volume, (parameters.sigma_z, parameters.sigma_xy, parameters.sigma_xy)
    )
    local = gaussian_psf_blur(
        volume,
        (
            max(0.35, parameters.sigma_z * pinhole_rejection),
            parameters.sigma_xy,
            parameters.sigma_xy,
        ),
    )
    expectation = normalize01((1.0 - pinhole_rejection) * blurred + pinhole_rejection * local)
    noisy = poisson_gaussian_noise(
        expectation + parameters.background,
        gain=parameters.gain,
        read_noise=parameters.read_noise,
        seed=seed,
    )
    return SyntheticImageResult(
        image=normalize01(noisy, robust=True),
        expectation=expectation,
        metadata={
            "modality": "confocal-like",
            "synthetic": True,
            "parameters": asdict(parameters),
            "pinhole_rejection": float(pinhole_rejection),
            "seed": int(seed),
        },
    )


def simulate_shg(
    collagen_amplitude: ArrayLike,
    orientation: ArrayLike,
    *,
    polarization_angle: float = 0.0,
    orientation_power: float = 4.0,
    coherent_background: float = 0.02,
    blur_sigma: float = 0.8,
    gain: float = 300.0,
    seed: int = 0,
) -> SyntheticImageResult:
    """Generate a polarization-sensitive SHG-like image.

    The orientation factor is a pedagogical axial approximation and is not a
    complete nonlinear susceptibility model.
    """
    amplitude = np.clip(np.asarray(collagen_amplitude, dtype=float), 0.0, None)
    theta = np.asarray(orientation, dtype=float)
    if amplitude.shape != theta.shape or amplitude.ndim != 2:
        raise ValueError("amplitude and orientation must be matching 2-D arrays")
    valid = np.isfinite(theta)
    factor = np.zeros_like(amplitude)
    factor[valid] = np.abs(np.cos(theta[valid] - polarization_angle)) ** orientation_power
    expectation = gaussian_psf_blur(amplitude**2 * factor + coherent_background, blur_sigma)
    expectation = normalize01(expectation)
    noisy = poisson_gaussian_noise(expectation, gain=gain, read_noise=1.0, seed=seed)
    return SyntheticImageResult(
        image=normalize01(noisy, robust=True),
        expectation=expectation,
        metadata={
            "modality": "polarization-sensitive-shg-like",
            "synthetic": True,
            "polarization_angle_rad": float(polarization_angle),
            "orientation_power": float(orientation_power),
            "seed": int(seed),
        },
    )


def height_from_mask(mask: ArrayLike, *, sigma: float = 2.0, relief: float = 1.0) -> FloatArray:
    """Create a smooth synthetic surface relief from a binary structure."""
    binary = np.asarray(mask, dtype=bool)
    inside = ndimage.distance_transform_edt(binary)
    outside = ndimage.distance_transform_edt(~binary)
    signed = inside - 0.2 * outside
    smooth = gaussian_psf_blur(signed, sigma)
    return relief * normalize01(smooth)


def _surface_shading(height: FloatArray, azimuth_deg: float, elevation_deg: float) -> FloatArray:
    gy, gx = np.gradient(height)
    normals = np.stack((-gx, -gy, np.ones_like(height)), axis=-1)
    normals /= np.maximum(np.linalg.norm(normals, axis=-1, keepdims=True), 1e-12)
    azimuth = np.deg2rad(azimuth_deg)
    elevation = np.deg2rad(elevation_deg)
    detector = np.array(
        [
            np.cos(elevation) * np.cos(azimuth),
            np.cos(elevation) * np.sin(azimuth),
            np.sin(elevation),
        ]
    )
    return np.clip(np.einsum("...i,i->...", normals, detector), 0.0, 1.0)


def simulate_sem(
    height: ArrayLike,
    composition: ArrayLike | None = None,
    parameters: SEMParameters = SEMParameters(),
    *,
    artifacts: ArtifactParameters | None = None,
    seed: int = 0,
) -> SyntheticImageResult:
    """Generate a fast secondary/backscatter-inspired SEM-like image."""
    surface = np.asarray(height, dtype=float)
    if surface.ndim != 2:
        raise ValueError("SEM-like simulation expects a 2-D height field")
    comp = np.zeros_like(surface) if composition is None else normalize01(composition)
    if comp.shape != surface.shape:
        raise ValueError("composition and height must have the same shape")
    shade = _surface_shading(
        normalize01(surface), parameters.detector_azimuth_deg, parameters.detector_elevation_deg
    )
    edges = normalize01(ndimage.gaussian_gradient_magnitude(surface, sigma=0.8))
    charging = parameters.charging_strength * gaussian_psf_blur(normalize01(surface) ** 3, 6.0)
    expectation = (
        parameters.topography_gain * shade
        + parameters.edge_gain * edges
        + parameters.composition_gain * comp
        + charging
    )
    expectation = gaussian_psf_blur(normalize01(expectation), parameters.blur_sigma)
    rng = np.random.default_rng(seed)
    noisy = expectation + rng.normal(0.0, parameters.noise_std, surface.shape)
    image = normalize01(noisy, robust=True)
    if artifacts is not None:
        image = apply_artifacts(image, artifacts, seed=seed + 31)
    return SyntheticImageResult(
        image=image,
        expectation=normalize01(expectation),
        metadata={
            "modality": "sem-like",
            "synthetic": True,
            "physical_scope": "phenomenological-not-electron-monte-carlo",
            "parameters": asdict(parameters),
            "seed": int(seed),
        },
    )


def simulate_fib_sem_stack(
    volume: ArrayLike,
    *,
    slice_axis: int = 0,
    blur_sigma: float = 0.8,
    noise_std: float = 0.02,
    drift_per_slice: tuple[float, float] = (0.0, 0.0),
    curtaining_strength: float = 0.0,
    missing_slice_probability: float = 0.0,
    seed: int = 0,
) -> SyntheticImageResult:
    """Generate a FIB-SEM-like serial-section stack with alignment artifacts."""
    data = np.moveaxis(np.asarray(volume, dtype=float), slice_axis, 0)
    if data.ndim != 3:
        raise ValueError("FIB-SEM stack simulation expects a 3-D volume")
    rng = np.random.default_rng(seed)
    expectation = np.empty_like(data, dtype=float)
    observed = np.empty_like(data, dtype=float)
    width = data.shape[2]
    stripe_x = np.linspace(0.0, 2.0 * np.pi * 12.0, width)
    curtain = 1.0 + curtaining_strength * np.sin(stripe_x + rng.uniform(0.0, 2.0 * np.pi))
    last_valid = np.zeros(data.shape[1:], dtype=float)
    for index, source in enumerate(data):
        section = gaussian_psf_blur(source, blur_sigma)
        section = normalize01(section)
        expectation[index] = section
        if rng.random() < missing_slice_probability and index > 0:
            image = last_valid.copy()
        else:
            shift = (drift_per_slice[0] * index, drift_per_slice[1] * index)
            image = ndimage.shift(section, shift=shift, order=1, mode="nearest")
            image *= curtain[None, :]
            image += rng.normal(0.0, noise_std, image.shape)
            last_valid = image.copy()
        observed[index] = normalize01(image, robust=True)
    restored = np.moveaxis(observed, 0, slice_axis)
    expected = np.moveaxis(expectation, 0, slice_axis)
    return SyntheticImageResult(
        image=restored,
        expectation=expected,
        metadata={
            "modality": "fib-sem-like-serial-stack",
            "synthetic": True,
            "slice_axis": int(slice_axis),
            "drift_per_slice": [float(v) for v in drift_per_slice],
            "curtaining_strength": float(curtaining_strength),
            "missing_slice_probability": float(missing_slice_probability),
            "seed": int(seed),
        },
    )


def resample_stack(
    volume: ArrayLike,
    source_spacing: tuple[float, float, float],
    target_spacing: tuple[float, float, float],
    *,
    order: int = 1,
) -> FloatArray:
    """Resample a 3-D stack between anisotropic voxel spacings."""
    if any(value <= 0.0 for value in (*source_spacing, *target_spacing)):
        raise ValueError("voxel spacings must be positive")
    factors = tuple(source / target for source, target in zip(source_spacing, target_spacing))
    return ndimage.zoom(np.asarray(volume, dtype=float), zoom=factors, order=order, mode="nearest")


def focus_series(
    image: ArrayLike,
    defocus_values: ArrayLike,
    *,
    base_sigma: float = 0.6,
) -> FloatArray:
    """Generate a stack of progressively defocused views."""
    source = np.asarray(image, dtype=float)
    values = np.asarray(defocus_values, dtype=float)
    frames = [gaussian_psf_blur(source, np.hypot(base_sigma, value)) for value in values]
    return np.stack([normalize01(frame) for frame in frames], axis=0)


def psnr(reference: ArrayLike, estimate: ArrayLike, *, data_range: float = 1.0) -> float:
    """Peak signal-to-noise ratio."""
    ref = np.asarray(reference, dtype=float)
    est = np.asarray(estimate, dtype=float)
    if ref.shape != est.shape:
        raise ValueError("arrays must have matching shapes")
    mse = float(np.mean((ref - est) ** 2))
    if mse <= 1e-30:
        return float("inf")
    return float(10.0 * np.log10(data_range**2 / mse))


def global_ssim(reference: ArrayLike, estimate: ArrayLike, *, data_range: float = 1.0) -> float:
    """A compact global SSIM diagnostic for synthetic benchmark tables."""
    ref = np.asarray(reference, dtype=float)
    est = np.asarray(estimate, dtype=float)
    if ref.shape != est.shape:
        raise ValueError("arrays must have matching shapes")
    c1 = (0.01 * data_range) ** 2
    c2 = (0.03 * data_range) ** 2
    mu_x = float(np.mean(ref))
    mu_y = float(np.mean(est))
    var_x = float(np.var(ref))
    var_y = float(np.var(est))
    cov = float(np.mean((ref - mu_x) * (est - mu_y)))
    numerator = (2.0 * mu_x * mu_y + c1) * (2.0 * cov + c2)
    denominator = (mu_x**2 + mu_y**2 + c1) * (var_x + var_y + c2)
    return float(numerator / max(denominator, 1e-30))


def export_multimodal_dataset(
    path: str | Path,
    *,
    ground_truth: dict[str, ArrayLike],
    modalities: dict[str, ArrayLike],
    metadata: dict[str, Any] | None = None,
) -> Path:
    """Export synchronized ground truth and modality arrays to compressed NPZ."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload: dict[str, Any] = {}
    for key, value in ground_truth.items():
        payload[f"gt_{key}"] = np.asarray(value)
    for key, value in modalities.items():
        payload[f"image_{key}"] = np.asarray(value)
    provenance = {
        "synthetic": True,
        "experimental_validation": False,
        "schema": "bmrt.synthetic-microscopy.v1",
        **(metadata or {}),
    }
    payload["metadata_json"] = np.asarray(json.dumps(provenance, sort_keys=True))
    np.savez_compressed(target, **payload)
    return target


def read_multimodal_metadata(path: str | Path) -> dict[str, Any]:
    """Read JSON provenance from an exported NPZ dataset."""
    with np.load(Path(path), allow_pickle=False) as archive:
        return json.loads(str(archive["metadata_json"].item()))
