import numpy as np
import pytest
from biomechanics_tutorials.fiber_reorientation import (
    ReorientationParameters,
    adaptation_time,
    alignment_index,
    analytical_constant_target,
    angular_difference,
    is_orthogonal,
    simulate_reorientation,
)


def test_axial_angle_equivalence():
    assert np.isclose(angular_difference(np.deg2rad(10), np.deg2rad(190)), 0, atol=1e-12)


def test_orthogonal_case_is_detected():
    assert bool(is_orthogonal(np.deg2rad(30), np.deg2rad(-60)))


def test_solution_moves_toward_target():
    p = ReorientationParameters(rate=0.5, duration=10, time_step=0.01)
    _, o, t = simulate_reorientation(np.deg2rad(-50), np.deg2rad(30), p)
    assert abs(float(angular_difference(t[-1], o[-1]))) < abs(float(angular_difference(t[0], o[0])))
    assert abs(float(angular_difference(t[-1], o[-1]))) < np.deg2rad(2)


def test_zero_rate_preserves_orientation():
    _, o, _ = simulate_reorientation(
        0.2, 1.0, ReorientationParameters(rate=0, duration=5, time_step=0.1)
    )
    assert np.allclose(o, o[0])


def test_alignment_index_bounds():
    v = alignment_index(np.linspace(-np.pi, np.pi, 100), 0)
    assert np.all(v >= 0) and np.all(v <= 1)


def test_numerical_solution_matches_analytical_solution():
    initial = np.deg2rad(-50)
    target = np.deg2rad(30)
    p = ReorientationParameters(rate=0.35, duration=12, time_step=0.002)
    time, numerical, _ = simulate_reorientation(initial, target, p)
    analytical = analytical_constant_target(time, initial, target, p.rate)
    assert np.max(np.abs(angular_difference(analytical, numerical))) < np.deg2rad(0.03)


def test_adaptation_time_scales_inversely_with_rate():
    i = np.deg2rad(-50)
    t = np.deg2rad(30)
    e = np.deg2rad(5)
    assert np.isclose(adaptation_time(i, t, 0.2, e), 2 * adaptation_time(i, t, 0.4, e))


def test_analytical_solution_rejects_orthogonal_case():
    with pytest.raises(ValueError, match="orthogonal"):
        analytical_constant_target(np.array([0, 1]), np.deg2rad(-60), np.deg2rad(30), 0.3)


def test_unstable_explicit_euler_step_is_rejected():
    with pytest.raises(ValueError, match="unstable"):
        ReorientationParameters(rate=4, duration=2, time_step=0.5).validate()
