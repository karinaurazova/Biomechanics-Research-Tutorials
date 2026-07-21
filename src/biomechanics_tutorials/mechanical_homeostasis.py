"""Educational feedback, turnover, and vascular homeostasis models.

The functions in this module are intentionally compact and transparent.  They are
verification-oriented teaching models, not calibrated descriptions of a particular
tissue, animal, patient, or experiment.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
from scipy.integrate import trapezoid


@dataclass(frozen=True)
class HomeostasisParameters:
    """Parameters for the scalar mechanical-homeostasis feedback model."""

    target_stress: float = 1.0
    adaptation_rate: float = 0.35
    dead_zone: float = 0.0
    response_limit: float | None = None
    sensor_bias: float = 0.0
    sensing_time_constant: float = 0.0
    delay: float = 0.0
    capacity_min: float = 1.0e-6
    capacity_max: float = np.inf
    feedback_sign: float = 1.0
    biological_bias: float = 0.0

    def validate(self) -> None:
        if self.target_stress <= 0.0:
            raise ValueError("target_stress must be positive")
        if self.adaptation_rate < 0.0:
            raise ValueError("adaptation_rate must be nonnegative")
        if self.dead_zone < 0.0:
            raise ValueError("dead_zone must be nonnegative")
        if self.response_limit is not None and self.response_limit <= 0.0:
            raise ValueError("response_limit must be positive when provided")
        if self.sensing_time_constant < 0.0:
            raise ValueError("sensing_time_constant must be nonnegative")
        if self.delay < 0.0:
            raise ValueError("delay must be nonnegative")
        if self.capacity_min <= 0.0:
            raise ValueError("capacity_min must be positive")
        if self.capacity_max <= self.capacity_min:
            raise ValueError("capacity_max must exceed capacity_min")
        if self.feedback_sign == 0.0:
            raise ValueError("feedback_sign must be nonzero")


@dataclass(frozen=True)
class ConstituentTurnoverParameters:
    """Homeostatic mass and first-order turnover parameters for one constituent."""

    name: str
    homeostatic_mass: float
    half_life: float
    production_sensitivity: float = 1.0
    removal_sensitivity: float = 0.0
    deposition_stretch: float = 1.0

    def validate(self) -> None:
        if not self.name:
            raise ValueError("name must not be empty")
        if self.homeostatic_mass <= 0.0:
            raise ValueError("homeostatic_mass must be positive")
        if self.half_life <= 0.0:
            raise ValueError("half_life must be positive")
        if self.deposition_stretch <= 0.0:
            raise ValueError("deposition_stretch must be positive")


@dataclass(frozen=True)
class VesselHomeostasisParameters:
    """Dimensionless two-stimulus adaptation parameters for an idealized artery."""

    homeostatic_pressure: float = 1.0
    homeostatic_flow: float = 1.0
    homeostatic_radius: float = 1.0
    homeostatic_thickness: float = 1.0
    radius_rate: float = 0.25
    thickness_rate: float = 0.18
    dead_zone: float = 0.0
    response_limit: float | None = 1.0
    radius_min: float = 0.15
    radius_max: float = 4.0
    thickness_min: float = 0.10
    thickness_max: float = 5.0

    def validate(self) -> None:
        positive = (
            self.homeostatic_pressure,
            self.homeostatic_flow,
            self.homeostatic_radius,
            self.homeostatic_thickness,
            self.radius_min,
            self.radius_max,
            self.thickness_min,
            self.thickness_max,
        )
        if any(value <= 0.0 for value in positive):
            raise ValueError("reference values and bounds must be positive")
        if self.radius_rate < 0.0 or self.thickness_rate < 0.0:
            raise ValueError("adaptation rates must be nonnegative")
        if self.radius_max <= self.radius_min:
            raise ValueError("radius_max must exceed radius_min")
        if self.thickness_max <= self.thickness_min:
            raise ValueError("thickness_max must exceed thickness_min")
        if self.dead_zone < 0.0:
            raise ValueError("dead_zone must be nonnegative")
        if self.response_limit is not None and self.response_limit <= 0.0:
            raise ValueError("response_limit must be positive when provided")


def _as_history(values: np.ndarray | Iterable[float] | float, size: int, name: str) -> np.ndarray:
    array = np.asarray(values, dtype=float)
    if array.ndim == 0:
        return np.full(size, float(array))
    if array.shape != (size,):
        raise ValueError(f"{name} must be scalar or have shape ({size},)")
    return array.copy()


def _validate_time(time: np.ndarray | Iterable[float]) -> np.ndarray:
    values = np.asarray(time, dtype=float)
    if values.ndim != 1 or values.size < 2:
        raise ValueError("time must be a one-dimensional array with at least two entries")
    if not np.all(np.diff(values) > 0.0):
        raise ValueError("time must be strictly increasing")
    return values


def relative_homeostatic_error(stimulus: np.ndarray | float, target: np.ndarray | float) -> np.ndarray:
    """Return the dimensionless deviation ``stimulus / target - 1``."""

    stimulus_values = np.asarray(stimulus, dtype=float)
    target_values = np.asarray(target, dtype=float)
    if np.any(target_values <= 0.0):
        raise ValueError("target values must be positive")
    return stimulus_values / target_values - 1.0


def feedback_response(
    error: np.ndarray | float,
    dead_zone: float = 0.0,
    response_limit: float | None = None,
) -> np.ndarray:
    """Apply a symmetric dead zone and optional smooth saturation to an error."""

    if dead_zone < 0.0:
        raise ValueError("dead_zone must be nonnegative")
    if response_limit is not None and response_limit <= 0.0:
        raise ValueError("response_limit must be positive when provided")
    values = np.asarray(error, dtype=float)
    active = np.sign(values) * np.maximum(np.abs(values) - dead_zone, 0.0)
    if response_limit is not None:
        active = response_limit * np.tanh(active / response_limit)
    return active


def analytical_capacity_response(
    time: np.ndarray | Iterable[float],
    load: float,
    initial_capacity: float,
    target_stress: float,
    adaptation_rate: float,
) -> np.ndarray:
    """Analytical solution for constant load and linear unsaturated feedback."""

    t = _validate_time(time)
    if load <= 0.0 or initial_capacity <= 0.0 or target_stress <= 0.0:
        raise ValueError("load, initial_capacity, and target_stress must be positive")
    if adaptation_rate < 0.0:
        raise ValueError("adaptation_rate must be nonnegative")
    equilibrium = load / target_stress
    return equilibrium + (initial_capacity - equilibrium) * np.exp(
        -adaptation_rate * (t - t[0])
    )


def generate_load_protocol(
    time: np.ndarray | Iterable[float],
    kind: str,
    baseline: float = 1.0,
    amplitude: float = 0.5,
    onset: float = 4.0,
    duration: float = 6.0,
    period: float = 4.0,
) -> np.ndarray:
    """Generate a deterministic positive load history for teaching experiments."""

    t = _validate_time(time)
    if baseline <= 0.0:
        raise ValueError("baseline must be positive")
    if duration <= 0.0 or period <= 0.0:
        raise ValueError("duration and period must be positive")
    load = np.full_like(t, baseline)
    if kind == "step":
        load[t >= onset] = baseline * (1.0 + amplitude)
    elif kind == "pulse":
        active = (t >= onset) & (t < onset + duration)
        load[active] = baseline * (1.0 + amplitude)
    elif kind == "ramp":
        fraction = np.clip((t - onset) / duration, 0.0, 1.0)
        load = baseline * (1.0 + amplitude * fraction)
    elif kind == "cyclic":
        active = t >= onset
        phase = 2.0 * np.pi * (t[active] - onset) / period
        load[active] = baseline * (1.0 + amplitude * np.sin(phase))
    else:
        raise ValueError("kind must be one of: step, pulse, ramp, cyclic")
    if np.any(load <= 0.0):
        raise ValueError("the selected protocol produced a nonpositive load")
    return load


def simulate_scalar_homeostasis(
    time: np.ndarray | Iterable[float],
    load: np.ndarray | Iterable[float] | float,
    initial_capacity: float = 1.0,
    parameters: HomeostasisParameters | None = None,
    target_stress: np.ndarray | Iterable[float] | float | None = None,
    measurement_noise_std: float = 0.0,
    seed: int = 0,
) -> dict[str, np.ndarray]:
    """Integrate a scalar stress-regulating feedback model with explicit Euler steps.

    The state ``capacity`` can represent an effective load-bearing area, mass, or
    stiffness-like structural variable.  Stress is ``load / capacity`` and the basic
    evolution law is ``d capacity / dt = k capacity response(error)``.
    """

    t = _validate_time(time)
    params = parameters or HomeostasisParameters()
    params.validate()
    if initial_capacity <= 0.0:
        raise ValueError("initial_capacity must be positive")
    if measurement_noise_std < 0.0:
        raise ValueError("measurement_noise_std must be nonnegative")
    loads = _as_history(load, t.size, "load")
    if np.any(loads <= 0.0):
        raise ValueError("load must remain positive")
    targets = _as_history(
        params.target_stress if target_stress is None else target_stress,
        t.size,
        "target_stress",
    )
    if np.any(targets <= 0.0):
        raise ValueError("target_stress must remain positive")

    rng = np.random.default_rng(seed)
    capacity = np.empty_like(t)
    stress = np.empty_like(t)
    measured_stress = np.empty_like(t)
    sensed_stress = np.empty_like(t)
    error = np.empty_like(t)
    delayed_error = np.empty_like(t)
    response = np.empty_like(t)
    capacity_rate = np.empty_like(t)
    capacity[0] = np.clip(initial_capacity, params.capacity_min, params.capacity_max)

    for index in range(t.size):
        stress[index] = loads[index] / capacity[index]
        noise = rng.normal(0.0, measurement_noise_std)
        measured_stress[index] = stress[index] * (1.0 + params.sensor_bias) + noise
        if index == 0 or params.sensing_time_constant == 0.0:
            sensed_stress[index] = measured_stress[index]
        else:
            dt = t[index] - t[index - 1]
            alpha = 1.0 - np.exp(-dt / params.sensing_time_constant)
            sensed_stress[index] = sensed_stress[index - 1] + alpha * (
                measured_stress[index] - sensed_stress[index - 1]
            )
        error[index] = relative_homeostatic_error(sensed_stress[index], targets[index])
        delayed_time = t[index] - params.delay
        delayed_index = max(0, int(np.searchsorted(t, delayed_time, side="right") - 1))
        delayed_error[index] = error[delayed_index] + params.biological_bias
        response[index] = params.feedback_sign * feedback_response(
            delayed_error[index], params.dead_zone, params.response_limit
        )
        capacity_rate[index] = params.adaptation_rate * capacity[index] * response[index]
        if index < t.size - 1:
            dt = t[index + 1] - t[index]
            capacity[index + 1] = np.clip(
                capacity[index] + dt * capacity_rate[index],
                params.capacity_min,
                params.capacity_max,
            )

    true_error = relative_homeostatic_error(stress, targets)
    return {
        "time": t,
        "load": loads,
        "target_stress": targets,
        "capacity": capacity,
        "stress": stress,
        "measured_stress": measured_stress,
        "sensed_stress": sensed_stress,
        "error": error,
        "true_error": true_error,
        "delayed_error": delayed_error,
        "response": response,
        "capacity_rate": capacity_rate,
    }


def homeostasis_metrics(
    time: np.ndarray | Iterable[float],
    error: np.ndarray | Iterable[float],
    tolerance: float = 0.02,
) -> dict[str, float]:
    """Summarize recovery using integral, peak, residual, and settling metrics."""

    t = _validate_time(time)
    values = _as_history(error, t.size, "error")
    if tolerance <= 0.0:
        raise ValueError("tolerance must be positive")
    outside = np.flatnonzero(np.abs(values) > tolerance)
    settling_time = 0.0 if outside.size == 0 else float(t[outside[-1]] - t[0])
    return {
        "iae": float(trapezoid(np.abs(values), t)),
        "rms": float(np.sqrt(np.mean(values**2))),
        "peak_abs_error": float(np.max(np.abs(values))),
        "final_abs_error": float(abs(values[-1])),
        "settling_time": settling_time,
    }


def survival_fraction(age: np.ndarray | Iterable[float] | float, half_life: float) -> np.ndarray:
    """First-order survival function with the requested half-life."""

    if half_life <= 0.0:
        raise ValueError("half_life must be positive")
    ages = np.asarray(age, dtype=float)
    if np.any(ages < 0.0):
        raise ValueError("age must be nonnegative")
    return np.exp(-np.log(2.0) * ages / half_life)


def simulate_constituent_turnover(
    time: np.ndarray | Iterable[float],
    stimulus_error: np.ndarray | Iterable[float] | float,
    constituents: Iterable[ConstituentTurnoverParameters],
) -> dict[str, np.ndarray | list[str]]:
    """Simulate production and removal of multiple constrained constituents."""

    t = _validate_time(time)
    errors = _as_history(stimulus_error, t.size, "stimulus_error")
    items = list(constituents)
    if not items:
        raise ValueError("at least one constituent is required")
    for item in items:
        item.validate()

    count = len(items)
    mass = np.empty((count, t.size), dtype=float)
    production = np.empty_like(mass)
    removal = np.empty_like(mass)
    for row, item in enumerate(items):
        mass[row, 0] = item.homeostatic_mass
        rate = np.log(2.0) / item.half_life
        for index in range(t.size):
            production[row, index] = (
                rate
                * item.homeostatic_mass
                * np.exp(item.production_sensitivity * errors[index])
            )
            removal[row, index] = (
                rate * mass[row, index] * np.exp(-item.removal_sensitivity * errors[index])
            )
            if index < t.size - 1:
                dt = t[index + 1] - t[index]
                mass[row, index + 1] = max(
                    mass[row, index]
                    + dt * (production[row, index] - removal[row, index]),
                    1.0e-12,
                )

    return {
        "time": t,
        "names": [item.name for item in items],
        "mass": mass,
        "production": production,
        "removal": removal,
        "total_mass": np.sum(mass, axis=0),
        "deposition_stretch": np.array([item.deposition_stretch for item in items]),
    }


def vessel_stimuli(
    pressure: np.ndarray | float,
    flow: np.ndarray | float,
    radius: np.ndarray | float,
    thickness: np.ndarray | float,
    parameters: VesselHomeostasisParameters | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Return normalized wall shear and circumferential wall stress."""

    params = parameters or VesselHomeostasisParameters()
    params.validate()
    pressure_values = np.asarray(pressure, dtype=float)
    flow_values = np.asarray(flow, dtype=float)
    radius_values = np.asarray(radius, dtype=float)
    thickness_values = np.asarray(thickness, dtype=float)
    if np.any(pressure_values <= 0.0) or np.any(flow_values <= 0.0):
        raise ValueError("pressure and flow must be positive")
    if np.any(radius_values <= 0.0) or np.any(thickness_values <= 0.0):
        raise ValueError("radius and thickness must be positive")
    shear_ratio = (flow_values / params.homeostatic_flow) * (
        params.homeostatic_radius / radius_values
    ) ** 3
    wall_stress_ratio = (
        (pressure_values / params.homeostatic_pressure)
        * (radius_values / params.homeostatic_radius)
        * (params.homeostatic_thickness / thickness_values)
    )
    return shear_ratio, wall_stress_ratio


def vessel_equilibrium(
    pressure: float,
    flow: float,
    parameters: VesselHomeostasisParameters | None = None,
) -> tuple[float, float]:
    """Analytical geometry that restores both normalized stimuli to one."""

    params = parameters or VesselHomeostasisParameters()
    params.validate()
    if pressure <= 0.0 or flow <= 0.0:
        raise ValueError("pressure and flow must be positive")
    radius = params.homeostatic_radius * (flow / params.homeostatic_flow) ** (1.0 / 3.0)
    thickness = (
        params.homeostatic_thickness
        * (pressure / params.homeostatic_pressure)
        * (radius / params.homeostatic_radius)
    )
    return float(radius), float(thickness)


def simulate_vessel_homeostasis(
    time: np.ndarray | Iterable[float],
    pressure: np.ndarray | Iterable[float] | float,
    flow: np.ndarray | Iterable[float] | float,
    initial_radius: float = 1.0,
    initial_thickness: float = 1.0,
    parameters: VesselHomeostasisParameters | None = None,
) -> dict[str, np.ndarray]:
    """Integrate coupled radius/thickness adaptation to two vascular stimuli."""

    t = _validate_time(time)
    params = parameters or VesselHomeostasisParameters()
    params.validate()
    pressures = _as_history(pressure, t.size, "pressure")
    flows = _as_history(flow, t.size, "flow")
    if np.any(pressures <= 0.0) or np.any(flows <= 0.0):
        raise ValueError("pressure and flow must remain positive")
    if initial_radius <= 0.0 or initial_thickness <= 0.0:
        raise ValueError("initial geometry must be positive")

    radius = np.empty_like(t)
    thickness = np.empty_like(t)
    shear = np.empty_like(t)
    wall_stress = np.empty_like(t)
    radius_rate = np.empty_like(t)
    thickness_rate = np.empty_like(t)
    radius[0] = np.clip(initial_radius, params.radius_min, params.radius_max)
    thickness[0] = np.clip(initial_thickness, params.thickness_min, params.thickness_max)

    for index in range(t.size):
        shear[index], wall_stress[index] = vessel_stimuli(
            pressures[index], flows[index], radius[index], thickness[index], params
        )
        shear_error = shear[index] - 1.0
        stress_error = wall_stress[index] - 1.0
        radius_rate[index] = params.radius_rate * radius[index] * feedback_response(
            shear_error, params.dead_zone, params.response_limit
        )
        thickness_rate[index] = params.thickness_rate * thickness[index] * feedback_response(
            stress_error, params.dead_zone, params.response_limit
        )
        if index < t.size - 1:
            dt = t[index + 1] - t[index]
            radius[index + 1] = np.clip(
                radius[index] + dt * radius_rate[index], params.radius_min, params.radius_max
            )
            thickness[index + 1] = np.clip(
                thickness[index] + dt * thickness_rate[index],
                params.thickness_min,
                params.thickness_max,
            )

    return {
        "time": t,
        "pressure": pressures,
        "flow": flows,
        "radius": radius,
        "thickness": thickness,
        "shear_ratio": shear,
        "wall_stress_ratio": wall_stress,
        "radius_rate": radius_rate,
        "thickness_rate": thickness_rate,
    }
