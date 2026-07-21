import numpy as np
import pytest

from biomechanics_tutorials.growth_kinematics import (
    GrowthLawParameters,
    GrowthMaterialParameters,
    commutator_norm,
    compose_growth_increments,
    elastic_cauchy_stress,
    elastic_energy_density,
    finite_difference_first_piola,
    growth_tensor_isotropic,
    growth_tensor_orthotropic,
    growth_tensor_transversely_isotropic,
    incompatibility_norm_2d,
    jacobian_bookkeeping,
    mandel_stress,
    material_basis,
    multiplicative_decomposition,
    reduced_strip_equilibrium,
    rotation_matrix,
    simulate_stress_driven_growth,
    total_first_piola,
    total_reference_energy,
    update_growth_tensor,
)


def test_identity_split_returns_identity_elastic_part():
    elastic, growth = multiplicative_decomposition(np.eye(3), np.eye(3))
    assert np.allclose(elastic, np.eye(3))
    assert np.allclose(growth, np.eye(3))


def test_jacobian_bookkeeping_is_multiplicative():
    total = np.diag([1.4, 0.9, 1.1])
    growth = np.diag([1.2, 1.05, 0.95])
    values = jacobian_bookkeeping(total, growth)
    assert values["J"] == pytest.approx(values["Je"] * values["Jg"])
    assert values["error"] == pytest.approx(0.0, abs=1.0e-12)


def test_isotropic_growth_volume_ratio_is_exact():
    growth = growth_tensor_isotropic(volume_ratio=1.728)
    assert np.linalg.det(growth) == pytest.approx(1.728)
    assert np.allclose(growth, 1.2 * np.eye(3))


def test_orthotropic_growth_preserves_principal_stretches_under_rotation():
    basis = material_basis([1.0, 1.0, 0.0], [0.0, 0.0, 1.0])
    growth = growth_tensor_orthotropic([1.3, 1.1, 0.9], basis)
    singular = np.sort(np.linalg.svd(growth, compute_uv=False))
    assert np.allclose(singular, np.sort([1.3, 1.1, 0.9]))


def test_free_growth_has_zero_elastic_energy_and_stress():
    growth = growth_tensor_transversely_isotropic(1.25, 1.08)
    elastic, _ = multiplicative_decomposition(growth, growth)
    assert elastic_energy_density(elastic) == pytest.approx(0.0, abs=1.0e-12)
    assert np.linalg.norm(elastic_cauchy_stress(elastic)) < 1.0e-10


def test_constrained_growth_generates_nonzero_stress():
    growth = growth_tensor_isotropic(linear_growth=1.15)
    elastic, _ = multiplicative_decomposition(np.eye(3), growth)
    assert elastic_energy_density(elastic) > 0.0
    assert np.linalg.norm(elastic_cauchy_stress(elastic)) > 0.0


def test_elastic_energy_is_frame_indifferent():
    deformation = np.diag([1.3, 0.95, 0.9])
    growth = np.diag([1.1, 1.0, 0.95])
    rotation = rotation_matrix([0.2, 0.8, 0.3], 0.7)
    original = total_reference_energy(deformation, growth)
    rotated = total_reference_energy(rotation @ deformation, growth)
    assert rotated == pytest.approx(original, rel=1.0e-12, abs=1.0e-12)


def test_analytical_total_piola_matches_finite_difference():
    deformation = np.array([[1.15, 0.12, 0.0], [0.02, 0.98, 0.05], [0.0, 0.0, 0.92]])
    growth = np.diag([1.08, 0.97, 1.02])
    parameters = GrowthMaterialParameters(1.4, 18.0)
    analytical = total_first_piola(deformation, growth, parameters)
    numerical = finite_difference_first_piola(deformation, growth, parameters)
    assert np.allclose(analytical, numerical, rtol=2.0e-5, atol=2.0e-6)


def test_zero_velocity_leaves_growth_unchanged():
    growth = np.diag([1.2, 0.9, 1.05])
    updated = update_growth_tensor(growth, np.zeros((3, 3)), 0.5)
    assert np.allclose(updated, growth)


def test_stress_driven_growth_relaxes_energy_at_fixed_stretch():
    time = np.linspace(0.0, 30.0, 1201)
    deformation = np.diag([1.35, 1.0 / np.sqrt(1.35), 1.0 / np.sqrt(1.35)])
    result = simulate_stress_driven_growth(
        time,
        deformation,
        law=GrowthLawParameters(rate=0.12, mode="diagonal", response_limit=0.15),
    )
    assert result["energy"][-1] < result["energy"][0]
    assert abs(result["mandel"][-1, 0, 0]) < abs(result["mandel"][0, 0, 0])
    assert np.all(np.linalg.det(result["Fg"]) > 0.0)


def test_mandel_stress_is_symmetric_for_isotropic_hyperelasticity():
    deformation = np.array([[1.1, 0.2, 0.0], [0.0, 0.95, 0.0], [0.0, 0.0, 1.0]])
    stress = mandel_stress(deformation)
    assert np.allclose(stress, stress.T, atol=1.0e-12)


def test_isotropic_growth_increments_commute():
    first = growth_tensor_isotropic(linear_growth=1.1)
    second = growth_tensor_isotropic(linear_growth=0.95)
    assert commutator_norm(first, second) == pytest.approx(0.0)
    assert np.allclose(
        compose_growth_increments([first, second]),
        compose_growth_increments([second, first]),
    )


def test_rotated_anisotropic_growth_increments_do_not_commute():
    first = growth_tensor_orthotropic([1.2, 0.95, 1.0])
    rotation = rotation_matrix([0.0, 0.0, 1.0], np.deg2rad(40.0))
    second = growth_tensor_orthotropic([1.15, 0.9, 1.0], rotation)
    assert commutator_norm(first, second) > 1.0e-3
    assert not np.allclose(
        compose_growth_increments([first, second]),
        compose_growth_increments([second, first]),
    )


def test_constant_growth_field_has_zero_row_wise_curl():
    field = np.zeros((21, 23, 2, 2))
    field[...] = np.diag([1.2, 0.9])
    assert np.max(incompatibility_norm_2d(field)) < 1.0e-12


def test_spatially_varying_isotropic_growth_is_detected_as_incompatible():
    y, x = np.mgrid[-1.0:1.0:31j, -1.0:1.0:33j]
    theta = 1.0 + 0.15 * x + 0.08 * y
    field = np.zeros(theta.shape + (2, 2))
    field[..., 0, 0] = theta
    field[..., 1, 1] = theta
    diagnostic = incompatibility_norm_2d(field, x[0, 1] - x[0, 0], y[1, 0] - y[0, 0])
    assert np.mean(diagnostic) > 0.05


def test_uniform_strip_growth_produces_no_curvature():
    z = np.linspace(-0.5, 0.5, 301)
    result = reduced_strip_equilibrium(z, np.full_like(z, 1.12))
    assert result["curvature"] == pytest.approx(0.0, abs=1.0e-10)
    assert result["lambda0"] == pytest.approx(1.12, rel=1.0e-10)


def test_growth_gradient_bends_reduced_strip_and_balances_resultants():
    z = np.linspace(-0.5, 0.5, 401)
    growth = 1.0 + 0.22 * z
    result = reduced_strip_equilibrium(z, growth)
    assert abs(result["curvature"]) > 0.1
    assert abs(result["force_residual"]) < 1.0e-6
    assert abs(result["moment_residual"]) < 1.0e-6


def test_same_total_deformation_can_hide_different_growth_states():
    total = np.diag([1.2, 0.95, 0.9])
    energy_a = total_reference_energy(total, np.eye(3))
    energy_b = total_reference_energy(total, np.diag([1.1, 1.0, 1.0]))
    assert energy_a != pytest.approx(energy_b)


def test_invalid_growth_parameters_are_rejected():
    with pytest.raises(ValueError):
        GrowthLawParameters(mode="unknown").validate()
    with pytest.raises(ValueError):
        growth_tensor_isotropic(linear_growth=-1.0)
    with pytest.raises(ValueError):
        multiplicative_decomposition(np.eye(3), np.diag([-1.0, 1.0, 1.0]))
