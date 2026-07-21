"""Tests for Tutorial 09 fiber-family remodeling."""

import numpy as np
import pytest

from biomechanics_tutorials.fiber_family_remodeling import (
    FiberFamily,
    FiberMaterialParameters,
    ODFRemodelingParameters,
    RecruitmentParameters,
    ReorientationParameters,
    TurnoverParameters,
    angular_integrated_energy,
    axial_angle_difference,
    axial_grid,
    axial_mean_angle,
    axial_order_parameter,
    axial_von_mises_density,
    compare_approach_state_count,
    discrete_family_energy,
    family_orientation_tensor,
    fiber_stretch,
    normalize_density,
    orientation_tensor_2d,
    planar_structure_tensor_energy,
    principal_direction_2d,
    recruited_fraction,
    recruitment_tension,
    simulate_cohort_turnover,
    simulate_discrete_reorientation,
    simulate_odf_remodeling,
    simulate_two_family_mass_remodeling,
    survival_fraction,
    wrap_axial,
)


def test_axial_wrapping_and_difference_respect_pi_periodicity():
    assert wrap_axial(np.deg2rad(170.0)) == pytest.approx(np.deg2rad(-10.0))
    difference = axial_angle_difference(np.deg2rad(85.0), np.deg2rad(-85.0))
    assert difference == pytest.approx(np.deg2rad(-10.0))


def test_axial_von_mises_density_is_normalized():
    theta = axial_grid(721)
    density = axial_von_mises_density(theta, 0.3, 4.0)
    assert np.sum(density) * np.pi / theta.size == pytest.approx(1.0, rel=2.0e-6)


def test_uniform_orientation_tensor_is_planar_isotropic():
    theta = axial_grid(720)
    density = np.ones_like(theta) / np.pi
    tensor = orientation_tensor_2d(theta, density)
    assert np.allclose(tensor, 0.5 * np.eye(2), atol=2.0e-6)
    assert np.trace(tensor) == pytest.approx(1.0)


def test_concentrated_distribution_recovers_mean_orientation():
    theta = axial_grid(721)
    mean = np.deg2rad(32.0)
    density = axial_von_mises_density(theta, mean, 18.0)
    recovered = axial_mean_angle(theta, density)
    assert abs(axial_angle_difference(mean, recovered)) < np.deg2rad(0.2)
    assert axial_order_parameter(theta, density) > 0.95


def test_discrete_orientation_tensor_matches_two_orthogonal_families():
    families = [
        FiberFamily(angle=0.0, mass_fraction=0.5),
        FiberFamily(angle=0.5 * np.pi, mass_fraction=0.5),
    ]
    tensor = family_orientation_tensor(families)
    assert np.allclose(tensor, 0.5 * np.eye(2), atol=1.0e-12)


def test_principal_direction_is_axial():
    tensor = np.diag([3.0, 1.0])
    angle, values = principal_direction_2d(tensor)
    assert angle == pytest.approx(0.0)
    assert values[-1] == pytest.approx(3.0)


def test_direct_reorientation_reduces_mismatch():
    time = np.linspace(0.0, 8.0, 401)
    result = simulate_discrete_reorientation(
        time,
        initial_angle=np.deg2rad(-55.0),
        target=np.deg2rad(25.0),
        parameters=ReorientationParameters(rate=1.0),
    )
    assert abs(result["error"][-1]) < abs(result["error"][0])
    assert abs(result["error"][-1]) < np.deg2rad(1.0)


def test_exactly_orthogonal_director_is_a_nonunique_stationary_case():
    time = np.linspace(0.0, 2.0, 21)
    result = simulate_discrete_reorientation(time, 0.0, 0.5 * np.pi)
    assert np.allclose(result["angle"], 0.0, atol=1.0e-12)


def test_odf_solver_conserves_probability_and_stays_nonnegative():
    theta = axial_grid(121)
    initial = axial_von_mises_density(theta, np.deg2rad(-35.0), 4.0)
    time = np.linspace(0.0, 2.0, 101)
    result = simulate_odf_remodeling(
        time,
        theta,
        initial,
        np.deg2rad(25.0),
        ODFRemodelingParameters(alignment_rate=0.8, rotational_diffusivity=0.02),
    )
    delta = np.pi / theta.size
    integrals = np.sum(result["density"], axis=1) * delta
    assert np.allclose(integrals, 1.0, atol=1.0e-8)
    assert np.min(result["density"]) >= 0.0


def test_odf_alignment_moves_mean_toward_target():
    theta = axial_grid(151)
    target = np.deg2rad(30.0)
    initial = axial_von_mises_density(theta, np.deg2rad(-40.0), 8.0)
    time = np.linspace(0.0, 5.0, 251)
    result = simulate_odf_remodeling(
        time,
        theta,
        initial,
        target,
        ODFRemodelingParameters(alignment_rate=1.0, rotational_diffusivity=0.005),
    )
    start_error = abs(axial_angle_difference(target, result["mean_angle"][0]))
    final_error = abs(axial_angle_difference(target, result["mean_angle"][-1]))
    assert final_error < 0.1 * start_error


def test_rotational_diffusion_reduces_order_parameter():
    theta = axial_grid(151)
    initial = axial_von_mises_density(theta, 0.0, 20.0)
    time = np.linspace(0.0, 3.0, 151)
    result = simulate_odf_remodeling(
        time,
        theta,
        initial,
        0.0,
        ODFRemodelingParameters(alignment_rate=0.0, rotational_diffusivity=0.05),
    )
    assert result["order_parameter"][-1] < result["order_parameter"][0]


def test_affine_fiber_stretch_is_correct_for_uniaxial_deformation():
    F = np.diag([1.2, 1.0 / np.sqrt(1.2)])
    assert fiber_stretch(F, 0.0) == pytest.approx(1.2)
    assert fiber_stretch(F, 0.5 * np.pi) == pytest.approx(1.0 / np.sqrt(1.2))


def test_discrete_and_angular_integration_agree_for_sharp_distribution():
    theta = axial_grid(1441)
    angle = np.deg2rad(20.0)
    density = axial_von_mises_density(theta, angle, 120.0)
    F = np.diag([1.15, 1.0 / np.sqrt(1.15)])
    material = FiberMaterialParameters(k1=2.0, k2=5.0)
    continuous = angular_integrated_energy(F, theta, density, material)
    discrete = discrete_family_energy(F, [FiberFamily(angle=angle)], material)
    assert continuous == pytest.approx(discrete, rel=0.04)


def test_planar_structure_tensor_matches_aligned_limit():
    F = np.diag([1.12, 1.0 / np.sqrt(1.12)])
    angle = np.deg2rad(10.0)
    material = FiberMaterialParameters(k1=2.0, k2=5.0)
    generalized = planar_structure_tensor_energy(F, angle, 0.0, material)
    discrete = discrete_family_energy(F, [FiberFamily(angle=angle)], material)
    assert generalized == pytest.approx(discrete, rel=1.0e-12)


def test_recruited_fraction_is_monotonic():
    stretch = np.linspace(0.95, 1.2, 100)
    fraction = recruited_fraction(stretch, RecruitmentParameters(mean=1.06, standard_deviation=0.02))
    assert np.all(np.diff(fraction) >= 0.0)
    assert fraction[0] < 0.01
    assert fraction[-1] > 0.99


def test_recruitment_tension_is_monotonic_and_zero_before_recruitment():
    stretch = np.linspace(0.9, 1.2, 101)
    tension = recruitment_tension(stretch)
    assert np.all(np.diff(tension) >= -1.0e-12)
    assert tension[0] == pytest.approx(0.0, abs=1.0e-8)


def test_survival_fraction_has_correct_half_life():
    assert survival_fraction(8.0, 8.0) == pytest.approx(0.5)
    assert survival_fraction(0.0, 8.0) == pytest.approx(1.0)


def test_cohort_turnover_reorients_by_replacement_not_direct_rotation():
    time = np.linspace(0.0, 20.0, 201)
    switch_time = 4.0
    result = simulate_cohort_turnover(
        time,
        stress_protocol=lambda _: 1.2,
        deposition_angle_protocol=lambda t: 0.0 if t < switch_time else np.deg2rad(60.0),
        parameters=TurnoverParameters(
            half_life=4.0,
            basal_production=0.3,
            stress_gain=0.0,
            target_stress=1.0,
        ),
        initial_angle=0.0,
    )
    assert abs(axial_angle_difference(np.deg2rad(60.0), result["mean_angle"][-1])) < np.deg2rad(8.0)
    assert result["mean_age"][-1] > 0.0


def test_two_family_mass_remodeling_favors_more_loaded_family():
    time = np.linspace(0.0, 8.0, 161)
    result = simulate_two_family_mass_remodeling(
        time,
        deformation_protocol=lambda _: np.diag([1.2, 1.0 / np.sqrt(1.2)]),
        family_angles=(0.0, 0.5 * np.pi),
        target_tension=0.2,
        adaptation_rate=0.5,
        removal_rate=0.2,
    )
    assert result["mass_fraction"][-1, 0] > result["mass_fraction"][0, 0]


def test_state_count_comparison_orders_model_complexity():
    counts = compare_approach_state_count(181, 100)
    assert counts["direct_family_rotation"] < counts["continuous_odf"]
    assert counts["continuous_odf"] < counts["cohort_turnover"]


def test_invalid_inputs_are_rejected():
    with pytest.raises(ValueError):
        normalize_density(np.arange(3.0), np.zeros(3))
    with pytest.raises(ValueError):
        planar_structure_tensor_energy(np.eye(2), 0.0, 0.6)
    with pytest.raises(ValueError):
        TurnoverParameters(half_life=0.0).validate()
