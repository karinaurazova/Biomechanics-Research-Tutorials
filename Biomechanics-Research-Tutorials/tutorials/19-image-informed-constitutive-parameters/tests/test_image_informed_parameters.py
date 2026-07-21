"""Tests for Tutorial 19 image-informed constitutive parameters."""

from __future__ import annotations

import numpy as np
import pytest

from biomechanics_tutorials.image_informed_parameters import (
    PARAMETER_NAMES,
    bayesian_linear_calibration,
    benchmark_calibration,
    build_synthetic_load_cases,
    build_synthetic_structural_fields,
    global_force_system,
    parameter_maps,
    solve_nonnegative_least_squares,
    stress_design_basis,
    stress_from_parameters,
    structural_order_from_kappa,
    true_parameter_set,
)


def test_structural_order_is_bounded_and_monotone() -> None:
    kappa = np.array([0.0, 1.0, 4.0, 20.0])
    order = structural_order_from_kappa(kappa)
    assert np.all(order >= 0.0)
    assert np.all(order < 1.0)
    assert np.all(np.diff(order) > 0.0)


def test_stress_model_is_linear_in_parameters() -> None:
    structure = build_synthetic_structural_fields(shape=(24, 24), seed=1)
    exx = np.full(structure.shape, 0.02)
    eyy = np.full(structure.shape, -0.005)
    gxy = np.zeros(structure.shape)
    p1 = np.array([10.0, 2.0, 30.0, 5.0])
    p2 = np.array([3.0, 4.0, 7.0, 2.0])
    s12 = stress_from_parameters(structure, exx, eyy, gxy, p1 + p2)
    s1 = stress_from_parameters(structure, exx, eyy, gxy, p1)
    s2 = stress_from_parameters(structure, exx, eyy, gxy, p2)
    assert np.max(np.abs(s12 - s1 - s2)) < 1.0e-12


def test_global_force_identification_recovers_truth_without_noise() -> None:
    structure = build_synthetic_structural_fields(shape=(42, 42), seed=2)
    truth = true_parameter_set().as_vector()
    load_cases = build_synthetic_load_cases(structure, true_parameter_set(), noise_level=0.0, seed=3)
    A, y, labels = global_force_system(structure, load_cases)
    result = solve_nonnegative_least_squares(A, y, method='test')
    assert len(labels) == len(y)
    assert A.shape[1] == len(PARAMETER_NAMES)
    assert result.parameters == pytest.approx(truth, rel=1.0e-5, abs=1.0e-5)


def test_bayesian_posterior_is_more_confident_than_prior() -> None:
    structure = build_synthetic_structural_fields(shape=(32, 32), seed=4)
    load_cases = build_synthetic_load_cases(structure, true_parameter_set(), noise_level=0.0, seed=5)
    A, y, _ = global_force_system(structure, load_cases)
    prior_mean = np.array([15.0, 20.0, 120.0, 50.0])
    prior_std = np.array([10.0, 10.0, 80.0, 40.0])
    posterior = bayesian_linear_calibration(A, y, prior_mean, prior_std, noise_std=0.02)
    assert np.all(posterior['std'] < prior_std)
    assert posterior['mean'].shape == prior_mean.shape


def test_parameter_maps_are_positive_on_mask() -> None:
    structure = build_synthetic_structural_fields(shape=(32, 32), seed=6)
    maps = parameter_maps(structure, true_parameter_set())
    for values in maps.values():
        assert values.shape == structure.shape
        assert np.all(values[structure.mask] >= 0.0)


def test_complete_benchmark_contains_expected_results() -> None:
    bundle = benchmark_calibration(seed=7, force_noise=0.01)
    methods = {result.method for result in bundle['results']}
    assert {'load_curve_only', 'virtual_fields', 'joint_global_plus_vfm', 'inverse_fe_like'} <= methods
    assert bundle['posterior']['mean'].shape == (4,)
    assert bundle['identifiability']['singular_values'].shape == (4,)


def test_design_basis_has_expected_shape() -> None:
    structure = build_synthetic_structural_fields(shape=(20, 22), seed=8)
    exx = np.ones(structure.shape) * 0.01
    eyy = np.ones(structure.shape) * 0.004
    gxy = np.ones(structure.shape) * 0.003
    basis = stress_design_basis(structure, exx, eyy, gxy)
    assert basis.shape == structure.shape + (3, 4)
