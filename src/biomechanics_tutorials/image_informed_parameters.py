"""Image-informed constitutive-parameter identification for Tutorial 19.

The module is deliberately lightweight. It does not replace a production finite-element
solver. Instead it provides a transparent verification environment where image-derived
structural fields, full-field strain maps and synthetic force data are linked through a
linear-in-parameters anisotropic constitutive model.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
from numpy.typing import ArrayLike
from scipy.ndimage import gaussian_filter
from scipy.optimize import least_squares, lsq_linear


@dataclass(frozen=True)
class StructuralFields:
    """Spatially resolved structural descriptors recovered from images.

    Parameters
    ----------
    theta:
        Axial fibre angle in radians. Angles differing by pi describe the same axis.
    kappa:
        Concentration parameter. Larger values mean stronger alignment around theta.
    rho_f:
        Fibre area/volume fraction proxy in [0, 1].
    connectivity:
        Dimensionless connectedness proxy in [0, 1].
    mask:
        Region of interest where the tissue exists.
    x, y:
        Normalized spatial coordinates used for plotting and synthetic strain fields.
    """

    theta: np.ndarray
    kappa: np.ndarray
    rho_f: np.ndarray
    connectivity: np.ndarray
    mask: np.ndarray
    x: np.ndarray
    y: np.ndarray

    @property
    def shape(self) -> tuple[int, int]:
        return self.theta.shape


@dataclass(frozen=True)
class ConstitutiveParameters:
    """Four interpretable parameters of the tutorial model.

    The stress is linear in this vector, but each basis term already depends on the
    image-informed structure. Units may be interpreted as kPa for small-strain examples.
    """

    matrix_base: float
    matrix_density_gain: float
    fiber_scale: float
    connectivity_scale: float

    def as_vector(self) -> np.ndarray:
        return np.array(
            [
                self.matrix_base,
                self.matrix_density_gain,
                self.fiber_scale,
                self.connectivity_scale,
            ],
            dtype=float,
        )


@dataclass(frozen=True)
class LoadCase:
    """Synthetic full-field DIC strain map and global force measurement."""

    name: str
    exx: np.ndarray
    eyy: np.ndarray
    gxy: np.ndarray
    true_force: np.ndarray
    measured_force: np.ndarray


@dataclass(frozen=True)
class CalibrationResult:
    """Result of an inverse identification run."""

    method: str
    parameters: np.ndarray
    predicted_observations: np.ndarray
    residual_norm: float
    condition_number: float


PARAMETER_NAMES = (
    "matrix_base",
    "matrix_density_gain",
    "fiber_scale",
    "connectivity_scale",
)


def axial_wrap(theta: ArrayLike) -> np.ndarray:
    """Wrap orientations to the axial interval [0, pi)."""

    return np.mod(np.asarray(theta, dtype=float), np.pi)


def axial_difference(a: ArrayLike, b: ArrayLike) -> np.ndarray:
    """Smallest signed difference between two axial orientations."""

    diff = np.asarray(a, dtype=float) - np.asarray(b, dtype=float)
    return 0.5 * np.arctan2(np.sin(2.0 * diff), np.cos(2.0 * diff))


def structural_order_from_kappa(kappa: ArrayLike) -> np.ndarray:
    """Map concentration to a bounded structural order proxy.

    The exact Bessel-function relation for the von Mises distribution is unnecessary for
    this tutorial. The monotone proxy kappa / (kappa + 2) is stable, bounded and easy to
    interpret: zero-like kappa gives weak order; large kappa approaches one.
    """

    kappa = np.maximum(np.asarray(kappa, dtype=float), 0.0)
    return kappa / (kappa + 2.0)


def true_parameter_set() -> ConstitutiveParameters:
    """Reference parameters used to generate synthetic measurements."""

    return ConstitutiveParameters(
        matrix_base=18.0,
        matrix_density_gain=24.0,
        fiber_scale=155.0,
        connectivity_scale=70.0,
    )


def vector_to_parameters(vector: ArrayLike) -> ConstitutiveParameters:
    vector = np.asarray(vector, dtype=float)
    if vector.shape != (4,):
        raise ValueError("Expected a vector with four parameters.")
    return ConstitutiveParameters(*map(float, vector))


def build_synthetic_structural_fields(
    shape: tuple[int, int] = (80, 80),
    seed: int = 19,
) -> StructuralFields:
    """Create image-derived fields with known ground truth.

    The fields mimic what Tutorials 17 and 18 would deliver after segmentation and ODF
    analysis: a local orientation angle, an alignment/concentration map, a fibre-fraction
    map and a connectivity proxy. Everything is synthetic and reproducible.
    """

    if shape[0] < 16 or shape[1] < 16:
        raise ValueError("Use at least a 16 by 16 grid for the synthetic benchmark.")

    rng = np.random.default_rng(seed)
    yy, xx = np.indices(shape, dtype=float)
    x = xx / max(shape[1] - 1, 1)
    y = yy / max(shape[0] - 1, 1)

    smooth_noise = gaussian_filter(rng.normal(size=shape), sigma=5.0)
    smooth_noise = (smooth_noise - smooth_noise.min()) / (np.ptp(smooth_noise) + 1.0e-12)

    curved_band = np.exp(-((y - 0.52 - 0.12 * np.sin(2.0 * np.pi * x)) ** 2) / (2.0 * 0.10**2))
    secondary_band = np.exp(-((x - 0.70 + 0.08 * np.cos(2.0 * np.pi * y)) ** 2) / (2.0 * 0.13**2))
    rho_f = np.clip(0.12 + 0.55 * curved_band + 0.20 * secondary_band + 0.18 * smooth_noise, 0.0, 1.0)

    connectivity = gaussian_filter(rho_f, sigma=2.2)
    connectivity = (connectivity - connectivity.min()) / (np.ptp(connectivity) + 1.0e-12)
    connectivity = np.clip(0.15 + 0.85 * connectivity, 0.0, 1.0)

    theta = np.deg2rad(20.0) + 0.58 * (y - 0.5) + 0.23 * np.sin(2.0 * np.pi * x)
    theta += 0.08 * (smooth_noise - 0.5)
    theta = axial_wrap(theta)

    kappa = 0.7 + 4.8 * rho_f + 4.5 * connectivity + 0.30 * rng.normal(size=shape)
    kappa = np.clip(kappa, 0.2, 12.0)

    mask = rho_f > 0.22
    return StructuralFields(theta=theta, kappa=kappa, rho_f=rho_f, connectivity=connectivity, mask=mask, x=x, y=y)


def plane_stress_isotropic_basis(exx: np.ndarray, eyy: np.ndarray, gxy: np.ndarray, nu: float = 0.45) -> np.ndarray:
    """Small-strain plane-stress response per unit Young-like modulus.

    The returned Voigt vector is [sigma_xx, sigma_yy, sigma_xy]. Engineering shear strain
    gamma_xy is used for the third strain component.
    """

    if not (-0.99 < nu < 0.5):
        raise ValueError("Poisson ratio must lie in the stable plane-stress range.")
    factor = 1.0 / (1.0 - nu**2)
    sxx = factor * (exx + nu * eyy)
    syy = factor * (nu * exx + eyy)
    sxy = factor * (0.5 * (1.0 - nu) * gxy)
    return np.stack([sxx, syy, sxy], axis=-1)


def fiber_basis(
    exx: np.ndarray,
    eyy: np.ndarray,
    gxy: np.ndarray,
    theta: np.ndarray,
) -> np.ndarray:
    """Stress direction generated by one axial fibre family per unit fibre stiffness."""

    nx = np.cos(theta)
    ny = np.sin(theta)
    fibre_strain = nx**2 * exx + ny**2 * eyy + nx * ny * gxy
    return np.stack(
        [
            fibre_strain * nx**2,
            fibre_strain * ny**2,
            fibre_strain * nx * ny,
        ],
        axis=-1,
    )


def stress_design_basis(
    structure: StructuralFields,
    exx: np.ndarray,
    eyy: np.ndarray,
    gxy: np.ndarray,
    nu: float = 0.45,
) -> np.ndarray:
    """Return B(x, y) so that sigma_voigt(x, y) = B(x, y) @ p."""

    iso = plane_stress_isotropic_basis(exx, eyy, gxy, nu=nu)
    fib = fiber_basis(exx, eyy, gxy, structure.theta)
    order = structural_order_from_kappa(structure.kappa)

    basis = np.empty(structure.shape + (3, 4), dtype=float)
    basis[..., :, 0] = iso
    basis[..., :, 1] = structure.rho_f[..., None] * iso
    basis[..., :, 2] = (structure.rho_f * order)[..., None] * fib
    basis[..., :, 3] = (structure.connectivity * order)[..., None] * fib
    return basis


def stress_from_parameters(
    structure: StructuralFields,
    exx: np.ndarray,
    eyy: np.ndarray,
    gxy: np.ndarray,
    parameters: ArrayLike | ConstitutiveParameters,
    nu: float = 0.45,
) -> np.ndarray:
    """Compute the stress field for one load case."""

    vector = parameters.as_vector() if isinstance(parameters, ConstitutiveParameters) else np.asarray(parameters, dtype=float)
    basis = stress_design_basis(structure, exx, eyy, gxy, nu=nu)
    return np.tensordot(basis, vector, axes=([-1], [0]))


def average_force_from_stress(stress: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Convert a stress field to a global reaction-like observation."""

    if stress.shape[-1] != 3:
        raise ValueError("Stress field must end with three Voigt components.")
    active = np.asarray(mask, dtype=bool)
    return np.nanmean(stress[active], axis=0)


def _strain_pattern(structure: StructuralFields, kind: str, amplitude: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    x, y = structure.x, structure.y
    perturb = 1.0 + 0.12 * np.sin(2.0 * np.pi * x) * np.cos(np.pi * y)
    shear_wave = np.sin(np.pi * x) * np.sin(2.0 * np.pi * y)

    if kind == "uniaxial_x":
        exx = amplitude * perturb
        eyy = -0.32 * amplitude * (1.0 + 0.08 * np.cos(2.0 * np.pi * y))
        gxy = 0.10 * amplitude * shear_wave
    elif kind == "uniaxial_y":
        exx = -0.30 * amplitude * (1.0 + 0.05 * np.sin(2.0 * np.pi * x))
        eyy = amplitude * perturb
        gxy = -0.08 * amplitude * shear_wave
    elif kind == "biaxial":
        exx = amplitude * (0.78 + 0.12 * x)
        eyy = amplitude * (0.58 + 0.18 * y)
        gxy = 0.05 * amplitude * shear_wave
    elif kind == "shear":
        exx = 0.18 * amplitude * np.cos(np.pi * y)
        eyy = -0.12 * amplitude * np.sin(np.pi * x)
        gxy = amplitude * (0.75 + 0.25 * shear_wave)
    elif kind == "gradient":
        exx = amplitude * (0.25 + 0.95 * x)
        eyy = amplitude * (0.10 + 0.55 * y)
        gxy = amplitude * 0.35 * (x - y)
    else:
        raise ValueError(f"Unknown strain pattern: {kind}")
    return exx, eyy, gxy


def build_synthetic_load_cases(
    structure: StructuralFields,
    parameters: ArrayLike | ConstitutiveParameters | None = None,
    noise_level: float = 0.015,
    seed: int = 1919,
) -> list[LoadCase]:
    """Generate full-field DIC strains and noisy global force measurements."""

    rng = np.random.default_rng(seed)
    p = true_parameter_set() if parameters is None else parameters
    names_and_amplitudes = [
        ("uniaxial_x_low", "uniaxial_x", 0.018),
        ("uniaxial_x_high", "uniaxial_x", 0.032),
        ("uniaxial_y", "uniaxial_y", 0.026),
        ("biaxial", "biaxial", 0.024),
        ("shear", "shear", 0.020),
        ("gradient", "gradient", 0.030),
    ]

    load_cases: list[LoadCase] = []
    for name, kind, amplitude in names_and_amplitudes:
        exx, eyy, gxy = _strain_pattern(structure, kind, amplitude)
        dic_noise = noise_level * amplitude * rng.normal(size=structure.shape)
        exx_m = exx + 0.35 * dic_noise
        eyy_m = eyy + 0.35 * rng.normal(scale=noise_level * amplitude, size=structure.shape)
        gxy_m = gxy + 0.50 * rng.normal(scale=noise_level * amplitude, size=structure.shape)

        stress = stress_from_parameters(structure, exx, eyy, gxy, p)
        true_force = average_force_from_stress(stress, structure.mask)
        measured_force = true_force + rng.normal(scale=noise_level * np.maximum(np.abs(true_force), 0.03))
        load_cases.append(
            LoadCase(
                name=name,
                exx=exx_m,
                eyy=eyy_m,
                gxy=gxy_m,
                true_force=true_force,
                measured_force=measured_force,
            )
        )
    return load_cases


def global_force_system(structure: StructuralFields, load_cases: Iterable[LoadCase]) -> tuple[np.ndarray, np.ndarray, list[str]]:
    """Assemble a linear inverse problem from global force components."""

    rows: list[np.ndarray] = []
    observations: list[float] = []
    labels: list[str] = []
    for case in load_cases:
        basis = stress_design_basis(structure, case.exx, case.eyy, case.gxy)
        reduced = np.nanmean(basis[structure.mask], axis=0)  # 3 components by 4 parameters
        for component, name in enumerate(("Fx", "Fy", "Fxy")):
            rows.append(reduced[component])
            observations.append(float(case.measured_force[component]))
            labels.append(f"{case.name}:{name}")
    return np.vstack(rows), np.asarray(observations), labels


def virtual_field_weights(structure: StructuralFields) -> dict[str, np.ndarray]:
    """Smooth virtual fields used to create additional weighted-work equations."""

    x, y = structure.x, structure.y
    weights = {
        "left": np.clip(1.0 - 2.0 * x, 0.0, 1.0),
        "right": np.clip(2.0 * x - 1.0, 0.0, 1.0),
        "bottom": np.clip(1.0 - 2.0 * y, 0.0, 1.0),
        "top": np.clip(2.0 * y - 1.0, 0.0, 1.0),
        "center": np.exp(-((x - 0.5) ** 2 + (y - 0.5) ** 2) / 0.10),
    }
    for key, value in list(weights.items()):
        value = value * structure.mask
        weights[key] = value / (np.nanmean(value[structure.mask]) + 1.0e-12)
    return weights


def virtual_field_system(
    structure: StructuralFields,
    load_cases: Iterable[LoadCase],
    true_parameters: ArrayLike | ConstitutiveParameters,
    noise_level: float = 0.01,
    seed: int = 29,
) -> tuple[np.ndarray, np.ndarray, list[str]]:
    """Assemble a verification-style virtual-fields inverse problem.

    In a real VFM experiment, the right-hand side comes from measured boundary work. In
    this synthetic benchmark it is generated from the known model and then perturbed, so
    the complete inverse pipeline can be checked against ground truth.
    """

    rng = np.random.default_rng(seed)
    p = true_parameters.as_vector() if isinstance(true_parameters, ConstitutiveParameters) else np.asarray(true_parameters, dtype=float)
    weights = virtual_field_weights(structure)
    rows: list[np.ndarray] = []
    observations: list[float] = []
    labels: list[str] = []
    for case in load_cases:
        basis = stress_design_basis(structure, case.exx, case.eyy, case.gxy)
        for weight_name, weight in weights.items():
            for component, component_name in enumerate(("xx", "yy", "xy")):
                row = np.nanmean((weight[..., None] * basis[..., component, :])[structure.mask], axis=0)
                y = float(row @ p)
                y += float(rng.normal(scale=noise_level * max(abs(y), 0.02)))
                rows.append(row)
                observations.append(y)
                labels.append(f"{case.name}:{weight_name}:sigma_{component_name}")
    return np.vstack(rows), np.asarray(observations), labels


def solve_nonnegative_least_squares(A: np.ndarray, y: np.ndarray, method: str) -> CalibrationResult:
    """Solve a non-negative parameter identification problem."""

    result = lsq_linear(A, y, bounds=(0.0, np.inf), lsmr_tol="auto")
    predicted = A @ result.x
    condition = float(np.linalg.cond(A)) if A.shape[0] >= A.shape[1] else float("inf")
    return CalibrationResult(
        method=method,
        parameters=result.x,
        predicted_observations=predicted,
        residual_norm=float(np.linalg.norm(predicted - y) / np.sqrt(max(len(y), 1))),
        condition_number=condition,
    )


def inverse_fe_like_calibration(
    structure: StructuralFields,
    load_cases: Iterable[LoadCase],
    initial: ArrayLike | None = None,
) -> CalibrationResult:
    """Calibrate positive parameters through a nonlinear optimizer.

    This mirrors the control flow of inverse FE calibration: propose material parameters,
    run a forward model, compare predicted reactions with measurements and update the
    parameters. The tutorial forward model is analytical, so the routine remains fast.
    """

    A, y, _ = global_force_system(structure, load_cases)
    if initial is None:
        initial = np.array([15.0, 20.0, 120.0, 50.0])
    initial = np.maximum(np.asarray(initial, dtype=float), 1.0e-6)
    scale = np.maximum(np.abs(y), 0.05)

    def residual(log_p: np.ndarray) -> np.ndarray:
        p = np.exp(log_p)
        data_residual = (A @ p - y) / scale
        prior_residual = 0.01 * (np.log(p) - np.log(initial))
        return np.concatenate([data_residual, prior_residual])

    opt = least_squares(residual, np.log(initial), max_nfev=2000, xtol=1.0e-12, ftol=1.0e-12)
    p = np.exp(opt.x)
    predicted = A @ p
    condition = float(np.linalg.cond(A)) if A.shape[0] >= A.shape[1] else float("inf")
    return CalibrationResult(
        method="inverse_fe_like",
        parameters=p,
        predicted_observations=predicted,
        residual_norm=float(np.linalg.norm(predicted - y) / np.sqrt(max(len(y), 1))),
        condition_number=condition,
    )


def bayesian_linear_calibration(
    A: np.ndarray,
    y: np.ndarray,
    prior_mean: ArrayLike,
    prior_std: ArrayLike,
    noise_std: float | ArrayLike,
) -> dict[str, np.ndarray | float]:
    """Gaussian posterior for a linearized calibration problem."""

    prior_mean = np.asarray(prior_mean, dtype=float)
    prior_std = np.asarray(prior_std, dtype=float)
    if np.isscalar(noise_std):
        noise_var = np.full_like(y, float(noise_std) ** 2, dtype=float)
    else:
        noise_var = np.asarray(noise_std, dtype=float) ** 2
    precision = A.T @ (A / noise_var[:, None]) + np.diag(1.0 / np.maximum(prior_std, 1.0e-12) ** 2)
    covariance = np.linalg.inv(precision)
    right = A.T @ (y / noise_var) + prior_mean / np.maximum(prior_std, 1.0e-12) ** 2
    mean = covariance @ right
    predicted = A @ mean
    residual = y - predicted
    return {
        "mean": mean,
        "std": np.sqrt(np.diag(covariance)),
        "covariance": covariance,
        "predicted": predicted,
        "residual_norm": float(np.linalg.norm(residual) / np.sqrt(max(len(y), 1))),
        "condition_number": float(np.linalg.cond(A)),
    }


def parameter_maps(structure: StructuralFields, parameters: ArrayLike | ConstitutiveParameters) -> dict[str, np.ndarray]:
    """Convert calibrated global parameters into spatial material maps."""

    p = parameters.as_vector() if isinstance(parameters, ConstitutiveParameters) else np.asarray(parameters, dtype=float)
    order = structural_order_from_kappa(structure.kappa)
    matrix_modulus = p[0] + p[1] * structure.rho_f
    fiber_modulus = p[2] * structure.rho_f * order + p[3] * structure.connectivity * order
    total_stiffness_index = matrix_modulus + fiber_modulus
    anisotropy_index = fiber_modulus / np.maximum(matrix_modulus, 1.0e-12)
    return {
        "matrix_modulus": matrix_modulus,
        "fiber_modulus": fiber_modulus,
        "total_stiffness_index": total_stiffness_index,
        "anisotropy_index": anisotropy_index,
        "structural_order": order,
    }


def summarize_parameter_maps(structure: StructuralFields, maps: dict[str, np.ndarray]) -> dict[str, float]:
    """Return compact scalar summaries for benchmark tables."""

    active = structure.mask
    summary: dict[str, float] = {}
    for name, values in maps.items():
        v = values[active]
        summary[f"{name}_mean"] = float(np.nanmean(v))
        summary[f"{name}_std"] = float(np.nanstd(v))
        summary[f"{name}_p05"] = float(np.nanpercentile(v, 5.0))
        summary[f"{name}_p95"] = float(np.nanpercentile(v, 95.0))
    return summary


def identifiability_metrics(A: np.ndarray) -> dict[str, np.ndarray | float]:
    """Singular-value diagnostics for the inverse problem."""

    _, singular_values, vh = np.linalg.svd(A, full_matrices=False)
    condition = float(singular_values[0] / max(singular_values[-1], 1.0e-15))
    return {
        "singular_values": singular_values,
        "condition_number": condition,
        "least_identifiable_direction": vh[-1],
    }


def benchmark_calibration(seed: int = 19, force_noise: float = 0.015) -> dict[str, object]:
    """Run the complete Tutorial 19 synthetic identification benchmark."""

    structure = build_synthetic_structural_fields(seed=seed)
    truth = true_parameter_set()
    load_cases = build_synthetic_load_cases(structure, truth, noise_level=force_noise, seed=seed + 100)

    A_global, y_global, labels_global = global_force_system(structure, load_cases)
    global_result = solve_nonnegative_least_squares(A_global, y_global, method="load_curve_only")

    A_virtual, y_virtual, labels_virtual = virtual_field_system(structure, load_cases, truth, noise_level=force_noise, seed=seed + 200)
    virtual_result = solve_nonnegative_least_squares(A_virtual, y_virtual, method="virtual_fields")

    A_joint = np.vstack([A_global, A_virtual])
    y_joint = np.concatenate([y_global, y_virtual])
    joint_result = solve_nonnegative_least_squares(A_joint, y_joint, method="joint_global_plus_vfm")

    inverse_result = inverse_fe_like_calibration(structure, load_cases)

    prior_mean = np.array([16.0, 20.0, 130.0, 55.0])
    prior_std = np.array([8.0, 12.0, 70.0, 35.0])
    noise_std = np.maximum(0.015 * np.abs(y_joint), 0.01)
    posterior = bayesian_linear_calibration(A_joint, y_joint, prior_mean, prior_std, noise_std)

    return {
        "structure": structure,
        "truth": truth,
        "load_cases": load_cases,
        "global_system": (A_global, y_global, labels_global),
        "virtual_system": (A_virtual, y_virtual, labels_virtual),
        "joint_system": (A_joint, y_joint),
        "results": [global_result, virtual_result, joint_result, inverse_result],
        "posterior": posterior,
        "maps_true": parameter_maps(structure, truth),
        "maps_joint": parameter_maps(structure, joint_result.parameters),
        "identifiability": identifiability_metrics(A_joint),
    }
