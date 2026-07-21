"""Educational active-mechanics models for Tutorial 04.

The module intentionally keeps the constitutive ingredients small and explicit.
All default parameters are synthetic teaching values and must not be interpreted
as fitted properties of a specific tissue, species, or patient.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np
from scipy.optimize import brentq

ArrayLike = float | np.ndarray


@dataclass(frozen=True)
class ActivationParameters:
    """Parameters for a normalized twitch-like activation waveform."""

    delay: float = 0.05
    tau_rise: float = 0.035
    tau_decay: float = 0.22


@dataclass(frozen=True)
class ForceLengthParameters:
    """Synthetic force-length relation parameters."""

    optimal_stretch: float = 1.10
    width_ascending: float = 0.18
    width_descending: float = 0.28


@dataclass(frozen=True)
class ForceVelocityParameters:
    """Synthetic Hill-type force-velocity parameters.

    Positive velocity denotes shortening and negative velocity denotes active
    lengthening in this educational sign convention.
    """

    maximum_shortening_velocity: float = 1.0
    curvature: float = 0.25
    eccentric_gain: float = 0.55
    eccentric_velocity_scale: float = 0.35


@dataclass(frozen=True)
class ActiveTensionParameters:
    """Combined active-tension parameters."""

    maximum_tension: float = 55.0
    force_length: ForceLengthParameters = ForceLengthParameters()
    force_velocity: ForceVelocityParameters = ForceVelocityParameters()


@dataclass(frozen=True)
class CrossbridgeParameters:
    """Minimal calcium/cross-bridge kinetic parameters."""

    calcium_time_constant: float = 0.035
    binding_rate: float = 8.0
    unbinding_rate: float = 1.8
    cooperativity: float = 3.0


def _as_array(value: ArrayLike) -> np.ndarray:
    return np.asarray(value, dtype=float)


def activation_biexponential(
    time: ArrayLike,
    parameters: ActivationParameters = ActivationParameters(),
) -> np.ndarray:
    """Return a normalized bi-exponential activation transient."""
    t = _as_array(time)
    shifted = np.maximum(t - parameters.delay, 0.0)
    raw = np.exp(-shifted / parameters.tau_decay) - np.exp(-shifted / parameters.tau_rise)
    raw = np.where(t >= parameters.delay, raw, 0.0)
    if parameters.tau_decay <= parameters.tau_rise:
        raise ValueError("tau_decay must exceed tau_rise")
    peak_time = (
        parameters.tau_rise
        * parameters.tau_decay
        / (parameters.tau_decay - parameters.tau_rise)
        * np.log(parameters.tau_decay / parameters.tau_rise)
    )
    peak = np.exp(-peak_time / parameters.tau_decay) - np.exp(-peak_time / parameters.tau_rise)
    return np.clip(raw / peak, 0.0, 1.0)


def activation_half_cosine(
    time: ArrayLike,
    onset: float = 0.05,
    duration: float = 0.45,
) -> np.ndarray:
    """Return a compact smooth half-cosine activation pulse."""
    t = _as_array(time)
    phase = (t - onset) / duration
    inside = (phase >= 0.0) & (phase <= 1.0)
    pulse = 0.5 * (1.0 - np.cos(2.0 * np.pi * phase))
    return np.where(inside, pulse, 0.0)


def calcium_gamma_transient(
    time: ArrayLike,
    onset: float = 0.03,
    shape: float = 3.0,
    scale: float = 0.045,
) -> np.ndarray:
    """Return a normalized gamma-shaped synthetic calcium transient."""
    t = _as_array(time)
    shifted = np.maximum(t - onset, 0.0)
    raw = shifted ** (shape - 1.0) * np.exp(-shifted / scale)
    peak_time = max((shape - 1.0) * scale, np.finfo(float).eps)
    peak = peak_time ** (shape - 1.0) * np.exp(-peak_time / scale)
    return np.where(t >= onset, raw / peak, 0.0)


def force_length(
    stretch: ArrayLike,
    parameters: ForceLengthParameters = ForceLengthParameters(),
) -> np.ndarray:
    """Return an asymmetric Gaussian force-length multiplier."""
    lam = _as_array(stretch)
    width = np.where(
        lam <= parameters.optimal_stretch,
        parameters.width_ascending,
        parameters.width_descending,
    )
    return np.exp(-(((lam - parameters.optimal_stretch) / width) ** 2))


def force_velocity(
    shortening_velocity: ArrayLike,
    parameters: ForceVelocityParameters = ForceVelocityParameters(),
) -> np.ndarray:
    """Return a continuous Hill-type force-velocity multiplier."""
    velocity = _as_array(shortening_velocity)
    vmax = parameters.maximum_shortening_velocity
    normalized = velocity / vmax
    concentric = (1.0 - normalized) / (1.0 + normalized / parameters.curvature)
    concentric = np.clip(concentric, 0.0, None)
    lengthening = -np.minimum(normalized, 0.0)
    eccentric = 1.0 + parameters.eccentric_gain * lengthening / (
        parameters.eccentric_velocity_scale + lengthening
    )
    return np.where(velocity >= 0.0, concentric, eccentric)


def active_tension(
    activation: ArrayLike,
    stretch: ArrayLike,
    shortening_velocity: ArrayLike = 0.0,
    parameters: ActiveTensionParameters = ActiveTensionParameters(),
) -> np.ndarray:
    """Combine activation, force-length, and force-velocity multipliers."""
    a = np.clip(_as_array(activation), 0.0, 1.0)
    return (
        parameters.maximum_tension
        * a
        * force_length(stretch, parameters.force_length)
        * force_velocity(shortening_velocity, parameters.force_velocity)
    )


def passive_uniaxial_nominal_stress(stretch: ArrayLike, shear_modulus: float = 12.0) -> np.ndarray:
    """Incompressible Neo-Hookean nominal stress for a uniaxial path."""
    lam = _as_array(stretch)
    if np.any(lam <= 0.0):
        raise ValueError("stretch must be positive")
    return shear_modulus * (lam - lam**-2)


def current_fiber_direction(
    deformation_gradient: np.ndarray, reference_fiber: np.ndarray
) -> np.ndarray:
    """Push a reference fiber to the current configuration and normalize it."""
    f = np.asarray(deformation_gradient, dtype=float)
    a0 = np.asarray(reference_fiber, dtype=float)
    a = f @ a0
    norm = np.linalg.norm(a)
    if norm <= 0.0:
        raise ValueError("deformed fiber direction has zero norm")
    return a / norm


def active_cauchy_stress(
    deformation_gradient: np.ndarray,
    reference_fiber: np.ndarray,
    tension: float,
    transverse_fraction: float = 0.0,
) -> np.ndarray:
    """Return an active Cauchy stress with optional transverse contribution."""
    a = current_fiber_direction(deformation_gradient, reference_fiber)
    identity = np.eye(3)
    fiber_projector = np.outer(a, a)
    transverse_projector = 0.5 * (identity - fiber_projector)
    return tension * (fiber_projector + transverse_fraction * transverse_projector)


def active_first_piola(
    deformation_gradient: np.ndarray,
    reference_fiber: np.ndarray,
    tension: float,
    transverse_fraction: float = 0.0,
) -> np.ndarray:
    """Convert active Cauchy stress to first Piola stress."""
    f = np.asarray(deformation_gradient, dtype=float)
    jacobian = float(np.linalg.det(f))
    sigma = active_cauchy_stress(
        f,
        reference_fiber,
        tension,
        transverse_fraction,
    )
    return jacobian * sigma @ np.linalg.inv(f).T


def active_strain_tensor(
    active_stretch: float,
    reference_fiber: np.ndarray = np.array([1.0, 0.0, 0.0]),
) -> np.ndarray:
    """Return a volume-preserving active deformation gradient."""
    if active_stretch <= 0.0:
        raise ValueError("active_stretch must be positive")
    a0 = np.asarray(reference_fiber, dtype=float)
    a0 = a0 / np.linalg.norm(a0)
    identity = np.eye(3)
    projector = np.outer(a0, a0)
    return active_stretch * projector + active_stretch ** (-0.5) * (identity - projector)


def active_strain_uniaxial_nominal_response(
    stretch: ArrayLike,
    active_stretch: float,
    shear_modulus: float = 12.0,
) -> np.ndarray:
    """Nominal response of a Neo-Hookean material under active strain."""
    lam = _as_array(stretch)
    la = float(active_stretch)
    return shear_modulus * (lam / la**2 - la / lam**2)


def active_stress_uniaxial_nominal_response(
    stretch: ArrayLike,
    tension: ArrayLike,
    shear_modulus: float = 12.0,
) -> np.ndarray:
    """Total nominal response for additive active Cauchy tension."""
    lam = _as_array(stretch)
    t = _as_array(tension)
    return passive_uniaxial_nominal_stress(lam, shear_modulus) + t / lam


def calibrate_active_stretch(
    reference_stretch: float,
    target_active_nominal: float,
    shear_modulus: float = 12.0,
    bracket: tuple[float, float] = (0.55, 0.999999),
) -> float:
    """Choose active stretch so active strain matches one active-stress datum."""
    passive = float(passive_uniaxial_nominal_stress(reference_stretch, shear_modulus))

    def residual(active_stretch: float) -> float:
        total = float(
            active_strain_uniaxial_nominal_response(
                reference_stretch,
                active_stretch,
                shear_modulus,
            )
        )
        return total - passive - target_active_nominal

    return float(brentq(residual, *bracket))


def neo_hookean_energy(deformation_gradient: np.ndarray, shear_modulus: float = 12.0) -> float:
    """Isochoric Neo-Hookean energy for det(F)=1 examples."""
    f = np.asarray(deformation_gradient, dtype=float)
    c = f.T @ f
    return 0.5 * shear_modulus * (float(np.trace(c)) - 3.0)


def active_strain_energy(
    deformation_gradient: np.ndarray,
    active_stretch: float,
    shear_modulus: float = 12.0,
    reference_fiber: np.ndarray = np.array([1.0, 0.0, 0.0]),
) -> float:
    """Evaluate passive energy on the elastic part Fe = F Fa^{-1}."""
    fa = active_strain_tensor(active_stretch, reference_fiber)
    fe = np.asarray(deformation_gradient, dtype=float) @ np.linalg.inv(fa)
    return neo_hookean_energy(fe, shear_modulus)


def simple_shear_gradient(amount: float) -> np.ndarray:
    """Simple shear that rotates a reference x-fiber in the x-y plane."""
    return np.array([[1.0, 0.0, 0.0], [amount, 1.0, 0.0], [0.0, 0.0, 1.0]])


def generalized_shear_response(
    energy_function: Callable[[np.ndarray], float],
    shear_amount: ArrayLike,
    step: float = 1.0e-5,
) -> np.ndarray:
    """Differentiate energy along the simple-shear path."""
    gamma = _as_array(shear_amount)
    flat = gamma.ravel()
    response = np.empty_like(flat)
    for index, value in enumerate(flat):
        plus = energy_function(simple_shear_gradient(float(value + step)))
        minus = energy_function(simple_shear_gradient(float(value - step)))
        response[index] = (plus - minus) / (2.0 * step)
    return response.reshape(gamma.shape)


def active_stress_shear_response(
    shear_amount: ArrayLike,
    tension: float,
    shear_modulus: float = 12.0,
    transverse_fraction: float = 0.0,
) -> np.ndarray:
    """Generalized simple-shear response for additive active stress."""
    gamma = _as_array(shear_amount)
    result = np.empty_like(gamma)
    a0 = np.array([1.0, 0.0, 0.0])
    for index, value in np.ndenumerate(gamma):
        f = simple_shear_gradient(float(value))
        passive = shear_modulus * float(value)
        active_p = active_first_piola(
            f,
            a0,
            tension,
            transverse_fraction,
        )
        result[index] = passive + active_p[1, 0]
    return result


def active_strain_shear_response(
    shear_amount: ArrayLike,
    active_stretch: float,
    shear_modulus: float = 12.0,
) -> np.ndarray:
    """Generalized simple-shear response for multiplicative active strain."""
    return generalized_shear_response(
        lambda f: active_strain_energy(f, active_stretch, shear_modulus),
        shear_amount,
    )


def simulate_crossbridge(
    time: np.ndarray,
    calcium_target: np.ndarray,
    parameters: CrossbridgeParameters = CrossbridgeParameters(),
    initial_calcium: float = 0.0,
    initial_bound_fraction: float = 0.0,
) -> dict[str, np.ndarray]:
    """Integrate a transparent two-state calcium/cross-bridge model."""
    t = np.asarray(time, dtype=float)
    target = np.asarray(calcium_target, dtype=float)
    if t.ndim != 1 or target.shape != t.shape:
        raise ValueError("time and calcium_target must be one-dimensional and equal length")
    calcium = np.empty_like(t)
    bound = np.empty_like(t)
    calcium[0] = initial_calcium
    bound[0] = initial_bound_fraction
    for i in range(t.size - 1):
        dt = t[i + 1] - t[i]
        dc = (target[i] - calcium[i]) / parameters.calcium_time_constant
        activation_term = parameters.binding_rate * calcium[i] ** parameters.cooperativity
        dx = activation_term * (1.0 - bound[i]) - parameters.unbinding_rate * bound[i]
        calcium[i + 1] = np.clip(calcium[i] + dt * dc, 0.0, 1.5)
        bound[i + 1] = np.clip(bound[i] + dt * dx, 0.0, 1.0)
    return {"time": t, "calcium": calcium, "bound_fraction": bound}


def simulate_isometric_twitch(
    time: np.ndarray,
    stretch: float,
    activation: np.ndarray,
    shear_modulus: float = 12.0,
    active_parameters: ActiveTensionParameters = ActiveTensionParameters(),
) -> dict[str, np.ndarray]:
    """Return passive, active, and total nominal stress at fixed stretch."""
    t = np.asarray(time, dtype=float)
    a = np.asarray(activation, dtype=float)
    passive_scalar = float(passive_uniaxial_nominal_stress(stretch, shear_modulus))
    passive = np.full_like(t, passive_scalar)
    tension = active_tension(a, stretch, 0.0, active_parameters)
    active_nominal = tension / stretch
    return {
        "time": t,
        "activation": a,
        "passive": passive,
        "active": active_nominal,
        "total": passive + active_nominal,
    }


def simulate_isotonic_shortening(
    time: np.ndarray,
    activation: np.ndarray,
    afterload: float,
    initial_stretch: float = 1.10,
    shear_modulus: float = 12.0,
    active_parameters: ActiveTensionParameters = ActiveTensionParameters(),
    stretch_bounds: tuple[float, float] = (0.72, 1.35),
) -> dict[str, np.ndarray]:
    """Solve a quasi-static afterload problem at each time point.

    Velocity dependence is intentionally omitted here so the scalar equilibrium
    remains transparent. It is examined independently in the force-velocity
    experiment.
    """
    t = np.asarray(time, dtype=float)
    a = np.asarray(activation, dtype=float)
    stretch = np.empty_like(t)
    stretch[0] = initial_stretch

    def equilibrium(lam: float, activation_level: float) -> float:
        tension = float(active_tension(activation_level, lam, 0.0, active_parameters))
        total = float(active_stress_uniaxial_nominal_response(lam, tension, shear_modulus))
        return total - afterload

    lower, upper = stretch_bounds
    for i in range(1, t.size):
        r_lower = equilibrium(lower, a[i])
        r_upper = equilibrium(upper, a[i])
        if r_lower * r_upper <= 0.0:
            stretch[i] = brentq(equilibrium, lower, upper, args=(float(a[i]),))
        else:
            candidates = np.array([lower, upper])
            residuals = np.abs([r_lower, r_upper])
            stretch[i] = float(candidates[int(np.argmin(residuals))])
    tension = active_tension(a, stretch, 0.0, active_parameters)
    total = active_stress_uniaxial_nominal_response(stretch, tension, shear_modulus)
    return {
        "time": t,
        "activation": a,
        "stretch": stretch,
        "total": total,
        "afterload": np.full_like(t, afterload),
    }
