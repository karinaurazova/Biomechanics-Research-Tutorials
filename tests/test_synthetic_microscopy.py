"""Tests for Tutorial 14 synthetic microscopy generators."""

from __future__ import annotations

import numpy as np

from biomechanics_tutorials.synthetic_microscopy import (
    ArtifactParameters,
    OpticalParameters,
    SEMParameters,
    apply_artifacts,
    export_multimodal_dataset,
    focus_series,
    gaussian_psf_blur,
    global_ssim,
    height_from_mask,
    normalize01,
    poisson_gaussian_noise,
    psnr,
    read_multimodal_metadata,
    resample_stack,
    simulate_brightfield,
    simulate_confocal_stack,
    simulate_fib_sem_stack,
    simulate_fluorescence,
    simulate_sem,
    simulate_shg,
)


def synthetic_disc(shape=(64, 64)):
    yy, xx = np.indices(shape)
    return ((xx - shape[1] / 2) ** 2 + (yy - shape[0] / 2) ** 2 < 14**2).astype(float)


def test_normalize_has_expected_range() -> None:
    result = normalize01(np.array([-2.0, 0.0, 2.0]))
    assert np.allclose(result, [0.0, 0.5, 1.0])


def test_gaussian_blur_preserves_constant_field() -> None:
    image = np.ones((32, 32))
    assert np.allclose(gaussian_psf_blur(image, 2.0), image)


def test_poisson_noise_is_seed_reproducible() -> None:
    image = np.full((16, 16), 0.4)
    first = poisson_gaussian_noise(image, seed=4)
    second = poisson_gaussian_noise(image, seed=4)
    assert np.allclose(first, second)


def test_fluorescence_output_shape_and_provenance() -> None:
    result = simulate_fluorescence(synthetic_disc(), seed=2)
    assert result.image.shape == (64, 64)
    assert result.metadata["synthetic"] is True
    assert result.metadata["modality"] == "widefield-fluorescence-like"


def test_more_blur_reduces_gradient_energy() -> None:
    signal = synthetic_disc()
    sharp = simulate_fluorescence(signal, OpticalParameters(sigma_xy=0.5), seed=1).expectation
    blurred = simulate_fluorescence(signal, OpticalParameters(sigma_xy=3.0), seed=1).expectation
    sharp_energy = np.mean(np.hypot(*np.gradient(sharp)))
    blur_energy = np.mean(np.hypot(*np.gradient(blurred)))
    assert blur_energy < sharp_energy


def test_brightfield_absorption_darkens_structure() -> None:
    result = simulate_brightfield(synthetic_disc(), absorption=3.0, noise_std=0.0)
    center = result.expectation[32, 32]
    corner = result.expectation[0, 0]
    assert center < corner


def test_confocal_stack_shape_and_finite_values() -> None:
    volume = np.zeros((12, 32, 32))
    volume[6, 12:20, 12:20] = 1.0
    result = simulate_confocal_stack(volume, seed=3)
    assert result.image.shape == volume.shape
    assert np.all(np.isfinite(result.image))


def test_shg_changes_with_polarization() -> None:
    amplitude = synthetic_disc()
    orientation = np.zeros_like(amplitude)
    parallel = simulate_shg(amplitude, orientation, polarization_angle=0.0, seed=5).expectation
    perpendicular = simulate_shg(
        amplitude, orientation, polarization_angle=np.pi / 2.0, seed=5
    ).expectation
    assert np.mean(parallel[amplitude > 0]) > np.mean(perpendicular[amplitude > 0])


def test_height_map_is_bounded() -> None:
    height = height_from_mask(synthetic_disc() > 0)
    assert np.min(height) >= 0.0
    assert np.max(height) <= 1.0 + 1e-12


def test_sem_detector_direction_changes_image() -> None:
    height = height_from_mask(synthetic_disc() > 0)
    first = simulate_sem(height, parameters=SEMParameters(detector_azimuth_deg=0.0), seed=1)
    second = simulate_sem(height, parameters=SEMParameters(detector_azimuth_deg=180.0), seed=1)
    assert np.mean(np.abs(first.expectation - second.expectation)) > 0.01


def test_sem_artifact_pipeline_remains_bounded() -> None:
    height = height_from_mask(synthetic_disc() > 0)
    result = simulate_sem(
        height,
        artifacts=ArtifactParameters(vignette_strength=0.4, stripe_strength=0.1),
        seed=2,
    )
    assert np.min(result.image) >= 0.0
    assert np.max(result.image) <= 1.0 + 1e-12


def test_fib_sem_stack_is_reproducible() -> None:
    volume = np.zeros((8, 24, 24))
    volume[:, 8:16, 9:15] = 1.0
    first = simulate_fib_sem_stack(volume, drift_per_slice=(0.1, 0.2), seed=7)
    second = simulate_fib_sem_stack(volume, drift_per_slice=(0.1, 0.2), seed=7)
    assert np.allclose(first.image, second.image)


def test_resampling_changes_shape_by_spacing_ratio() -> None:
    volume = np.zeros((10, 12, 14))
    resampled = resample_stack(volume, (2.0, 1.0, 1.0), (1.0, 1.0, 1.0))
    assert resampled.shape[0] == 20
    assert resampled.shape[1:] == (12, 14)


def test_focus_series_contains_requested_frames() -> None:
    series = focus_series(synthetic_disc(), [0.0, 1.0, 2.0])
    assert series.shape == (3, 64, 64)
    assert np.mean(np.hypot(*np.gradient(series[-1]))) < np.mean(np.hypot(*np.gradient(series[0])))


def test_image_quality_metrics_for_identical_images() -> None:
    image = synthetic_disc()
    assert np.isinf(psnr(image, image))
    assert abs(global_ssim(image, image) - 1.0) < 1e-12


def test_artifacts_are_seed_reproducible() -> None:
    image = synthetic_disc()
    parameters = ArtifactParameters(dead_pixel_fraction=0.05, line_jitter=0.3)
    assert np.allclose(
        apply_artifacts(image, parameters, seed=4),
        apply_artifacts(image, parameters, seed=4),
    )


def test_dataset_export_preserves_synthetic_provenance(tmp_path) -> None:
    path = export_multimodal_dataset(
        tmp_path / "sample.npz",
        ground_truth={"mask": synthetic_disc() > 0},
        modalities={"fluorescence": synthetic_disc()},
        metadata={"seed": 12},
    )
    metadata = read_multimodal_metadata(path)
    assert metadata["synthetic"] is True
    assert metadata["experimental_validation"] is False
    assert metadata["seed"] == 12
