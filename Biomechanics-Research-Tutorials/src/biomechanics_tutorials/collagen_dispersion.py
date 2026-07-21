"""Planar collagen-fiber dispersion and a minimal angular-integration model.

Fiber orientations are axial: ``theta`` and ``theta + pi`` denote the same
physical line.  The module uses a pi-periodic von Mises distribution and a
simple tension-only exponential fiber energy.  It is intended for teaching and
verification, not as a validated tissue-specific constitutive law.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy.special import i0, i1

from .fiber_reorientation import wrap_orientation


@dataclass(frozen=True)
class DispersionParameters:
    """Parameters of the axial orientation distribution."""

    mean_angle: float = 0.0
    concentration: float = 4.0
    quadrature_points: int = 721

    def validate(self) -> None:
        if self.concentration < 0:
            raise ValueError("concentration must be non-negative")
        if self.quadrature_points < 33:
            raise ValueError("quadrature_points must be at least 33")
        if self.quadrature_points % 2 == 0:
            raise ValueError("quadrature_points must be odd")


@dataclass(frozen=True)
class FiberMaterialParameters:
    """Dimensionless material parameters for the educational energy model."""

    matrix_shear: float = 0.2
    fiber_stiffness: float = 2.0
    fiber_nonlinearity: float = 6.0

    def validate(self) -> None:
        if self.matrix_shear < 0:
            raise ValueError("matrix_shear must be non-negative")
        if self.fiber_stiffness < 0:
            raise ValueError("fiber_stiffness must be non-negative")
        if self.fiber_nonlinearity <= 0:
            raise ValueError("fiber_nonlinearity must be positive")


def axial_von_mises_density(
    theta: ArrayLike,
    mean_angle: float,
    concentration: float,
) -> NDArray[np.float64]:
    """Evaluate a normalized pi-periodic von Mises density.

    The density is

    ``rho(theta) = exp(beta*cos(2*(theta-mu))) / (pi*I0(beta))``.
    """
    if concentration < 0:
        raise ValueError("concentration must be non-negative")
    theta_array = np.asarray(theta, dtype=float)
    mean = float(wrap_orientation(mean_angle))
    return np.exp(concentration * np.cos(2.0 * (theta_array - mean))) / (
        np.pi * i0(concentration)
    )


def orientation_grid(points: int = 721) -> NDArray[np.float64]:
    """Return an integration grid on one axial period ``[-pi/2, pi/2]``."""
    if points < 33:
        raise ValueError("points must be at least 33")
    if points % 2 == 0:
        raise ValueError("points must be odd")
    return np.linspace(-np.pi / 2.0, np.pi / 2.0, points)


def order_parameter(concentration: ArrayLike) -> NDArray[np.float64]:
    """Return the axial second-order parameter ``S = I1(beta)/I0(beta)``."""
    beta = np.asarray(concentration, dtype=float)
    if np.any(beta < 0):
        raise ValueError("concentration must be non-negative")
    return i1(beta) / i0(beta)


def dispersion_index(concentration: ArrayLike) -> NDArray[np.float64]:
    """Return ``D = 1 - S``: zero for perfect alignment, one for uniformity."""
    return 1.0 - order_parameter(concentration)


def orientation_tensor(mean_angle: float, concentration: float) -> NDArray[np.float64]:
    """Return the analytical planar second-order orientation tensor."""
    if concentration < 0:
        raise ValueError("concentration must be non-negative")
    mean = float(wrap_orientation(mean_angle))
    s = float(order_parameter(concentration))
    c2 = np.cos(2.0 * mean)
    s2 = np.sin(2.0 * mean)
    return 0.5 * np.array(
        [
            [1.0 + s * c2, s * s2],
            [s * s2, 1.0 - s * c2],
        ],
        dtype=float,
    )


def numerical_orientation_tensor(
    mean_angle: float,
    concentration: float,
    points: int = 721,
) -> NDArray[np.float64]:
    """Compute the orientation tensor by numerical angular integration."""
    theta = orientation_grid(points)
    rho = axial_von_mises_density(theta, mean_angle, concentration)
    directions = np.stack((np.cos(theta), np.sin(theta)), axis=-1)
    dyads = directions[:, :, None] * directions[:, None, :]
    return np.trapezoid(rho[:, None, None] * dyads, theta, axis=0)


def fiber_stretch_squared(theta: ArrayLike, stretch: float) -> NDArray[np.float64]:
    """Return ``I4`` for in-plane fibers under incompressible uniaxial stretch.

    The deformation is ``F = diag(lambda, lambda**(-1/2), lambda**(-1/2))``.
    """
    if stretch <= 0:
        raise ValueError("stretch must be positive")
    theta_array = np.asarray(theta, dtype=float)
    return stretch**2 * np.cos(theta_array) ** 2 + stretch ** (-1.0) * np.sin(theta_array) ** 2


def fiber_energy_density(
    stretch_squared: ArrayLike,
    fiber_stiffness: float,
    fiber_nonlinearity: float,
) -> NDArray[np.float64]:
    """Evaluate a tension-only exponential fiber energy density."""
    if fiber_stiffness < 0:
        raise ValueError("fiber_stiffness must be non-negative")
    if fiber_nonlinearity <= 0:
        raise ValueError("fiber_nonlinearity must be positive")
    i4 = np.asarray(stretch_squared, dtype=float)
    strain = np.maximum(i4 - 1.0, 0.0)
    return fiber_stiffness / (2.0 * fiber_nonlinearity) * (
        np.exp(fiber_nonlinearity * strain**2) - 1.0
    )


def total_strain_energy(
    stretch: ArrayLike,
    distribution: DispersionParameters | None = None,
    material: FiberMaterialParameters | None = None,
) -> NDArray[np.float64]:
    """Return matrix-plus-fiber strain energy for one or more stretches."""
    dist = distribution or DispersionParameters()
    mat = material or FiberMaterialParameters()
    dist.validate()
    mat.validate()
    stretches = np.asarray(stretch, dtype=float)
    if np.any(stretches <= 0):
        raise ValueError("all stretches must be positive")

    theta = orientation_grid(dist.quadrature_points)
    rho = axial_von_mises_density(theta, dist.mean_angle, dist.concentration)
    flat = stretches.reshape(-1)
    energies = np.empty_like(flat)
    for index, lam in enumerate(flat):
        i4 = fiber_stretch_squared(theta, float(lam))
        fiber = np.trapezoid(
            rho * fiber_energy_density(i4, mat.fiber_stiffness, mat.fiber_nonlinearity),
            theta,
        )
        matrix = 0.5 * mat.matrix_shear * (lam**2 + 2.0 * lam ** (-1.0) - 3.0)
        energies[index] = matrix + fiber
    return energies.reshape(stretches.shape)


def nominal_stress(
    stretch: ArrayLike,
    distribution: DispersionParameters | None = None,
    material: FiberMaterialParameters | None = None,
) -> NDArray[np.float64]:
    """Return the analytical derivative of the educational strain energy."""
    dist = distribution or DispersionParameters()
    mat = material or FiberMaterialParameters()
    dist.validate()
    mat.validate()
    stretches = np.asarray(stretch, dtype=float)
    if np.any(stretches <= 0):
        raise ValueError("all stretches must be positive")

    theta = orientation_grid(dist.quadrature_points)
    rho = axial_von_mises_density(theta, dist.mean_angle, dist.concentration)
    cos2 = np.cos(theta) ** 2
    sin2 = np.sin(theta) ** 2
    flat = stretches.reshape(-1)
    stresses = np.empty_like(flat)
    for index, lam in enumerate(flat):
        i4 = lam**2 * cos2 + lam ** (-1.0) * sin2
        strain = np.maximum(i4 - 1.0, 0.0)
        active = i4 > 1.0
        di4 = 2.0 * lam * cos2 - lam ** (-2.0) * sin2
        fiber_integrand = (
            mat.fiber_stiffness
            * np.exp(mat.fiber_nonlinearity * strain**2)
            * strain
            * di4
            * active
        )
        fiber_stress = np.trapezoid(rho * fiber_integrand, theta)
        matrix_stress = mat.matrix_shear * (lam - lam ** (-2.0))
        stresses[index] = matrix_stress + fiber_stress
    return stresses.reshape(stretches.shape)


def sample_axial_von_mises(
    count: int,
    mean_angle: float,
    concentration: float,
    *,
    seed: int | None = None,
) -> NDArray[np.float64]:
    """Sample axial orientations by halving a directional von Mises variable."""
    if count <= 0:
        raise ValueError("count must be positive")
    if concentration < 0:
        raise ValueError("concentration must be non-negative")
    rng = np.random.default_rng(seed)
    doubled = rng.vonmises(mu=0.0, kappa=concentration, size=count)
    return wrap_orientation(float(wrap_orientation(mean_angle)) + 0.5 * doubled)
