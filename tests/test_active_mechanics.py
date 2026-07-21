import numpy as np

from biomechanics_tutorials.active_mechanics import (
    activation_biexponential,
    active_strain_shear_response,
    active_strain_tensor,
    active_strain_uniaxial_nominal_response,
    active_stress_shear_response,
    active_tension,
    calibrate_active_stretch,
    calcium_gamma_transient,
    force_length,
    force_velocity,
    passive_uniaxial_nominal_stress,
    simulate_crossbridge,
    simulate_isotonic_shortening,
)


def test_activation_is_normalized_and_nonnegative():
    time = np.linspace(0.0, 1.0, 2001)
    activation = activation_biexponential(time)
    assert np.min(activation) >= 0.0
    assert np.max(activation) == np.max(activation)
    assert np.isclose(np.max(activation), 1.0, atol=2e-4)


def test_force_length_peaks_at_optimal_stretch():
    stretches = np.linspace(0.7, 1.5, 2001)
    values = force_length(stretches)
    peak = stretches[np.argmax(values)]
    assert np.isclose(peak, 1.10, atol=1e-3)


def test_force_velocity_equals_one_at_zero_and_decreases_with_shortening():
    values = force_velocity(np.array([-0.4, 0.0, 0.4]))
    assert values[0] > values[1] > values[2]
    assert np.isclose(values[1], 1.0)


def test_active_tension_vanishes_at_zero_activation():
    assert np.isclose(active_tension(0.0, 1.1), 0.0)


def test_active_strain_tensor_is_volume_preserving():
    fa = active_strain_tensor(0.82)
    assert np.isclose(np.linalg.det(fa), 1.0, atol=1e-12)


def test_active_strain_reduces_to_passive_when_active_stretch_is_one():
    stretches = np.linspace(0.85, 1.3, 11)
    assert np.allclose(
        active_strain_uniaxial_nominal_response(stretches, 1.0),
        passive_uniaxial_nominal_stress(stretches),
    )


def test_calibration_matches_requested_active_nominal_datum():
    reference_stretch = 1.12
    target = 20.0
    active_stretch = calibrate_active_stretch(reference_stretch, target)
    passive = passive_uniaxial_nominal_stress(reference_stretch)
    total = active_strain_uniaxial_nominal_response(reference_stretch, active_stretch)
    assert np.isclose(total - passive, target, rtol=1e-8, atol=1e-8)


def test_active_stress_and_active_strain_diverge_in_shear_after_calibration():
    reference_stretch = 1.1
    tension = 25.0
    target_active_nominal = tension / reference_stretch
    active_stretch = calibrate_active_stretch(reference_stretch, target_active_nominal)
    gamma = np.array([0.2, 0.5])
    stress_response = active_stress_shear_response(gamma, tension)
    strain_response = active_strain_shear_response(gamma, active_stretch)
    assert not np.allclose(stress_response, strain_response)


def test_crossbridge_fraction_remains_bounded_and_lags_calcium():
    time = np.linspace(0.0, 0.8, 1601)
    target = calcium_gamma_transient(time)
    result = simulate_crossbridge(time, target)
    bound = result["bound_fraction"]
    calcium = result["calcium"]
    assert np.all((bound >= 0.0) & (bound <= 1.0))
    assert time[np.argmax(bound)] > time[np.argmax(calcium)]


def test_lower_afterload_produces_more_shortening():
    time = np.linspace(0.0, 0.8, 401)
    activation = activation_biexponential(time)
    low = simulate_isotonic_shortening(time, activation, afterload=12.0)
    high = simulate_isotonic_shortening(time, activation, afterload=35.0)
    assert np.min(low["stretch"]) < np.min(high["stretch"])
