"""Stress-driven isotropic volumetric growth models and verification utilities.

The module builds on the multiplicative split ``F = Fe Fg`` and restricts the
local growth tensor to ``Fg = Jg**(1/3) I``.  It is deliberately explicit about
stress measures, homeostatic targets, boundary control, growth/resorption,
regularisation, and numerical updates.  All values are synthetic teaching
parameters and must not be interpreted as tissue-specific calibration.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

import numpy as np
from scipy.optimize import brentq

from .growth_kinematics import (
    GrowthMaterialParameters,
    elastic_cauchy_stress,
    elastic_energy_density,
    mandel_stress,
    multiplicative_decomposition,
)

ArrayLike = np.ndarray | Sequence[float]


@dataclass(frozen=True)
class VolumetricGrowthLawParameters:
    """Parameters for ``d ln(Jg) / dt = k R(error)``."""

    rate: float = 0.08
    target: float = 0.0
    scale: float = 1.0
    measure: str = "mean_mandel"
    dead_zone: float = 0.0
    response_limit: float | None = 1.0
    tensile_gain: float = 1.0
    compressive_gain: float = 1.0
    allow_resorption: bool = True
    jg_min: float = 0.20
    jg_max: float = 5.0

    def validate(self) -> None:
        if self.rate < 0.0:
            raise ValueError("rate must be nonnegative")
        if self.scale <= 0.0:
            raise ValueError("scale must be positive")
        if self.measure not in {
            "mean_mandel",
            "mean_cauchy",
            "pressure",
            "von_mises",
            "max_principal",
            "energy",
        }:
            raise ValueError("unsupported stress or energy measure")
        if self.dead_zone < 0.0:
            raise ValueError("dead_zone must be nonnegative")
        if self.response_limit is not None and self.response_limit <= 0.0:
            raise ValueError("response_limit must be positive when provided")
        if self.tensile_gain < 0.0 or self.compressive_gain < 0.0:
            raise ValueError("response gains must be nonnegative")
        if self.jg_min <= 0.0 or self.jg_max <= self.jg_min:
            raise ValueError("growth bounds must satisfy 0 < jg_min < jg_max")


def _matrix3(value: ArrayLike, name: str) -> np.ndarray:
    matrix = np.asarray(value, dtype=float)
    if matrix.shape != (3, 3):
        raise ValueError(f"{name} must have shape (3, 3)")
    if not np.all(np.isfinite(matrix)):
        raise ValueError(f"{name} must contain finite values")
    if np.linalg.det(matrix) <= 0.0:
        raise ValueError(f"{name} must have positive determinant")
    return matrix


def _time_values(time: Iterable[float] | np.ndarray) -> np.ndarray:
    values = np.asarray(time, dtype=float)
    if values.ndim != 1 or values.size < 2:
        raise ValueError("time must be one-dimensional with at least two values")
    if not np.all(np.isfinite(values)) or not np.all(np.diff(values) > 0.0):
        raise ValueError("time must be finite and strictly increasing")
    return values


def _deformation_history(F: ArrayLike, count: int) -> np.ndarray:
    values = np.asarray(F, dtype=float)
    if values.shape == (3, 3):
        values = np.repeat(values[None, :, :], count, axis=0)
    if values.shape != (count, 3, 3):
        raise ValueError(f"F must have shape (3,3) or ({count},3,3)")
    for index, matrix in enumerate(values):
        _matrix3(matrix, f"F[{index}]")
    return values


def isotropic_growth_tensor(volume_ratio: float) -> np.ndarray:
    """Return ``Fg = Jg^(1/3) I`` for positive growth volume ratio ``Jg``."""

    if not np.isfinite(volume_ratio) or volume_ratio <= 0.0:
        raise ValueError("volume_ratio must be positive and finite")
    return float(volume_ratio) ** (1.0 / 3.0) * np.eye(3)


def stress_invariants(stress: ArrayLike) -> dict[str, float | np.ndarray]:
    """Return sign-explicit invariants for a symmetric Cauchy-like stress tensor.

    Tension is positive.  Consequently ``mean_stress = tr(stress)/3`` and
    ``pressure = -mean_stress``.
    """

    tensor = np.asarray(stress, dtype=float)
    if tensor.shape != (3, 3):
        raise ValueError("stress must have shape (3, 3)")
    symmetric = 0.5 * (tensor + tensor.T)
    mean_stress = float(np.trace(symmetric) / 3.0)
    deviator = symmetric - mean_stress * np.eye(3)
    von_mises = float(np.sqrt(1.5 * np.sum(deviator * deviator)))
    principal = np.linalg.eigvalsh(symmetric)
    return {
        "mean_stress": mean_stress,
        "pressure": -mean_stress,
        "deviator": deviator,
        "von_mises": von_mises,
        "principal": principal,
        "max_principal": float(principal[-1]),
        "min_principal": float(principal[0]),
    }


def evaluate_growth_stimulus(
    F: ArrayLike,
    volume_ratio: float,
    measure: str = "mean_mandel",
    material: GrowthMaterialParameters | None = None,
) -> dict[str, float | np.ndarray]:
    """Evaluate elastic state and the selected scalar growth stimulus."""

    total = _matrix3(F, "F")
    growth = isotropic_growth_tensor(volume_ratio)
    elastic, _ = multiplicative_decomposition(total, growth)
    cauchy = elastic_cauchy_stress(elastic, material)
    mandel = mandel_stress(elastic, material)
    energy = elastic_energy_density(elastic, material)
    cauchy_invariants = stress_invariants(cauchy)
    mandel_invariants = stress_invariants(mandel)

    if measure == "mean_mandel":
        stimulus = mandel_invariants["mean_stress"]
    elif measure == "mean_cauchy":
        stimulus = cauchy_invariants["mean_stress"]
    elif measure == "pressure":
        stimulus = cauchy_invariants["pressure"]
    elif measure == "von_mises":
        stimulus = cauchy_invariants["von_mises"]
    elif measure == "max_principal":
        stimulus = cauchy_invariants["max_principal"]
    elif measure == "energy":
        stimulus = energy
    else:
        raise ValueError("unsupported stress or energy measure")

    return {
        "stimulus": float(stimulus),
        "Fe": elastic,
        "Fg": growth,
        "cauchy": cauchy,
        "mandel": mandel,
        "energy": float(energy),
        "cauchy_invariants": cauchy_invariants,
        "mandel_invariants": mandel_invariants,
    }


def normalized_homeostatic_error(stimulus: float, target: float, scale: float) -> float:
    """Return dimensionless signed error relative to a stated scale."""

    if scale <= 0.0:
        raise ValueError("scale must be positive")
    return float((stimulus - target) / scale)


def growth_response(error: float, parameters: VolumetricGrowthLawParameters) -> float:
    """Apply dead zone, asymmetric gains, optional resorption, and saturation."""

    parameters.validate()
    active = np.sign(error) * max(abs(error) - parameters.dead_zone, 0.0)
    if active >= 0.0:
        active *= parameters.tensile_gain
    else:
        if not parameters.allow_resorption:
            active = 0.0
        else:
            active *= parameters.compressive_gain
    if parameters.response_limit is not None:
        limit = parameters.response_limit
        active = limit * np.tanh(active / limit)
    return float(active)


def log_volume_growth_rate(
    stimulus: float,
    parameters: VolumetricGrowthLawParameters | None = None,
) -> float:
    """Return ``d ln(Jg)/dt`` for a scalar stimulus."""

    params = parameters or VolumetricGrowthLawParameters()
    params.validate()
    error = normalized_homeostatic_error(stimulus, params.target, params.scale)
    return params.rate * growth_response(error, params)


def volumetric_growth_velocity_gradient(log_jg_rate: float) -> np.ndarray:
    """Return isotropic ``Lg = (d ln Jg/dt)/3 I``."""

    if not np.isfinite(log_jg_rate):
        raise ValueError("log_jg_rate must be finite")
    return float(log_jg_rate) / 3.0 * np.eye(3)


def update_volume_ratio_exponential(
    volume_ratio: float,
    log_jg_rate: float,
    dt: float,
    jg_min: float = 0.20,
    jg_max: float = 5.0,
) -> float:
    """Positivity-preserving exponential update for ``Jg``."""

    if volume_ratio <= 0.0:
        raise ValueError("volume_ratio must be positive")
    if dt < 0.0:
        raise ValueError("dt must be nonnegative")
    if jg_min <= 0.0 or jg_max <= jg_min:
        raise ValueError("growth bounds must satisfy 0 < jg_min < jg_max")
    updated = float(volume_ratio * np.exp(dt * log_jg_rate))
    return float(np.clip(updated, jg_min, jg_max))


def update_volume_ratio_explicit_euler(
    volume_ratio: float,
    log_jg_rate: float,
    dt: float,
) -> float:
    """Naive Euler update included only for numerical-comparison experiments."""

    if volume_ratio <= 0.0:
        raise ValueError("volume_ratio must be positive")
    if dt < 0.0:
        raise ValueError("dt must be nonnegative")
    return float(volume_ratio * (1.0 + dt * log_jg_rate))


def simulate_prescribed_deformation(
    time: Iterable[float] | np.ndarray,
    F: ArrayLike,
    jg0: float = 1.0,
    material: GrowthMaterialParameters | None = None,
    law: VolumetricGrowthLawParameters | None = None,
) -> dict[str, np.ndarray]:
    """Integrate isotropic volumetric growth under prescribed deformation history."""

    t = _time_values(time)
    deformation = _deformation_history(F, t.size)
    parameters = law or VolumetricGrowthLawParameters()
    parameters.validate()
    if jg0 <= 0.0:
        raise ValueError("jg0 must be positive")

    jg = np.empty(t.size)
    stimulus = np.empty(t.size)
    error = np.empty(t.size)
    rate = np.empty(t.size)
    energy = np.empty(t.size)
    mean_cauchy = np.empty(t.size)
    mean_mandel = np.empty(t.size)
    von_mises = np.empty(t.size)
    elastic_jacobian = np.empty(t.size)
    dissipation_indicator = np.empty(t.size)
    jg[0] = jg0

    for index in range(t.size):
        state = evaluate_growth_stimulus(
            deformation[index], jg[index], parameters.measure, material
        )
        stimulus[index] = float(state["stimulus"])
        error[index] = normalized_homeostatic_error(
            stimulus[index], parameters.target, parameters.scale
        )
        rate[index] = parameters.rate * growth_response(error[index], parameters)
        energy[index] = float(state["energy"])
        mean_cauchy[index] = float(state["cauchy_invariants"]["mean_stress"])
        mean_mandel[index] = float(state["mandel_invariants"]["mean_stress"])
        von_mises[index] = float(state["cauchy_invariants"]["von_mises"])
        elastic_jacobian[index] = float(np.linalg.det(state["Fe"]))
        lg = volumetric_growth_velocity_gradient(rate[index])
        dissipation_indicator[index] = float(np.sum(state["mandel"] * lg))
        if index < t.size - 1:
            jg[index + 1] = update_volume_ratio_exponential(
                jg[index],
                rate[index],
                t[index + 1] - t[index],
                parameters.jg_min,
                parameters.jg_max,
            )

    return {
        "time": t,
        "F": deformation,
        "Jg": jg,
        "stimulus": stimulus,
        "error": error,
        "log_jg_rate": rate,
        "energy": energy,
        "mean_cauchy": mean_cauchy,
        "mean_mandel": mean_mandel,
        "von_mises": von_mises,
        "Je": elastic_jacobian,
        "dissipation_indicator": dissipation_indicator,
    }


def isotropic_elastic_stretch_for_mean_cauchy(
    mean_cauchy: float,
    material: GrowthMaterialParameters | None = None,
    lower: float = 0.20,
    upper: float = 5.0,
) -> float:
    """Solve the isotropic elastic stretch producing a prescribed mean Cauchy stress."""

    if lower <= 0.0 or upper <= lower:
        raise ValueError("stretch bracket must satisfy 0 < lower < upper")

    def residual(alpha: float) -> float:
        stress = elastic_cauchy_stress(alpha * np.eye(3), material)
        return float(np.trace(stress) / 3.0 - mean_cauchy)

    if residual(lower) * residual(upper) > 0.0:
        raise ValueError("prescribed stress is outside the supplied stretch bracket")
    return float(brentq(residual, lower, upper))


def simulate_prescribed_mean_stress(
    time: Iterable[float] | np.ndarray,
    mean_stress: float | Sequence[float] | np.ndarray,
    jg0: float = 1.0,
    material: GrowthMaterialParameters | None = None,
    law: VolumetricGrowthLawParameters | None = None,
) -> dict[str, np.ndarray]:
    """Integrate growth while isotropic mean Cauchy stress is externally controlled.

    Under ideal stress control the elastic stretch is fixed by the imposed stress.
    Growth changes the total size but cannot change the controlled stress itself.
    """

    t = _time_values(time)
    values = np.asarray(mean_stress, dtype=float)
    if values.ndim == 0:
        values = np.full(t.size, float(values))
    if values.shape != (t.size,):
        raise ValueError("mean_stress must be scalar or match time")
    parameters = law or VolumetricGrowthLawParameters(measure="mean_cauchy")
    parameters.validate()
    if jg0 <= 0.0:
        raise ValueError("jg0 must be positive")

    jg = np.empty(t.size)
    elastic_stretch = np.empty(t.size)
    total_stretch = np.empty(t.size)
    stimulus = np.empty(t.size)
    error = np.empty(t.size)
    rate = np.empty(t.size)
    jg[0] = jg0

    for index, imposed in enumerate(values):
        elastic_stretch[index] = isotropic_elastic_stretch_for_mean_cauchy(
            imposed, material
        )
        total_stretch[index] = elastic_stretch[index] * jg[index] ** (1.0 / 3.0)
        if parameters.measure == "mean_cauchy":
            stimulus[index] = imposed
        else:
            state = evaluate_growth_stimulus(
                total_stretch[index] * np.eye(3), jg[index], parameters.measure, material
            )
            stimulus[index] = float(state["stimulus"])
        error[index] = normalized_homeostatic_error(
            stimulus[index], parameters.target, parameters.scale
        )
        rate[index] = parameters.rate * growth_response(error[index], parameters)
        if index < t.size - 1:
            jg[index + 1] = update_volume_ratio_exponential(
                jg[index],
                rate[index],
                t[index + 1] - t[index],
                parameters.jg_min,
                parameters.jg_max,
            )

    return {
        "time": t,
        "mean_stress": values,
        "Jg": jg,
        "elastic_stretch": elastic_stretch,
        "total_stretch": total_stretch,
        "stimulus": stimulus,
        "error": error,
        "log_jg_rate": rate,
    }


def mass_ratio_from_growth(volume_ratio: ArrayLike, density_ratio: ArrayLike = 1.0) -> np.ndarray:
    """Return mass ratio ``m/m0 = (rho/rho0) Jg``."""

    jg = np.asarray(volume_ratio, dtype=float)
    density = np.asarray(density_ratio, dtype=float)
    if np.any(jg <= 0.0) or np.any(density <= 0.0):
        raise ValueError("volume and density ratios must be positive")
    return density * jg


def density_ratio_from_mass(volume_ratio: ArrayLike, mass_ratio: ArrayLike) -> np.ndarray:
    """Return density ratio implied by independent mass and volume changes."""

    jg = np.asarray(volume_ratio, dtype=float)
    mass = np.asarray(mass_ratio, dtype=float)
    if np.any(jg <= 0.0) or np.any(mass <= 0.0):
        raise ValueError("volume and mass ratios must be positive")
    return mass / jg


def homeostatic_band_value(
    stimulus: ArrayLike,
    target: float,
    half_width: float,
    scale: float = 1.0,
) -> np.ndarray:
    """Signed distance from a scalar homeostatic band in normalized units."""

    if half_width < 0.0 or scale <= 0.0:
        raise ValueError("half_width must be nonnegative and scale positive")
    error = (np.asarray(stimulus, dtype=float) - target) / scale
    return np.sign(error) * np.maximum(np.abs(error) - half_width, 0.0)


def linearized_log_growth_eigenvalue(
    F: ArrayLike,
    jg_equilibrium: float,
    law: VolumetricGrowthLawParameters,
    material: GrowthMaterialParameters | None = None,
    perturbation: float = 1.0e-5,
) -> float:
    """Numerically linearise ``d ln(Jg)/dt`` about a proposed equilibrium."""

    if perturbation <= 0.0:
        raise ValueError("perturbation must be positive")
    law.validate()
    x0 = np.log(jg_equilibrium)

    def rhs(log_jg: float) -> float:
        state = evaluate_growth_stimulus(F, np.exp(log_jg), law.measure, material)
        return log_volume_growth_rate(float(state["stimulus"]), law)

    return float((rhs(x0 + perturbation) - rhs(x0 - perturbation)) / (2.0 * perturbation))


def laplacian_neumann_1d(values: ArrayLike, dx: float) -> np.ndarray:
    """Second derivative with zero-flux boundary conditions."""

    field = np.asarray(values, dtype=float)
    if field.ndim != 1 or field.size < 3:
        raise ValueError("values must be one-dimensional with at least three entries")
    if dx <= 0.0:
        raise ValueError("dx must be positive")
    padded = np.pad(field, 1, mode="edge")
    return (padded[:-2] - 2.0 * padded[1:-1] + padded[2:]) / dx**2


def simulate_spatial_growth_field(
    time: Iterable[float] | np.ndarray,
    position: ArrayLike,
    total_deformation: ArrayLike,
    initial_jg: ArrayLike,
    target: ArrayLike,
    law: VolumetricGrowthLawParameters | None = None,
    material: GrowthMaterialParameters | None = None,
    diffusivity: float = 0.0,
) -> dict[str, np.ndarray]:
    """Integrate a one-dimensional heterogeneous volumetric-growth field.

    Each material point shares the prescribed total deformation.  A Laplacian
    term in ``ln(Jg)`` can be enabled as a transparent regularisation device.
    This is a local toy problem, not a finite-element equilibrium solution.
    """

    t = _time_values(time)
    x = np.asarray(position, dtype=float)
    if x.ndim != 1 or x.size < 3 or not np.all(np.diff(x) > 0.0):
        raise ValueError("position must be strictly increasing and one-dimensional")
    if not np.allclose(np.diff(x), np.diff(x)[0], rtol=1.0e-5, atol=1.0e-12):
        raise ValueError("position must be uniformly spaced")
    deformation = _matrix3(total_deformation, "total_deformation")
    initial = np.asarray(initial_jg, dtype=float)
    targets = np.asarray(target, dtype=float)
    if initial.shape != x.shape or targets.shape != x.shape:
        raise ValueError("initial_jg and target must match position")
    if np.any(initial <= 0.0):
        raise ValueError("initial_jg must be positive")
    if diffusivity < 0.0:
        raise ValueError("diffusivity must be nonnegative")

    parameters = law or VolumetricGrowthLawParameters()
    parameters.validate()
    dx = float(x[1] - x[0])
    jg = np.empty((t.size, x.size))
    stimulus = np.empty_like(jg)
    error = np.empty_like(jg)
    local_rate = np.empty_like(jg)
    jg[0] = initial

    for step in range(t.size):
        for point in range(x.size):
            state = evaluate_growth_stimulus(
                deformation, jg[step, point], parameters.measure, material
            )
            stimulus[step, point] = float(state["stimulus"])
            error[step, point] = normalized_homeostatic_error(
                stimulus[step, point], targets[point], parameters.scale
            )
            local_rate[step, point] = parameters.rate * growth_response(
                error[step, point], parameters
            )
        if step < t.size - 1:
            dt = t[step + 1] - t[step]
            log_jg = np.log(jg[step])
            regularized_rate = local_rate[step] + diffusivity * laplacian_neumann_1d(
                log_jg, dx
            )
            candidate = np.exp(log_jg + dt * regularized_rate)
            jg[step + 1] = np.clip(candidate, parameters.jg_min, parameters.jg_max)

    return {
        "time": t,
        "position": x,
        "Jg": jg,
        "stimulus": stimulus,
        "error": error,
        "log_jg_rate": local_rate,
    }
