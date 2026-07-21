"""Tests for Tutorial 16 synthetic digital image correlation."""

from __future__ import annotations

import numpy as np

from biomechanics_tutorials.digital_image_correlation import (
    DICParameters,
    SpeckleParameters,
    correlation_surface,
    dic_metrics,
    displacement_field,
    estimate_subset_displacement,
    export_dic_dataset,
    forward_backward_error,
    generate_natural_texture,
    generate_speckle_pattern,
    principal_strains_2d,
    quadratic_subpixel_peak,
    read_dic_metadata,
    refine_affine_subset,
    run_subset_dic,
    sample_truth_on_dic_grid,
    strain_fields,
    virtual_extensometer,
    warp_image,
    zncc,
    znssd,
)


def test_speckle_pattern_is_reproducible() -> None:
    params = SpeckleParameters(seed=7)
    first = generate_speckle_pattern((64, 72), params)
    second = generate_speckle_pattern((64, 72), params)
    assert np.allclose(first, second)


def test_speckle_pattern_is_bounded_and_textured() -> None:
    image = generate_speckle_pattern((64, 64), SpeckleParameters(seed=2))
    assert np.min(image) >= 0.0
    assert np.max(image) <= 1.0
    assert np.std(image) > 0.08


def test_natural_texture_is_bounded() -> None:
    image = generate_natural_texture((48, 50), seed=3)
    assert image.shape == (48, 50)
    assert np.min(image) >= 0.0
    assert np.max(image) <= 1.0


def test_translation_field_is_constant() -> None:
    u, v = displacement_field((20, 30), "translation", amplitude=4.0)
    assert np.allclose(u, 4.0)
    assert np.allclose(v, -2.2)


def test_warp_identity_returns_reference() -> None:
    reference = generate_speckle_pattern((48, 48), SpeckleParameters(seed=4))
    zeros = np.zeros_like(reference)
    deformed = warp_image(reference, zeros, zeros, interpolation_order=3)
    assert np.allclose(reference, deformed, atol=2e-5)


def test_zncc_identical_is_one() -> None:
    rng = np.random.default_rng(4)
    patch = rng.normal(size=(15, 15))
    assert np.isclose(zncc(patch, patch), 1.0)
    assert np.isclose(znssd(patch, patch), 0.0)


def test_correlation_surface_finds_integer_translation() -> None:
    reference = generate_speckle_pattern((96, 96), SpeckleParameters(seed=8))
    u = np.full_like(reference, 3.0)
    v = np.full_like(reference, -2.0)
    deformed = warp_image(reference, u, v, interpolation_order=1)
    scores, shifts_u, shifts_v = correlation_surface(reference, deformed, 48, 48, 10, 5)
    iy, ix = np.unravel_index(np.nanargmax(scores), scores.shape)
    assert shifts_u[ix] == 3
    assert shifts_v[iy] == -2


def test_subpixel_peak_refinement() -> None:
    # Samples of -(x-0.25)^2 at x=-1,0,1.
    values = [-(x - 0.25) ** 2 for x in (-1.0, 0.0, 1.0)]
    assert np.isclose(quadratic_subpixel_peak(*values), 0.25)


def test_subset_estimate_recovers_fractional_translation() -> None:
    reference = generate_speckle_pattern((112, 112), SpeckleParameters(seed=12))
    u = np.full_like(reference, 2.4)
    v = np.full_like(reference, -1.6)
    deformed = warp_image(reference, u, v, interpolation_order=3)
    estimate_u, estimate_v, score = estimate_subset_displacement(
        reference, deformed, 56, 56, subset_radius=13, search_radius=5, subpixel=True
    )
    assert abs(estimate_u - 2.4) < 0.18
    assert abs(estimate_v + 1.6) < 0.18
    assert score > 0.9


def test_affine_refinement_recovers_small_strain() -> None:
    reference = generate_speckle_pattern((100, 100), SpeckleParameters(seed=21))
    yy, xx = np.indices(reference.shape, dtype=float)
    u = 0.018 * (xx - 50.0) + 1.2
    v = -0.011 * (yy - 50.0) - 0.8
    deformed = warp_image(reference, u, v, interpolation_order=3)
    parameters, score = refine_affine_subset(reference, deformed, 50, 50, 1.2, -0.8, 15)
    assert abs(parameters[0] - 1.2) < 0.12
    assert abs(parameters[1] + 0.8) < 0.12
    assert abs(parameters[2] - 0.018) < 0.01
    assert abs(parameters[5] + 0.011) < 0.01
    assert score > 0.95


def test_grid_dic_recovers_uniform_translation() -> None:
    reference = generate_speckle_pattern((120, 128), SpeckleParameters(seed=10))
    u = np.full_like(reference, 2.75)
    v = np.full_like(reference, 1.35)
    deformed = warp_image(reference, u, v, interpolation_order=3)
    result = run_subset_dic(
        reference,
        deformed,
        DICParameters(subset_radius=11, step=20, search_radius=5),
        correlation_threshold=0.7,
    )
    assert np.nanmedian(np.abs(result.u - 2.75)) < 0.18
    assert np.nanmedian(np.abs(result.v - 1.35)) < 0.18
    assert np.mean(result.valid) > 0.95


def test_strain_fields_for_affine_displacement() -> None:
    yy, xx = np.indices((60, 70), dtype=float)
    u = 0.04 * xx + 0.02 * yy
    v = -0.01 * xx + 0.03 * yy
    strain = strain_fields(u, v)
    assert np.allclose(np.median(strain.small_exx), 0.04)
    assert np.allclose(np.median(strain.small_eyy), 0.03)
    assert np.allclose(np.median(strain.small_exy), 0.005)
    expected_j = (1.04 * 1.03) - (0.02 * -0.01)
    assert np.allclose(np.median(strain.jacobian), expected_j)


def test_green_strain_differs_from_small_strain_at_large_deformation() -> None:
    yy, xx = np.indices((30, 30), dtype=float)
    u = 0.20 * xx
    v = np.zeros_like(u)
    strain = strain_fields(u, v)
    assert np.median(strain.green_exx) > np.median(strain.small_exx)


def test_principal_strains_for_diagonal_tensor() -> None:
    maximum, minimum, angle = principal_strains_2d(0.10, -0.02, 0.0)
    assert np.isclose(maximum, 0.10)
    assert np.isclose(minimum, -0.02)
    assert np.isclose(angle, 0.0)


def test_virtual_extensometer_matches_uniaxial_field() -> None:
    yy, xx = np.indices((80, 80), dtype=float)
    u = 0.05 * xx
    v = np.zeros_like(u)
    value = virtual_extensometer(u, v, (10.0, 40.0), (70.0, 40.0))
    assert np.isclose(value, 0.05)


def test_metrics_zero_for_exact_fields() -> None:
    field = np.ones((4, 5))
    metrics = dic_metrics(field, field * 2.0, field, field * 2.0)
    assert metrics["vector_rmse"] == 0.0
    assert metrics["coverage"] == 1.0


def test_forward_backward_zero_for_opposite_fields() -> None:
    image = generate_speckle_pattern((96, 96), SpeckleParameters(seed=16))
    u = np.full_like(image, 2.0)
    v = np.full_like(image, -1.0)
    deformed = warp_image(image, u, v)
    params = DICParameters(subset_radius=9, step=18, search_radius=4)
    forward = run_subset_dic(image, deformed, params, correlation_threshold=0.6)
    backward = run_subset_dic(deformed, image, params, correlation_threshold=0.6)
    error = forward_backward_error(forward, backward)
    assert np.nanmedian(error) < 0.3


def test_truth_sampling_matches_constant_field() -> None:
    image = generate_speckle_pattern((80, 80), SpeckleParameters(seed=17))
    u = np.full_like(image, 1.5)
    v = np.full_like(image, -0.4)
    result = run_subset_dic(
        image,
        warp_image(image, u, v),
        DICParameters(subset_radius=8, step=16, search_radius=3),
    )
    assert np.allclose(sample_truth_on_dic_grid(u, result), 1.5)


def test_dataset_export_preserves_synthetic_provenance(tmp_path) -> None:
    reference = generate_speckle_pattern((32, 32), SpeckleParameters(seed=1))
    u, v = displacement_field(reference.shape, "translation", 1.0)
    deformed = warp_image(reference, u, v)
    path = export_dic_dataset(tmp_path / "sample.npz", reference, deformed, u, v, {"seed": 1})
    metadata = read_dic_metadata(path)
    assert metadata["synthetic"] is True
    assert metadata["experimental_validation"] is False
    assert metadata["seed"] == 1


def test_invalid_parameter_values_raise() -> None:
    try:
        DICParameters(subset_radius=1)
    except ValueError:
        return
    raise AssertionError("invalid subset radius must raise")
