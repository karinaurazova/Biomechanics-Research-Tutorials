"""Finite-growth kinematics and verification-oriented morphoelastic models.

The module implements the multiplicative split ``F = Fe Fg`` together with
transparent utilities for homogeneous stress-driven growth, anisotropic growth
tensors, incompatibility diagnostics, and a reduced differential-growth strip.
All parameters are synthetic teaching values; the code is not calibrated to a
particular tissue, animal, patient, or experiment.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

import numpy as np
from scipy.linalg import expm
from scipy.integrate import trapezoid


ArrayLike = np.ndarray | Sequence[float]


@dataclass(frozen=True)
class GrowthMaterialParameters:
    """Compressible neo-Hookean parameters for the elastic accommodation."""

    shear_modulus: float = 1.0
    bulk_modulus: float = 50.0

    def validate(self) -> None:
        if self.shear_modulus <= 0.0:
            raise ValueError("shear_modulus must be positive")
        if self.bulk_modulus <= 0.0:
            raise ValueError("bulk_modulus must be positive")


@dataclass(frozen=True)
class GrowthLawParameters:
    """Parameters for a Mandel-stress-driven growth update."""

    rate: float = 0.08
    target_mandel: float = 0.0
    mode: str = "diagonal"
    dead_zone: float = 0.0
    response_limit: float | None = 0.20
    allow_resorption: bool = True
    growth_min: float = 0.25
    growth_max: float = 4.0

    def validate(self) -> None:
        if self.rate < 0.0:
            raise ValueError("rate must be nonnegative")
        if self.mode not in {"isotropic", "diagonal", "symmetric"}:
            raise ValueError("mode must be isotropic, diagonal, or symmetric")
        if self.dead_zone < 0.0:
            raise ValueError("dead_zone must be nonnegative")
        if self.response_limit is not None and self.response_limit <= 0.0:
            raise ValueError("response_limit must be positive when provided")
        if self.growth_min <= 0.0:
            raise ValueError("growth_min must be positive")
        if self.growth_max <= self.growth_min:
            raise ValueError("growth_max must exceed growth_min")


def _matrix3(value: ArrayLike, name: str) -> np.ndarray:
    matrix = np.asarray(value, dtype=float)
    if matrix.shape != (3, 3):
        raise ValueError(f"{name} must have shape (3, 3)")
    if not np.all(np.isfinite(matrix)):
        raise ValueError(f"{name} must contain finite values")
    return matrix


def _positive_determinant(matrix: np.ndarray, name: str) -> float:
    determinant = float(np.linalg.det(matrix))
    if determinant <= 0.0:
        raise ValueError(f"{name} must have positive determinant")
    return determinant


def _unit(vector: ArrayLike, name: str) -> np.ndarray:
    values = np.asarray(vector, dtype=float)
    if values.shape != (3,):
        raise ValueError(f"{name} must have shape (3,)")
    norm = float(np.linalg.norm(values))
    if norm <= 0.0:
        raise ValueError(f"{name} must be nonzero")
    return values / norm


def material_basis(fiber: ArrayLike, sheet: ArrayLike | None = None) -> np.ndarray:
    """Return a right-handed orthonormal basis with columns ``fiber, sheet, normal``."""

    f = _unit(fiber, "fiber")
    if sheet is None:
        candidates = np.eye(3)
        trial = candidates[np.argmin(np.abs(candidates @ f))]
    else:
        trial = np.asarray(sheet, dtype=float)
        if trial.shape != (3,):
            raise ValueError("sheet must have shape (3,)")
    s_raw = trial - np.dot(trial, f) * f
    s = _unit(s_raw, "sheet after orthogonalization")
    n = np.cross(f, s)
    n = _unit(n, "normal")
    s = np.cross(n, f)
    return np.column_stack((f, s, n))


def rotation_matrix(axis: ArrayLike, angle: float) -> np.ndarray:
    """Return a proper orthogonal rotation matrix from axis-angle data."""

    a = _unit(axis, "axis")
    skew = np.array(
        [[0.0, -a[2], a[1]], [a[2], 0.0, -a[0]], [-a[1], a[0], 0.0]]
    )
    identity = np.eye(3)
    return identity + np.sin(angle) * skew + (1.0 - np.cos(angle)) * (skew @ skew)


def growth_tensor_isotropic(
    linear_growth: float | None = None,
    volume_ratio: float | None = None,
) -> np.ndarray:
    """Construct isotropic growth from a linear stretch or volume ratio ``Jg``."""

    if (linear_growth is None) == (volume_ratio is None):
        raise ValueError("provide exactly one of linear_growth or volume_ratio")
    if volume_ratio is not None:
        if volume_ratio <= 0.0:
            raise ValueError("volume_ratio must be positive")
        linear_growth = float(volume_ratio) ** (1.0 / 3.0)
    assert linear_growth is not None
    if linear_growth <= 0.0:
        raise ValueError("linear_growth must be positive")
    return float(linear_growth) * np.eye(3)


def growth_tensor_orthotropic(
    stretches: ArrayLike,
    basis: np.ndarray | None = None,
) -> np.ndarray:
    """Construct an orthotropic growth tensor in a supplied material basis."""

    principal = np.asarray(stretches, dtype=float)
    if principal.shape != (3,):
        raise ValueError("stretches must have shape (3,)")
    if np.any(principal <= 0.0):
        raise ValueError("growth stretches must be positive")
    q = np.eye(3) if basis is None else _matrix3(basis, "basis")
    if not np.allclose(q.T @ q, np.eye(3), atol=1.0e-10):
        raise ValueError("basis must be orthonormal")
    if np.linalg.det(q) <= 0.0:
        raise ValueError("basis must be right-handed")
    return q @ np.diag(principal) @ q.T


def growth_tensor_transversely_isotropic(
    fiber_growth: float,
    transverse_growth: float,
    fiber: ArrayLike = (1.0, 0.0, 0.0),
) -> np.ndarray:
    """Construct a transversely isotropic growth tensor about ``fiber``."""

    if fiber_growth <= 0.0 or transverse_growth <= 0.0:
        raise ValueError("growth stretches must be positive")
    a = _unit(fiber, "fiber")
    projector = np.outer(a, a)
    return fiber_growth * projector + transverse_growth * (np.eye(3) - projector)


def multiplicative_decomposition(F: ArrayLike, Fg: ArrayLike) -> tuple[np.ndarray, np.ndarray]:
    """Return ``Fe`` and a validated copy of ``Fg`` for ``F = Fe Fg``."""

    total = _matrix3(F, "F")
    growth = _matrix3(Fg, "Fg")
    _positive_determinant(total, "F")
    _positive_determinant(growth, "Fg")
    elastic = total @ np.linalg.inv(growth)
    _positive_determinant(elastic, "Fe")
    return elastic, growth.copy()


def jacobian_bookkeeping(F: ArrayLike, Fg: ArrayLike) -> dict[str, float]:
    """Return ``J``, ``Je``, ``Jg``, and the multiplicative determinant error."""

    elastic, growth = multiplicative_decomposition(F, Fg)
    total = _matrix3(F, "F")
    j = _positive_determinant(total, "F")
    je = _positive_determinant(elastic, "Fe")
    jg = _positive_determinant(growth, "Fg")
    return {"J": j, "Je": je, "Jg": jg, "error": j - je * jg}


def elastic_energy_density(
    Fe: ArrayLike,
    parameters: GrowthMaterialParameters | None = None,
) -> float:
    """Compressible neo-Hookean energy per unit grown stress-free volume."""

    params = parameters or GrowthMaterialParameters()
    params.validate()
    elastic = _matrix3(Fe, "Fe")
    je = _positive_determinant(elastic, "Fe")
    i1 = float(np.trace(elastic.T @ elastic))
    log_je = np.log(je)
    return float(
        0.5 * params.shear_modulus * (i1 - 3.0 - 2.0 * log_je)
        + 0.5 * params.bulk_modulus * log_je**2
    )


def elastic_first_piola(
    Fe: ArrayLike,
    parameters: GrowthMaterialParameters | None = None,
) -> np.ndarray:
    """First Piola stress conjugate to ``Fe`` for the elastic energy."""

    params = parameters or GrowthMaterialParameters()
    params.validate()
    elastic = _matrix3(Fe, "Fe")
    je = _positive_determinant(elastic, "Fe")
    inverse_transpose = np.linalg.inv(elastic).T
    return (
        params.shear_modulus * (elastic - inverse_transpose)
        + params.bulk_modulus * np.log(je) * inverse_transpose
    )


def total_reference_energy(
    F: ArrayLike,
    Fg: ArrayLike,
    parameters: GrowthMaterialParameters | None = None,
) -> float:
    """Energy per original reference volume using ``Psi = Jg W(Fe)``."""

    elastic, growth = multiplicative_decomposition(F, Fg)
    return _positive_determinant(growth, "Fg") * elastic_energy_density(elastic, parameters)


def total_first_piola(
    F: ArrayLike,
    Fg: ArrayLike,
    parameters: GrowthMaterialParameters | None = None,
) -> np.ndarray:
    """Stress conjugate to total ``F`` for ``Psi(F,Fg) = Jg W(F Fg^-1)``."""

    elastic, growth = multiplicative_decomposition(F, Fg)
    jg = _positive_determinant(growth, "Fg")
    return jg * elastic_first_piola(elastic, parameters) @ np.linalg.inv(growth).T


def elastic_cauchy_stress(
    Fe: ArrayLike,
    parameters: GrowthMaterialParameters | None = None,
) -> np.ndarray:
    """Elastic Cauchy stress in the current configuration."""

    elastic = _matrix3(Fe, "Fe")
    je = _positive_determinant(elastic, "Fe")
    return elastic_first_piola(elastic, parameters) @ elastic.T / je


def mandel_stress(
    Fe: ArrayLike,
    parameters: GrowthMaterialParameters | None = None,
) -> np.ndarray:
    """Return the Mandel stress ``M = Fe^T Pe`` conjugate to growth rate."""

    elastic = _matrix3(Fe, "Fe")
    return elastic.T @ elastic_first_piola(elastic, parameters)


def push_forward_direction(F: ArrayLike, direction: ArrayLike) -> np.ndarray:
    """Push a material direction forward and normalize it."""

    total = _matrix3(F, "F")
    a0 = _unit(direction, "direction")
    return _unit(total @ a0, "pushed direction")


def growth_velocity_gradient(
    mandel: ArrayLike,
    parameters: GrowthLawParameters | None = None,
    target: ArrayLike | float | None = None,
) -> np.ndarray:
    """Map Mandel-stress error to a symmetric growth velocity gradient ``Lg``."""

    params = parameters or GrowthLawParameters()
    params.validate()
    stress = _matrix3(mandel, "mandel")
    symmetric = 0.5 * (stress + stress.T)
    if target is None:
        target_matrix = params.target_mandel * np.eye(3)
    else:
        target_array = np.asarray(target, dtype=float)
        if target_array.ndim == 0:
            target_matrix = float(target_array) * np.eye(3)
        else:
            target_matrix = _matrix3(target_array, "target")
    error = symmetric - target_matrix

    if params.mode == "isotropic":
        error = np.trace(error) / 3.0 * np.eye(3)
    elif params.mode == "diagonal":
        error = np.diag(np.diag(error))

    active = np.sign(error) * np.maximum(np.abs(error) - params.dead_zone, 0.0)
    if not params.allow_resorption:
        active = np.maximum(active, 0.0)
    if params.response_limit is not None:
        active = params.response_limit * np.tanh(active / params.response_limit)
    return params.rate * active


def update_growth_tensor(
    Fg: ArrayLike,
    Lg: ArrayLike,
    dt: float,
    growth_min: float = 0.25,
    growth_max: float = 4.0,
) -> np.ndarray:
    """Exponentially update ``Fg`` and clip its singular values to physical bounds."""

    growth = _matrix3(Fg, "Fg")
    velocity = _matrix3(Lg, "Lg")
    _positive_determinant(growth, "Fg")
    if dt < 0.0:
        raise ValueError("dt must be nonnegative")
    if growth_min <= 0.0 or growth_max <= growth_min:
        raise ValueError("growth bounds must satisfy 0 < growth_min < growth_max")
    candidate = expm(dt * velocity) @ growth
    u, singular, vt = np.linalg.svd(candidate)
    clipped = np.clip(singular, growth_min, growth_max)
    updated = u @ np.diag(clipped) @ vt
    if np.linalg.det(updated) <= 0.0:
        u[:, -1] *= -1.0
        updated = u @ np.diag(clipped) @ vt
    _positive_determinant(updated, "updated Fg")
    return updated


def _time_values(time: Iterable[float] | np.ndarray) -> np.ndarray:
    values = np.asarray(time, dtype=float)
    if values.ndim != 1 or values.size < 2:
        raise ValueError("time must be one-dimensional with at least two entries")
    if not np.all(np.diff(values) > 0.0):
        raise ValueError("time must be strictly increasing")
    return values


def _deformation_history(F: ArrayLike, count: int) -> np.ndarray:
    values = np.asarray(F, dtype=float)
    if values.shape == (3, 3):
        values = np.repeat(values[None, :, :], count, axis=0)
    if values.shape != (count, 3, 3):
        raise ValueError(f"F must have shape (3,3) or ({count},3,3)")
    for index, matrix in enumerate(values):
        _positive_determinant(matrix, f"F[{index}]")
    return values


def simulate_stress_driven_growth(
    time: Iterable[float] | np.ndarray,
    F: ArrayLike,
    Fg0: ArrayLike | None = None,
    material: GrowthMaterialParameters | None = None,
    law: GrowthLawParameters | None = None,
    target_mandel: ArrayLike | float | None = None,
) -> dict[str, np.ndarray]:
    """Integrate homogeneous stress-driven growth at a prescribed deformation history."""

    t = _time_values(time)
    deformation = _deformation_history(F, t.size)
    material_parameters = material or GrowthMaterialParameters()
    growth_parameters = law or GrowthLawParameters()
    material_parameters.validate()
    growth_parameters.validate()
    initial_growth = np.eye(3) if Fg0 is None else _matrix3(Fg0, "Fg0")
    _positive_determinant(initial_growth, "Fg0")

    growth = np.empty((t.size, 3, 3))
    elastic = np.empty_like(growth)
    mandel_values = np.empty_like(growth)
    cauchy = np.empty_like(growth)
    piola = np.empty_like(growth)
    energy = np.empty(t.size)
    jacobians = np.empty((t.size, 3))
    dissipation_indicator = np.empty(t.size)
    growth[0] = initial_growth

    for index in range(t.size):
        elastic[index], _ = multiplicative_decomposition(deformation[index], growth[index])
        mandel_values[index] = mandel_stress(elastic[index], material_parameters)
        cauchy[index] = elastic_cauchy_stress(elastic[index], material_parameters)
        piola[index] = total_first_piola(deformation[index], growth[index], material_parameters)
        energy[index] = total_reference_energy(deformation[index], growth[index], material_parameters)
        jacobians[index] = (
            np.linalg.det(deformation[index]),
            np.linalg.det(elastic[index]),
            np.linalg.det(growth[index]),
        )
        velocity = growth_velocity_gradient(
            mandel_values[index], growth_parameters, target_mandel
        )
        dissipation_indicator[index] = float(np.sum(mandel_values[index] * velocity))
        if index < t.size - 1:
            growth[index + 1] = update_growth_tensor(
                growth[index],
                velocity,
                t[index + 1] - t[index],
                growth_parameters.growth_min,
                growth_parameters.growth_max,
            )

    return {
        "time": t,
        "F": deformation,
        "Fg": growth,
        "Fe": elastic,
        "mandel": mandel_values,
        "cauchy": cauchy,
        "piola": piola,
        "energy": energy,
        "jacobians": jacobians,
        "dissipation_indicator": dissipation_indicator,
    }


def compose_growth_increments(increments: Sequence[ArrayLike]) -> np.ndarray:
    """Compose growth increments in the listed chronological order."""

    result = np.eye(3)
    for index, increment in enumerate(increments):
        matrix = _matrix3(increment, f"increments[{index}]")
        _positive_determinant(matrix, f"increments[{index}]")
        result = matrix @ result
    return result


def commutator_norm(A: ArrayLike, B: ArrayLike) -> float:
    """Return the Frobenius norm of ``AB - BA``."""

    first = _matrix3(A, "A")
    second = _matrix3(B, "B")
    return float(np.linalg.norm(first @ second - second @ first))


def row_wise_curl_2d(
    growth_field: np.ndarray,
    dx: float = 1.0,
    dy: float = 1.0,
) -> np.ndarray:
    """Compute the row-wise curl of a 2-D growth-tensor field.

    ``growth_field`` has shape ``(ny, nx, 2, 2)``.  If the field is a gradient
    of a compatible mapping on a simply connected domain, each row-wise curl is
    zero.  This is a pedagogical incompatibility diagnostic, not a replacement
    for a complete geometric compatibility analysis.
    """

    field = np.asarray(growth_field, dtype=float)
    if field.ndim != 4 or field.shape[-2:] != (2, 2):
        raise ValueError("growth_field must have shape (ny, nx, 2, 2)")
    if field.shape[0] < 3 or field.shape[1] < 3:
        raise ValueError("growth_field must contain at least 3 by 3 points")
    if dx <= 0.0 or dy <= 0.0:
        raise ValueError("dx and dy must be positive")
    curl = np.empty(field.shape[:2] + (2,))
    for row in range(2):
        d_fi2_dx = np.gradient(field[..., row, 1], dx, axis=1, edge_order=2)
        d_fi1_dy = np.gradient(field[..., row, 0], dy, axis=0, edge_order=2)
        curl[..., row] = d_fi2_dx - d_fi1_dy
    return curl


def incompatibility_norm_2d(
    growth_field: np.ndarray,
    dx: float = 1.0,
    dy: float = 1.0,
) -> np.ndarray:
    """Return the pointwise norm of the row-wise curl diagnostic."""

    curl = row_wise_curl_2d(growth_field, dx, dy)
    return np.linalg.norm(curl, axis=-1)


def reduced_strip_equilibrium(
    thickness_coordinate: ArrayLike,
    growth_stretch: ArrayLike,
    young_modulus: float = 1.0,
) -> dict[str, np.ndarray | float]:
    """Solve a reduced force- and moment-free differential-growth strip.

    The total axial stretch is approximated by ``lambda(z) = lambda0 + kappa z``.
    A quadratic morphoelastic energy penalizes ``lambda / growth_stretch - 1``.
    This reduced model illustrates curvature generated by incompatible through-
    thickness growth; it is not a full finite-element shell or beam solution.
    """

    z = np.asarray(thickness_coordinate, dtype=float)
    growth = np.asarray(growth_stretch, dtype=float)
    if z.ndim != 1 or z.size < 3:
        raise ValueError("thickness_coordinate must be one-dimensional")
    if growth.shape != z.shape:
        raise ValueError("growth_stretch must match thickness_coordinate")
    if not np.all(np.diff(z) > 0.0):
        raise ValueError("thickness_coordinate must be strictly increasing")
    if np.any(growth <= 0.0):
        raise ValueError("growth_stretch must be positive")
    if young_modulus <= 0.0:
        raise ValueError("young_modulus must be positive")

    design = np.column_stack((1.0 / growth, z / growth))
    target = np.ones_like(z)
    weights = np.gradient(z)
    weighted_design = design * np.sqrt(weights[:, None])
    weighted_target = target * np.sqrt(weights)
    coefficients, *_ = np.linalg.lstsq(weighted_design, weighted_target, rcond=None)
    lambda0, curvature = coefficients
    total_stretch = lambda0 + curvature * z
    elastic_stretch = total_stretch / growth
    strain = elastic_stretch - 1.0
    nominal_stress = young_modulus * strain / growth
    energy_density = 0.5 * young_modulus * strain**2
    force_residual = float(trapezoid(nominal_stress, z))
    moment_residual = float(trapezoid(nominal_stress * z, z))
    energy = float(trapezoid(energy_density, z))
    return {
        "lambda0": float(lambda0),
        "curvature": float(curvature),
        "total_stretch": total_stretch,
        "elastic_stretch": elastic_stretch,
        "nominal_stress": nominal_stress,
        "energy_density": energy_density,
        "force_residual": force_residual,
        "moment_residual": moment_residual,
        "energy": energy,
    }


def finite_difference_first_piola(
    F: ArrayLike,
    Fg: ArrayLike,
    parameters: GrowthMaterialParameters | None = None,
    step: float = 1.0e-6,
) -> np.ndarray:
    """Numerically differentiate total energy with respect to ``F``."""

    total = _matrix3(F, "F")
    growth = _matrix3(Fg, "Fg")
    if step <= 0.0:
        raise ValueError("step must be positive")
    derivative = np.empty((3, 3))
    for row in range(3):
        for column in range(3):
            perturbation = np.zeros((3, 3))
            perturbation[row, column] = step
            plus = total_reference_energy(total + perturbation, growth, parameters)
            minus = total_reference_energy(total - perturbation, growth, parameters)
            derivative[row, column] = (plus - minus) / (2.0 * step)
    return derivative
