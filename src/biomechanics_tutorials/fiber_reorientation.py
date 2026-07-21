"""Minimal orientation-remodeling model for an undirected fiber family.

Angles are represented in radians. Fiber orientation is axial, not directional:
``theta`` and ``theta + pi`` describe the same physical axis.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Callable
import numpy as np
from numpy.typing import ArrayLike, NDArray

TargetFunction = Callable[[float], float]


@dataclass(frozen=True)
class ReorientationParameters:
    """Parameters of the first-order reorientation law."""

    rate: float = 0.35
    duration: float = 20.0
    time_step: float = 0.01

    def validate(self) -> None:
        if self.rate < 0:
            raise ValueError("rate must be non-negative")
        if self.duration <= 0:
            raise ValueError("duration must be positive")
        if self.time_step <= 0:
            raise ValueError("time_step must be positive")
        if self.time_step > self.duration:
            raise ValueError("time_step must not exceed duration")
        if self.rate * self.time_step >= 2.0:
            raise ValueError(
                "explicit Euler is unstable for the local relaxation problem when rate*time_step >= 2"
            )


def wrap_orientation(theta: ArrayLike) -> NDArray[np.float64]:
    """Map axial orientations to ``[-pi/2, pi/2)``."""
    values = np.asarray(theta, dtype=float)
    return (values + np.pi / 2.0) % np.pi - np.pi / 2.0


def angular_difference(target: ArrayLike, current: ArrayLike) -> NDArray[np.float64]:
    """Return the shortest signed axial angle from current to target.

    At an exactly 90-degree mismatch the sign is mathematically non-unique;
    floating-point roundoff may select either branch.
    """
    target_array = np.asarray(target, dtype=float)
    current_array = np.asarray(current, dtype=float)
    return 0.5 * np.arctan2(
        np.sin(2.0 * (target_array - current_array)),
        np.cos(2.0 * (target_array - current_array)),
    )


def is_orthogonal(
    target: ArrayLike, current: ArrayLike, *, atol: float = 1e-10
) -> NDArray[np.bool_]:
    """Identify the axial 90-degree case where rotation direction is non-unique."""
    mismatch = np.abs(angular_difference(target, current))
    return np.isclose(mismatch, np.pi / 2.0, atol=atol, rtol=0.0)


def reorientation_rate(
    theta: ArrayLike, target: ArrayLike, rate_constant: float
) -> NDArray[np.float64]:
    """Evaluate dtheta/dt = k * Delta(theta_target, theta)."""
    if rate_constant < 0:
        raise ValueError("rate_constant must be non-negative")
    return rate_constant * angular_difference(target, theta)


def simulate_reorientation(
    initial_orientation: float,
    target_orientation: float | TargetFunction,
    parameters: ReorientationParameters | None = None,
) -> tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]]:
    """Integrate the reorientation model with explicit Euler stepping."""
    params = parameters or ReorientationParameters()
    params.validate()
    steps = int(np.ceil(params.duration / params.time_step))
    time = np.linspace(0.0, params.duration, steps + 1)
    orientation = np.empty_like(time)
    target_history = np.empty_like(time)
    orientation[0] = float(wrap_orientation(initial_orientation))
    if callable(target_orientation):
        target_function = target_orientation
    else:
        constant_target = float(target_orientation)

        def target_function(_t: float) -> float:
            return constant_target

    target_history[0] = float(wrap_orientation(target_function(time[0])))
    for index in range(steps):
        target_now = float(wrap_orientation(target_function(time[index])))
        target_history[index] = target_now
        derivative = float(reorientation_rate(orientation[index], target_now, params.rate))
        dt = time[index + 1] - time[index]
        orientation[index + 1] = float(wrap_orientation(orientation[index] + dt * derivative))
    target_history[-1] = float(wrap_orientation(target_function(time[-1])))
    return time, orientation, target_history


def analytical_constant_target(
    time: ArrayLike,
    initial_orientation: float,
    target_orientation: float,
    rate_constant: float,
) -> NDArray[np.float64]:
    """Analytical solution for a fixed target on a unique angular branch."""
    if rate_constant < 0:
        raise ValueError("rate_constant must be non-negative")
    if bool(is_orthogonal(target_orientation, initial_orientation)):
        raise ValueError("the exactly orthogonal case has no unique analytical branch")
    time_array = np.asarray(time, dtype=float)
    if np.any(time_array < 0):
        raise ValueError("time values must be non-negative")
    initial_error = float(angular_difference(target_orientation, initial_orientation))
    error = initial_error * np.exp(-rate_constant * time_array)
    return wrap_orientation(target_orientation - error)


def adaptation_time(
    initial_orientation: float,
    target_orientation: float,
    rate_constant: float,
    tolerance: float,
) -> float:
    """Return analytical time needed to reach an angular tolerance."""
    if rate_constant <= 0:
        raise ValueError("rate_constant must be positive")
    if tolerance <= 0 or tolerance >= np.pi / 2.0:
        raise ValueError("tolerance must lie between 0 and pi/2 radians")
    if bool(is_orthogonal(target_orientation, initial_orientation)):
        raise ValueError("the exactly orthogonal case has no unique rotation branch")
    initial_error = abs(float(angular_difference(target_orientation, initial_orientation)))
    if initial_error <= tolerance:
        return 0.0
    return float(np.log(initial_error / tolerance) / rate_constant)


def alignment_index(theta: ArrayLike, target: ArrayLike) -> NDArray[np.float64]:
    """Return an axial alignment index from zero to one."""
    difference = angular_difference(target, theta)
    return np.cos(difference) ** 2
