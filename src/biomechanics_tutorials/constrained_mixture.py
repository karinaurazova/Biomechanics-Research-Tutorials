"""Synthetic constrained-mixture models for soft-tissue growth and remodeling.

The implementation is intentionally reduced and verification-oriented. It is not a
validated model of a specific heart, vessel, animal, or patient. The module separates
constituent mass turnover, survival, deposition stretch, natural configurations,
mechanobiological feedback, and mixture stress so that the assumptions remain visible.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Callable, Literal, Sequence

import numpy as np

Array = np.ndarray
ScalarProtocol = Callable[[float], float]
TensorProtocol = Callable[[float], Array]
StimulusMode = Literal["stress", "stretch", "energy"]
ConstituentKind = Literal["fiber", "matrix"]


@dataclass(frozen=True)
class ConstituentParameters:
    """Parameters of one load-bearing constituent in a constrained mixture."""

    name: str
    kind: ConstituentKind
    initial_mass: float
    half_life: float
    stiffness: float
    deposition_stretch: float = 1.0
    angle_degrees: float = 0.0
    exponential_parameter: float = 6.0
    basal_production: float | None = None
    production_gain: float = 1.0
    removal_gain: float = 0.2
    target_stress: float | None = None
    target_stretch: float | None = None
    stimulus_mode: StimulusMode = "stress"
    dead_zone: float = 0.02
    saturation: float = 2.0

    def validate(self) -> None:
        if not self.name:
            raise ValueError("name must not be empty")
        if self.kind not in {"fiber", "matrix"}:
            raise ValueError("kind must be 'fiber' or 'matrix'")
        if self.initial_mass < 0.0:
            raise ValueError("initial_mass must be non-negative")
        if self.half_life <= 0.0:
            raise ValueError("half_life must be positive")
        if self.stiffness < 0.0:
            raise ValueError("stiffness must be non-negative")
        if self.deposition_stretch <= 0.0:
            raise ValueError("deposition_stretch must be positive")
        if self.exponential_parameter <= 0.0:
            raise ValueError("exponential_parameter must be positive")
        if self.basal_production is not None and self.basal_production < 0.0:
            raise ValueError("basal_production must be non-negative")
        if self.production_gain < 0.0 or self.removal_gain < 0.0:
            raise ValueError("feedback gains must be non-negative")
        if self.dead_zone < 0.0 or self.saturation <= 0.0:
            raise ValueError("dead_zone must be non-negative and saturation positive")
        if self.stimulus_mode not in {"stress", "stretch", "energy"}:
            raise ValueError("unsupported stimulus_mode")

    @property
    def hazard(self) -> float:
        return float(np.log(2.0) / self.half_life)

    @property
    def homeostatic_production(self) -> float:
        if self.basal_production is not None:
            return float(self.basal_production)
        return self.hazard * self.initial_mass


@dataclass(frozen=True)
class CohortRecord:
    """One deposited constituent cohort and its current surviving mass."""

    birth_time: float
    mass: float
    natural_stretch: float
    angle_degrees: float

    def validate(self) -> None:
        if self.mass < 0.0:
            raise ValueError("cohort mass must be non-negative")
        if self.natural_stretch <= 0.0:
            raise ValueError("natural_stretch must be positive")


@dataclass(frozen=True)
class MixtureSimulationParameters:
    """Numerical controls shared by the reduced mixture simulators."""

    feedback_scale: float = 1.0
    minimum_multiplier: float = 0.0
    maximum_multiplier: float = 5.0
    history_cutoff_fraction: float = 1e-8

    def validate(self) -> None:
        if self.feedback_scale <= 0.0:
            raise ValueError("feedback_scale must be positive")
        if self.minimum_multiplier < 0.0:
            raise ValueError("minimum_multiplier must be non-negative")
        if self.maximum_multiplier < self.minimum_multiplier:
            raise ValueError("maximum_multiplier must exceed minimum_multiplier")
        if not 0.0 <= self.history_cutoff_fraction < 1.0:
            raise ValueError("history_cutoff_fraction must lie in [0, 1)")


def _validate_time(time: Array) -> Array:
    values = np.asarray(time, dtype=float)
    if values.ndim != 1 or values.size < 2:
        raise ValueError("time must be one-dimensional with at least two values")
    if not np.all(np.isfinite(values)) or np.any(np.diff(values) <= 0.0):
        raise ValueError("time must be finite and strictly increasing")
    return values


def axial_wrap(angle_radians: Array | float) -> Array:
    """Wrap axial angles to [-pi/2, pi/2)."""

    angle = np.asarray(angle_radians, dtype=float)
    return (angle + np.pi / 2.0) % np.pi - np.pi / 2.0


def direction_vector(angle_degrees: float) -> Array:
    """Return a planar unit material direction embedded in three dimensions."""

    angle = np.deg2rad(float(angle_degrees))
    return np.array([np.cos(angle), np.sin(angle), 0.0], dtype=float)


def fiber_stretch(deformation_gradient: Array, angle_degrees: float) -> float:
    """Stretch of a material line with the specified reference orientation."""

    deformation = np.asarray(deformation_gradient, dtype=float)
    if deformation.shape != (3, 3):
        raise ValueError("deformation_gradient must have shape (3, 3)")
    direction = direction_vector(angle_degrees)
    return float(np.linalg.norm(deformation @ direction))


def survival_fraction(age: Array | float, half_life: float) -> Array:
    """Exponential surviving fraction with the requested half-life."""

    if half_life <= 0.0:
        raise ValueError("half_life must be positive")
    age_array = np.maximum(np.asarray(age, dtype=float), 0.0)
    return np.exp(-np.log(2.0) * age_array / half_life)


def fiber_specific_tension(
    elastic_stretch: Array | float,
    stiffness: float,
    exponential_parameter: float = 6.0,
) -> Array:
    """Tension-only exponential nominal stress per unit constituent mass."""

    if stiffness < 0.0 or exponential_parameter <= 0.0:
        raise ValueError("stiffness must be non-negative and exponential_parameter positive")
    stretch = np.asarray(elastic_stretch, dtype=float)
    strain = np.maximum(stretch - 1.0, 0.0)
    return stiffness * strain * np.exp(exponential_parameter * strain**2)


def fiber_specific_energy(
    elastic_stretch: Array | float,
    stiffness: float,
    exponential_parameter: float = 6.0,
) -> Array:
    """Tension-only exponential energy per unit constituent mass."""

    if stiffness < 0.0 or exponential_parameter <= 0.0:
        raise ValueError("stiffness must be non-negative and exponential_parameter positive")
    stretch = np.asarray(elastic_stretch, dtype=float)
    strain = np.maximum(stretch - 1.0, 0.0)
    return stiffness * np.expm1(exponential_parameter * strain**2) / (
        2.0 * exponential_parameter
    )


def matrix_specific_nominal_stress(stretch: Array | float, stiffness: float) -> Array:
    """Incompressible neo-Hookean uniaxial nominal stress per unit matrix mass."""

    if stiffness < 0.0:
        raise ValueError("stiffness must be non-negative")
    lam = np.asarray(stretch, dtype=float)
    if np.any(lam <= 0.0):
        raise ValueError("stretch must be positive")
    return stiffness * (lam - lam ** (-2.0))


def matrix_specific_energy(stretch: Array | float, stiffness: float) -> Array:
    """Reduced incompressible neo-Hookean energy per unit matrix mass."""

    if stiffness < 0.0:
        raise ValueError("stiffness must be non-negative")
    lam = np.asarray(stretch, dtype=float)
    if np.any(lam <= 0.0):
        raise ValueError("stretch must be positive")
    return 0.5 * stiffness * (lam**2 + 2.0 / lam - 3.0)


def cohort_elastic_stretch(
    current_stretch: Array | float,
    birth_stretch: Array | float,
    deposition_stretch: Array | float,
) -> Array:
    """Elastic cohort stretch using the standard deposition-stretch construction."""

    current = np.asarray(current_stretch, dtype=float)
    birth = np.asarray(birth_stretch, dtype=float)
    deposition = np.asarray(deposition_stretch, dtype=float)
    if np.any(current <= 0.0) or np.any(birth <= 0.0) or np.any(deposition <= 0.0):
        raise ValueError("all stretches must be positive")
    return current * deposition / birth


def constituent_stress_from_cohorts(
    current_stretch: float,
    cohorts: Sequence[CohortRecord],
    constituent: ConstituentParameters,
) -> float:
    """Mass-weighted nominal stress of one constituent history."""

    constituent.validate()
    total = 0.0
    for cohort in cohorts:
        cohort.validate()
        elastic = current_stretch / cohort.natural_stretch
        if constituent.kind == "fiber":
            specific = fiber_specific_tension(
                elastic,
                constituent.stiffness,
                constituent.exponential_parameter,
            )
        else:
            specific = matrix_specific_nominal_stress(elastic, constituent.stiffness)
        total += cohort.mass * float(specific)
    return float(total)


def constituent_energy_from_cohorts(
    current_stretch: float,
    cohorts: Sequence[CohortRecord],
    constituent: ConstituentParameters,
) -> float:
    """Mass-weighted stored energy of one constituent history."""

    constituent.validate()
    total = 0.0
    for cohort in cohorts:
        cohort.validate()
        elastic = current_stretch / cohort.natural_stretch
        if constituent.kind == "fiber":
            specific = fiber_specific_energy(
                elastic,
                constituent.stiffness,
                constituent.exponential_parameter,
            )
        else:
            specific = matrix_specific_energy(elastic, constituent.stiffness)
        total += cohort.mass * float(specific)
    return float(total)


def _dead_zone(error: float, width: float) -> float:
    magnitude = max(abs(error) - width, 0.0)
    return float(np.sign(error) * magnitude)


def feedback_multiplier(
    error: float,
    gain: float,
    saturation: float,
    dead_zone: float = 0.0,
    minimum: float = 0.0,
    maximum: float = 5.0,
) -> float:
    """Bounded positive multiplier for production or removal."""

    if gain < 0.0 or saturation <= 0.0:
        raise ValueError("gain must be non-negative and saturation positive")
    effective = _dead_zone(float(error), float(dead_zone))
    response = saturation * np.tanh(gain * effective / saturation)
    return float(np.clip(1.0 + response, minimum, maximum))


def initialize_homeostatic_targets(
    deformation_gradient: Array,
    constituents: Sequence[ConstituentParameters],
) -> list[ConstituentParameters]:
    """Assign stress and stretch targets from a chosen homeostatic configuration."""

    initialized: list[ConstituentParameters] = []
    matrix_stretch = float(np.linalg.det(deformation_gradient) ** (1.0 / 3.0))
    for constituent in constituents:
        constituent.validate()
        stretch = (
            fiber_stretch(deformation_gradient, constituent.angle_degrees)
            if constituent.kind == "fiber"
            else matrix_stretch
        )
        natural = stretch / constituent.deposition_stretch
        cohort = CohortRecord(0.0, constituent.initial_mass, natural, constituent.angle_degrees)
        stress = constituent_stress_from_cohorts(stretch, [cohort], constituent)
        initialized.append(
            replace(
                constituent,
                target_stress=stress,
                target_stretch=stretch,
                basal_production=constituent.homeostatic_production,
            )
        )
    return initialized


def constituent_stimulus_error(
    stress: float,
    stretch: float,
    energy: float,
    constituent: ConstituentParameters,
    scale: float = 1.0,
) -> float:
    """Normalized constituent-specific mechanobiological error."""

    if scale <= 0.0:
        raise ValueError("scale must be positive")
    if constituent.stimulus_mode == "stress":
        target = constituent.target_stress
        value = stress
    elif constituent.stimulus_mode == "stretch":
        target = constituent.target_stretch
        value = stretch
    else:
        target = None if constituent.target_stress is None else abs(constituent.target_stress)
        value = energy
    if target is None:
        raise ValueError(f"homeostatic target is missing for {constituent.name}")
    denominator = max(abs(float(target)), scale)
    return float((value - float(target)) / denominator)


def _protocol_tensor(protocol: TensorProtocol | Array, time: float) -> Array:
    value = protocol(time) if callable(protocol) else protocol
    deformation = np.asarray(value, dtype=float)
    if deformation.shape != (3, 3):
        raise ValueError("deformation protocol must return a (3, 3) tensor")
    if np.linalg.det(deformation) <= 0.0:
        raise ValueError("deformation gradient must have positive determinant")
    return deformation


def _constituent_stretch(deformation: Array, constituent: ConstituentParameters) -> float:
    if constituent.kind == "fiber":
        return fiber_stretch(deformation, constituent.angle_degrees)
    return float(np.linalg.det(deformation) ** (1.0 / 3.0))


def simulate_constrained_mixture(
    time: Array,
    deformation_protocol: TensorProtocol | Array,
    constituents: Sequence[ConstituentParameters],
    parameters: MixtureSimulationParameters | None = None,
) -> dict[str, object]:
    """Simulate a reduced full-history constrained mixture.

    Existing cohorts share the observable deformation but retain constituent-specific
    natural stretches. At every time step they lose mass through a stress-sensitive
    hazard, and new cohorts are deposited with their prescribed deposition stretch.
    """

    values = _validate_time(time)
    settings = parameters or MixtureSimulationParameters()
    settings.validate()
    if not constituents:
        raise ValueError("at least one constituent is required")
    for constituent in constituents:
        constituent.validate()
        if constituent.target_stress is None or constituent.target_stretch is None:
            raise ValueError("initialize homeostatic targets before simulation")

    n_steps = values.size
    names = [constituent.name for constituent in constituents]
    mass = {name: np.zeros(n_steps) for name in names}
    stress = {name: np.zeros(n_steps) for name in names}
    energy = {name: np.zeros(n_steps) for name in names}
    production = {name: np.zeros(n_steps) for name in names}
    removal = {name: np.zeros(n_steps) for name in names}
    mean_age = {name: np.zeros(n_steps) for name in names}
    mean_natural_stretch = {name: np.zeros(n_steps) for name in names}
    stretch_history = {name: np.zeros(n_steps) for name in names}
    histories: dict[str, list[CohortRecord]] = {}

    initial_deformation = _protocol_tensor(deformation_protocol, values[0])
    for constituent in constituents:
        stretch = _constituent_stretch(initial_deformation, constituent)
        natural = stretch / constituent.deposition_stretch
        histories[constituent.name] = [
            CohortRecord(values[0], constituent.initial_mass, natural, constituent.angle_degrees)
        ]

    total_stress = np.zeros(n_steps)
    total_energy = np.zeros(n_steps)
    total_mass = np.zeros(n_steps)
    cohort_count = np.zeros(n_steps, dtype=int)

    for index, current_time in enumerate(values):
        deformation = _protocol_tensor(deformation_protocol, current_time)
        for constituent in constituents:
            name = constituent.name
            current_stretch = _constituent_stretch(deformation, constituent)
            stretch_history[name][index] = current_stretch
            cohorts = histories[name]

            constituent_mass = sum(cohort.mass for cohort in cohorts)
            constituent_stress = constituent_stress_from_cohorts(
                current_stretch,
                cohorts,
                constituent,
            )
            constituent_energy = constituent_energy_from_cohorts(
                current_stretch,
                cohorts,
                constituent,
            )
            ages = np.array([current_time - cohort.birth_time for cohort in cohorts])
            cohort_masses = np.array([cohort.mass for cohort in cohorts])
            natural_values = np.array([cohort.natural_stretch for cohort in cohorts])

            mass[name][index] = constituent_mass
            stress[name][index] = constituent_stress
            energy[name][index] = constituent_energy
            if constituent_mass > 0.0:
                mean_age[name][index] = float(np.dot(ages, cohort_masses) / constituent_mass)
                mean_natural_stretch[name][index] = float(
                    np.exp(np.dot(np.log(natural_values), cohort_masses) / constituent_mass)
                )

            error = constituent_stimulus_error(
                constituent_stress,
                current_stretch,
                constituent_energy,
                constituent,
                settings.feedback_scale,
            )
            production_multiplier = feedback_multiplier(
                error,
                constituent.production_gain,
                constituent.saturation,
                constituent.dead_zone,
                settings.minimum_multiplier,
                settings.maximum_multiplier,
            )
            removal_multiplier = feedback_multiplier(
                abs(error),
                constituent.removal_gain,
                constituent.saturation,
                0.0,
                settings.minimum_multiplier,
                settings.maximum_multiplier,
            )
            production[name][index] = constituent.homeostatic_production * production_multiplier
            removal[name][index] = constituent.hazard * removal_multiplier * constituent_mass

            if index < n_steps - 1:
                dt = values[index + 1] - current_time
                survival = np.exp(-constituent.hazard * removal_multiplier * dt)
                updated: list[CohortRecord] = []
                cutoff = settings.history_cutoff_fraction * max(constituent.initial_mass, 1.0)
                for cohort in cohorts:
                    remaining = cohort.mass * survival
                    if remaining > cutoff:
                        updated.append(replace(cohort, mass=remaining))
                deposited_mass = production[name][index] * dt
                if deposited_mass > 0.0:
                    natural_stretch = current_stretch / constituent.deposition_stretch
                    updated.append(
                        CohortRecord(
                            current_time,
                            deposited_mass,
                            natural_stretch,
                            constituent.angle_degrees,
                        )
                    )
                histories[name] = updated

        total_stress[index] = sum(stress[name][index] for name in names)
        total_energy[index] = sum(energy[name][index] for name in names)
        total_mass[index] = sum(mass[name][index] for name in names)
        cohort_count[index] = sum(len(histories[name]) for name in names)

    return {
        "time": values,
        "mass": mass,
        "stress": stress,
        "energy": energy,
        "production": production,
        "removal": removal,
        "mean_age": mean_age,
        "mean_natural_stretch": mean_natural_stretch,
        "stretch": stretch_history,
        "total_mass": total_mass,
        "total_stress": total_stress,
        "total_energy": total_energy,
        "cohort_count": cohort_count,
        "final_cohorts": histories,
    }


def simulate_homogenized_mixture(
    time: Array,
    deformation_protocol: TensorProtocol | Array,
    constituents: Sequence[ConstituentParameters],
    parameters: MixtureSimulationParameters | None = None,
) -> dict[str, object]:
    """Simulate a reduced homogenized constrained-mixture analog.

    Each constituent is represented by its total mass and one mass-weighted natural
    stretch. This reduction is computationally cheap but discards the age distribution.
    """

    values = _validate_time(time)
    settings = parameters or MixtureSimulationParameters()
    settings.validate()
    if not constituents:
        raise ValueError("at least one constituent is required")
    for constituent in constituents:
        constituent.validate()
        if constituent.target_stress is None or constituent.target_stretch is None:
            raise ValueError("initialize homeostatic targets before simulation")

    names = [constituent.name for constituent in constituents]
    n_steps = values.size
    mass = {name: np.zeros(n_steps) for name in names}
    natural = {name: np.zeros(n_steps) for name in names}
    stress = {name: np.zeros(n_steps) for name in names}
    production = {name: np.zeros(n_steps) for name in names}
    removal = {name: np.zeros(n_steps) for name in names}
    total_stress = np.zeros(n_steps)
    total_mass = np.zeros(n_steps)

    initial_deformation = _protocol_tensor(deformation_protocol, values[0])
    for constituent in constituents:
        name = constituent.name
        initial_stretch = _constituent_stretch(initial_deformation, constituent)
        mass[name][0] = constituent.initial_mass
        natural[name][0] = initial_stretch / constituent.deposition_stretch

    for index, current_time in enumerate(values):
        deformation = _protocol_tensor(deformation_protocol, current_time)
        for constituent in constituents:
            name = constituent.name
            current_stretch = _constituent_stretch(deformation, constituent)
            elastic = current_stretch / natural[name][index]
            if constituent.kind == "fiber":
                specific_stress = fiber_specific_tension(
                    elastic,
                    constituent.stiffness,
                    constituent.exponential_parameter,
                )
                specific_energy = fiber_specific_energy(
                    elastic,
                    constituent.stiffness,
                    constituent.exponential_parameter,
                )
            else:
                specific_stress = matrix_specific_nominal_stress(elastic, constituent.stiffness)
                specific_energy = matrix_specific_energy(elastic, constituent.stiffness)
            stress[name][index] = mass[name][index] * float(specific_stress)
            error = constituent_stimulus_error(
                stress[name][index],
                current_stretch,
                mass[name][index] * float(specific_energy),
                constituent,
                settings.feedback_scale,
            )
            p_multiplier = feedback_multiplier(
                error,
                constituent.production_gain,
                constituent.saturation,
                constituent.dead_zone,
                settings.minimum_multiplier,
                settings.maximum_multiplier,
            )
            r_multiplier = feedback_multiplier(
                abs(error),
                constituent.removal_gain,
                constituent.saturation,
                0.0,
                settings.minimum_multiplier,
                settings.maximum_multiplier,
            )
            production[name][index] = constituent.homeostatic_production * p_multiplier
            removal[name][index] = constituent.hazard * r_multiplier * mass[name][index]

            if index < n_steps - 1:
                dt = values[index + 1] - current_time
                surviving_mass = mass[name][index] * np.exp(
                    -constituent.hazard * r_multiplier * dt
                )
                deposited_mass = production[name][index] * dt
                next_mass = surviving_mass + deposited_mass
                deposited_natural = current_stretch / constituent.deposition_stretch
                if next_mass > 0.0:
                    weighted_log = (
                        surviving_mass * np.log(natural[name][index])
                        + deposited_mass * np.log(deposited_natural)
                    ) / next_mass
                    natural[name][index + 1] = np.exp(weighted_log)
                else:
                    natural[name][index + 1] = natural[name][index]
                mass[name][index + 1] = next_mass

        total_stress[index] = sum(stress[name][index] for name in names)
        total_mass[index] = sum(mass[name][index] for name in names)

    return {
        "time": values,
        "mass": mass,
        "natural_stretch": natural,
        "stress": stress,
        "production": production,
        "removal": removal,
        "total_mass": total_mass,
        "total_stress": total_stress,
    }


def make_incompressible_biaxial_deformation(lambda_f: float, lambda_s: float) -> Array:
    """Diagonal incompressible deformation in fiber-sheet-normal coordinates."""

    if lambda_f <= 0.0 or lambda_s <= 0.0:
        raise ValueError("principal stretches must be positive")
    lambda_n = 1.0 / (lambda_f * lambda_s)
    return np.diag([lambda_f, lambda_s, lambda_n])


def cardiac_constituents() -> list[ConstituentParameters]:
    """Return a transparent synthetic myocardial constituent set."""

    return [
        ConstituentParameters(
            name="cardiomyocytes",
            kind="fiber",
            initial_mass=0.58,
            half_life=45.0,
            stiffness=5.5,
            deposition_stretch=1.06,
            angle_degrees=0.0,
            exponential_parameter=5.0,
            production_gain=1.4,
            removal_gain=0.15,
            stimulus_mode="stretch",
        ),
        ConstituentParameters(
            name="collagen_plus",
            kind="fiber",
            initial_mass=0.12,
            half_life=18.0,
            stiffness=12.0,
            deposition_stretch=1.04,
            angle_degrees=45.0,
            exponential_parameter=10.0,
            production_gain=2.0,
            removal_gain=0.35,
            stimulus_mode="stress",
        ),
        ConstituentParameters(
            name="collagen_minus",
            kind="fiber",
            initial_mass=0.12,
            half_life=18.0,
            stiffness=12.0,
            deposition_stretch=1.04,
            angle_degrees=-45.0,
            exponential_parameter=10.0,
            production_gain=2.0,
            removal_gain=0.35,
            stimulus_mode="stress",
        ),
        ConstituentParameters(
            name="matrix",
            kind="matrix",
            initial_mass=0.18,
            half_life=70.0,
            stiffness=1.4,
            deposition_stretch=1.0,
            production_gain=0.5,
            removal_gain=0.1,
            stimulus_mode="energy",
        ),
    ]


def initialize_cardiac_constituents(
    lambda_f: float = 1.08,
    lambda_s: float = 1.03,
) -> list[ConstituentParameters]:
    """Initialize the synthetic myocardium at a chosen homeostatic deformation."""

    deformation = make_incompressible_biaxial_deformation(lambda_f, lambda_s)
    return initialize_homeostatic_targets(deformation, cardiac_constituents())


def cardiac_loading_protocol(
    mode: Literal["homeostasis", "pressure", "volume", "combined", "reversal"],
    onset: float = 10.0,
    reversal_time: float = 55.0,
) -> TensorProtocol:
    """Return a smooth synthetic loading protocol in fiber-sheet coordinates."""

    if mode not in {"homeostasis", "pressure", "volume", "combined", "reversal"}:
        raise ValueError("unsupported cardiac loading mode")

    def smooth_step(time: float, center: float, width: float = 2.5) -> float:
        return float(0.5 * (1.0 + np.tanh((time - center) / width)))

    def protocol(time: float) -> Array:
        activation = smooth_step(time, onset)
        if mode == "homeostasis":
            activation = 0.0
        if mode == "reversal":
            activation *= 1.0 - smooth_step(time, reversal_time)
        if mode == "pressure":
            lambda_f = 1.08 + 0.025 * activation
            lambda_s = 1.03 + 0.055 * activation
        elif mode == "volume":
            lambda_f = 1.08 + 0.075 * activation
            lambda_s = 1.03 + 0.018 * activation
        elif mode in {"combined", "reversal"}:
            lambda_f = 1.08 + 0.055 * activation
            lambda_s = 1.03 + 0.045 * activation
        else:
            lambda_f = 1.08
            lambda_s = 1.03
        return make_incompressible_biaxial_deformation(lambda_f, lambda_s)

    return protocol


def mixture_mass_fractions(result: dict[str, object]) -> dict[str, Array]:
    """Normalize constituent masses by total mixture mass."""

    masses = result["mass"]
    if not isinstance(masses, dict):
        raise TypeError("result['mass'] must be a dictionary")
    total = np.zeros_like(next(iter(masses.values())), dtype=float)
    for values in masses.values():
        total += np.asarray(values, dtype=float)
    denominator = np.maximum(total, np.finfo(float).eps)
    return {name: np.asarray(values, dtype=float) / denominator for name, values in masses.items()}


def truncate_cohort_history(
    cohorts: Sequence[CohortRecord],
    current_time: float,
    maximum_age: float,
) -> list[CohortRecord]:
    """Discard cohorts older than a specified history window."""

    if maximum_age <= 0.0:
        raise ValueError("maximum_age must be positive")
    return [cohort for cohort in cohorts if current_time - cohort.birth_time <= maximum_age]


def history_truncation_error(
    current_stretch: float,
    cohorts: Sequence[CohortRecord],
    constituent: ConstituentParameters,
    current_time: float,
    maximum_age: float,
) -> float:
    """Relative constituent-stress error introduced by history truncation."""

    full = constituent_stress_from_cohorts(current_stretch, cohorts, constituent)
    truncated = constituent_stress_from_cohorts(
        current_stretch,
        truncate_cohort_history(cohorts, current_time, maximum_age),
        constituent,
    )
    return float(abs(truncated - full) / max(abs(full), np.finfo(float).eps))


def polarimetry_to_mixture_prior(
    mean_angle_degrees: Array | float,
    concentration: Array | float,
    retardance: Array | float,
    minimum_collagen_fraction: float = 0.05,
    maximum_collagen_fraction: float = 0.45,
) -> dict[str, Array]:
    """Map synthetic polarization-inspired observables to mixture priors.

    This is a transparent pedagogical mapping, not an experimentally calibrated inverse
    law. Concentration controls directional order; retardance controls a bounded collagen
    mass prior; the mean angle sets the symmetric collagen-family directions.
    """

    if not 0.0 <= minimum_collagen_fraction < maximum_collagen_fraction <= 1.0:
        raise ValueError("collagen-fraction bounds must lie in [0, 1]")
    angle = np.asarray(mean_angle_degrees, dtype=float)
    beta = np.clip(np.asarray(concentration, dtype=float), 0.0, 1.0)
    retardance_array = np.asarray(retardance, dtype=float)
    normalized_retardance = (retardance_array - np.nanmin(retardance_array)) / max(
        float(np.nanmax(retardance_array) - np.nanmin(retardance_array)),
        np.finfo(float).eps,
    )
    collagen_fraction = minimum_collagen_fraction + (
        maximum_collagen_fraction - minimum_collagen_fraction
    ) * normalized_retardance
    half_spread = 45.0 * (1.0 - beta)
    return {
        "mean_angle_degrees": angle,
        "family_plus_degrees": angle + half_spread,
        "family_minus_degrees": angle - half_spread,
        "directional_order": beta,
        "collagen_fraction": collagen_fraction,
    }



def generic_fibrous_constituents() -> list[ConstituentParameters]:
    """Return a universal four-constituent educational mixture.

    The internal names are retained for backward compatibility with Tutorial 11,
    while the teaching text interprets them generically as primary load-bearing
    fibers/cells, two collagen-like families, and an isotropic matrix.
    """
    return cardiac_constituents()


def initialize_generic_constituents(
    lambda_primary: float = 1.08,
    lambda_transverse: float = 1.03,
) -> list[ConstituentParameters]:
    """Initialize the generic mixture at a chosen biaxial homeostatic state."""
    deformation = make_incompressible_biaxial_deformation(lambda_primary, lambda_transverse)
    return initialize_homeostatic_targets(deformation, generic_fibrous_constituents())


def generic_loading_protocol(
    mode: Literal["homeostasis", "pressure", "volume", "combined", "reversal"],
    onset: float = 10.0,
    reversal_time: float = 55.0,
) -> TensorProtocol:
    """Return a generic axial/transverse loading protocol."""
    return cardiac_loading_protocol(mode, onset=onset, reversal_time=reversal_time)


def imaging_to_mixture_prior(
    mean_angle_degrees: Array | float,
    concentration: Array | float,
    structural_contrast: Array | float,
    minimum_collagen_fraction: float = 0.05,
    maximum_collagen_fraction: float = 0.45,
) -> dict[str, Array]:
    """Map generic orientation-sensitive imaging features to transparent priors."""
    return polarimetry_to_mixture_prior(
        mean_angle_degrees,
        concentration,
        structural_contrast,
        minimum_collagen_fraction,
        maximum_collagen_fraction,
    )

def model_state_count(
    n_constituents: int,
    n_time_steps: int,
    n_spatial_points: int = 1,
) -> dict[str, int]:
    """Compare state counts of kinematic, homogenized, and full-history models."""

    if n_constituents <= 0 or n_time_steps <= 1 or n_spatial_points <= 0:
        raise ValueError("state-count arguments must be positive")
    return {
        "kinematic_growth": 9 * n_spatial_points,
        "homogenized_mixture": 2 * n_constituents * n_spatial_points,
        "full_history_mixture": n_constituents * n_time_steps * n_spatial_points,
    }


def mixture_metrics(result: dict[str, object]) -> dict[str, float]:
    """Summarize a constrained-mixture simulation."""

    total_mass = np.asarray(result["total_mass"], dtype=float)
    total_stress = np.asarray(result["total_stress"], dtype=float)
    return {
        "initial_mass": float(total_mass[0]),
        "final_mass": float(total_mass[-1]),
        "mass_ratio": float(total_mass[-1] / max(total_mass[0], np.finfo(float).eps)),
        "initial_stress": float(total_stress[0]),
        "final_stress": float(total_stress[-1]),
        "peak_stress": float(np.max(total_stress)),
    }


__all__ = [
    "CohortRecord",
    "ConstituentParameters",
    "MixtureSimulationParameters",
    "axial_wrap",
    "cardiac_constituents",
    "cardiac_loading_protocol",
    "cohort_elastic_stretch",
    "constituent_energy_from_cohorts",
    "constituent_stimulus_error",
    "constituent_stress_from_cohorts",
    "direction_vector",
    "feedback_multiplier",
    "fiber_specific_energy",
    "fiber_specific_tension",
    "fiber_stretch",
    "history_truncation_error",
    "imaging_to_mixture_prior",
    "generic_loading_protocol",
    "initialize_generic_constituents",
    "generic_fibrous_constituents",
    "initialize_cardiac_constituents",
    "initialize_homeostatic_targets",
    "make_incompressible_biaxial_deformation",
    "matrix_specific_energy",
    "matrix_specific_nominal_stress",
    "mixture_mass_fractions",
    "mixture_metrics",
    "model_state_count",
    "polarimetry_to_mixture_prior",
    "simulate_constrained_mixture",
    "simulate_homogenized_mixture",
    "survival_fraction",
    "truncate_cohort_history",
]
