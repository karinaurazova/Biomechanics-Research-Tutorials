import numpy as np
import pytest

from biomechanics_tutorials.collagen_dispersion import (
    DispersionParameters,
    FiberMaterialParameters,
    axial_von_mises_density,
    dispersion_index,
    nominal_stress,
    numerical_orientation_tensor,
    order_parameter,
    orientation_grid,
    orientation_tensor,
    sample_axial_von_mises,
    total_strain_energy,
)


def test_density_integrates_to_one():
    theta = orientation_grid(4001)
    rho = axial_von_mises_density(theta, np.deg2rad(23), 5.0)
    assert np.isclose(np.trapezoid(rho, theta), 1.0, atol=1e-7)


def test_density_is_axially_periodic():
    theta = np.linspace(-1.2, 1.2, 40)
    first = axial_von_mises_density(theta, 0.3, 4.0)
    second = axial_von_mises_density(theta + np.pi, 0.3, 4.0)
    assert np.allclose(first, second)


def test_uniform_distribution_has_isotropic_tensor():
    assert np.allclose(orientation_tensor(0.7, 0.0), 0.5 * np.eye(2), atol=1e-12)


def test_orientation_tensor_matches_numerical_integration():
    analytical = orientation_tensor(np.deg2rad(31), 3.2)
    numerical = numerical_orientation_tensor(np.deg2rad(31), 3.2, points=4001)
    assert np.allclose(analytical, numerical, atol=2e-7)
    assert np.isclose(np.trace(numerical), 1.0, atol=2e-7)


def test_order_increases_and_dispersion_decreases():
    beta = np.array([0.0, 0.5, 2.0, 8.0])
    assert np.all(np.diff(order_parameter(beta)) > 0)
    assert np.all(np.diff(dispersion_index(beta)) < 0)


def test_energy_and_stress_vanish_in_reference_state():
    stretches = np.array([1.0])
    assert np.allclose(total_strain_energy(stretches), 0.0, atol=1e-12)
    assert np.allclose(nominal_stress(stretches), 0.0, atol=1e-12)


def test_aligned_concentrated_family_is_stiffer_in_fiber_direction():
    material = FiberMaterialParameters(matrix_shear=0.2, fiber_stiffness=2.0, fiber_nonlinearity=6.0)
    uniform = nominal_stress(
        1.18,
        DispersionParameters(mean_angle=0.0, concentration=0.0, quadrature_points=2001),
        material,
    )
    concentrated = nominal_stress(
        1.18,
        DispersionParameters(mean_angle=0.0, concentration=12.0, quadrature_points=2001),
        material,
    )
    assert float(concentrated) > float(uniform)


def test_mean_orientation_changes_response():
    material = FiberMaterialParameters()
    parallel = nominal_stress(
        1.2,
        DispersionParameters(mean_angle=0.0, concentration=10.0, quadrature_points=2001),
        material,
    )
    transverse = nominal_stress(
        1.2,
        DispersionParameters(mean_angle=np.pi / 2, concentration=10.0, quadrature_points=2001),
        material,
    )
    assert float(parallel) > float(transverse)


def test_sampling_is_reproducible_and_axial():
    a = sample_axial_von_mises(100, 0.2, 3.0, seed=42)
    b = sample_axial_von_mises(100, 0.2 + np.pi, 3.0, seed=42)
    assert np.allclose(a, b)
    assert np.all(a >= -np.pi / 2) and np.all(a < np.pi / 2)


def test_invalid_parameters_are_rejected():
    with pytest.raises(ValueError):
        DispersionParameters(concentration=-1).validate()
    with pytest.raises(ValueError):
        DispersionParameters(quadrature_points=100).validate()
    with pytest.raises(ValueError):
        FiberMaterialParameters(fiber_nonlinearity=0).validate()


def test_nominal_stress_matches_energy_derivative():
    distribution = DispersionParameters(
        mean_angle=np.deg2rad(24.0), concentration=5.0, quadrature_points=2001
    )
    material = FiberMaterialParameters()
    stretch = 1.12
    step = 1e-6
    finite_difference = (
        total_strain_energy(stretch + step, distribution, material)
        - total_strain_energy(stretch - step, distribution, material)
    ) / (2.0 * step)
    analytical = nominal_stress(stretch, distribution, material)
    assert np.isclose(analytical, finite_difference, rtol=2e-6, atol=2e-7)
