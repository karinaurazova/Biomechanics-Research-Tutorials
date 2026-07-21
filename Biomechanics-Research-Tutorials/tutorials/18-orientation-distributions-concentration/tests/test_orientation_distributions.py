"""Tests for Tutorial 18 orientation distributions."""

from __future__ import annotations

import numpy as np
import pytest

from biomechanics_tutorials.orientation_distributions import (
    axial_difference,
    axial_mean_resultant,
    benchmark_modalities,
    build_synthetic_orientation_dataset,
    histogram_odf,
    jensen_shannon_divergence,
    kappa_from_resultant,
    orientation_statistics,
    orientation_tensor,
)


def test_axial_difference_identifies_opposite_directions() -> None:
    diff = axial_difference(np.array([0.0]), np.pi)
    assert abs(float(diff[0])) < 1.0e-12


def test_aligned_distribution_has_high_resultant_and_kappa() -> None:
    angles = np.full(50, np.deg2rad(35.0))
    mean, resultant = axial_mean_resultant(angles)
    assert np.rad2deg(mean) == pytest.approx(35.0)
    assert resultant == pytest.approx(1.0)
    assert kappa_from_resultant(resultant) > 1.0e3


def test_uniform_axial_distribution_has_low_concentration() -> None:
    angles = np.linspace(0.0, np.pi, 360, endpoint=False)
    stats = orientation_statistics(angles)
    assert stats.resultant_length < 1.0e-12
    assert stats.tensor_anisotropy < 1.0e-12
    assert stats.entropy > 0.98


def test_orientation_tensor_trace_is_one() -> None:
    angles = np.deg2rad(np.array([0.0, 30.0, 90.0]))
    tensor = orientation_tensor(angles)
    assert np.trace(tensor) == pytest.approx(1.0)


def test_histogram_odf_integrates_to_one() -> None:
    angles = np.linspace(0.0, np.pi, 100, endpoint=False)
    centers, density = histogram_odf(angles, n_bins=20)
    spacing = centers[1] - centers[0]
    assert np.sum(density) * spacing == pytest.approx(1.0, rel=1.0e-12)


def test_js_divergence_is_zero_for_same_distribution() -> None:
    p = np.array([0.2, 0.3, 0.5])
    assert jensen_shannon_divergence(p, p) == pytest.approx(0.0)


def test_synthetic_dataset_contains_all_modalities() -> None:
    dataset = build_synthetic_orientation_dataset(shape=(96, 96), seed=4)
    assert dataset.mask.shape == (96, 96)
    assert dataset.sem_like_image.shape == dataset.mask.shape
    assert np.any(dataset.segmented_mask)
    assert np.nanmax(dataset.polarization_orientation) <= np.pi


def test_benchmark_modalities_reports_ground_truth_and_errors() -> None:
    dataset = build_synthetic_orientation_dataset(shape=(96, 96), seed=5)
    results, centers, densities = benchmark_modalities(dataset, n_bins=18)
    assert set(results) == {
        "ground_truth",
        "sem_like_gradient",
        "polarization_like_map",
        "segmented_mask",
    }
    assert len(centers) == 18
    assert densities["ground_truth"].shape == centers.shape
    assert results["ground_truth"]["js_to_ground_truth"] == pytest.approx(0.0)
    assert abs(results["polarization_like_map"]["stiffness_error_percent"]) < 70.0
