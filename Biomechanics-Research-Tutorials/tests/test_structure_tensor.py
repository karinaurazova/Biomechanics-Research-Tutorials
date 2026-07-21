import numpy as np
import pytest

from biomechanics_tutorials.structure_tensor import (
    StructureTensorParameters,
    axial_angle_difference,
    confidence_mask,
    orientation_error_metrics,
    structure_tensor_orientation,
    synthetic_crossing_fibers,
    synthetic_curved_fibers,
    synthetic_parallel_fibers,
    weighted_axial_mean,
    wrap_axial_radians,
)


def test_axial_wrapping_identifies_180_degree_equivalence():
    assert np.isclose(wrap_axial_radians(np.deg2rad(190.0)), np.deg2rad(10.0))
    assert np.isclose(axial_angle_difference(np.deg2rad(10), np.deg2rad(190)), 0.0)


def test_parallel_field_is_recovered_with_small_error():
    image, truth = synthetic_parallel_fibers(angle_degrees=32.0, noise_std=0.01)
    result = structure_tensor_orientation(image, StructureTensorParameters(1.0, 3.0))
    mask = confidence_mask(result, 0.45, 0.15, border=10)
    metrics = orientation_error_metrics(result["orientation"], truth, mask)
    assert metrics["mae_deg"] < 1.0
    assert metrics["coverage"] > 0.35


def test_orientation_is_axial_for_opposite_line_directions():
    image_a, _ = synthetic_parallel_fibers(angle_degrees=20.0)
    image_b, _ = synthetic_parallel_fibers(angle_degrees=200.0)
    assert np.allclose(image_a, image_b)


def test_curved_field_is_recovered_away_from_boundaries():
    image, truth = synthetic_curved_fibers(noise_std=0.01)
    result = structure_tensor_orientation(image, StructureTensorParameters(1.0, 3.0))
    mask = confidence_mask(result, 0.35, 0.10, border=12)
    metrics = orientation_error_metrics(result["orientation"], truth, mask)
    assert metrics["mae_deg"] < 2.5


def test_coherence_is_bounded():
    image, _ = synthetic_parallel_fibers()
    result = structure_tensor_orientation(image)
    assert np.all(result["coherence"] >= 0.0)
    assert np.all(result["coherence"] <= 1.0)


def test_larger_integration_scale_reduces_noisy_parallel_error():
    image, truth = synthetic_parallel_fibers(angle_degrees=-27.0, noise_std=0.12, seed=7)
    small = structure_tensor_orientation(image, StructureTensorParameters(1.0, 1.0))
    large = structure_tensor_orientation(image, StructureTensorParameters(1.0, 5.0))
    mask = np.zeros(image.shape, dtype=bool)
    mask[12:-12, 12:-12] = True
    small_error = orientation_error_metrics(small["orientation"], truth, mask)["mae_deg"]
    large_error = orientation_error_metrics(large["orientation"], truth, mask)["mae_deg"]
    assert large_error < small_error


def test_crossing_pattern_has_no_single_angle_ground_truth():
    image, directions = synthetic_crossing_fibers()
    result = structure_tensor_orientation(image, StructureTensorParameters(1.0, 4.0))
    assert image.shape == result["orientation"].shape
    assert len(directions) == 2
    assert not np.isclose(directions[0], directions[1])


def test_weighted_axial_mean_recovers_equivalent_directions():
    angles = np.deg2rad([5.0, 185.0, 6.0, -174.0])
    mean, order = weighted_axial_mean(angles)
    assert abs(np.rad2deg(axial_angle_difference(mean, np.deg2rad(5.5)))) < 0.6
    assert order > 0.99


def test_metrics_report_zero_error_for_exact_field():
    truth = np.full((5, 5), np.deg2rad(15.0))
    metrics = orientation_error_metrics(truth, truth)
    assert metrics["mae_deg"] == pytest.approx(0.0)
    assert metrics["coverage"] == pytest.approx(1.0)


def test_invalid_parameters_are_rejected():
    with pytest.raises(ValueError):
        StructureTensorParameters(0.0, 2.0).validate()
    with pytest.raises(ValueError):
        StructureTensorParameters(1.0, -1.0).validate()
