"""Tests for Tutorial 10 extracellular-matrix turnover."""

import numpy as np
import pytest

from biomechanics_tutorials.ecm_turnover import (
    CollagenKineticsParameters,
    MatrixComponent,
    MechanobiologyParameters,
    SurvivalParameters,
    collagen_fiber_tension,
    compare_model_state_count,
    effective_collagen_stiffness,
    hazard_rate,
    matrix_nominal_stress,
    mmp_timp_activity,
    production_multiplier,
    pulse_chase_fraction,
    simulate_cohort_turnover,
    simulate_collagen_maturation,
    simulate_homogenized_turnover,
    simulate_multicomponent_ecm,
    simulate_spatial_degradation,
    survival_fraction,
    tangent_modulus,
    turnover_metrics,
)


def test_exponential_survival_has_correct_half_life():
    parameters = SurvivalParameters(model="exponential", half_life=12.0)
    assert survival_fraction(12.0, parameters) == pytest.approx(0.5)
    assert hazard_rate(5.0, parameters) == pytest.approx(np.log(2.0) / 12.0)


def test_weibull_survival_is_monotone_and_has_correct_half_life():
    parameters = SurvivalParameters(model="weibull", half_life=10.0, shape=2.0)
    age = np.linspace(0.0, 30.0, 101)
    survival = survival_fraction(age, parameters)
    assert np.all(np.diff(survival) <= 1.0e-12)
    assert survival_fraction(10.0, parameters) == pytest.approx(0.5)


def test_timp_reduces_effective_mmp_activity():
    low_inhibition = mmp_timp_activity(2.0, 0.2)
    high_inhibition = mmp_timp_activity(2.0, 2.0)
    assert high_inhibition < low_inhibition


def test_stress_overload_increases_production_multiplier():
    parameters = MechanobiologyParameters(target_stress=1.0, production_gain=1.5)
    assert production_multiplier(1.4, parameters) > production_multiplier(1.0, parameters)


def test_crosslinks_raise_effective_collagen_stiffness():
    low = effective_collagen_stiffness(1.0, 0.1)
    high = effective_collagen_stiffness(1.0, 0.8)
    assert high > low


def test_collagen_tension_is_zero_in_compression_and_positive_in_tension():
    assert collagen_fiber_tension(0.9) == pytest.approx(0.0)
    assert collagen_fiber_tension(1.1) > 0.0


def test_deposition_stretch_creates_prestress_at_unit_total_stretch():
    unstressed = collagen_fiber_tension(1.0, deposition_stretch=1.0)
    prestressed = collagen_fiber_tension(1.0, deposition_stretch=1.08)
    assert prestressed > unstressed


def test_matrix_stress_and_tangent_modulus_are_positive_in_extension():
    stress = matrix_nominal_stress(1.1, 1.0, 1.0, 0.5)
    modulus = tangent_modulus(1.1, 1.0, 1.0, 0.5)
    assert stress > 0.0
    assert modulus > 0.0


def test_collagen_maturation_remains_nonnegative_and_crosslinks_bounded():
    time = np.linspace(0.0, 30.0, 301)
    result = simulate_collagen_maturation(time)
    for key in ["precursor", "immature", "mature", "mmp", "timp"]:
        assert np.min(result[key]) >= 0.0
    assert np.min(result["crosslinks"]) >= 0.0
    assert np.max(result["crosslinks"]) <= 1.0


def test_sustained_overload_increases_synthesis_and_mature_collagen():
    time = np.linspace(0.0, 60.0, 601)
    control = simulate_collagen_maturation(time, stress_protocol=1.0)
    overload = simulate_collagen_maturation(time, stress_protocol=1.35)
    assert overload["synthesis"][-1] > control["synthesis"][-1]
    assert overload["mature"][-1] > control["mature"][-1]


def test_inflammation_increases_enzyme_activity_and_reduces_mature_collagen():
    time = np.linspace(0.0, 40.0, 401)
    control = simulate_collagen_maturation(time, inflammation_protocol=0.0)
    inflamed = simulate_collagen_maturation(time, inflammation_protocol=1.0)
    assert inflamed["enzyme_activity"][-1] > control["enzyme_activity"][-1]
    assert inflamed["mature"][-1] < control["mature"][-1]


def test_cohort_and_homogenized_models_agree_for_exponential_survival():
    time = np.linspace(0.0, 50.0, 1001)
    half_life = 10.0
    removal_rate = np.log(2.0) / half_life
    production = removal_rate
    cohort = simulate_cohort_turnover(
        time,
        production,
        SurvivalParameters(model="exponential", half_life=half_life),
        initial_mass=1.0,
    )
    homogenized = simulate_homogenized_turnover(time, production, half_life, initial_mass=1.0)
    assert cohort["mass"][-1] == pytest.approx(homogenized["mass"][-1], rel=5.0e-3)
    assert cohort["mass"][-1] == pytest.approx(1.0, rel=5.0e-3)


def test_cohort_mean_age_and_initial_fraction_are_physical():
    time = np.linspace(0.0, 20.0, 201)
    result = simulate_cohort_turnover(time, 0.05, initial_mass=1.0)
    assert result["mean_age"][-1] > 0.0
    assert 0.0 <= result["retained_initial_fraction"][-1] <= 1.0
    assert result["retained_initial_fraction"][-1] < result["retained_initial_fraction"][0]


def test_pulse_chase_fraction_stays_one_during_pulse_and_then_decays():
    time = np.linspace(0.0, 30.0, 301)
    fraction = pulse_chase_fraction(time, pulse_end=5.0, survival_parameters=SurvivalParameters(half_life=10.0))
    assert np.allclose(fraction[time <= 5.0], 1.0)
    assert fraction[-1] < fraction[time > 5.0][0]


def test_multicomponent_model_preserves_nonnegative_masses_and_normalized_fractions():
    time = np.linspace(0.0, 20.0, 201)
    components = [
        MatrixComponent("elastin", 1.0, 0.0, 1000.0, 0.5),
        MatrixComponent("collagen-I", 1.0, np.log(2.0) / 20.0, 20.0, 2.0, production_gain=0.5),
        MatrixComponent("proteoglycan", 0.3, np.log(2.0) * 0.3 / 5.0, 5.0, 0.2),
    ]
    result = simulate_multicomponent_ecm(time, components, stress_protocol=1.2)
    assert np.min(result["mass"]) >= 0.0
    assert np.allclose(np.sum(result["mass_fraction"], axis=1), 1.0)


def test_spatial_degradation_is_nonnegative_and_local_enzyme_source_lowers_collagen():
    time = np.linspace(0.0, 1.0, 201)
    coordinate = np.linspace(0.0, 1.0, 101)
    def source(x: np.ndarray, _time: float) -> np.ndarray:
        return 4.0 * np.exp(-((x - 0.5) / 0.08) ** 2)

    result = simulate_spatial_degradation(
        time,
        coordinate,
        np.ones_like(coordinate),
        source,
        enzyme_diffusivity=0.002,
    )
    center = coordinate.size // 2
    assert np.min(result["collagen"]) >= 0.0
    assert result["collagen"][-1, center] < result["collagen"][-1, 0]


def test_turnover_metrics_close_mass_balance_for_homogenized_model():
    time = np.linspace(0.0, 30.0, 3001)
    result = simulate_homogenized_turnover(time, 0.08, half_life=12.0, initial_mass=1.0)
    metrics = turnover_metrics(time, result["mass"], result["production"], result["removal"])
    assert abs(metrics["balance_residual"]) < 2.0e-3


def test_same_steady_mass_can_hide_different_fluxes():
    time = np.linspace(0.0, 60.0, 601)
    slow = simulate_homogenized_turnover(time, np.log(2.0) / 20.0, half_life=20.0)
    fast = simulate_homogenized_turnover(time, np.log(2.0) / 5.0, half_life=5.0)
    assert slow["mass"][-1] == pytest.approx(fast["mass"][-1], rel=2.0e-3)
    assert fast["production"][-1] > slow["production"][-1]


def test_state_count_comparison_orders_model_complexity():
    counts = compare_model_state_count(100, 4)
    assert counts["net_mass_ode"] < counts["maturation_ode"]
    assert counts["maturation_ode"] < counts["age_structured_cohorts"]
    assert counts["age_structured_cohorts"] < counts["spatial_cohort_model"]


def test_invalid_parameters_are_rejected():
    with pytest.raises(ValueError):
        SurvivalParameters(half_life=0.0).validate()
    with pytest.raises(ValueError):
        CollagenKineticsParameters(inhibition_constant=0.0).validate()
    with pytest.raises(ValueError):
        simulate_homogenized_turnover(np.array([0.0, 1.0]), 1.0, half_life=0.0)
