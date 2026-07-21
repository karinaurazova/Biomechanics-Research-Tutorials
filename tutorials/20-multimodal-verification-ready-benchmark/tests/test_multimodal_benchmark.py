"""Tests for Tutorial 20 multimodal benchmark."""
from __future__ import annotations
import numpy as np
from biomechanics_tutorials.multimodal_benchmark import (
    PARAMETER_NAMES, binary_metrics, generate_ground_truth_microstructure,
    render_modalities, run_full_benchmark, stress_from_parameters,
)

def test_ground_truth_contains_expected_fields() -> None:
    truth = generate_ground_truth_microstructure(shape=(64, 72), seed=1)
    assert truth.fiber_mask.shape == (64, 72)
    assert truth.tissue_mask.dtype == bool
    assert truth.fiber_mask.sum() > 0
    assert truth.pore_mask.sum() > 0
    assert truth.parameters.shape == (len(PARAMETER_NAMES),)
    assert np.all((truth.theta >= 0.0) & (truth.theta < np.pi))

def test_modalities_are_bounded_and_same_shape() -> None:
    truth = generate_ground_truth_microstructure(shape=(64, 72), seed=2)
    modalities = render_modalities(truth, seed=3)
    for image in [modalities.sem_like, modalities.polarization_intensity, modalities.fluorescence_like, modalities.dic_reference]:
        assert image.shape == truth.shape
        assert np.nanmin(image) >= -1.0e-10
        assert np.nanmax(image) <= 1.0 + 1.0e-10

def test_segmentation_metrics_for_truth_are_perfect() -> None:
    truth = generate_ground_truth_microstructure(shape=(64, 72), seed=4)
    metrics = binary_metrics(truth.fiber_mask, truth.fiber_mask)
    assert metrics['dice'] == 1.0
    assert metrics['iou'] == 1.0
    assert metrics['precision'] == 1.0
    assert metrics['recall'] == 1.0

def test_stress_model_is_linear_in_parameters() -> None:
    truth = generate_ground_truth_microstructure(shape=(64, 72), seed=5)
    exx = np.full(truth.shape, 0.01) * truth.tissue_mask
    eyy = np.full(truth.shape, -0.002) * truth.tissue_mask
    gxy = np.full(truth.shape, 0.003) * truth.tissue_mask
    p = truth.parameters
    s1 = stress_from_parameters(exx, eyy, gxy, truth.theta, truth.rho_f, truth.connectivity, truth.tissue_mask, p)
    s2 = stress_from_parameters(exx, eyy, gxy, truth.theta, truth.rho_f, truth.connectivity, truth.tissue_mask, 2.0 * p)
    assert np.max(np.abs(s2 - 2.0 * s1)) < 1.0e-10

def test_full_benchmark_runs_and_reports_expected_scenarios() -> None:
    result = run_full_benchmark(seed=6, shape=(64, 72), force_noise=0.0, dic_noise=0.0)
    scenarios = {str(row['scenario']) for row in result.parameter_results}
    assert {'oracle_ground_truth', 'sem_only', 'polarization_only', 'multimodal_fusion'} <= scenarios
    assert len(result.segmentation_metrics) >= 5
    assert len(result.orientation_metrics) >= 4
    assert len(result.error_budget) == 3

def test_oracle_parameter_recovery_is_accurate_without_noise() -> None:
    result = run_full_benchmark(seed=7, shape=(72, 80), force_noise=0.0, dic_noise=0.0)
    oracle = next(row for row in result.parameter_results if row['scenario'] == 'oracle_ground_truth')
    assert float(oracle['relative_parameter_error']) < 1.0e-8
