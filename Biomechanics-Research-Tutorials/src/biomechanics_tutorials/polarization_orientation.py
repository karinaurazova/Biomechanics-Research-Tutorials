"""Synthetic polarization-like imaging and orientation recovery.

All models in this module are educational forward/inverse models. They generate
synthetic data with known ground truth and do not represent a calibrated optical
instrument or experimental validation pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy.ndimage import gaussian_filter

FloatArray = NDArray[np.float64]


@dataclass(frozen=True)
class PolarizationParameters:
    """Parameters of the reduced crossed-polarizer forward model."""

    wavelength_nm: float = 550.0
    baseline: float = 0.03
    gain: float = 1.0
    extinction_leak: float = 0.015
    read_noise_std: float = 0.01
    photon_count: float = 1500.0
    blur_sigma: float = 0.6
    depolarization: float = 0.0

    def __post_init__(self) -> None:
        if self.wavelength_nm <= 0.0:
            raise ValueError("wavelength_nm must be positive")
        if self.gain < 0.0 or self.extinction_leak < 0.0:
            raise ValueError("gain and extinction_leak must be non-negative")
        if self.read_noise_std < 0.0 or self.photon_count <= 0.0:
            raise ValueError("noise parameters must be physically admissible")
        if self.blur_sigma < 0.0:
            raise ValueError("blur_sigma must be non-negative")
        if not 0.0 <= self.depolarization <= 1.0:
            raise ValueError("depolarization must lie in [0, 1]")


@dataclass(frozen=True)
class PolarizationSeries:
    """A synthetic angular image series and its noise-free expectation."""

    angles_rad: FloatArray
    images: FloatArray
    expectation: FloatArray
    metadata: dict[str, object]


@dataclass(frozen=True)
class OrientationRecovery:
    """Recovered axial orientation and harmonic observables."""

    orientation_rad: FloatArray
    modulation: FloatArray
    offset: FloatArray
    residual_rms: FloatArray
    confidence: FloatArray


def axial_wrap(angle: ArrayLike) -> FloatArray:
    """Wrap axial angles to ``[-pi/2, pi/2)``."""

    values = np.asarray(angle, dtype=float)
    return ((values + np.pi / 2.0) % np.pi) - np.pi / 2.0


def axial_difference(a: ArrayLike, b: ArrayLike) -> FloatArray:
    """Smallest signed difference between axial directions."""

    return axial_wrap(np.asarray(a, dtype=float) - np.asarray(b, dtype=float))


def retardance_from_birefringence(
    birefringence: ArrayLike,
    thickness_um: ArrayLike,
    wavelength_nm: float = 550.0,
) -> FloatArray:
    """Return phase retardance in radians: ``delta = 2*pi*Delta n*d/lambda``."""

    if wavelength_nm <= 0.0:
        raise ValueError("wavelength_nm must be positive")
    delta_n = np.asarray(birefringence, dtype=float)
    thickness = np.asarray(thickness_um, dtype=float)
    if np.any(thickness < 0.0):
        raise ValueError("thickness_um must be non-negative")
    wavelength_um = wavelength_nm * 1.0e-3
    return 2.0 * np.pi * delta_n * thickness / wavelength_um


def crossed_polarizer_intensity(
    orientation_rad: ArrayLike,
    retardance_rad: ArrayLike,
    analyzer_angle_rad: float,
    amplitude: ArrayLike | float = 1.0,
    baseline: ArrayLike | float = 0.0,
) -> FloatArray:
    """Reduced crossed-polarizer intensity model.

    ``I = I_bg + A sin^2(2(alpha-theta)) sin^2(delta/2)``.
    The expression is axial and therefore invariant under ``alpha -> alpha+pi``.
    """

    alpha = np.asarray(orientation_rad, dtype=float)
    delta = np.asarray(retardance_rad, dtype=float)
    amp = np.asarray(amplitude, dtype=float)
    bg = np.asarray(baseline, dtype=float)
    return bg + amp * np.sin(2.0 * (alpha - analyzer_angle_rad)) ** 2 * np.sin(delta / 2.0) ** 2


def jones_linear_retarder(
    orientation_rad: float,
    retardance_rad: float,
) -> NDArray[np.complex128]:
    """Jones matrix of an ideal linear retarder in the laboratory basis."""

    c = float(np.cos(orientation_rad))
    s = float(np.sin(orientation_rad))
    rotation = np.array([[c, -s], [s, c]], dtype=complex)
    phase = np.array(
        [[np.exp(-0.5j * retardance_rad), 0.0], [0.0, np.exp(0.5j * retardance_rad)]],
        dtype=complex,
    )
    return rotation @ phase @ rotation.T


def multilayer_jones_intensity(
    orientations_rad: ArrayLike,
    retardances_rad: ArrayLike,
    polarizer_angle_rad: float,
    analyzer_angle_rad: float,
) -> float:
    """Intensity through an ordered stack of ideal linear retarders."""

    orientations = np.asarray(orientations_rad, dtype=float)
    retardances = np.asarray(retardances_rad, dtype=float)
    if orientations.shape != retardances.shape:
        raise ValueError("orientations and retardances must have equal shape")
    input_vector = np.array(
        [np.cos(polarizer_angle_rad), np.sin(polarizer_angle_rad)], dtype=complex
    )
    state = input_vector
    for angle, retardance in zip(orientations, retardances):
        state = jones_linear_retarder(float(angle), float(retardance)) @ state
    analyzer = np.array([np.cos(analyzer_angle_rad), np.sin(analyzer_angle_rad)], dtype=complex)
    return float(np.abs(np.vdot(analyzer, state)) ** 2)


def add_polarization_noise(
    expectation: ArrayLike,
    photon_count: float = 1500.0,
    read_noise_std: float = 0.01,
    seed: int = 0,
) -> FloatArray:
    """Apply Poisson photon noise and additive Gaussian read noise."""

    if photon_count <= 0.0 or read_noise_std < 0.0:
        raise ValueError("invalid noise parameters")
    rng = np.random.default_rng(seed)
    expected = np.clip(np.asarray(expectation, dtype=float), 0.0, None)
    scale = max(float(np.max(expected)), 1.0e-12)
    photons = rng.poisson(np.clip(expected / scale, 0.0, 1.0) * photon_count)
    noisy = photons / photon_count * scale
    noisy += rng.normal(0.0, read_noise_std, size=expected.shape)
    return np.clip(noisy, 0.0, None)


def simulate_polarization_series(
    orientation_rad: ArrayLike,
    retardance_rad: ArrayLike,
    angles_rad: ArrayLike,
    amplitude: ArrayLike | float = 1.0,
    parameters: PolarizationParameters | None = None,
    illumination: ArrayLike | float = 1.0,
    seed: int = 0,
) -> PolarizationSeries:
    """Generate a crossed-polarizer angular image series."""

    params = parameters or PolarizationParameters()
    orientation = np.asarray(orientation_rad, dtype=float)
    retardance = np.asarray(retardance_rad, dtype=float)
    if orientation.shape != retardance.shape:
        raise ValueError("orientation and retardance must have equal shape")
    angles = np.asarray(angles_rad, dtype=float)
    if angles.ndim != 1 or angles.size < 3:
        raise ValueError("angles_rad must be a one-dimensional sequence of at least three angles")
    amplitude_field = np.asarray(amplitude, dtype=float)
    illumination_field = np.asarray(illumination, dtype=float)
    frames = []
    for angle in angles:
        frame = crossed_polarizer_intensity(
            orientation,
            retardance,
            float(angle),
            amplitude=params.gain * amplitude_field,
            baseline=params.baseline + params.extinction_leak,
        )
        frame = illumination_field * frame
        mean_level = np.mean(frame)
        frame = (1.0 - params.depolarization) * frame + params.depolarization * mean_level
        if params.blur_sigma > 0.0:
            frame = gaussian_filter(frame, params.blur_sigma, mode="reflect")
        frames.append(frame)
    expectation = np.stack(frames)
    images = add_polarization_noise(
        expectation,
        photon_count=params.photon_count,
        read_noise_std=params.read_noise_std,
        seed=seed,
    )
    return PolarizationSeries(
        angles_rad=angles,
        images=images,
        expectation=expectation,
        metadata={
            "synthetic": True,
            "experimental_validation": False,
            "forward_model": "reduced-crossed-polarizer",
            "wavelength_nm": params.wavelength_nm,
            "seed": seed,
        },
    )


def harmonic_design_matrix(angles_rad: ArrayLike) -> FloatArray:
    """Return the fourth-harmonic design matrix for crossed polarizers."""

    angles = np.asarray(angles_rad, dtype=float)
    return np.column_stack([np.ones_like(angles), np.cos(4.0 * angles), np.sin(4.0 * angles)])


def recover_orientation_harmonic(
    images: ArrayLike,
    angles_rad: ArrayLike,
    regularization: float = 0.0,
) -> OrientationRecovery:
    """Recover axial orientation from an angular series by harmonic regression."""

    stack = np.asarray(images, dtype=float)
    angles = np.asarray(angles_rad, dtype=float)
    if stack.ndim < 2 or stack.shape[0] != angles.size:
        raise ValueError("the first image axis must match angles_rad")
    design = harmonic_design_matrix(angles)
    gram = design.T @ design + regularization * np.eye(3)
    coefficients = np.linalg.solve(gram, design.T @ stack.reshape(stack.shape[0], -1))
    offset = coefficients[0]
    cosine = coefficients[1]
    sine = coefficients[2]
    modulation = np.hypot(cosine, sine)
    # For I = c0 + cc cos(4 theta) + cs sin(4 theta), the physical axis is
    # alpha = 1/4 atan2(-cs, -cc), modulo pi/2 for this reduced setup.
    orientation = axial_wrap(0.25 * np.arctan2(-sine, -cosine))
    fitted = design @ coefficients
    residual = np.sqrt(np.mean((stack.reshape(stack.shape[0], -1) - fitted) ** 2, axis=0))
    confidence = modulation / (np.abs(offset) + residual + 1.0e-12)
    shape = stack.shape[1:]
    return OrientationRecovery(
        orientation_rad=orientation.reshape(shape),
        modulation=modulation.reshape(shape),
        offset=offset.reshape(shape),
        residual_rms=residual.reshape(shape),
        confidence=confidence.reshape(shape),
    )


def estimate_retardance_from_modulation(
    modulation: ArrayLike,
    amplitude: ArrayLike | float = 1.0,
) -> FloatArray:
    """Estimate principal retardance branch from harmonic modulation.

    In the reduced model the fourth-harmonic amplitude equals
    ``0.5*A*sin(delta/2)^2``. The inverse is branch-limited to ``[0, pi]``.
    """

    mod = np.asarray(modulation, dtype=float)
    amp = np.asarray(amplitude, dtype=float)
    ratio = np.clip(2.0 * mod / np.maximum(amp, 1.0e-12), 0.0, 1.0)
    return 2.0 * np.arcsin(np.sqrt(ratio))


def orientation_error_deg(
    estimate_rad: ArrayLike,
    truth_rad: ArrayLike,
    mask: ArrayLike | None = None,
) -> FloatArray:
    """Absolute axial orientation error in degrees."""

    error = np.rad2deg(np.abs(axial_difference(estimate_rad, truth_rad)))
    if mask is None:
        return error
    return error[np.asarray(mask, dtype=bool)]


def quadrature_orientation_error_deg(
    estimate_rad: ArrayLike,
    truth_rad: ArrayLike,
    mask: ArrayLike | None = None,
) -> FloatArray:
    """Absolute orientation error modulo 90 degrees.

    This metric is appropriate only for the reduced crossed-polarizer model,
    which cannot distinguish axes separated by ``pi/2`` without additional
    optical information.
    """

    difference = 0.5 * axial_wrap(2.0 * (np.asarray(estimate_rad) - np.asarray(truth_rad)))
    error = np.rad2deg(np.abs(difference))
    if mask is None:
        return error
    return error[np.asarray(mask, dtype=bool)]


def synthetic_illumination_field(
    shape: tuple[int, int],
    gradient: tuple[float, float] = (0.15, -0.1),
    vignette: float = 0.15,
) -> FloatArray:
    """Generate a smooth multiplicative illumination field."""

    yy, xx = np.indices(shape, dtype=float)
    x = (xx - (shape[1] - 1) / 2.0) / max(shape[1] - 1, 1)
    y = (yy - (shape[0] - 1) / 2.0) / max(shape[0] - 1, 1)
    field = 1.0 + gradient[0] * x + gradient[1] * y - vignette * (x**2 + y**2)
    return np.clip(field, 0.2, None)


def calibration_sweep(
    known_orientations_rad: ArrayLike,
    angular_offset_rad: float = 0.0,
    gain: float = 1.0,
) -> FloatArray:
    """Synthetic calibration response for known axial targets."""

    known = np.asarray(known_orientations_rad, dtype=float)
    return gain * axial_wrap(known + angular_offset_rad)


def export_polarization_dataset(
    path: str | Path,
    series: PolarizationSeries,
    ground_truth: dict[str, ArrayLike],
    metadata: dict[str, object] | None = None,
) -> Path:
    """Export a synthetic series, ground truth, and JSON metadata to NPZ."""

    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    merged = dict(series.metadata)
    merged.update(metadata or {})
    merged["synthetic"] = True
    merged["experimental_validation"] = False
    arrays: dict[str, object] = {
        "angles_rad": series.angles_rad,
        "images": series.images,
        "expectation": series.expectation,
        "metadata_json": np.array(json.dumps(merged, sort_keys=True)),
    }
    for key, value in ground_truth.items():
        arrays[f"ground_truth_{key}"] = np.asarray(value)
    np.savez_compressed(destination, **arrays)
    return destination


def read_polarization_metadata(path: str | Path) -> dict[str, object]:
    """Read JSON metadata from an exported synthetic dataset."""

    with np.load(path, allow_pickle=False) as data:
        return json.loads(str(data["metadata_json"]))
