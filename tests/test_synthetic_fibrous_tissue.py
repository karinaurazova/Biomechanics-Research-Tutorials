"""Tests for Tutorial 13 synthetic fibrous-tissue generators."""

from __future__ import annotations

import numpy as np

from biomechanics_tutorials.synthetic_fibrous_tissue import (
    add_branches,
    apply_defects,
    axial_difference,
    axial_mean,
    axial_order_parameter,
    export_network_dataset,
    generate_crossing_families,
    generate_fiber_volume,
    generate_layered_network,
    generate_mikado_network,
    generate_parallel_bundle,
    generate_spatial_gradient_network,
    generate_voronoi_network,
    morphological_skeleton,
    network_metrics,
    rasterize_network,
    read_dataset_metadata,
    sample_axial_von_mises,
    skeleton_graph_metrics,
    tissue_preset,
)


def test_axial_difference_respects_pi_periodicity() -> None:
    difference = axial_difference(np.deg2rad(89.0), np.deg2rad(-89.0))
    assert abs(np.rad2deg(difference)) < 3.0


def test_axial_moments_for_aligned_and_orthogonal_samples() -> None:
    aligned = np.zeros(20)
    orthogonal = np.tile([0.0, np.pi / 2.0], 10)
    assert abs(axial_mean(aligned)) < 1e-12
    assert axial_order_parameter(aligned) > 0.999
    assert axial_order_parameter(orthogonal) < 1e-12


def test_von_mises_sampling_is_reproducible() -> None:
    first = sample_axial_von_mises(0.3, 8.0, 100, np.random.default_rng(42))
    second = sample_axial_von_mises(0.3, 8.0, 100, np.random.default_rng(42))
    assert np.allclose(first, second)


def test_mikado_generation_is_reproducible() -> None:
    first = generate_mikado_network(12, seed=7)
    second = generate_mikado_network(12, seed=7)
    assert len(first.fibers) == len(second.fibers)
    assert np.allclose(first.fibers[3].points, second.fibers[3].points)


def test_parallel_bundle_has_high_order_parameter() -> None:
    network = generate_parallel_bundle(20, angle=0.4, waviness=0.0, seed=2)
    raster = rasterize_network(network, (128, 128))
    metrics = network_metrics(network, raster)
    assert metrics["order_parameter"] > 0.97
    assert abs(axial_difference(metrics["mean_orientation_rad"], 0.4)) < 0.05


def test_crossing_families_have_labels_and_reduced_coherence() -> None:
    network = generate_crossing_families(n_per_family=12, seed=3)
    raster = rasterize_network(network, (128, 128))
    labels = set(np.unique(raster.family[raster.family >= 0]))
    assert labels == {0, 1}
    assert np.nanmin(raster.coherence[raster.mask]) < 0.8


def test_raster_ground_truth_shapes_and_ranges() -> None:
    network = generate_mikado_network(15, seed=4)
    raster = rasterize_network(network, (96, 120), noise_std=0.02)
    assert raster.image.shape == (96, 120)
    assert raster.mask.dtype == bool
    assert np.all((raster.image >= 0.0) & (raster.image <= 1.0))
    assert np.nanmin(raster.coherence) >= 0.0
    assert np.nanmax(raster.coherence) <= 1.0 + 1e-12


def test_thicker_fibers_reduce_porosity() -> None:
    thin = generate_mikado_network(35, radius=0.003, seed=8)
    thick = generate_mikado_network(35, radius=0.012, seed=8)
    thin_raster = rasterize_network(thin, (160, 160))
    thick_raster = rasterize_network(thick, (160, 160))
    assert np.mean(thick_raster.mask) > np.mean(thin_raster.mask)


def test_skeleton_is_subset_of_mask_and_has_metrics() -> None:
    raster = rasterize_network(generate_parallel_bundle(12, seed=5), (128, 128))
    skeleton = morphological_skeleton(raster.mask)
    metrics = skeleton_graph_metrics(skeleton)
    assert np.all(~skeleton | raster.mask)
    assert metrics["skeleton_pixels"] > 0
    assert metrics["components"] >= 1


def test_branches_increase_fiber_count() -> None:
    base = generate_parallel_bundle(20, seed=6)
    branched = add_branches(base, branch_probability=1.0, seed=7)
    assert len(branched.fibers) > len(base.fibers)


def test_defects_remove_or_split_fibers() -> None:
    base = generate_parallel_bundle(30, seed=6)
    defective = apply_defects(base, deletion_fraction=0.4, gap_probability=0.0, seed=1)
    assert len(defective.fibers) < len(base.fibers)


def test_layered_network_contains_all_families() -> None:
    network = generate_layered_network((-0.5, 0.0, 0.5), fibers_per_layer=8, seed=4)
    assert {fiber.family for fiber in network.fibers} == {0, 1, 2}


def test_gradient_network_changes_orientation_across_image() -> None:
    network = generate_spatial_gradient_network(40, seed=9)
    raster = rasterize_network(network, (160, 160))
    left = raster.orientation[:, :50]
    right = raster.orientation[:, -50:]
    left_value = axial_mean(left[np.isfinite(left)])
    right_value = axial_mean(right[np.isfinite(right)])
    assert abs(axial_difference(left_value, right_value)) > 0.3


def test_voronoi_network_has_finite_segments() -> None:
    network = generate_voronoi_network(30, seed=11)
    assert len(network.fibers) > 10
    assert all(np.all(np.isfinite(fiber.points)) for fiber in network.fibers)


def test_3d_volume_contains_orientation_ground_truth() -> None:
    result = generate_fiber_volume((24, 32, 32), n_fibers=8, seed=12)
    assert result.volume.shape == (24, 32, 32)
    assert result.orientation.shape == (24, 32, 32, 3)
    occupied = result.volume
    norms = np.linalg.norm(result.orientation[occupied], axis=1)
    assert np.allclose(norms, 1.0, atol=1e-6)


def test_preset_catalog_returns_nonempty_networks() -> None:
    for name in ["tendon", "skin", "artery", "myocardium", "valve", "lung", "scaffold"]:
        assert len(tissue_preset(name, seed=1).fibers) > 0


def test_exported_dataset_preserves_provenance(tmp_path) -> None:
    network = generate_mikado_network(10, seed=22)
    raster = rasterize_network(network, (64, 64))
    path = tmp_path / "dataset.npz"
    export_network_dataset(path, network, raster)
    metadata = read_dataset_metadata(path)
    assert metadata["synthetic"] is True
    assert metadata["experimental_validation"] is False
    assert metadata["seed"] == 22
