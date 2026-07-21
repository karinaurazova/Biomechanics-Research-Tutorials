"""Tests for Tutorial 15 polarization-like orientation maps."""

from __future__ import annotations

import numpy as np

from biomechanics_tutorials.polarization_orientation import (
    PolarizationParameters,
    axial_difference,
    axial_wrap,
    calibration_sweep,
    crossed_polarizer_intensity,
    estimate_retardance_from_modulation,
    export_polarization_dataset,
    harmonic_design_matrix,
    jones_linear_retarder,
    multilayer_jones_intensity,
    orientation_error_deg,
    read_polarization_metadata,
    recover_orientation_harmonic,
    retardance_from_birefringence,
    simulate_polarization_series,
    synthetic_illumination_field,
)


def test_axial_wrap_is_pi_periodic() -> None:
    angle = np.array([-1.2, 0.4, 1.3])
    assert np.allclose(axial_wrap(angle), axial_wrap(angle + np.pi))


def test_axial_difference_zero_for_pi_shift() -> None:
    assert np.allclose(axial_difference(0.3, 0.3 + np.pi), 0.0)


def test_retardance_scales_with_thickness() -> None:
    values = retardance_from_birefringence(0.001, np.array([1.0, 2.0, 3.0]))
    assert np.allclose(values / values[0], [1.0, 2.0, 3.0])


def test_crossed_polarizer_is_axial() -> None:
    theta = 0.4
    first = crossed_polarizer_intensity(theta, 1.2, 0.7)
    second = crossed_polarizer_intensity(theta + np.pi, 1.2, 0.7)
    assert np.allclose(first, second)


def test_zero_retardance_has_zero_modulated_signal() -> None:
    angles = np.linspace(0, np.pi, 20, endpoint=False)
    values = crossed_polarizer_intensity(0.4, 0.0, angles)
    assert np.allclose(values, 0.0)


def test_jones_retarder_is_unitary() -> None:
    matrix = jones_linear_retarder(0.6, 1.3)
    assert np.allclose(matrix.conj().T @ matrix, np.eye(2), atol=1e-12)


def test_multilayer_intensity_is_bounded() -> None:
    value = multilayer_jones_intensity([0.1, 0.7], [1.0, 0.4], 0.0, 0.8)
    assert 0.0 <= value <= 1.0 + 1e-12


def test_series_reproducible_by_seed() -> None:
    shape = (24, 24)
    orientation = np.full(shape, 0.35)
    retardance = np.full(shape, 1.2)
    angles = np.linspace(0, np.pi, 8, endpoint=False)
    first = simulate_polarization_series(orientation, retardance, angles, seed=5)
    second = simulate_polarization_series(orientation, retardance, angles, seed=5)
    assert np.allclose(first.images, second.images)


def test_series_metadata_marks_synthetic() -> None:
    field = np.zeros((8, 8))
    angles = np.linspace(0, np.pi, 6, endpoint=False)
    result = simulate_polarization_series(field, np.ones_like(field), angles)
    assert result.metadata["synthetic"] is True
    assert result.metadata["experimental_validation"] is False


def test_harmonic_design_has_three_columns() -> None:
    angles = np.linspace(0, np.pi, 7, endpoint=False)
    assert harmonic_design_matrix(angles).shape == (7, 3)


def test_harmonic_recovery_matches_uniform_axis() -> None:
    shape = (30, 30)
    truth = np.full(shape, np.deg2rad(18.0))
    ret = np.full(shape, 1.4)
    angles = np.linspace(0, np.pi, 16, endpoint=False)
    series = simulate_polarization_series(
        truth,
        ret,
        angles,
        parameters=PolarizationParameters(read_noise_std=0.0, photon_count=1e8, blur_sigma=0.0),
        seed=1,
    )
    recovered = recover_orientation_harmonic(series.expectation, angles)
    error = orientation_error_deg(recovered.orientation_rad, truth)
    assert np.median(error) < 1e-8


def test_modulation_increases_with_small_retardance() -> None:
    shape = (4, 4)
    angles = np.linspace(0, np.pi, 12, endpoint=False)
    axis = np.zeros(shape)
    low = simulate_polarization_series(
        axis,
        np.full(shape, 0.3),
        angles,
        parameters=PolarizationParameters(read_noise_std=0, photon_count=1e8, blur_sigma=0),
    ).expectation
    high = simulate_polarization_series(
        axis,
        np.full(shape, 1.0),
        angles,
        parameters=PolarizationParameters(read_noise_std=0, photon_count=1e8, blur_sigma=0),
    ).expectation
    assert np.mean(recover_orientation_harmonic(high, angles).modulation) > np.mean(
        recover_orientation_harmonic(low, angles).modulation
    )


def test_retardance_inverse_on_principal_branch() -> None:
    delta = np.array([0.2, 0.8, 1.5, 2.8])
    mod = 0.5 * np.sin(delta / 2) ** 2
    estimate = estimate_retardance_from_modulation(mod)
    assert np.allclose(estimate, delta)


def test_illumination_field_is_positive() -> None:
    field = synthetic_illumination_field((40, 30), gradient=(0.8, -0.7), vignette=0.5)
    assert np.min(field) > 0


def test_calibration_sweep_applies_offset() -> None:
    known = np.deg2rad(np.array([-30.0, 0.0, 30.0]))
    measured = calibration_sweep(known, np.deg2rad(5))
    assert np.allclose(axial_difference(measured, known), np.deg2rad(5))


def test_orientation_error_respects_mask() -> None:
    truth = np.zeros((2, 2))
    estimate = np.full((2, 2), 0.1)
    mask = np.array([[1, 0], [0, 1]], dtype=bool)
    assert orientation_error_deg(estimate, truth, mask).shape == (2,)


def test_dataset_export_preserves_provenance(tmp_path) -> None:
    field = np.zeros((8, 8))
    angles = np.linspace(0, np.pi, 6, endpoint=False)
    series = simulate_polarization_series(field, np.ones_like(field), angles)
    path = export_polarization_dataset(
        tmp_path / "sample.npz", series, {"orientation": field}, {"seed": 12}
    )
    metadata = read_polarization_metadata(path)
    assert metadata["synthetic"] is True
    assert metadata["experimental_validation"] is False
    assert metadata["seed"] == 12


def test_invalid_parameters_raise() -> None:
    try:
        PolarizationParameters(depolarization=1.5)
    except ValueError:
        return
    raise AssertionError("invalid depolarization should raise")
