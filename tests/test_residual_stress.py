"""Verification tests for Tutorial 12 residual-stress models."""

from __future__ import annotations

import numpy as np

from biomechanics_tutorials.residual_stress import (
    SectorLayer,
    closure_factor,
    curvature_to_opening_angle,
    equilibrated_strip,
    inverse_loss_surface,
    monte_carlo_opening_angle,
    multi_sector_angles,
    opening_sector_coordinates,
    pressure_for_inner_radius,
    radial_boundary_residual,
    ring_coordinates,
    solve_sector_tube,
    stress_uniformity,
)


def test_closure_factor_zero_angle_is_one() -> None:
    assert closure_factor(0.0) == 1.0


def test_closure_factor_increases_with_opening_angle() -> None:
    assert closure_factor(120.0) > closure_factor(60.0) > 1.0


def test_unloaded_closed_sector_has_zero_boundary_tractions() -> None:
    solution = solve_sector_tube([SectorLayer(1.0, 1.4, 120.0)])
    inner, outer = radial_boundary_residual(solution)
    assert abs(inner) < 5.0e-7
    assert abs(outer) < 5.0e-10


def test_pressurized_sector_recovers_inner_and_outer_tractions() -> None:
    solution = solve_sector_tube(
        [SectorLayer(1.0, 1.4, 100.0)], pressure=0.20, axial_stretch=1.08
    )
    inner, outer = radial_boundary_residual(solution)
    assert abs(inner) < 5.0e-6
    assert abs(outer) < 5.0e-10


def test_pressure_function_matches_solution_pressure() -> None:
    layer = SectorLayer(1.0, 1.4, 90.0)
    solution = solve_sector_tube([layer], pressure=0.16)
    pressure = pressure_for_inner_radius([layer], solution.current_boundaries[0])
    assert np.isclose(pressure, 0.16, atol=1.0e-8)


def test_incompressibility_is_satisfied() -> None:
    solution = solve_sector_tube(
        [SectorLayer(1.0, 1.35, 110.0)], pressure=0.12, axial_stretch=1.15
    )
    product = (
        solution.radial_stretch
        * solution.circumferential_stretch
        * solution.axial_stretch
    )
    assert np.max(np.abs(product - 1.0)) < 1.0e-11


def test_opening_angle_changes_residual_stress() -> None:
    low = solve_sector_tube([SectorLayer(1.0, 1.4, 30.0)])
    high = solve_sector_tube([SectorLayer(1.0, 1.4, 150.0)])
    assert np.ptp(high.circumferential_stress) > np.ptp(low.circumferential_stress)


def test_residual_stress_can_reduce_loaded_stress_nonuniformity() -> None:
    no_residual = solve_sector_tube(
        [SectorLayer(1.0, 1.4, 0.0)], pressure=0.20
    )
    residual = solve_sector_tube(
        [SectorLayer(1.0, 1.4, 60.0)], pressure=0.20
    )
    assert stress_uniformity(residual.circumferential_stress) < stress_uniformity(
        no_residual.circumferential_stress
    )


def test_fiber_reinforcement_changes_loaded_stress() -> None:
    isotropic = solve_sector_tube(
        [SectorLayer(1.0, 1.4, 90.0, fiber_modulus=0.0)], pressure=0.18
    )
    reinforced = solve_sector_tube(
        [SectorLayer(1.0, 1.4, 90.0, fiber_modulus=5.0, fiber_slack_stretch=1.02)],
        pressure=0.18,
    )
    assert not np.allclose(
        isotropic.circumferential_stress,
        reinforced.circumferential_stress,
    )


def test_multilayer_solution_is_continuous_in_radius() -> None:
    layers = [
        SectorLayer(1.0, 1.2, 130.0, 1.2),
        SectorLayer(1.2, 1.5, 70.0, 0.7, fiber_modulus=2.0),
    ]
    solution = solve_sector_tube(layers, pressure=0.14, axial_stretch=1.05)
    assert np.all(np.diff(solution.radius) > 0.0)
    assert solution.current_boundaries.size == 3
    assert set(np.unique(solution.layer_index)) == {0, 1}


def test_strip_linear_eigenstrain_is_released_by_curvature() -> None:
    z = np.linspace(-0.5, 0.5, 401)
    target = 0.04 * z
    result = equilibrated_strip(z, target)
    assert np.isclose(result["curvature"], 0.04, atol=2.0e-5)
    assert np.max(np.abs(result["stress"])) < 5.0e-5


def test_strip_force_and_moment_balance() -> None:
    z = np.linspace(-0.5, 0.5, 401)
    target = 0.02 * np.tanh(6.0 * z)
    modulus = 1.0 + 0.7 * (z > 0.0)
    result = equilibrated_strip(z, target, modulus)
    assert abs(result["force_residual"]) < 1.0e-8
    assert abs(result["moment_residual"]) < 1.0e-8


def test_curvature_to_opening_angle() -> None:
    assert np.isclose(curvature_to_opening_angle(np.pi, 1.0), 180.0)


def test_sector_and_ring_coordinates_have_expected_radii() -> None:
    xi, yi, xo, yo = opening_sector_coordinates(1.0, 1.4, 90.0)
    assert np.allclose(np.hypot(xi, yi), 1.0)
    assert np.allclose(np.hypot(xo, yo), 1.4)
    xi, yi, xo, yo = ring_coordinates(0.8, 1.2)
    assert np.allclose(np.hypot(xi, yi), 0.8)
    assert np.allclose(np.hypot(xo, yo), 1.2)


def test_monte_carlo_angles_are_reproducible_and_bounded() -> None:
    first = monte_carlo_opening_angle(90.0, 5.0, 100, seed=4)
    second = monte_carlo_opening_angle(90.0, 5.0, 100, seed=4)
    assert np.array_equal(first, second)
    assert np.all((first >= 0.0) & (first <= 340.0))


def test_multi_sector_field_has_requested_mean() -> None:
    _, angles = multi_sector_angles(100.0, 25.0, sectors=100)
    assert np.isclose(np.mean(angles), 100.0, atol=1.0e-12)


def test_inverse_surface_has_minimum_near_truth() -> None:
    truth = SectorLayer(1.0, 1.4, 100.0, shear_modulus=1.5)
    solution = solve_sector_tube([truth], pressure=0.12)
    angles = np.linspace(70.0, 130.0, 13)
    moduli = np.linspace(0.8, 2.2, 15)
    loss = inverse_loss_surface(
        solution.current_boundaries[0],
        solution.current_boundaries[-1],
        0.12,
        angles,
        moduli,
    )
    index = np.unravel_index(np.nanargmin(loss), loss.shape)
    assert abs(angles[index[0]] - 100.0) <= 5.1
    assert abs(moduli[index[1]] - 1.5) <= 0.21


def test_stress_uniformity_is_zero_for_constant_field() -> None:
    assert stress_uniformity(np.ones(20)) == 0.0


def test_solution_arrays_are_finite() -> None:
    solution = solve_sector_tube(
        [SectorLayer(1.0, 1.5, 140.0, 1.0, 1.5, 1.02)],
        pressure=0.15,
        axial_stretch=1.1,
    )
    for array in (
        solution.radius,
        solution.reference_radius,
        solution.radial_stretch,
        solution.circumferential_stretch,
        solution.radial_stress,
        solution.circumferential_stress,
    ):
        assert np.all(np.isfinite(array))
