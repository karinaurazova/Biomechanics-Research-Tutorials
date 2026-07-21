"""Verification tests for Tutorial 11 constrained-mixture models."""

from __future__ import annotations

import numpy as np
import pytest

from biomechanics_tutorials.constrained_mixture import (
    CohortRecord,
    ConstituentParameters,
    MixtureSimulationParameters,
    cardiac_loading_protocol,
    cohort_elastic_stretch,
    constituent_stress_from_cohorts,
    feedback_multiplier,
    fiber_specific_tension,
    fiber_stretch,
    history_truncation_error,
    initialize_cardiac_constituents,
    initialize_homeostatic_targets,
    make_incompressible_biaxial_deformation,
    matrix_specific_nominal_stress,
    mixture_mass_fractions,
    mixture_metrics,
    model_state_count,
    polarimetry_to_mixture_prior,
    simulate_constrained_mixture,
    simulate_homogenized_mixture,
    survival_fraction,
)


def test_survival_fraction_has_requested_half_life():
    assert survival_fraction(12.0, 12.0) == pytest.approx(0.5)


def test_cohort_elastic_stretch_recovers_deposition_stretch_at_birth():
    value = cohort_elastic_stretch(1.15, 1.15, 1.06)
    assert value == pytest.approx(1.06)


def test_fiber_specific_tension_is_tension_only():
    assert fiber_specific_tension(0.95, 3.0) == pytest.approx(0.0)
    assert fiber_specific_tension(1.08, 3.0) > 0.0


def test_matrix_nominal_stress_changes_sign_about_unit_stretch():
    assert matrix_specific_nominal_stress(1.0, 2.0) == pytest.approx(0.0)
    assert matrix_specific_nominal_stress(1.1, 2.0) > 0.0
    assert matrix_specific_nominal_stress(0.9, 2.0) < 0.0


def test_directional_fiber_stretch_matches_diagonal_deformation():
    deformation = np.diag([1.2, 0.9, 1.0 / 1.08])
    assert fiber_stretch(deformation, 0.0) == pytest.approx(1.2)
    assert fiber_stretch(deformation, 90.0) == pytest.approx(0.9)


def test_homeostatic_initialization_assigns_targets_and_balanced_production():
    constituent = ConstituentParameters("fiber", "fiber", 1.0, 10.0, 4.0, 1.05)
    initialized = initialize_homeostatic_targets(np.diag([1.1, 1.0, 1.0 / 1.1]), [constituent])
    item = initialized[0]
    assert item.target_stress is not None
    assert item.target_stretch == pytest.approx(1.1)
    assert item.basal_production == pytest.approx(np.log(2.0) / 10.0)


def test_feedback_multiplier_is_positive_bounded_and_monotone():
    low = feedback_multiplier(-1.0, 2.0, 1.5, minimum=0.0, maximum=4.0)
    mid = feedback_multiplier(0.0, 2.0, 1.5, minimum=0.0, maximum=4.0)
    high = feedback_multiplier(1.0, 2.0, 1.5, minimum=0.0, maximum=4.0)
    assert 0.0 <= low < mid < high <= 4.0


def test_constituent_stress_is_mass_weighted_sum_of_cohorts():
    constituent = ConstituentParameters("fiber", "fiber", 1.0, 10.0, 4.0)
    cohorts = [
        CohortRecord(0.0, 0.4, 1.0, 0.0),
        CohortRecord(1.0, 0.6, 1.0, 0.0),
    ]
    total = constituent_stress_from_cohorts(1.08, cohorts, constituent)
    expected = float(fiber_specific_tension(1.08, 4.0))
    assert total == pytest.approx(expected)


def test_homeostatic_full_history_simulation_preserves_mass_approximately():
    time = np.linspace(0.0, 40.0, 401)
    constituents = initialize_cardiac_constituents()
    result = simulate_constrained_mixture(
        time,
        cardiac_loading_protocol("homeostasis"),
        constituents,
        MixtureSimulationParameters(history_cutoff_fraction=0.0),
    )
    assert result["total_mass"][-1] == pytest.approx(result["total_mass"][0], rel=0.015)


def test_pressure_overload_increases_collagen_mass():
    time = np.linspace(0.0, 80.0, 401)
    constituents = initialize_cardiac_constituents()
    result = simulate_constrained_mixture(time, cardiac_loading_protocol("pressure"), constituents)
    collagen_initial = result["mass"]["collagen_plus"][0] + result["mass"]["collagen_minus"][0]
    collagen_final = result["mass"]["collagen_plus"][-1] + result["mass"]["collagen_minus"][-1]
    assert collagen_final > collagen_initial


def test_volume_overload_increases_cardiomyocyte_mass():
    time = np.linspace(0.0, 80.0, 401)
    constituents = initialize_cardiac_constituents()
    result = simulate_constrained_mixture(time, cardiac_loading_protocol("volume"), constituents)
    assert result["mass"]["cardiomyocytes"][-1] > result["mass"]["cardiomyocytes"][0]


def test_reversal_reduces_late_overload_response():
    time = np.linspace(0.0, 100.0, 501)
    constituents = initialize_cardiac_constituents()
    sustained = simulate_constrained_mixture(time, cardiac_loading_protocol("combined"), constituents)
    reversal = simulate_constrained_mixture(time, cardiac_loading_protocol("reversal"), constituents)
    assert reversal["total_mass"][-1] < sustained["total_mass"][-1]


def test_mass_fractions_sum_to_one():
    time = np.linspace(0.0, 10.0, 51)
    constituents = initialize_cardiac_constituents()
    result = simulate_constrained_mixture(time, cardiac_loading_protocol("homeostasis"), constituents)
    fractions = mixture_mass_fractions(result)
    total = sum(fractions.values())
    assert np.allclose(total, 1.0)


def test_full_and_homogenized_models_agree_at_initial_time():
    time = np.linspace(0.0, 20.0, 101)
    constituents = initialize_cardiac_constituents()
    protocol = cardiac_loading_protocol("homeostasis")
    full = simulate_constrained_mixture(time, protocol, constituents)
    reduced = simulate_homogenized_mixture(time, protocol, constituents)
    assert full["total_mass"][0] == pytest.approx(reduced["total_mass"][0])
    assert full["total_stress"][0] == pytest.approx(reduced["total_stress"][0])


def test_homogenized_model_remains_positive():
    time = np.linspace(0.0, 80.0, 401)
    constituents = initialize_cardiac_constituents()
    result = simulate_homogenized_mixture(time, cardiac_loading_protocol("combined"), constituents)
    for values in result["mass"].values():
        assert np.all(values > 0.0)
    for values in result["natural_stretch"].values():
        assert np.all(values > 0.0)


def test_history_truncation_error_decreases_with_larger_window():
    constituent = ConstituentParameters("fiber", "fiber", 1.0, 10.0, 4.0)
    cohorts = [
        CohortRecord(float(index), 0.1, 0.98 + 0.002 * index, 0.0)
        for index in range(20)
    ]
    short = history_truncation_error(1.1, cohorts, constituent, 20.0, 3.0)
    long = history_truncation_error(1.1, cohorts, constituent, 20.0, 15.0)
    assert long <= short


def test_polarimetry_prior_is_bounded_and_symmetric():
    prior = polarimetry_to_mixture_prior(
        np.array([10.0, 20.0]),
        np.array([1.0, 0.0]),
        np.array([0.2, 0.8]),
    )
    assert np.all((prior["collagen_fraction"] >= 0.05) & (prior["collagen_fraction"] <= 0.45))
    mean = 0.5 * (prior["family_plus_degrees"] + prior["family_minus_degrees"])
    assert np.allclose(mean, prior["mean_angle_degrees"])


def test_model_state_count_orders_complexity():
    counts = model_state_count(4, 100, 10)
    assert counts["full_history_mixture"] > counts["homogenized_mixture"]
    assert counts["full_history_mixture"] > counts["kinematic_growth"]


def test_mixture_metrics_are_consistent():
    time = np.linspace(0.0, 20.0, 101)
    constituents = initialize_cardiac_constituents()
    result = simulate_constrained_mixture(time, cardiac_loading_protocol("pressure"), constituents)
    metrics = mixture_metrics(result)
    assert metrics["mass_ratio"] == pytest.approx(metrics["final_mass"] / metrics["initial_mass"])
    assert metrics["peak_stress"] >= metrics["initial_stress"]


def test_invalid_constituent_and_numerical_parameters_are_rejected():
    with pytest.raises(ValueError):
        ConstituentParameters("", "fiber", 1.0, 10.0, 1.0).validate()
    with pytest.raises(ValueError):
        MixtureSimulationParameters(feedback_scale=0.0).validate()
    with pytest.raises(ValueError):
        make_incompressible_biaxial_deformation(-1.0, 1.0)
