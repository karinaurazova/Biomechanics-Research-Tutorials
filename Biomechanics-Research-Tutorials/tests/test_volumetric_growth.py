"""Tests for Tutorial 08 stress-driven volumetric growth."""

import numpy as np
import pytest

from biomechanics_tutorials.growth_kinematics import GrowthMaterialParameters
from biomechanics_tutorials.volumetric_growth import (
    VolumetricGrowthLawParameters,
    density_ratio_from_mass,
    evaluate_growth_stimulus,
    growth_response,
    homeostatic_band_value,
    isotropic_elastic_stretch_for_mean_cauchy,
    isotropic_growth_tensor,
    laplacian_neumann_1d,
    linearized_log_growth_eigenvalue,
    mass_ratio_from_growth,
    simulate_prescribed_deformation,
    simulate_prescribed_mean_stress,
    simulate_spatial_growth_field,
    stress_invariants,
    update_volume_ratio_explicit_euler,
    update_volume_ratio_exponential,
    volumetric_growth_velocity_gradient,
)


def test_isotropic_growth_tensor_has_prescribed_determinant():
    for jg in (0.7, 1.0, 1.8):
        assert np.linalg.det(isotropic_growth_tensor(jg)) == pytest.approx(jg)


def test_stress_sign_convention_and_von_mises():
    hydrostatic_tension = 3.0 * np.eye(3)
    result = stress_invariants(hydrostatic_tension)
    assert result["mean_stress"] == pytest.approx(3.0)
    assert result["pressure"] == pytest.approx(-3.0)
    assert result["von_mises"] == pytest.approx(0.0)


def test_growth_velocity_gradient_recovers_log_jg_rate():
    rate = 0.27
    lg = volumetric_growth_velocity_gradient(rate)
    assert np.trace(lg) == pytest.approx(rate)


def test_exponential_update_preserves_positivity_when_euler_fails():
    jg = 1.0
    rate = -4.0
    dt = 0.5
    assert update_volume_ratio_explicit_euler(jg, rate, dt) < 0.0
    assert update_volume_ratio_exponential(jg, rate, dt) > 0.0


def test_dead_zone_and_no_resorption_behave_as_stated():
    law = VolumetricGrowthLawParameters(dead_zone=0.1, response_limit=None)
    assert growth_response(0.05, law) == pytest.approx(0.0)
    assert growth_response(0.3, law) == pytest.approx(0.2)
    no_resorption = VolumetricGrowthLawParameters(
        dead_zone=0.0, response_limit=None, allow_resorption=False
    )
    assert growth_response(-0.5, no_resorption) == pytest.approx(0.0)


def test_free_growth_state_is_stress_free():
    jg = 1.6
    F = isotropic_growth_tensor(jg)
    state = evaluate_growth_stimulus(F, jg, "mean_mandel")
    assert np.linalg.norm(state["cauchy"]) < 1.0e-12
    assert state["energy"] == pytest.approx(0.0, abs=1.0e-12)


def test_prescribed_deformation_relaxes_mean_mandel_stimulus():
    time = np.linspace(0.0, 20.0, 401)
    F = 1.12 * np.eye(3)
    initial = evaluate_growth_stimulus(F, 1.0, "mean_mandel")["stimulus"]
    law = VolumetricGrowthLawParameters(
        rate=0.25,
        target=0.0,
        scale=max(abs(float(initial)), 1.0),
        measure="mean_mandel",
        response_limit=2.0,
    )
    result = simulate_prescribed_deformation(time, F, law=law)
    assert abs(result["mean_mandel"][-1]) < abs(result["mean_mandel"][0])
    assert result["Jg"][-1] > 1.0


def test_isotropic_growth_cannot_remove_deviatoric_stress_under_uniaxial_constraint():
    time = np.linspace(0.0, 30.0, 601)
    F = np.diag([1.25, 1.0, 1.0])
    initial = evaluate_growth_stimulus(F, 1.0, "mean_mandel")["stimulus"]
    law = VolumetricGrowthLawParameters(
        rate=0.25,
        target=0.0,
        scale=max(abs(float(initial)), 1.0),
        measure="mean_mandel",
        response_limit=2.0,
    )
    result = simulate_prescribed_deformation(time, F, law=law)
    assert abs(result["mean_mandel"][-1]) < 0.05 * abs(result["mean_mandel"][0])
    assert result["von_mises"][-1] > 0.1


def test_stress_control_keeps_stress_while_size_changes():
    time = np.linspace(0.0, 5.0, 101)
    law = VolumetricGrowthLawParameters(
        rate=0.2,
        target=0.0,
        scale=1.0,
        measure="mean_cauchy",
        response_limit=None,
    )
    result = simulate_prescribed_mean_stress(time, mean_stress=0.5, law=law)
    assert np.allclose(result["stimulus"], 0.5)
    assert result["total_stretch"][-1] > result["total_stretch"][0]


def test_isotropic_stress_inverse_solver_matches_forward_stress():
    material = GrowthMaterialParameters(shear_modulus=1.2, bulk_modulus=15.0)
    target = 0.8
    alpha = isotropic_elastic_stretch_for_mean_cauchy(target, material)
    state = evaluate_growth_stimulus(alpha * np.eye(3), 1.0, "mean_cauchy", material)
    assert state["stimulus"] == pytest.approx(target, rel=1.0e-9)


def test_mass_density_volume_bookkeeping_is_invertible():
    jg = np.array([0.8, 1.0, 1.5])
    density = np.array([1.1, 1.0, 0.9])
    mass = mass_ratio_from_growth(jg, density)
    assert np.allclose(density_ratio_from_mass(jg, mass), density)


def test_homeostatic_band_is_zero_inside_band():
    values = homeostatic_band_value(np.array([0.9, 1.0, 1.1, 1.3]), 1.0, 0.1)
    assert np.allclose(values[:3], 0.0)
    assert values[-1] == pytest.approx(0.2)


def test_linearized_equilibrium_is_stable_under_fixed_hydrostatic_deformation():
    F = 1.1 * np.eye(3)
    equilibrium = np.linalg.det(F)
    law = VolumetricGrowthLawParameters(
        rate=0.1,
        target=0.0,
        scale=1.0,
        measure="mean_mandel",
        response_limit=None,
    )
    eigenvalue = linearized_log_growth_eigenvalue(F, equilibrium, law)
    assert eigenvalue < 0.0


def test_neumann_laplacian_annihilates_constant_field():
    assert np.allclose(laplacian_neumann_1d(np.ones(20), 0.1), 0.0)


def test_spatial_regularisation_reduces_growth_field_roughness():
    x = np.linspace(0.0, 1.0, 61)
    time = np.linspace(0.0, 3.0, 301)
    target = 0.15 * np.sin(8.0 * np.pi * x)
    initial = np.ones_like(x)
    law = VolumetricGrowthLawParameters(
        rate=0.25,
        target=0.0,
        scale=1.0,
        measure="mean_mandel",
        response_limit=2.0,
    )
    local = simulate_spatial_growth_field(
        time, x, 1.08 * np.eye(3), initial, target, law, diffusivity=0.0
    )
    smooth = simulate_spatial_growth_field(
        time, x, 1.08 * np.eye(3), initial, target, law, diffusivity=2.0e-4
    )
    rough_local = np.sum(np.diff(np.log(local["Jg"][-1])) ** 2)
    rough_smooth = np.sum(np.diff(np.log(smooth["Jg"][-1])) ** 2)
    assert rough_smooth < rough_local


def test_invalid_parameters_are_rejected():
    with pytest.raises(ValueError):
        VolumetricGrowthLawParameters(scale=0.0).validate()
    with pytest.raises(ValueError):
        isotropic_growth_tensor(-1.0)
    with pytest.raises(ValueError):
        update_volume_ratio_exponential(1.0, 0.1, -0.1)
