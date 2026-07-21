"""Synthetic extracellular-matrix turnover models for Tutorial 10.

The module separates open-system mass balance, cohort survival, biochemical
maturation, cross-linking, enzyme regulation, and mechanical readouts.  It is
intended for verification-oriented teaching, not tissue-specific prediction.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping, Sequence

import numpy as np

Array = np.ndarray
ScalarProtocol = Callable[[float], float]


@dataclass(frozen=True)
class SurvivalParameters:
    """Parameters of a cohort survival law."""

    model: str = "exponential"
    half_life: float = 20.0
    shape: float = 1.0

    def validate(self) -> None:
        if self.model not in {"exponential", "weibull"}:
            raise ValueError("model must be 'exponential' or 'weibull'")
        if self.half_life <= 0.0:
            raise ValueError("half_life must be positive")
        if self.shape <= 0.0:
            raise ValueError("shape must be positive")


@dataclass(frozen=True)
class MechanobiologyParameters:
    """Dimensionless stress-feedback parameters for ECM production/removal."""

    target_stress: float = 1.0
    stress_scale: float = 1.0
    production_gain: float = 1.0
    degradation_gain: float = 0.4
    dead_zone: float = 0.0
    saturation: float = 2.0

    def validate(self) -> None:
        if self.target_stress <= 0.0:
            raise ValueError("target_stress must be positive")
        if self.stress_scale <= 0.0:
            raise ValueError("stress_scale must be positive")
        if self.dead_zone < 0.0:
            raise ValueError("dead_zone must be non-negative")
        if self.saturation <= 0.0:
            raise ValueError("saturation must be positive")


@dataclass(frozen=True)
class CollagenKineticsParameters:
    """Reduced collagen synthesis, maturation, degradation, and cross-link kinetics."""

    basal_synthesis: float = 0.08
    secretion_rate: float = 1.2
    maturation_rate: float = 0.16
    immature_degradation_rate: float = 0.10
    mature_degradation_rate: float = 0.025
    crosslink_formation_rate: float = 0.08
    crosslink_loss_rate: float = 0.01
    mmp_relaxation_rate: float = 0.7
    timp_relaxation_rate: float = 0.5
    mmp_baseline: float = 1.0
    timp_baseline: float = 1.0
    mmp_inflammation_gain: float = 2.0
    timp_inflammation_gain: float = 0.25
    inhibition_constant: float = 0.6
    crosslink_stiffness_gain: float = 2.0
    feedback: MechanobiologyParameters = MechanobiologyParameters()

    def validate(self) -> None:
        positive = {
            "basal_synthesis": self.basal_synthesis,
            "secretion_rate": self.secretion_rate,
            "maturation_rate": self.maturation_rate,
            "immature_degradation_rate": self.immature_degradation_rate,
            "mature_degradation_rate": self.mature_degradation_rate,
            "mmp_relaxation_rate": self.mmp_relaxation_rate,
            "timp_relaxation_rate": self.timp_relaxation_rate,
            "mmp_baseline": self.mmp_baseline,
            "timp_baseline": self.timp_baseline,
            "inhibition_constant": self.inhibition_constant,
        }
        for name, value in positive.items():
            if value <= 0.0:
                raise ValueError(f"{name} must be positive")
        if self.crosslink_formation_rate < 0.0 or self.crosslink_loss_rate < 0.0:
            raise ValueError("cross-link rates must be non-negative")
        if self.crosslink_stiffness_gain < 0.0:
            raise ValueError("crosslink_stiffness_gain must be non-negative")
        self.feedback.validate()


@dataclass(frozen=True)
class MatrixComponent:
    """One homogenized ECM constituent."""

    name: str
    initial_mass: float
    basal_production: float
    half_life: float
    stiffness: float
    deposition_stretch: float = 1.0
    production_gain: float = 0.0
    degradation_gain: float = 0.0

    def validate(self) -> None:
        if not self.name:
            raise ValueError("component name must not be empty")
        if self.initial_mass < 0.0:
            raise ValueError("initial_mass must be non-negative")
        if self.basal_production < 0.0:
            raise ValueError("basal_production must be non-negative")
        if self.half_life <= 0.0:
            raise ValueError("half_life must be positive")
        if self.stiffness < 0.0:
            raise ValueError("stiffness must be non-negative")
        if self.deposition_stretch <= 0.0:
            raise ValueError("deposition_stretch must be positive")


@dataclass(frozen=True)
class Cohort:
    """A deposited ECM cohort with birth time and natural stretch."""

    birth_time: float
    deposited_mass: float
    deposition_stretch: float = 1.0
    stiffness: float = 1.0

    def validate(self) -> None:
        if self.deposited_mass < 0.0:
            raise ValueError("deposited_mass must be non-negative")
        if self.deposition_stretch <= 0.0:
            raise ValueError("deposition_stretch must be positive")
        if self.stiffness < 0.0:
            raise ValueError("stiffness must be non-negative")


def _validate_time(time: Array) -> Array:
    values = np.asarray(time, dtype=float)
    if values.ndim != 1 or values.size < 2:
        raise ValueError("time must be a one-dimensional array with at least two values")
    if not np.all(np.isfinite(values)) or np.any(np.diff(values) <= 0.0):
        raise ValueError("time must be finite and strictly increasing")
    return values


def _protocol_value(protocol: ScalarProtocol | float, time: float) -> float:
    value = protocol(time) if callable(protocol) else protocol
    return float(value)


def survival_fraction(age: Array | float, parameters: SurvivalParameters | None = None) -> Array:
    """Return the surviving fraction of a cohort at non-negative age."""

    params = parameters or SurvivalParameters()
    params.validate()
    age_array = np.maximum(np.asarray(age, dtype=float), 0.0)
    if params.model == "exponential":
        result = np.exp(-np.log(2.0) * age_array / params.half_life)
    else:
        scale = params.half_life / np.power(np.log(2.0), 1.0 / params.shape)
        result = np.exp(-np.power(age_array / scale, params.shape))
    return result


def hazard_rate(age: Array | float, parameters: SurvivalParameters | None = None) -> Array:
    """Instantaneous hazard corresponding to the selected survival law."""

    params = parameters or SurvivalParameters()
    params.validate()
    age_array = np.maximum(np.asarray(age, dtype=float), 0.0)
    if params.model == "exponential":
        return np.full_like(age_array, np.log(2.0) / params.half_life)
    scale = params.half_life / np.power(np.log(2.0), 1.0 / params.shape)
    safe_age = np.maximum(age_array, np.finfo(float).eps)
    return params.shape * np.power(safe_age / scale, params.shape - 1.0) / scale


def mechanobiological_error(stress: Array | float, parameters: MechanobiologyParameters) -> Array:
    """Normalized stress error with an optional dead zone."""

    parameters.validate()
    error = (np.asarray(stress, dtype=float) - parameters.target_stress) / parameters.stress_scale
    magnitude = np.maximum(np.abs(error) - parameters.dead_zone, 0.0)
    return np.sign(error) * magnitude


def bounded_feedback(error: Array | float, gain: float, saturation: float) -> Array:
    """Smooth bounded mechanobiological response."""

    if saturation <= 0.0:
        raise ValueError("saturation must be positive")
    return saturation * np.tanh(gain * np.asarray(error, dtype=float) / saturation)


def production_multiplier(stress: Array | float, parameters: MechanobiologyParameters) -> Array:
    """Non-negative production multiplier under stress feedback."""

    error = mechanobiological_error(stress, parameters)
    response = bounded_feedback(error, parameters.production_gain, parameters.saturation)
    return np.maximum(1.0 + response, 0.0)


def degradation_multiplier(stress: Array | float, parameters: MechanobiologyParameters) -> Array:
    """Non-negative stress-sensitive degradation multiplier."""

    error = mechanobiological_error(stress, parameters)
    response = bounded_feedback(np.abs(error), parameters.degradation_gain, parameters.saturation)
    return np.maximum(1.0 + response, 0.0)


def mmp_timp_activity(mmp: Array | float, timp: Array | float, inhibition_constant: float = 0.6) -> Array:
    """Dimensionless effective collagenolytic activity."""

    if inhibition_constant <= 0.0:
        raise ValueError("inhibition_constant must be positive")
    mmp_array = np.maximum(np.asarray(mmp, dtype=float), 0.0)
    timp_array = np.maximum(np.asarray(timp, dtype=float), 0.0)
    return mmp_array / (1.0 + timp_array / inhibition_constant)


def effective_collagen_stiffness(
    mature_mass: Array | float,
    crosslink_fraction: Array | float,
    base_stiffness: float = 1.0,
    crosslink_gain: float = 2.0,
) -> Array:
    """Reduced collagen stiffness from mature mass and cross-link fraction."""

    if base_stiffness < 0.0 or crosslink_gain < 0.0:
        raise ValueError("stiffness parameters must be non-negative")
    mass = np.maximum(np.asarray(mature_mass, dtype=float), 0.0)
    fraction = np.clip(np.asarray(crosslink_fraction, dtype=float), 0.0, 1.0)
    return base_stiffness * mass * (1.0 + crosslink_gain * fraction)


def collagen_fiber_tension(
    stretch: Array | float,
    mass: Array | float = 1.0,
    stiffness: float = 2.0,
    deposition_stretch: Array | float = 1.0,
    crosslink_fraction: Array | float = 0.0,
    crosslink_gain: float = 2.0,
    exponential_parameter: float = 6.0,
) -> Array:
    """Tension-only collagen response with deposition prestretch and cross-links."""

    if stiffness < 0.0 or exponential_parameter <= 0.0:
        raise ValueError("stiffness must be non-negative and exponential_parameter positive")
    elastic_stretch = np.asarray(stretch, dtype=float) * np.asarray(deposition_stretch, dtype=float)
    strain = np.maximum(elastic_stretch - 1.0, 0.0)
    effective = effective_collagen_stiffness(
        mass,
        crosslink_fraction,
        base_stiffness=stiffness,
        crosslink_gain=crosslink_gain,
    )
    return effective * strain * np.exp(exponential_parameter * strain * strain)


def matrix_nominal_stress(
    stretch: Array | float,
    elastin_mass: Array | float,
    collagen_mass: Array | float,
    collagen_crosslinks: Array | float,
    collagen_deposition_stretch: Array | float = 1.0,
    elastin_modulus: float = 0.8,
    collagen_modulus: float = 2.0,
) -> Array:
    """Reduced uniaxial matrix-plus-collagen nominal stress."""

    stretch_array = np.asarray(stretch, dtype=float)
    if np.any(stretch_array <= 0.0):
        raise ValueError("stretch must be positive")
    matrix = elastin_modulus * np.asarray(elastin_mass, dtype=float) * (
        stretch_array - stretch_array**-2
    )
    collagen = collagen_fiber_tension(
        stretch_array,
        mass=collagen_mass,
        stiffness=collagen_modulus,
        deposition_stretch=collagen_deposition_stretch,
        crosslink_fraction=collagen_crosslinks,
    )
    return matrix + collagen


def tangent_modulus(
    stretch: float,
    elastin_mass: float,
    collagen_mass: float,
    collagen_crosslinks: float,
    collagen_deposition_stretch: float = 1.0,
    step: float = 1.0e-5,
) -> float:
    """Finite-difference tangent modulus of the reduced ECM response."""

    if stretch <= step:
        raise ValueError("stretch must exceed the finite-difference step")
    upper = matrix_nominal_stress(
        stretch + step,
        elastin_mass,
        collagen_mass,
        collagen_crosslinks,
        collagen_deposition_stretch,
    )
    lower = matrix_nominal_stress(
        stretch - step,
        elastin_mass,
        collagen_mass,
        collagen_crosslinks,
        collagen_deposition_stretch,
    )
    return float((upper - lower) / (2.0 * step))


def simulate_collagen_maturation(
    time: Array,
    stress_protocol: ScalarProtocol | float = 1.0,
    inflammation_protocol: ScalarProtocol | float = 0.0,
    parameters: CollagenKineticsParameters | None = None,
    initial_state: Sequence[float] = (0.07, 0.25, 1.0, 0.45, 1.0, 1.0),
) -> Mapping[str, Array]:
    """Integrate precursor, immature/mature collagen, cross-links, MMP, and TIMP."""

    params = parameters or CollagenKineticsParameters()
    params.validate()
    times = _validate_time(time)
    initial = np.asarray(initial_state, dtype=float)
    if initial.shape != (6,) or np.any(initial < 0.0):
        raise ValueError("initial_state must contain six non-negative values")

    state = np.empty((times.size, 6), dtype=float)
    state[0] = initial
    stress = np.empty(times.size)
    inflammation = np.empty(times.size)
    synthesis = np.empty(times.size)
    enzyme_activity = np.empty(times.size)

    def rhs(t: float, y: Array) -> Array:
        precursor, immature, mature, crosslinks, mmp, timp = y
        current_stress = _protocol_value(stress_protocol, t)
        current_inflammation = max(_protocol_value(inflammation_protocol, t), 0.0)
        multiplier = float(production_multiplier(current_stress, params.feedback))
        synth = params.basal_synthesis * multiplier
        target_mmp = params.mmp_baseline * (1.0 + params.mmp_inflammation_gain * current_inflammation)
        target_timp = params.timp_baseline * (1.0 + params.timp_inflammation_gain * current_inflammation)
        active_enzyme = float(mmp_timp_activity(mmp, timp, params.inhibition_constant))
        stress_degradation = float(degradation_multiplier(current_stress, params.feedback))
        degradation_factor = active_enzyme * stress_degradation

        d_precursor = synth - params.secretion_rate * precursor
        d_immature = (
            params.secretion_rate * precursor
            - params.maturation_rate * immature
            - params.immature_degradation_rate * degradation_factor * immature
        )
        d_mature = (
            params.maturation_rate * immature
            - params.mature_degradation_rate * degradation_factor * mature
        )
        mature_fraction = mature / (mature + 0.25)
        d_crosslinks = (
            params.crosslink_formation_rate * mature_fraction * (1.0 - crosslinks)
            - params.crosslink_loss_rate * degradation_factor * crosslinks
        )
        d_mmp = params.mmp_relaxation_rate * (target_mmp - mmp)
        d_timp = params.timp_relaxation_rate * (target_timp - timp)
        return np.array([d_precursor, d_immature, d_mature, d_crosslinks, d_mmp, d_timp])

    for index, current_time in enumerate(times):
        stress[index] = _protocol_value(stress_protocol, current_time)
        inflammation[index] = max(_protocol_value(inflammation_protocol, current_time), 0.0)
        synthesis[index] = params.basal_synthesis * float(
            production_multiplier(stress[index], params.feedback)
        )
        enzyme_activity[index] = float(
            mmp_timp_activity(state[index, 4], state[index, 5], params.inhibition_constant)
        )
        if index == times.size - 1:
            break
        step = times[index + 1] - current_time
        y = state[index]
        k1 = rhs(current_time, y)
        k2 = rhs(current_time + 0.5 * step, np.maximum(y + 0.5 * step * k1, 0.0))
        k3 = rhs(current_time + 0.5 * step, np.maximum(y + 0.5 * step * k2, 0.0))
        k4 = rhs(current_time + step, np.maximum(y + step * k3, 0.0))
        state[index + 1] = np.maximum(y + step * (k1 + 2.0 * k2 + 2.0 * k3 + k4) / 6.0, 0.0)
        state[index + 1, 3] = np.clip(state[index + 1, 3], 0.0, 1.0)

    total_collagen = state[:, 1] + state[:, 2]
    stiffness = effective_collagen_stiffness(
        state[:, 2],
        state[:, 3],
        crosslink_gain=params.crosslink_stiffness_gain,
    )
    return {
        "time": times,
        "precursor": state[:, 0],
        "immature": state[:, 1],
        "mature": state[:, 2],
        "crosslinks": state[:, 3],
        "mmp": state[:, 4],
        "timp": state[:, 5],
        "stress": stress,
        "inflammation": inflammation,
        "synthesis": synthesis,
        "enzyme_activity": enzyme_activity,
        "total_collagen": total_collagen,
        "effective_stiffness": stiffness,
    }


def simulate_cohort_turnover(
    time: Array,
    production_protocol: ScalarProtocol | float,
    survival_parameters: SurvivalParameters | None = None,
    deposition_stretch_protocol: ScalarProtocol | float = 1.0,
    initial_mass: float = 1.0,
    initial_age: float = 0.0,
) -> Mapping[str, Array]:
    """Track explicit ECM cohorts and their surviving mass and prestretch."""

    params = survival_parameters or SurvivalParameters()
    params.validate()
    times = _validate_time(time)
    if initial_mass < 0.0 or initial_age < 0.0:
        raise ValueError("initial mass and age must be non-negative")

    births = [float(times[0] - initial_age)]
    deposited = [float(initial_mass / survival_fraction(initial_age, params))]
    prestretches = [float(_protocol_value(deposition_stretch_protocol, times[0]))]
    total_mass = np.empty(times.size)
    mean_age = np.empty(times.size)
    mean_prestretch = np.empty(times.size)
    production = np.empty(times.size)
    retained_initial_fraction = np.empty(times.size)

    for index, current_time in enumerate(times):
        if index > 0:
            step = times[index] - times[index - 1]
            rate = max(_protocol_value(production_protocol, times[index - 1]), 0.0)
            births.append(float(times[index - 1] + 0.5 * step))
            deposited.append(rate * step)
            prestretches.append(float(_protocol_value(deposition_stretch_protocol, current_time)))
        birth_array = np.asarray(births)
        deposit_array = np.asarray(deposited)
        prestretch_array = np.asarray(prestretches)
        age = np.maximum(current_time - birth_array, 0.0)
        surviving = deposit_array * survival_fraction(age, params)
        mass = float(np.sum(surviving))
        total_mass[index] = mass
        mean_age[index] = float(np.sum(surviving * age) / mass) if mass > 0.0 else 0.0
        mean_prestretch[index] = (
            float(np.sum(surviving * prestretch_array) / mass) if mass > 0.0 else 1.0
        )
        production[index] = max(_protocol_value(production_protocol, current_time), 0.0)
        initial_surviving = deposited[0] * float(survival_fraction(age[0], params))
        retained_initial_fraction[index] = initial_surviving / mass if mass > 0.0 else 0.0

    return {
        "time": times,
        "mass": total_mass,
        "mean_age": mean_age,
        "mean_deposition_stretch": mean_prestretch,
        "production": production,
        "retained_initial_fraction": retained_initial_fraction,
        "birth_times": np.asarray(births),
        "deposited_masses": np.asarray(deposited),
        "deposition_stretches": np.asarray(prestretches),
    }


def simulate_homogenized_turnover(
    time: Array,
    production_protocol: ScalarProtocol | float,
    half_life: float,
    initial_mass: float = 1.0,
) -> Mapping[str, Array]:
    """Integrate a homogenized first-order mass-turnover equation."""

    times = _validate_time(time)
    if half_life <= 0.0 or initial_mass < 0.0:
        raise ValueError("half_life must be positive and initial_mass non-negative")
    removal_rate = np.log(2.0) / half_life
    mass = np.empty(times.size)
    mass[0] = initial_mass
    production = np.empty(times.size)
    removal = np.empty(times.size)
    for index, current_time in enumerate(times):
        production[index] = max(_protocol_value(production_protocol, current_time), 0.0)
        removal[index] = removal_rate * mass[index]
        if index == times.size - 1:
            break
        step = times[index + 1] - current_time
        midpoint_time = current_time + 0.5 * step
        midpoint_production = max(_protocol_value(production_protocol, midpoint_time), 0.0)
        midpoint_mass = max(mass[index] + 0.5 * step * (production[index] - removal[index]), 0.0)
        midpoint_removal = removal_rate * midpoint_mass
        mass[index + 1] = max(mass[index] + step * (midpoint_production - midpoint_removal), 0.0)
    return {
        "time": times,
        "mass": mass,
        "production": production,
        "removal": removal,
        "net_rate": production - removal,
    }


def pulse_chase_fraction(
    time: Array | float,
    pulse_end: float,
    survival_parameters: SurvivalParameters | None = None,
) -> Array:
    """Idealized labelled fraction following a finite deposition pulse."""

    params = survival_parameters or SurvivalParameters()
    params.validate()
    values = np.asarray(time, dtype=float)
    if pulse_end <= 0.0:
        raise ValueError("pulse_end must be positive")
    labelled_age = np.maximum(values - pulse_end, 0.0)
    labelled = survival_fraction(labelled_age, params)
    return np.where(values <= pulse_end, 1.0, labelled)


def simulate_multicomponent_ecm(
    time: Array,
    components: Sequence[MatrixComponent],
    stress_protocol: ScalarProtocol | float = 1.0,
    target_stress: float = 1.0,
) -> Mapping[str, Array]:
    """Homogenized turnover of several ECM components under shared loading."""

    times = _validate_time(time)
    if target_stress <= 0.0 or not components:
        raise ValueError("target_stress must be positive and components non-empty")
    for component in components:
        component.validate()
    masses = np.empty((times.size, len(components)), dtype=float)
    masses[0] = [component.initial_mass for component in components]
    production = np.empty_like(masses)
    removal = np.empty_like(masses)
    stress = np.array([_protocol_value(stress_protocol, value) for value in times])

    for index, current_time in enumerate(times):
        error = stress[index] / target_stress - 1.0
        for component_index, component in enumerate(components):
            basal_removal = np.log(2.0) / component.half_life
            production[index, component_index] = max(
                component.basal_production * (1.0 + component.production_gain * error),
                0.0,
            )
            removal[index, component_index] = max(
                basal_removal
                * (1.0 + component.degradation_gain * abs(error))
                * masses[index, component_index],
                0.0,
            )
        if index == times.size - 1:
            break
        step = times[index + 1] - current_time
        masses[index + 1] = np.maximum(
            masses[index] + step * (production[index] - removal[index]),
            0.0,
        )

    total_mass = np.sum(masses, axis=1)
    fractions = np.divide(
        masses,
        total_mass[:, None],
        out=np.zeros_like(masses),
        where=total_mass[:, None] > 0.0,
    )
    effective_stiffness = masses @ np.asarray([component.stiffness for component in components])
    return {
        "time": times,
        "names": np.asarray([component.name for component in components], dtype=object),
        "mass": masses,
        "mass_fraction": fractions,
        "production": production,
        "removal": removal,
        "total_mass": total_mass,
        "effective_stiffness": effective_stiffness,
        "stress": stress,
    }


def simulate_spatial_degradation(
    time: Array,
    coordinate: Array,
    initial_collagen: Array,
    enzyme_source: Callable[[Array, float], Array],
    enzyme_diffusivity: float = 0.01,
    enzyme_decay: float = 0.4,
    degradation_rate: float = 0.5,
    collagen_production: float = 0.02,
) -> Mapping[str, Array]:
    """One-dimensional reaction-diffusion degradation with no-flux boundaries."""

    times = _validate_time(time)
    x = np.asarray(coordinate, dtype=float)
    collagen0 = np.asarray(initial_collagen, dtype=float)
    if x.ndim != 1 or x.size < 3 or collagen0.shape != x.shape:
        raise ValueError("coordinate and initial_collagen must be matching one-dimensional arrays")
    if np.any(np.diff(x) <= 0.0) or np.any(collagen0 < 0.0):
        raise ValueError("coordinate must increase and collagen must be non-negative")
    if min(enzyme_diffusivity, enzyme_decay, degradation_rate, collagen_production) < 0.0:
        raise ValueError("spatial parameters must be non-negative")
    dx = float(np.mean(np.diff(x)))
    collagen = np.empty((times.size, x.size), dtype=float)
    enzyme = np.zeros_like(collagen)
    collagen[0] = collagen0

    def laplacian(values: Array) -> Array:
        padded = np.pad(values, 1, mode="edge")
        return (padded[:-2] - 2.0 * padded[1:-1] + padded[2:]) / dx**2

    for index, current_time in enumerate(times[:-1]):
        step = times[index + 1] - current_time
        source = np.maximum(np.asarray(enzyme_source(x, current_time), dtype=float), 0.0)
        if source.shape != x.shape:
            raise ValueError("enzyme_source must return an array matching coordinate")
        enzyme_rate = enzyme_diffusivity * laplacian(enzyme[index]) + source - enzyme_decay * enzyme[index]
        enzyme[index + 1] = np.maximum(enzyme[index] + step * enzyme_rate, 0.0)
        collagen_rate = collagen_production - degradation_rate * enzyme[index] * collagen[index]
        collagen[index + 1] = np.maximum(collagen[index] + step * collagen_rate, 0.0)

    return {
        "time": times,
        "coordinate": x,
        "collagen": collagen,
        "enzyme": enzyme,
    }


def turnover_metrics(time: Array, mass: Array, production: Array, removal: Array) -> Mapping[str, float]:
    """Summarize open-system turnover trajectories."""

    times = _validate_time(time)
    mass_array = np.asarray(mass, dtype=float)
    production_array = np.asarray(production, dtype=float)
    removal_array = np.asarray(removal, dtype=float)
    if mass_array.shape != times.shape or production_array.shape != times.shape or removal_array.shape != times.shape:
        raise ValueError("mass, production, and removal must match time")
    cumulative_production = float(np.trapezoid(production_array, times))
    cumulative_removal = float(np.trapezoid(removal_array, times))
    balance_residual = float(
        mass_array[-1] - mass_array[0] - cumulative_production + cumulative_removal
    )
    return {
        "initial_mass": float(mass_array[0]),
        "final_mass": float(mass_array[-1]),
        "minimum_mass": float(np.min(mass_array)),
        "maximum_mass": float(np.max(mass_array)),
        "cumulative_production": cumulative_production,
        "cumulative_removal": cumulative_removal,
        "balance_residual": balance_residual,
    }


def compare_model_state_count(number_of_time_steps: int, number_of_components: int = 1) -> Mapping[str, int]:
    """Compare state burden of turnover modeling levels."""

    if number_of_time_steps <= 0 or number_of_components <= 0:
        raise ValueError("state-count arguments must be positive")
    return {
        "net_mass_ode": number_of_components,
        "maturation_ode": 6 * number_of_components,
        "age_structured_cohorts": number_of_time_steps * number_of_components,
        "spatial_cohort_model": number_of_time_steps * number_of_components**2,
    }
