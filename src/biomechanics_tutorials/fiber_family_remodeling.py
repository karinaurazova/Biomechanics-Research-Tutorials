"""Fiber-family remodeling models for Tutorial 09.

The module deliberately separates four modelling layers:

1. direct rotation of discrete fiber families;
2. evolution of a continuous axial orientation distribution;
3. structural constitutive integration over fiber directions;
4. cohort-based turnover with deposition, survival, and prestretch.

All quantities are synthetic teaching examples.  The functions are intended for
verification-oriented tutorials, not tissue-specific parameter identification.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence

import numpy as np
from scipy.special import i0

Array = np.ndarray


@dataclass(frozen=True)
class ReorientationParameters:
    """Parameters for direct rotation of a discrete fiber family."""

    rate: float = 0.8
    dead_zone: float = 0.0
    maximum_rate: float | None = None

    def validate(self) -> None:
        if self.rate < 0.0:
            raise ValueError("rate must be non-negative")
        if not 0.0 <= self.dead_zone < 0.5 * np.pi:
            raise ValueError("dead_zone must lie in [0, pi/2)")
        if self.maximum_rate is not None and self.maximum_rate <= 0.0:
            raise ValueError("maximum_rate must be positive")


@dataclass(frozen=True)
class ODFRemodelingParameters:
    """Parameters for conservative orientation-distribution evolution."""

    alignment_rate: float = 1.0
    rotational_diffusivity: float = 0.02
    dead_zone: float = 0.0

    def validate(self) -> None:
        if self.alignment_rate < 0.0:
            raise ValueError("alignment_rate must be non-negative")
        if self.rotational_diffusivity < 0.0:
            raise ValueError("rotational_diffusivity must be non-negative")
        if not 0.0 <= self.dead_zone < 0.5 * np.pi:
            raise ValueError("dead_zone must lie in [0, pi/2)")


@dataclass(frozen=True)
class FiberMaterialParameters:
    """Tension-only exponential fiber material parameters."""

    k1: float = 3.0
    k2: float = 8.0
    slack_stretch: float = 1.0

    def validate(self) -> None:
        if self.k1 <= 0.0 or self.k2 <= 0.0:
            raise ValueError("k1 and k2 must be positive")
        if self.slack_stretch <= 0.0:
            raise ValueError("slack_stretch must be positive")


@dataclass(frozen=True)
class FiberFamily:
    """State of one discrete load-bearing fiber family."""

    angle: float
    mass_fraction: float = 1.0
    deposition_stretch: float = 1.0
    slack_stretch: float = 1.0

    def validate(self) -> None:
        if self.mass_fraction < 0.0:
            raise ValueError("mass_fraction must be non-negative")
        if self.deposition_stretch <= 0.0:
            raise ValueError("deposition_stretch must be positive")
        if self.slack_stretch <= 0.0:
            raise ValueError("slack_stretch must be positive")


@dataclass(frozen=True)
class TurnoverParameters:
    """Parameters for a cohort-based constrained-mixture teaching model."""

    half_life: float = 8.0
    basal_production: float = 0.08
    stress_gain: float = 0.7
    target_stress: float = 1.0
    deposition_stretch: float = 1.08
    minimum_production: float = 0.0

    def validate(self) -> None:
        if self.half_life <= 0.0:
            raise ValueError("half_life must be positive")
        if self.basal_production < 0.0:
            raise ValueError("basal_production must be non-negative")
        if self.target_stress <= 0.0:
            raise ValueError("target_stress must be positive")
        if self.deposition_stretch <= 0.0:
            raise ValueError("deposition_stretch must be positive")
        if self.minimum_production < 0.0:
            raise ValueError("minimum_production must be non-negative")


@dataclass(frozen=True)
class Cohort:
    """A deposited fiber cohort with a fixed natural direction and prestretch."""

    birth_time: float
    initial_mass: float
    angle: float
    deposition_stretch: float


@dataclass(frozen=True)
class RecruitmentParameters:
    """Distribution of recruitment stretches for crimped fibers."""

    mean: float = 1.06
    standard_deviation: float = 0.025

    def validate(self) -> None:
        if self.mean <= 0.0:
            raise ValueError("mean must be positive")
        if self.standard_deviation <= 0.0:
            raise ValueError("standard_deviation must be positive")


def wrap_axial(angle: Array | float) -> Array | float:
    """Wrap an axial angle to [-pi/2, pi/2)."""

    wrapped = (np.asarray(angle) + 0.5 * np.pi) % np.pi - 0.5 * np.pi
    if np.isscalar(angle):
        return float(wrapped)
    return wrapped


def axial_angle_difference(target: Array | float, current: Array | float) -> Array | float:
    """Shortest signed axial difference target-current in [-pi/2, pi/2)."""

    difference = 0.5 * np.arctan2(
        np.sin(2.0 * (np.asarray(target) - np.asarray(current))),
        np.cos(2.0 * (np.asarray(target) - np.asarray(current))),
    )
    if np.isscalar(target) and np.isscalar(current):
        return float(difference)
    return difference


def axial_grid(number_of_angles: int = 181) -> Array:
    """Uniform periodic grid on the axial domain [-pi/2, pi/2)."""

    if number_of_angles < 8:
        raise ValueError("number_of_angles must be at least 8")
    return np.linspace(-0.5 * np.pi, 0.5 * np.pi, number_of_angles, endpoint=False)


def normalize_density(theta: Array, density: Array) -> Array:
    """Normalize a non-negative axial density using periodic quadrature."""

    angles = np.asarray(theta, dtype=float)
    values = np.asarray(density, dtype=float)
    if angles.ndim != 1 or values.shape != angles.shape:
        raise ValueError("theta and density must be one-dimensional arrays of equal size")
    values = np.maximum(values, 0.0)
    delta = np.pi / angles.size
    integral = float(np.sum(values) * delta)
    if integral <= 0.0:
        raise ValueError("density must have positive integral")
    return values / integral


def axial_von_mises_density(theta: Array, mean_angle: float, concentration: float) -> Array:
    """Normalized axial von Mises density on a pi-periodic orientation domain."""

    if concentration < 0.0:
        raise ValueError("concentration must be non-negative")
    values = np.exp(concentration * np.cos(2.0 * (theta - mean_angle)))
    analytical_normalizer = np.pi * i0(concentration)
    return values / analytical_normalizer


def orientation_tensor_2d(theta: Array, density: Array) -> Array:
    """Second-order orientation tensor A=<a tensor a> for planar axial fibers."""

    rho = normalize_density(theta, density)
    delta = np.pi / theta.size
    directions = np.stack((np.cos(theta), np.sin(theta)), axis=1)
    return np.einsum("n,ni,nj->ij", rho * delta, directions, directions)


def axial_order_parameter(theta: Array, density: Array) -> float:
    """Magnitude of the second circular moment, from zero to one."""

    rho = normalize_density(theta, density)
    delta = np.pi / theta.size
    moment = np.sum(rho * np.exp(2.0j * theta)) * delta
    return float(np.abs(moment))


def axial_mean_angle(theta: Array, density: Array) -> float:
    """Mean axial orientation based on the second circular moment."""

    rho = normalize_density(theta, density)
    delta = np.pi / theta.size
    moment = np.sum(rho * np.exp(2.0j * theta)) * delta
    if abs(moment) < 1.0e-14:
        return 0.0
    return float(wrap_axial(0.5 * np.angle(moment)))


def family_orientation_tensor(families: Sequence[FiberFamily]) -> Array:
    """Mass-weighted orientation tensor of discrete families."""

    if not families:
        raise ValueError("at least one family is required")
    masses = np.asarray([family.mass_fraction for family in families], dtype=float)
    total = float(np.sum(masses))
    if total <= 0.0:
        raise ValueError("total family mass must be positive")
    tensor = np.zeros((2, 2), dtype=float)
    for family in families:
        family.validate()
        direction = np.array([np.cos(family.angle), np.sin(family.angle)])
        tensor += family.mass_fraction * np.outer(direction, direction)
    return tensor / total


def principal_direction_2d(tensor: Array, largest: bool = True) -> tuple[float, Array]:
    """Principal axial direction and eigenvalues of a symmetric 2x2 tensor."""

    values, vectors = np.linalg.eigh(np.asarray(tensor, dtype=float))
    index = int(np.argmax(values) if largest else np.argmin(values))
    vector = vectors[:, index]
    angle = wrap_axial(np.arctan2(vector[1], vector[0]))
    return float(angle), values


def reorientation_rate(
    current_angle: float,
    target_angle: float,
    parameters: ReorientationParameters | None = None,
) -> float:
    """Axial first-order alignment rate with optional dead zone and saturation."""

    params = parameters or ReorientationParameters()
    params.validate()
    mismatch = axial_angle_difference(target_angle, current_angle)
    if abs(mismatch) <= params.dead_zone:
        return 0.0
    effective = np.sign(mismatch) * (abs(mismatch) - params.dead_zone)
    rate = 0.5 * params.rate * np.sin(2.0 * effective)
    if params.maximum_rate is not None:
        rate = float(np.clip(rate, -params.maximum_rate, params.maximum_rate))
    return float(rate)


def simulate_discrete_reorientation(
    time: Array,
    initial_angle: float,
    target: float | Callable[[float], float],
    parameters: ReorientationParameters | None = None,
) -> dict[str, Array]:
    """Integrate direct family rotation on the axial orientation manifold."""

    t = np.asarray(time, dtype=float)
    if t.ndim != 1 or t.size < 2 or np.any(np.diff(t) <= 0.0):
        raise ValueError("time must be strictly increasing")
    params = parameters or ReorientationParameters()
    params.validate()
    angles = np.empty_like(t)
    targets = np.empty_like(t)
    rates = np.empty_like(t)
    angles[0] = wrap_axial(initial_angle)
    for index, current_time in enumerate(t):
        targets[index] = wrap_axial(target(current_time) if callable(target) else target)
        rates[index] = reorientation_rate(angles[index], targets[index], params)
        if index < t.size - 1:
            dt = t[index + 1] - current_time
            angles[index + 1] = wrap_axial(angles[index] + dt * rates[index])
    error = np.asarray(axial_angle_difference(targets, angles), dtype=float)
    return {"time": t, "angle": angles, "target": targets, "rate": rates, "error": error}


def rotational_velocity(
    theta: Array,
    target_angle: float,
    alignment_rate: float,
    dead_zone: float = 0.0,
) -> Array:
    """Angular drift velocity for an axial orientation distribution."""

    mismatch = np.asarray(axial_angle_difference(target_angle, theta), dtype=float)
    effective = np.sign(mismatch) * np.maximum(np.abs(mismatch) - dead_zone, 0.0)
    return 0.5 * alignment_rate * np.sin(2.0 * effective)


def _conservative_odf_step(
    theta: Array,
    density: Array,
    target_angle: float,
    dt: float,
    parameters: ODFRemodelingParameters,
) -> Array:
    """One positivity-corrected finite-volume drift-diffusion step."""

    if dt <= 0.0:
        raise ValueError("dt must be positive")
    rho = normalize_density(theta, density)
    delta = np.pi / theta.size
    velocity = rotational_velocity(
        theta,
        target_angle,
        parameters.alignment_rate,
        parameters.dead_zone,
    )
    face_velocity = 0.5 * (velocity + np.roll(velocity, -1))
    right_state = np.roll(rho, -1)
    upwind = np.where(face_velocity >= 0.0, rho, right_state)
    flux = face_velocity * upwind
    divergence = (flux - np.roll(flux, 1)) / delta
    laplacian = (np.roll(rho, -1) - 2.0 * rho + np.roll(rho, 1)) / delta**2
    updated = rho - dt * divergence + dt * parameters.rotational_diffusivity * laplacian
    updated = np.maximum(updated, 0.0)
    return normalize_density(theta, updated)


def simulate_odf_remodeling(
    time: Array,
    theta: Array,
    initial_density: Array,
    target: float | Callable[[float], float],
    parameters: ODFRemodelingParameters | None = None,
) -> dict[str, Array]:
    """Evolve a continuous axial orientation density by drift and diffusion."""

    t = np.asarray(time, dtype=float)
    angles = np.asarray(theta, dtype=float)
    if t.ndim != 1 or t.size < 2 or np.any(np.diff(t) <= 0.0):
        raise ValueError("time must be strictly increasing")
    params = parameters or ODFRemodelingParameters()
    params.validate()
    history = np.empty((t.size, angles.size), dtype=float)
    targets = np.empty_like(t)
    means = np.empty_like(t)
    orders = np.empty_like(t)
    history[0] = normalize_density(angles, initial_density)
    for index, current_time in enumerate(t):
        targets[index] = wrap_axial(target(current_time) if callable(target) else target)
        means[index] = axial_mean_angle(angles, history[index])
        orders[index] = axial_order_parameter(angles, history[index])
        if index < t.size - 1:
            dt_total = t[index + 1] - current_time
            delta = np.pi / angles.size
            max_velocity = max(params.alignment_rate * 0.5, 1.0e-12)
            drift_limit = 0.45 * delta / max_velocity
            if params.rotational_diffusivity > 0.0:
                diffusion_limit = 0.20 * delta**2 / params.rotational_diffusivity
            else:
                diffusion_limit = np.inf
            number_of_substeps = max(
                1,
                int(np.ceil(dt_total / min(drift_limit, diffusion_limit))),
            )
            substep = dt_total / number_of_substeps
            updated = history[index].copy()
            for _ in range(number_of_substeps):
                updated = _conservative_odf_step(
                    angles,
                    updated,
                    targets[index],
                    substep,
                    params,
                )
            history[index + 1] = updated
    return {
        "time": t,
        "theta": angles,
        "density": history,
        "target": targets,
        "mean_angle": means,
        "order_parameter": orders,
    }


def direction_2d(angle: float) -> Array:
    return np.array([np.cos(angle), np.sin(angle)], dtype=float)


def fiber_stretch(deformation_gradient: Array, angle: float) -> float:
    """Affine stretch of a planar fiber direction."""

    F = np.asarray(deformation_gradient, dtype=float)
    if F.shape != (2, 2):
        raise ValueError("deformation_gradient must be 2x2")
    direction = direction_2d(angle)
    return float(np.linalg.norm(F @ direction))


def fiber_energy_from_stretch(
    stretch: Array | float,
    parameters: FiberMaterialParameters | None = None,
) -> Array | float:
    """Tension-only exponential fiber energy."""

    params = parameters or FiberMaterialParameters()
    params.validate()
    effective_stretch = np.asarray(stretch, dtype=float) / params.slack_stretch
    strain_measure = np.maximum(effective_stretch**2 - 1.0, 0.0)
    energy = params.k1 / (2.0 * params.k2) * (
        np.exp(params.k2 * strain_measure**2) - 1.0
    )
    if np.isscalar(stretch):
        return float(energy)
    return energy


def fiber_tension_proxy(
    stretch: Array | float,
    parameters: FiberMaterialParameters | None = None,
) -> Array | float:
    """Derivative-like tensile force proxy for recruitment/remodeling studies."""

    params = parameters or FiberMaterialParameters()
    params.validate()
    effective_stretch = np.asarray(stretch, dtype=float) / params.slack_stretch
    strain_measure = np.maximum(effective_stretch**2 - 1.0, 0.0)
    tension = (
        2.0
        * params.k1
        * effective_stretch
        * strain_measure
        * np.exp(params.k2 * strain_measure**2)
        / params.slack_stretch
    )
    tension = np.where(effective_stretch > 1.0, tension, 0.0)
    if np.isscalar(stretch):
        return float(tension)
    return tension


def discrete_family_energy(
    deformation_gradient: Array,
    families: Sequence[FiberFamily],
    material: FiberMaterialParameters | None = None,
) -> float:
    """Mass-weighted energy of discrete fiber families."""

    if not families:
        raise ValueError("at least one family is required")
    total = 0.0
    for family in families:
        family.validate()
        stretch = fiber_stretch(deformation_gradient, family.angle)
        effective = stretch * family.deposition_stretch
        family_material = FiberMaterialParameters(
            k1=(material or FiberMaterialParameters()).k1,
            k2=(material or FiberMaterialParameters()).k2,
            slack_stretch=family.slack_stretch,
        )
        total += family.mass_fraction * fiber_energy_from_stretch(effective, family_material)
    return float(total)


def angular_integrated_energy(
    deformation_gradient: Array,
    theta: Array,
    density: Array,
    material: FiberMaterialParameters | None = None,
) -> float:
    """Lanir-style angular integration of a tension-only fiber energy."""

    rho = normalize_density(theta, density)
    delta = np.pi / theta.size
    stretches = np.array([fiber_stretch(deformation_gradient, angle) for angle in theta])
    energy = fiber_energy_from_stretch(stretches, material)
    return float(np.sum(rho * energy) * delta)


def planar_structure_tensor_energy(
    deformation_gradient: Array,
    mean_angle: float,
    dispersion: float,
    material: FiberMaterialParameters | None = None,
) -> float:
    """Planar generalized-structure-tensor approximation.

    ``dispersion`` lies in [0, 0.5].  Zero is perfectly aligned; 0.5 is
    in-plane isotropy.  This is a pedagogical planar analogue of the GOH
    structural-tensor construction, not a replacement for the full 3-D model.
    """

    if not 0.0 <= dispersion <= 0.5:
        raise ValueError("dispersion must lie in [0, 0.5]")
    params = material or FiberMaterialParameters()
    direction = direction_2d(mean_angle)
    H = dispersion * np.eye(2) + (1.0 - 2.0 * dispersion) * np.outer(direction, direction)
    C = np.asarray(deformation_gradient, dtype=float).T @ np.asarray(
        deformation_gradient, dtype=float
    )
    pseudo_invariant = float(np.trace(H @ C))
    effective_stretch = np.sqrt(max(pseudo_invariant, 0.0))
    return float(fiber_energy_from_stretch(effective_stretch, params))


def recruited_fraction(
    stretch: Array | float,
    parameters: RecruitmentParameters | None = None,
) -> Array | float:
    """Gaussian CDF approximation for gradual collagen recruitment."""

    from scipy.special import ndtr

    params = parameters or RecruitmentParameters()
    params.validate()
    value = ndtr((np.asarray(stretch) - params.mean) / params.standard_deviation)
    if np.isscalar(stretch):
        return float(value)
    return value


def recruitment_tension(
    stretch: Array,
    parameters: RecruitmentParameters | None = None,
    fiber_stiffness: float = 1.0,
    number_of_slack_samples: int = 301,
) -> Array:
    """Integrate linear post-recruitment fibers over a slack-stretch distribution."""

    params = parameters or RecruitmentParameters()
    params.validate()
    if fiber_stiffness <= 0.0:
        raise ValueError("fiber_stiffness must be positive")
    lower = max(0.7, params.mean - 5.0 * params.standard_deviation)
    upper = params.mean + 5.0 * params.standard_deviation
    slack = np.linspace(lower, upper, number_of_slack_samples)
    density = np.exp(-0.5 * ((slack - params.mean) / params.standard_deviation) ** 2)
    density /= np.trapezoid(density, slack)
    values = []
    for lam in np.asarray(stretch, dtype=float):
        strain = np.maximum(lam / slack - 1.0, 0.0)
        values.append(np.trapezoid(fiber_stiffness * strain * density, slack))
    return np.asarray(values)


def survival_fraction(age: Array | float, half_life: float) -> Array | float:
    """Exponential survival fraction based on a constituent half-life."""

    if half_life <= 0.0:
        raise ValueError("half_life must be positive")
    age_array = np.maximum(np.asarray(age, dtype=float), 0.0)
    value = np.exp(-np.log(2.0) * age_array / half_life)
    if np.isscalar(age):
        return float(value)
    return value


def production_rate(stress: float, parameters: TurnoverParameters) -> float:
    """Stress-regulated cohort production rate with a non-negative floor."""

    parameters.validate()
    error = stress / parameters.target_stress - 1.0
    rate = parameters.basal_production * (1.0 + parameters.stress_gain * error)
    return float(max(rate, parameters.minimum_production))


def simulate_cohort_turnover(
    time: Array,
    stress_protocol: Callable[[float], float],
    deposition_angle_protocol: Callable[[float], float],
    parameters: TurnoverParameters | None = None,
    initial_mass: float = 1.0,
    initial_angle: float = 0.0,
) -> dict[str, Array | list[list[Cohort]]]:
    """Track deposition and survival of fiber cohorts.

    Existing cohorts keep their deposition angle.  Remodeling of the ensemble
    occurs because old cohorts disappear while new cohorts are deposited in a
    mechanically selected direction.  This cleanly contrasts with direct
    rotation of pre-existing fibers.
    """

    t = np.asarray(time, dtype=float)
    if t.ndim != 1 or t.size < 2 or np.any(np.diff(t) <= 0.0):
        raise ValueError("time must be strictly increasing")
    if initial_mass <= 0.0:
        raise ValueError("initial_mass must be positive")
    params = parameters or TurnoverParameters()
    params.validate()
    cohorts: list[Cohort] = [
        Cohort(
            birth_time=float(t[0]),
            initial_mass=initial_mass,
            angle=wrap_axial(initial_angle),
            deposition_stretch=params.deposition_stretch,
        )
    ]
    mass = np.empty_like(t)
    mean_angle = np.empty_like(t)
    order = np.empty_like(t)
    mean_age = np.empty_like(t)
    production = np.empty_like(t)
    stress = np.empty_like(t)
    snapshots: list[list[Cohort]] = []

    for index, current_time in enumerate(t):
        stress[index] = stress_protocol(float(current_time))
        current_masses = np.array(
            [
                cohort.initial_mass
                * survival_fraction(current_time - cohort.birth_time, params.half_life)
                for cohort in cohorts
            ],
            dtype=float,
        )
        angles = np.array([cohort.angle for cohort in cohorts], dtype=float)
        total_mass = float(np.sum(current_masses))
        mass[index] = total_mass
        moment = np.sum(current_masses * np.exp(2.0j * angles)) / total_mass
        mean_angle[index] = wrap_axial(0.5 * np.angle(moment))
        order[index] = abs(moment)
        ages = current_time - np.array([cohort.birth_time for cohort in cohorts])
        mean_age[index] = float(np.sum(current_masses * ages) / total_mass)
        production[index] = production_rate(stress[index], params)
        snapshots.append(list(cohorts))
        if index < t.size - 1:
            dt = t[index + 1] - current_time
            new_mass = production[index] * dt
            if new_mass > 0.0:
                cohorts.append(
                    Cohort(
                        birth_time=float(t[index + 1]),
                        initial_mass=float(new_mass),
                        angle=wrap_axial(deposition_angle_protocol(float(t[index + 1]))),
                        deposition_stretch=params.deposition_stretch,
                    )
                )

    return {
        "time": t,
        "stress": stress,
        "mass": mass,
        "mean_angle": mean_angle,
        "order_parameter": order,
        "mean_age": mean_age,
        "production_rate": production,
        "cohorts": snapshots,
    }


def simulate_two_family_mass_remodeling(
    time: Array,
    deformation_protocol: Callable[[float], Array],
    initial_masses: tuple[float, float] = (0.5, 0.5),
    family_angles: tuple[float, float] = (-0.5, 0.5),
    target_tension: float = 1.0,
    adaptation_rate: float = 0.3,
    removal_rate: float = 0.05,
    material: FiberMaterialParameters | None = None,
) -> dict[str, Array]:
    """Competing family mass fractions driven by family-specific tension."""

    t = np.asarray(time, dtype=float)
    if target_tension <= 0.0 or adaptation_rate < 0.0 or removal_rate < 0.0:
        raise ValueError("invalid remodeling parameters")
    masses = np.empty((t.size, 2), dtype=float)
    tensions = np.empty((t.size, 2), dtype=float)
    masses[0] = np.asarray(initial_masses, dtype=float)
    if np.any(masses[0] <= 0.0):
        raise ValueError("initial masses must be positive")
    params = material or FiberMaterialParameters()
    for index, current_time in enumerate(t):
        F = deformation_protocol(float(current_time))
        for family_index, angle in enumerate(family_angles):
            stretch = fiber_stretch(F, angle)
            tensions[index, family_index] = fiber_tension_proxy(stretch, params)
        if index < t.size - 1:
            dt = t[index + 1] - current_time
            normalized_error = tensions[index] / target_tension - 1.0
            production = adaptation_rate * np.maximum(normalized_error, 0.0)
            removal = removal_rate * np.maximum(-normalized_error, 0.0)
            log_rate = production - removal
            masses[index + 1] = masses[index] * np.exp(dt * log_rate)
    fractions = masses / np.sum(masses, axis=1, keepdims=True)
    return {
        "time": t,
        "mass": masses,
        "mass_fraction": fractions,
        "tension": tensions,
        "angles": np.asarray(family_angles),
    }


def compare_approach_state_count(number_of_angles: int = 181, number_of_cohorts: int = 100) -> dict[str, int]:
    """Transparent state-count comparison for four modeling approaches."""

    if number_of_angles <= 0 or number_of_cohorts <= 0:
        raise ValueError("counts must be positive")
    return {
        "direct_family_rotation": 1,
        "generalized_structure_tensor": 2,
        "continuous_odf": number_of_angles,
        "cohort_turnover": 4 * number_of_cohorts,
    }


__all__ = [
    "Cohort",
    "FiberFamily",
    "FiberMaterialParameters",
    "ODFRemodelingParameters",
    "RecruitmentParameters",
    "ReorientationParameters",
    "TurnoverParameters",
    "angular_integrated_energy",
    "axial_angle_difference",
    "axial_grid",
    "axial_mean_angle",
    "axial_order_parameter",
    "axial_von_mises_density",
    "compare_approach_state_count",
    "direction_2d",
    "discrete_family_energy",
    "family_orientation_tensor",
    "fiber_energy_from_stretch",
    "fiber_stretch",
    "fiber_tension_proxy",
    "normalize_density",
    "orientation_tensor_2d",
    "planar_structure_tensor_energy",
    "principal_direction_2d",
    "production_rate",
    "recruited_fraction",
    "recruitment_tension",
    "reorientation_rate",
    "rotational_velocity",
    "simulate_cohort_turnover",
    "simulate_discrete_reorientation",
    "simulate_odf_remodeling",
    "simulate_two_family_mass_remodeling",
    "survival_fraction",
    "wrap_axial",
]
