import numpy as np
import pytest

from biomechanics_tutorials.mechanical_homeostasis import (
    ConstituentTurnoverParameters,
    HomeostasisParameters,
    VesselHomeostasisParameters,
    analytical_capacity_response,
    feedback_response,
    generate_load_protocol,
    homeostasis_metrics,
    relative_homeostatic_error,
    simulate_constituent_turnover,
    simulate_scalar_homeostasis,
    simulate_vessel_homeostasis,
    survival_fraction,
    vessel_equilibrium,
    vessel_stimuli,
)


def test_relative_error_is_zero_at_target():
    assert relative_homeostatic_error(2.5, 2.5) == pytest.approx(0.0)


def test_feedback_dead_zone_and_saturation():
    values = feedback_response(np.array([-0.5, -0.05, 0.05, 0.5]), 0.1, 0.2)
    assert values[1] == pytest.approx(0.0)
    assert values[2] == pytest.approx(0.0)
    assert abs(values[0]) < 0.2
    assert abs(values[-1]) < 0.2


def test_numerical_solution_matches_analytical_constant_load_response():
    time = np.linspace(0.0, 12.0, 2401)
    params = HomeostasisParameters(target_stress=1.0, adaptation_rate=0.4)
    numerical = simulate_scalar_homeostasis(time, 1.5, 1.0, params)
    analytical = analytical_capacity_response(time, 1.5, 1.0, 1.0, 0.4)
    assert np.max(np.abs(numerical["capacity"] - analytical)) < 5.0e-4


def test_step_load_is_regulated_toward_target_stress():
    time = np.linspace(0.0, 30.0, 3001)
    load = generate_load_protocol(time, "step", amplitude=0.6, onset=3.0)
    result = simulate_scalar_homeostasis(time, load)
    assert abs(result["true_error"][-1]) < 1.0e-3
    assert result["capacity"][-1] == pytest.approx(1.6, rel=2.0e-3)


def test_sensor_bias_shifts_true_equilibrium():
    time = np.linspace(0.0, 40.0, 4001)
    params = HomeostasisParameters(adaptation_rate=0.3, sensor_bias=0.1)
    result = simulate_scalar_homeostasis(time, 1.4, parameters=params)
    expected_true_stress = 1.0 / 1.1
    assert result["stress"][-1] == pytest.approx(expected_true_stress, rel=2.0e-3)


def test_wrong_feedback_sign_is_maladaptive():
    time = np.linspace(0.0, 8.0, 801)
    load = generate_load_protocol(time, "step", amplitude=0.2, onset=1.0)
    stable = simulate_scalar_homeostasis(time, load)
    unstable = simulate_scalar_homeostasis(
        time,
        load,
        parameters=HomeostasisParameters(
            feedback_sign=-1.0,
            adaptation_rate=0.25,
            capacity_min=0.2,
            capacity_max=3.0,
        ),
    )
    assert abs(stable["true_error"][-1]) < abs(unstable["true_error"][-1])


def test_survival_fraction_equals_one_half_at_half_life():
    assert survival_fraction(5.0, 5.0) == pytest.approx(0.5)


def test_constituent_turnover_balances_at_homeostasis():
    time = np.linspace(0.0, 10.0, 101)
    constituent = ConstituentTurnoverParameters("collagen", 0.7, 8.0)
    result = simulate_constituent_turnover(time, 0.0, [constituent])
    assert np.allclose(result["production"], result["removal"])
    assert np.allclose(result["mass"], 0.7)


def test_positive_stimulus_increases_sensitive_constituent_mass():
    time = np.linspace(0.0, 20.0, 401)
    constituent = ConstituentTurnoverParameters("collagen", 1.0, 6.0, 1.5)
    result = simulate_constituent_turnover(time, 0.2, [constituent])
    assert result["mass"][0, -1] > result["mass"][0, 0]


def test_vessel_equilibrium_restores_both_stimuli():
    params = VesselHomeostasisParameters()
    radius, thickness = vessel_equilibrium(1.4, 1.8, params)
    shear, wall = vessel_stimuli(1.4, 1.8, radius, thickness, params)
    assert shear == pytest.approx(1.0)
    assert wall == pytest.approx(1.0)


def test_vessel_model_converges_after_pressure_and_flow_step():
    time = np.linspace(0.0, 60.0, 6001)
    pressure = np.where(time < 2.0, 1.0, 1.35)
    flow = np.where(time < 2.0, 1.0, 1.50)
    result = simulate_vessel_homeostasis(time, pressure, flow)
    assert result["shear_ratio"][-1] == pytest.approx(1.0, abs=2.0e-3)
    assert result["wall_stress_ratio"][-1] == pytest.approx(1.0, abs=2.0e-3)


def test_metrics_report_zero_for_perfect_homeostasis():
    time = np.linspace(0.0, 5.0, 51)
    metrics = homeostasis_metrics(time, np.zeros_like(time))
    assert metrics["iae"] == pytest.approx(0.0)
    assert metrics["settling_time"] == pytest.approx(0.0)


def test_invalid_parameters_are_rejected():
    with pytest.raises(ValueError):
        HomeostasisParameters(target_stress=0.0).validate()
    with pytest.raises(ValueError):
        VesselHomeostasisParameters(radius_min=1.0, radius_max=0.5).validate()
    with pytest.raises(ValueError):
        generate_load_protocol(np.linspace(0.0, 1.0, 10), "unknown")
