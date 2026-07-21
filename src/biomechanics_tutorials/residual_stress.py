"""Residual stress, opening-angle, and cut-release teaching models.

The module contains synthetic verification-oriented implementations for
thick-walled sectors, multilayer tubes, strip curling, and inverse sensitivity.
It is intentionally explicit about reference configurations and sign
conventions. It is not a patient-specific or tissue-calibrated solver.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
from numpy.typing import ArrayLike
from scipy.integrate import cumulative_trapezoid, trapezoid
from scipy.optimize import brentq


@dataclass(frozen=True)
class SectorLayer:
    """One layer of a stress-free open sector.

    Parameters
    ----------
    inner_radius, outer_radius:
        Radii in the opened stress-free sector.
    opening_angle_degrees:
        Missing angular wedge. The material sector angle is ``2π - alpha``.
    shear_modulus:
        Neo-Hookean shear modulus in synthetic units.
    fiber_modulus:
        Optional circumferential tension-only reinforcement.
    fiber_slack_stretch:
        Stretch at which the circumferential reinforcement is recruited.
    """

    inner_radius: float
    outer_radius: float
    opening_angle_degrees: float
    shear_modulus: float = 1.0
    fiber_modulus: float = 0.0
    fiber_slack_stretch: float = 1.0

    def __post_init__(self) -> None:
        if not (0.0 < self.inner_radius < self.outer_radius):
            raise ValueError("Require 0 < inner_radius < outer_radius.")
        if not (0.0 <= self.opening_angle_degrees < 350.0):
            raise ValueError("opening_angle_degrees must be in [0, 350).")
        if self.shear_modulus <= 0.0 or self.fiber_modulus < 0.0:
            raise ValueError("Material moduli must be non-negative and mu positive.")
        if self.fiber_slack_stretch <= 0.0:
            raise ValueError("fiber_slack_stretch must be positive.")

    @property
    def sector_angle(self) -> float:
        return 2.0 * np.pi - np.deg2rad(self.opening_angle_degrees)

    @property
    def closure_factor(self) -> float:
        return 2.0 * np.pi / self.sector_angle


@dataclass(frozen=True)
class TubeSolution:
    radius: np.ndarray
    reference_radius: np.ndarray
    radial_stretch: np.ndarray
    circumferential_stretch: np.ndarray
    radial_stress: np.ndarray
    circumferential_stress: np.ndarray
    layer_index: np.ndarray
    current_boundaries: np.ndarray
    pressure: float
    axial_stretch: float

    @property
    def von_mises_plane(self) -> np.ndarray:
        return np.abs(self.circumferential_stress - self.radial_stress)


def closure_factor(opening_angle_degrees: float) -> float:
    """Return the sector-to-ring angular closure factor."""
    alpha = np.deg2rad(float(opening_angle_degrees))
    if not 0.0 <= alpha < 2.0 * np.pi:
        raise ValueError("Opening angle must lie in [0, 360) degrees.")
    return 2.0 * np.pi / (2.0 * np.pi - alpha)


def _current_boundaries(
    layers: Sequence[SectorLayer], inner_radius: float, axial_stretch: float
) -> np.ndarray:
    boundaries = [float(inner_radius)]
    current = float(inner_radius)
    for layer in layers:
        increment = (
            layer.outer_radius**2 - layer.inner_radius**2
        ) / (layer.closure_factor * axial_stretch)
        current = float(np.sqrt(current**2 + increment))
        boundaries.append(current)
    return np.asarray(boundaries)


def _layer_kinematics(
    layer: SectorLayer,
    current_inner: float,
    current_outer: float,
    axial_stretch: float,
    points: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    radius = np.linspace(current_inner, current_outer, points)
    kappa = layer.closure_factor
    reference_radius = np.sqrt(
        layer.inner_radius**2
        + kappa * axial_stretch * (radius**2 - current_inner**2)
    )
    circumferential = kappa * radius / reference_radius
    radial = 1.0 / (circumferential * axial_stretch)
    isotropic_difference = layer.shear_modulus * (
        circumferential**2 - radial**2
    )
    recruitment = np.maximum(
        circumferential / layer.fiber_slack_stretch - 1.0, 0.0
    )
    fiber_difference = layer.fiber_modulus * recruitment**2
    difference = isotropic_difference + fiber_difference
    return radius, reference_radius, radial, circumferential, difference


def pressure_for_inner_radius(
    layers: Sequence[SectorLayer],
    inner_radius: float,
    *,
    axial_stretch: float = 1.0,
    points_per_layer: int = 240,
) -> float:
    """Return internal pressure associated with closing/loading the sectors."""
    if inner_radius <= 0.0 or axial_stretch <= 0.0:
        raise ValueError("inner_radius and axial_stretch must be positive.")
    boundaries = _current_boundaries(layers, inner_radius, axial_stretch)
    pressure = 0.0
    for index, layer in enumerate(layers):
        radius, _, _, _, difference = _layer_kinematics(
            layer,
            boundaries[index],
            boundaries[index + 1],
            axial_stretch,
            points_per_layer,
        )
        pressure += float(trapezoid(difference / radius, radius))
    return pressure


def solve_inner_radius(
    layers: Sequence[SectorLayer],
    pressure: float,
    *,
    axial_stretch: float = 1.0,
    bracket: tuple[float, float] | None = None,
) -> float:
    """Solve the inverse closure problem for the current inner radius."""
    if not layers:
        raise ValueError("At least one layer is required.")
    if axial_stretch <= 0.0:
        raise ValueError("axial_stretch must be positive.")
    scale = min(layer.inner_radius for layer in layers)
    if bracket is None:
        lower = max(1.0e-4, 0.05 * scale)
        upper = 5.0 * max(layer.outer_radius for layer in layers)
    else:
        lower, upper = bracket

    def residual(value: float) -> float:
        return pressure_for_inner_radius(
            layers, value, axial_stretch=axial_stretch
        ) - pressure

    f_lower = residual(lower)
    f_upper = residual(upper)
    attempts = 0
    while f_lower * f_upper > 0.0 and attempts < 12:
        lower *= 0.55
        upper *= 1.6
        f_lower = residual(lower)
        f_upper = residual(upper)
        attempts += 1
    if f_lower * f_upper > 0.0:
        raise RuntimeError("Could not bracket the tube-equilibrium solution.")
    return float(brentq(residual, lower, upper, xtol=1.0e-12, rtol=1.0e-11))


def solve_sector_tube(
    layers: Sequence[SectorLayer],
    *,
    pressure: float = 0.0,
    axial_stretch: float = 1.0,
    points_per_layer: int = 240,
) -> TubeSolution:
    """Close an open sector (or multiple sectors) into a loaded tube."""
    if pressure < 0.0:
        raise ValueError("The pressure convention requires pressure >= 0.")
    inner_radius = solve_inner_radius(
        layers, pressure, axial_stretch=axial_stretch
    )
    boundaries = _current_boundaries(layers, inner_radius, axial_stretch)

    radius_parts: list[np.ndarray] = []
    reference_parts: list[np.ndarray] = []
    radial_stretch_parts: list[np.ndarray] = []
    circumferential_parts: list[np.ndarray] = []
    difference_parts: list[np.ndarray] = []
    layer_indices: list[np.ndarray] = []

    for index, layer in enumerate(layers):
        result = _layer_kinematics(
            layer,
            boundaries[index],
            boundaries[index + 1],
            axial_stretch,
            points_per_layer,
        )
        radius, reference, radial, circumferential, difference = result
        if index > 0:
            radius = radius[1:]
            reference = reference[1:]
            radial = radial[1:]
            circumferential = circumferential[1:]
            difference = difference[1:]
        radius_parts.append(radius)
        reference_parts.append(reference)
        radial_stretch_parts.append(radial)
        circumferential_parts.append(circumferential)
        difference_parts.append(difference)
        layer_indices.append(np.full(radius.size, index, dtype=int))

    radius = np.concatenate(radius_parts)
    reference = np.concatenate(reference_parts)
    radial_stretch = np.concatenate(radial_stretch_parts)
    circumferential_stretch = np.concatenate(circumferential_parts)
    difference = np.concatenate(difference_parts)
    layer_index = np.concatenate(layer_indices)

    # sigma_r(b)=0 and equilibrium d sigma_r / dr = (sigma_theta-sigma_r)/r.
    integrand = difference / radius
    reverse_integral = cumulative_trapezoid(
        integrand[::-1], radius[::-1], initial=0.0
    )[::-1]
    radial_stress = reverse_integral
    circumferential_stress = radial_stress + difference

    return TubeSolution(
        radius=radius,
        reference_radius=reference,
        radial_stretch=radial_stretch,
        circumferential_stretch=circumferential_stretch,
        radial_stress=radial_stress,
        circumferential_stress=circumferential_stress,
        layer_index=layer_index,
        current_boundaries=boundaries,
        pressure=float(pressure),
        axial_stretch=float(axial_stretch),
    )


def radial_boundary_residual(solution: TubeSolution) -> tuple[float, float]:
    """Return inner and outer radial-traction residuals."""
    return (
        float(solution.radial_stress[0] + solution.pressure),
        float(solution.radial_stress[-1]),
    )


def stress_uniformity(values: ArrayLike) -> float:
    """Coefficient of variation based on absolute mean stress."""
    array = np.asarray(values, dtype=float)
    return float(np.std(array) / max(abs(np.mean(array)), 1.0e-12))


def stress_gradient(values: ArrayLike, coordinate: ArrayLike) -> float:
    """Normalized inner-to-outer stress contrast."""
    values_array = np.asarray(values, dtype=float)
    coordinate_array = np.asarray(coordinate, dtype=float)
    slope = np.polyfit(coordinate_array, values_array, 1)[0]
    return float(slope * (coordinate_array[-1] - coordinate_array[0]) / max(np.ptp(values_array), 1.0e-12))


def opening_sector_coordinates(
    inner_radius: float,
    outer_radius: float,
    opening_angle_degrees: float,
    *,
    points: int = 220,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Coordinates of inner and outer arcs of an opened sector."""
    angle = 2.0 * np.pi - np.deg2rad(opening_angle_degrees)
    theta = np.linspace(-angle / 2.0, angle / 2.0, points)
    return (
        inner_radius * np.cos(theta),
        inner_radius * np.sin(theta),
        outer_radius * np.cos(theta),
        outer_radius * np.sin(theta),
    )


def ring_coordinates(
    inner_radius: float, outer_radius: float, *, points: int = 300
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    theta = np.linspace(0.0, 2.0 * np.pi, points)
    return (
        inner_radius * np.cos(theta),
        inner_radius * np.sin(theta),
        outer_radius * np.cos(theta),
        outer_radius * np.sin(theta),
    )


def equilibrated_strip(
    coordinate: ArrayLike,
    eigenstrain: ArrayLike,
    modulus: ArrayLike | float = 1.0,
) -> dict[str, np.ndarray | float]:
    """Find force- and moment-free extension and curvature of a cut strip."""
    z = np.asarray(coordinate, dtype=float)
    target = np.asarray(eigenstrain, dtype=float)
    elastic_modulus = np.broadcast_to(np.asarray(modulus, dtype=float), z.shape)
    if z.ndim != 1 or target.shape != z.shape:
        raise ValueError("coordinate and eigenstrain must be one-dimensional and aligned.")
    if np.any(elastic_modulus <= 0.0):
        raise ValueError("modulus must be positive.")

    matrix = np.array(
        [
            [trapezoid(elastic_modulus, z), trapezoid(elastic_modulus * z, z)],
            [trapezoid(elastic_modulus * z, z), trapezoid(elastic_modulus * z**2, z)],
        ]
    )
    right = np.array(
        [
            trapezoid(elastic_modulus * target, z),
            trapezoid(elastic_modulus * target * z, z),
        ]
    )
    extension, curvature = np.linalg.solve(matrix, right)
    strain = extension + curvature * z
    stress = elastic_modulus * (strain - target)
    return {
        "extension": float(extension),
        "curvature": float(curvature),
        "strain": strain,
        "stress": stress,
        "force_residual": float(trapezoid(stress, z)),
        "moment_residual": float(trapezoid(stress * z, z)),
    }


def curvature_to_opening_angle(curvature: float, arc_length: float) -> float:
    """Small-strip geometric conversion used for teaching comparisons."""
    return float(np.rad2deg(curvature * arc_length))


def monte_carlo_opening_angle(
    mean_angle: float,
    standard_deviation: float,
    samples: int,
    *,
    seed: int = 0,
) -> np.ndarray:
    rng = np.random.default_rng(seed)
    angles = rng.normal(mean_angle, standard_deviation, samples)
    return np.clip(angles, 0.0, 340.0)


def multi_sector_angles(
    base_angle: float,
    harmonic_amplitude: float,
    sectors: int = 24,
    *,
    harmonic: int = 2,
) -> tuple[np.ndarray, np.ndarray]:
    """Synthetic circumferentially heterogeneous opening-angle field."""
    locations = np.linspace(0.0, 2.0 * np.pi, sectors, endpoint=False)
    angles = base_angle + harmonic_amplitude * np.cos(harmonic * locations)
    return locations, np.clip(angles, 0.0, 340.0)


def inverse_loss_surface(
    measured_inner_radius: float,
    measured_outer_radius: float,
    measured_pressure: float,
    angles: ArrayLike,
    moduli: ArrayLike,
    *,
    reference_inner: float = 1.0,
    reference_outer: float = 1.4,
    axial_stretch: float = 1.0,
) -> np.ndarray:
    """Synthetic inverse loss over opening angle and stiffness."""
    angle_values = np.asarray(angles, dtype=float)
    modulus_values = np.asarray(moduli, dtype=float)
    loss = np.empty((angle_values.size, modulus_values.size))
    scale_r = max(measured_outer_radius - measured_inner_radius, 1.0e-6)
    for i, angle in enumerate(angle_values):
        for j, modulus in enumerate(modulus_values):
            layer = SectorLayer(
                reference_inner,
                reference_outer,
                angle,
                shear_modulus=float(modulus),
            )
            try:
                solution = solve_sector_tube(
                    [layer], pressure=measured_pressure, axial_stretch=axial_stretch
                )
                radius_error = (
                    (solution.current_boundaries[0] - measured_inner_radius) / scale_r
                ) ** 2 + (
                    (solution.current_boundaries[-1] - measured_outer_radius) / scale_r
                ) ** 2
                loss[i, j] = radius_error
            except RuntimeError:
                loss[i, j] = np.nan
    return loss


def homeostatic_growth_angles(
    initial_angle: float,
    target_uniformity: float,
    gain: float,
    steps: int,
    evaluator,
    *,
    lower: float = 0.0,
    upper: float = 300.0,
) -> np.ndarray:
    """Simple stress-uniformity feedback for a synthetic opening angle."""
    angles = np.empty(steps + 1)
    angles[0] = initial_angle
    for index in range(steps):
        uniformity = float(evaluator(angles[index]))
        error = uniformity - target_uniformity
        angles[index + 1] = np.clip(angles[index] - gain * error, lower, upper)
    return angles
