"""Orientation distributions and concentration parameters for Tutorial 18.

The functions in this module are intentionally lightweight and dependency-limited.
They operate on synthetic, verification-ready microstructures where the true axial
orientation field is known. Angles are axial, so theta and theta + pi describe the
same fibre direction.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Tuple

import numpy as np
from scipy import ndimage

Array = np.ndarray
EPS = 1.0e-12


@dataclass(frozen=True)
class OrientationStats:
    """Summary statistics for an axial orientation distribution."""

    mean_angle_rad: float
    mean_angle_deg: float
    resultant_length: float
    kappa: float
    tensor_anisotropy: float
    entropy: float
    n_effective: float


@dataclass(frozen=True)
class SyntheticOrientationDataset:
    """Synthetic multimodal representation of the same fibrous architecture."""

    mask: Array
    family_id: Array
    true_orientation: Array
    sem_like_image: Array
    polarization_orientation: Array
    polarization_confidence: Array
    segmented_mask: Array
    segmented_orientation: Array
    sem_orientation: Array
    sem_confidence: Array


def axial_wrap(theta: Array | float) -> Array | float:
    """Map angles to the axial interval [0, pi)."""

    return np.mod(theta, np.pi)


def axial_difference(theta: Array, reference: Array | float) -> Array:
    """Smallest signed difference between axial angles in radians."""

    return 0.5 * np.arctan2(np.sin(2.0 * (theta - reference)), np.cos(2.0 * (theta - reference)))


def orientation_vector(theta: Array) -> Tuple[Array, Array]:
    """Return unit-vector components for an axial orientation angle."""

    return np.cos(theta), np.sin(theta)


def normalise_weights(weights: Array | None, shape: Tuple[int, ...]) -> Array:
    """Return non-negative weights with unit sum."""

    if weights is None:
        w = np.ones(shape, dtype=float)
    else:
        w = np.asarray(weights, dtype=float)
        if w.shape != shape:
            raise ValueError(f"weights shape {w.shape} does not match angles shape {shape}")
        w = np.maximum(w, 0.0)
    total = float(np.sum(w))
    if total <= EPS:
        raise ValueError("orientation weights must contain positive mass")
    return w / total


def axial_mean_resultant(angles: Array, weights: Array | None = None) -> Tuple[float, float]:
    """Mean axis and resultant length for axial data.

    Axial data are handled by doubling the angles, computing the circular mean,
    and halving the resulting phase.
    """

    theta = np.asarray(angles, dtype=float)
    if theta.size == 0:
        raise ValueError("at least one orientation angle is required")
    w = normalise_weights(weights, theta.shape)
    c = float(np.sum(w * np.cos(2.0 * theta)))
    s = float(np.sum(w * np.sin(2.0 * theta)))
    mean = 0.5 * np.arctan2(s, c)
    return float(axial_wrap(mean)), float(np.hypot(c, s))


def kappa_from_resultant(resultant_length: float) -> float:
    """Approximate von-Mises concentration parameter from mean resultant length.

    The approximation is applied to doubled angles, which is the standard
    transformation for axial data.
    """

    r = float(np.clip(resultant_length, 0.0, 0.999999))
    if r < 1e-8:
        return 0.0
    if r < 0.53:
        return float(2.0 * r + r**3 + 5.0 * r**5 / 6.0)
    if r < 0.85:
        return float(-0.4 + 1.39 * r + 0.43 / (1.0 - r))
    return float(1.0 / (r**3 - 4.0 * r**2 + 3.0 * r))


def orientation_tensor(angles: Array, weights: Array | None = None) -> Array:
    """Second-order orientation tensor A = <a ⊗ a>."""

    theta = np.asarray(angles, dtype=float)
    w = normalise_weights(weights, theta.shape)
    c = np.cos(theta)
    s = np.sin(theta)
    return np.array(
        [
            [float(np.sum(w * c * c)), float(np.sum(w * c * s))],
            [float(np.sum(w * c * s)), float(np.sum(w * s * s))],
        ]
    )


def tensor_anisotropy(angles: Array, weights: Array | None = None) -> float:
    """Difference between the two eigenvalues of the orientation tensor."""

    eig = np.linalg.eigvalsh(orientation_tensor(angles, weights))
    return float(eig[-1] - eig[0])


def histogram_odf(
    angles: Array,
    weights: Array | None = None,
    n_bins: int = 36,
    smoothing_sigma_bins: float = 0.0,
) -> Tuple[Array, Array]:
    """Estimate an axial orientation distribution function on [0, pi)."""

    theta = np.asarray(angles, dtype=float)
    if theta.size == 0:
        raise ValueError("at least one orientation angle is required")
    w = normalise_weights(weights, theta.shape)
    edges = np.linspace(0.0, np.pi, n_bins + 1)
    mass, _ = np.histogram(axial_wrap(theta).ravel(), bins=edges, weights=w.ravel())
    if smoothing_sigma_bins > 0.0:
        mass = ndimage.gaussian_filter1d(mass, smoothing_sigma_bins, mode="wrap")
    mass = np.maximum(mass, 0.0)
    mass = mass / max(float(np.sum(mass)), EPS)
    centers = 0.5 * (edges[:-1] + edges[1:])
    density = mass / (edges[1] - edges[0])
    return centers, density


def probability_mass_from_density(density: Array) -> Array:
    """Convert any non-negative ODF-like vector to probability mass."""

    p = np.maximum(np.asarray(density, dtype=float), 0.0)
    total = float(np.sum(p))
    if total <= EPS:
        raise ValueError("distribution must contain positive mass")
    return p / total


def jensen_shannon_divergence(p: Array, q: Array) -> float:
    """Jensen-Shannon divergence between two discrete orientation distributions."""

    pp = probability_mass_from_density(p)
    qq = probability_mass_from_density(q)
    m = 0.5 * (pp + qq)

    def kl(a: Array, b: Array) -> float:
        mask = a > 0.0
        return float(np.sum(a[mask] * np.log(a[mask] / np.maximum(b[mask], EPS))))

    return 0.5 * kl(pp, m) + 0.5 * kl(qq, m)


def circular_entropy_from_density(density: Array) -> float:
    """Normalized entropy of an axial ODF: 0 is concentrated, 1 is uniform."""

    p = probability_mass_from_density(density)
    entropy = -float(np.sum(p * np.log(np.maximum(p, EPS))))
    return entropy / np.log(len(p))


def orientation_statistics(
    angles: Array,
    weights: Array | None = None,
    n_bins: int = 36,
) -> OrientationStats:
    """Compute interpretable concentration statistics for an axial distribution."""

    theta = np.asarray(angles, dtype=float)
    mean, r = axial_mean_resultant(theta, weights)
    _, density = histogram_odf(theta, weights, n_bins=n_bins, smoothing_sigma_bins=1.0)
    w = normalise_weights(weights, theta.shape)
    n_effective = 1.0 / float(np.sum(w * w))
    return OrientationStats(
        mean_angle_rad=mean,
        mean_angle_deg=float(np.rad2deg(mean)),
        resultant_length=r,
        kappa=kappa_from_resultant(r),
        tensor_anisotropy=tensor_anisotropy(theta, weights),
        entropy=circular_entropy_from_density(density),
        n_effective=n_effective,
    )


def otsu_threshold(image: Array, n_bins: int = 256) -> float:
    """Compute an Otsu threshold for a normalized image without scikit-image."""

    values = np.asarray(image, dtype=float).ravel()
    values = values[np.isfinite(values)]
    hist, edges = np.histogram(values, bins=n_bins, range=(float(values.min()), float(values.max())))
    centers = 0.5 * (edges[:-1] + edges[1:])
    hist = hist.astype(float)
    weight0 = np.cumsum(hist)
    weight1 = np.cumsum(hist[::-1])[::-1]
    mean0 = np.cumsum(hist * centers) / np.maximum(weight0, EPS)
    mean1 = (np.cumsum((hist * centers)[::-1]) / np.maximum(weight1[::-1], EPS))[::-1]
    variance = weight0[:-1] * weight1[1:] * (mean0[:-1] - mean1[1:]) ** 2
    return float(centers[:-1][np.argmax(variance)])


def normalize01(image: Array) -> Array:
    """Normalize an array to [0, 1]."""

    x = np.asarray(image, dtype=float)
    lo = float(np.nanmin(x))
    hi = float(np.nanmax(x))
    if hi - lo < EPS:
        return np.zeros_like(x, dtype=float)
    return (x - lo) / (hi - lo)


def generate_synthetic_architecture(
    shape: Tuple[int, int] = (192, 192),
    seed: int = 18,
    base_angle_deg: float = 24.0,
    concentration: float = 0.82,
    pore_count: int = 18,
) -> Tuple[Array, Array, Array]:
    """Create a synthetic fibrous mask, family labels, and exact orientation field."""

    rng = np.random.default_rng(seed)
    ny, nx = shape
    yy, xx = np.indices(shape)
    x = (xx - nx / 2.0) / (nx / 2.0)
    y = (yy - ny / 2.0) / (ny / 2.0)
    base = np.deg2rad(base_angle_deg)
    bend = np.deg2rad(18.0 * (1.0 - 0.45 * concentration))
    theta_main = axial_wrap(base + bend * np.sin(2.2 * np.pi * y + 0.7 * x) + 0.13 * x)

    normal_main = -np.sin(base) * x + np.cos(base) * y
    waviness = 0.045 * np.sin(3.0 * np.pi * x + 1.5 * np.sin(2.0 * np.pi * y))
    phase = (normal_main + waviness) * 11.0
    stripe = np.abs((phase - np.floor(phase)) - 0.5)
    width = 0.18 + 0.08 * concentration
    main = stripe < width

    secondary_angle = axial_wrap(base + np.deg2rad(63.0))
    normal_secondary = -np.sin(secondary_angle) * x + np.cos(secondary_angle) * y
    stripe2 = np.abs(((normal_secondary + 0.025 * np.sin(4.0 * y)) * 8.5) % 1.0 - 0.5)
    inclusion = ((x + 0.08) / 0.72) ** 2 + ((y - 0.03) / 0.55) ** 2 < 1.0
    secondary = (stripe2 < 0.15) & inclusion

    mask = main | secondary
    family = np.zeros(shape, dtype=np.int16)
    family[main] = 1
    family[secondary] = 2
    orientation = np.full(shape, np.nan, dtype=float)
    orientation[main] = theta_main[main]
    orientation[secondary] = secondary_angle

    # Pores remove material and create realistic topological sensitivity.
    for _ in range(pore_count):
        cy = rng.uniform(0.12 * ny, 0.88 * ny)
        cx = rng.uniform(0.12 * nx, 0.88 * nx)
        radius = rng.uniform(3.0, 8.5)
        pore = (yy - cy) ** 2 + (xx - cx) ** 2 <= radius**2
        mask[pore] = False
        family[pore] = 0
        orientation[pore] = np.nan

    # Keep only the largest connected structure and a few branches.
    labels, nlabels = ndimage.label(mask)
    if nlabels > 0:
        sizes = ndimage.sum(mask, labels, index=np.arange(1, nlabels + 1))
        keep = np.argsort(sizes)[-min(5, len(sizes)):] + 1
        mask = np.isin(labels, keep)
        family[~mask] = 0
        orientation[~mask] = np.nan
    return mask, family, orientation


def simulate_sem_like_image(mask: Array, seed: int = 18) -> Array:
    """Create an SEM-like intensity image from a binary synthetic structure."""

    rng = np.random.default_rng(seed)
    mask_float = mask.astype(float)
    height = normalize01(ndimage.gaussian_filter(mask_float, 1.1) + 0.55 * ndimage.distance_transform_edt(mask))
    gy, gx = np.gradient(height)
    detector = normalize01(0.52 + 0.75 * gx - 0.35 * gy + 0.35 * height)
    texture = ndimage.gaussian_filter(rng.normal(0.0, 1.0, mask.shape), 1.0)
    fine = ndimage.gaussian_filter(rng.normal(0.0, 1.0, mask.shape), 0.35)
    yy, xx = np.indices(mask.shape)
    vignette = 1.0 - 0.22 * ((xx - mask.shape[1] / 2) ** 2 + (yy - mask.shape[0] / 2) ** 2) / (0.5 * max(mask.shape)) ** 2
    image = detector * vignette + 0.08 * texture + 0.025 * fine
    image = 0.18 + 0.78 * normalize01(image)
    image[~ndimage.binary_dilation(mask, iterations=2)] *= 0.55
    return normalize01(image)


def segment_sem_like_image(image: Array) -> Array:
    """Simple Otsu + morphology segmentation used as a segmentation-derived modality."""

    threshold = otsu_threshold(image)
    rough = image > threshold
    rough = ndimage.binary_opening(rough, structure=np.ones((2, 2)))
    rough = ndimage.binary_closing(rough, structure=np.ones((3, 3)), iterations=2)
    rough = ndimage.binary_fill_holes(rough)
    return rough.astype(bool)


def structure_tensor_orientation(image: Array, sigma: float = 1.0, rho: float = 3.0) -> Tuple[Array, Array]:
    """Recover local line orientation and coherence from image gradients."""

    smooth = ndimage.gaussian_filter(np.asarray(image, dtype=float), sigma)
    gy, gx = np.gradient(smooth)
    jxx = ndimage.gaussian_filter(gx * gx, rho)
    jyy = ndimage.gaussian_filter(gy * gy, rho)
    jxy = ndimage.gaussian_filter(gx * gy, rho)
    gradient_axis = 0.5 * np.arctan2(2.0 * jxy, jxx - jyy)
    line_axis = axial_wrap(gradient_axis + np.pi / 2.0)
    coherence = np.sqrt((jxx - jyy) ** 2 + 4.0 * jxy**2) / np.maximum(jxx + jyy, EPS)
    return line_axis, np.clip(coherence, 0.0, 1.0)


def simulate_polarization_like_orientation(
    true_orientation: Array,
    mask: Array,
    seed: int = 18,
    noise_deg: float = 6.0,
) -> Tuple[Array, Array]:
    """Create a noisy polarization-like orientation map and confidence map."""

    rng = np.random.default_rng(seed)
    valid = mask & np.isfinite(true_orientation)
    confidence = np.zeros(mask.shape, dtype=float)
    local_density = ndimage.gaussian_filter(mask.astype(float), 3.0)
    edge_loss = ndimage.gaussian_gradient_magnitude(mask.astype(float), 1.2)
    confidence[valid] = np.clip(0.92 * local_density[valid] - 0.45 * edge_loss[valid] + 0.08, 0.04, 0.98)
    noise = rng.normal(0.0, np.deg2rad(noise_deg), mask.shape) / np.maximum(confidence, 0.1)
    estimate = np.full(mask.shape, np.nan, dtype=float)
    estimate[valid] = axial_wrap(true_orientation[valid] + noise[valid])
    return estimate, confidence


def build_synthetic_orientation_dataset(
    shape: Tuple[int, int] = (192, 192),
    seed: int = 18,
    concentration: float = 0.82,
    pore_count: int = 18,
) -> SyntheticOrientationDataset:
    """Create all modalities used in Tutorial 18."""

    mask, family, true_orientation = generate_synthetic_architecture(
        shape=shape, seed=seed, concentration=concentration, pore_count=pore_count
    )
    sem = simulate_sem_like_image(mask, seed=seed + 1)
    segmented = segment_sem_like_image(sem)
    sem_orientation, sem_confidence = structure_tensor_orientation(sem, sigma=1.0, rho=3.2)
    seg_orientation, _ = structure_tensor_orientation(segmented.astype(float), sigma=1.0, rho=2.5)
    pol_orientation, pol_confidence = simulate_polarization_like_orientation(
        true_orientation, mask, seed=seed + 2
    )
    return SyntheticOrientationDataset(
        mask=mask,
        family_id=family,
        true_orientation=true_orientation,
        sem_like_image=sem,
        polarization_orientation=pol_orientation,
        polarization_confidence=pol_confidence,
        segmented_mask=segmented,
        segmented_orientation=seg_orientation,
        sem_orientation=sem_orientation,
        sem_confidence=sem_confidence,
    )


def sample_valid(angles: Array, mask: Array, weights: Array | None = None) -> Tuple[Array, Array | None]:
    """Extract finite orientation samples and optional weights from a mask."""

    valid = mask & np.isfinite(angles)
    if not np.any(valid):
        raise ValueError("no valid orientation samples inside mask")
    if weights is None:
        return axial_wrap(angles[valid]), None
    return axial_wrap(angles[valid]), np.asarray(weights, dtype=float)[valid]


def simple_anisotropic_stiffness(mean_angle: float, concentration: float, load_angle: float = 0.0) -> float:
    """Toy image-informed stiffness index based on orientation and alignment.

    This is not a constitutive law. It illustrates why ODF errors matter before
    a later tutorial introduces image-informed constitutive parameters.
    """

    directional = np.cos(axial_difference(np.array([mean_angle]), load_angle))[0] ** 2
    return float(1.0 + 4.0 * concentration * directional)


def benchmark_modalities(dataset: SyntheticOrientationDataset, n_bins: int = 36) -> Tuple[Dict[str, dict], Array, Dict[str, Array]]:
    """Compare ODF recovery across ground-truth, SEM-like, polarization-like and mask modalities."""

    gt_angles, gt_weights = sample_valid(dataset.true_orientation, dataset.mask)
    centers, gt_density = histogram_odf(gt_angles, gt_weights, n_bins=n_bins, smoothing_sigma_bins=1.0)
    gt_stats = orientation_statistics(gt_angles, gt_weights, n_bins=n_bins)
    gt_stiffness = simple_anisotropic_stiffness(gt_stats.mean_angle_rad, gt_stats.resultant_length)

    modalities = {
        "ground_truth": (dataset.true_orientation, dataset.mask, None),
        "sem_like_gradient": (dataset.sem_orientation, dataset.mask, dataset.sem_confidence),
        "polarization_like_map": (
            dataset.polarization_orientation,
            dataset.mask,
            dataset.polarization_confidence,
        ),
        "segmented_mask": (dataset.segmented_orientation, dataset.segmented_mask, None),
    }

    results: Dict[str, dict] = {}
    densities: Dict[str, Array] = {"ground_truth": gt_density}
    for name, (angles_map, valid_mask, weights_map) in modalities.items():
        angles, weights = sample_valid(angles_map, valid_mask, weights_map)
        stats = orientation_statistics(angles, weights, n_bins=n_bins)
        _, density = histogram_odf(angles, weights, n_bins=n_bins, smoothing_sigma_bins=1.0)
        densities[name] = density
        common = dataset.mask & valid_mask & np.isfinite(angles_map) & np.isfinite(dataset.true_orientation)
        if np.any(common):
            error = np.abs(axial_difference(angles_map[common], dataset.true_orientation[common]))
            orientation_mae_deg = float(np.rad2deg(np.mean(error)))
        else:
            orientation_mae_deg = float("nan")
        stiffness = simple_anisotropic_stiffness(stats.mean_angle_rad, stats.resultant_length)
        results[name] = {
            "mean_angle_deg": stats.mean_angle_deg,
            "resultant_length": stats.resultant_length,
            "kappa": stats.kappa,
            "tensor_anisotropy": stats.tensor_anisotropy,
            "entropy": stats.entropy,
            "n_effective": stats.n_effective,
            "js_to_ground_truth": jensen_shannon_divergence(gt_density, density),
            "orientation_mae_deg": orientation_mae_deg,
            "stiffness_index": stiffness,
            "stiffness_error_percent": 100.0 * (stiffness - gt_stiffness) / gt_stiffness,
        }
    return results, centers, densities


def concentration_sweep(
    concentrations: Iterable[float] = (0.35, 0.55, 0.75, 0.90),
    seed: int = 80,
) -> list[dict]:
    """Show how true and recovered concentration change with structural order."""

    rows: list[dict] = []
    for idx, concentration in enumerate(concentrations):
        dataset = build_synthetic_orientation_dataset(seed=seed + idx, concentration=concentration)
        results, _, _ = benchmark_modalities(dataset)
        for modality, values in results.items():
            rows.append(
                {
                    "target_concentration": float(concentration),
                    "modality": modality,
                    "resultant_length": float(values["resultant_length"]),
                    "kappa": float(values["kappa"]),
                    "js_to_ground_truth": float(values["js_to_ground_truth"]),
                    "orientation_mae_deg": float(values["orientation_mae_deg"]),
                }
            )
    return rows


def format_benchmark_csv(results: Dict[str, dict]) -> str:
    """Return a small CSV string for reproducible benchmark storage."""

    columns = [
        "modality",
        "mean_angle_deg",
        "resultant_length",
        "kappa",
        "tensor_anisotropy",
        "entropy",
        "n_effective",
        "js_to_ground_truth",
        "orientation_mae_deg",
        "stiffness_index",
        "stiffness_error_percent",
    ]
    lines = [",".join(columns)]
    for modality, row in results.items():
        values = [modality] + [f"{float(row[col]):.8g}" for col in columns[1:]]
        lines.append(",".join(values))
    return "\n".join(lines) + "\n"
