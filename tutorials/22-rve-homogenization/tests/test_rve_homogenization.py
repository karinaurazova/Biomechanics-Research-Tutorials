from __future__ import annotations

import numpy as np

from biomechanics_tutorials.rve_homogenization import (
    affine_displacement,
    create_periodic_tri_mesh,
    generate_microstructure,
    homogenize_rve,
    periodic_reduction_matrix,
    plane_stress_isotropic,
)


def test_periodic_mesh_and_reduction_matrix_have_expected_sizes():
    mesh = create_periodic_tri_mesh(nx=4, ny=3)
    assert mesh.n_nodes == 20
    assert mesh.n_elements == 24
    P, mapping = periodic_reduction_matrix(mesh)
    assert P.shape[0] == mesh.n_dofs
    assert P.shape[1] == 2 * mesh.nx * mesh.ny - 2
    assert len(mapping) == P.shape[1]


def test_affine_displacement_produces_expected_engineering_shear():
    mesh = create_periodic_tri_mesh(nx=2, ny=2, length=1.0, height=1.0)
    u = affine_displacement(mesh, np.array([0.0, 0.0, 1.0]))
    top_right = np.argmax(mesh.nodes[:, 0] + mesh.nodes[:, 1])
    assert np.isclose(u[top_right, 0], 0.5)
    assert np.isclose(u[top_right, 1], 0.5)


def test_microstructure_fields_are_finite_and_bounded():
    micro = generate_microstructure(nx=8, ny=7, seed=22)
    assert micro.theta.shape == (7, 8)
    assert np.all((micro.rho_f >= 0.0) & (micro.rho_f <= 1.0))
    assert np.all((micro.pore >= 0.0) & (micro.pore <= 1.0))
    assert np.all((micro.connectivity >= 0.0) & (micro.connectivity <= 1.0))


def test_plane_stress_matrix_is_positive_definite():
    C = plane_stress_isotropic(10.0, 0.3)
    assert np.all(np.linalg.eigvalsh(C) > 0.0)


def test_periodic_homogenization_is_symmetric_and_consistent():
    result = homogenize_rve(nx=6, ny=6, seed=22)
    C = result.periodic_stiffness
    assert C.shape == (3, 3)
    assert np.allclose(C, C.T, atol=1e-7)
    assert np.all(np.linalg.eigvalsh(C) > 0.0)
    assert result.metrics["max_hill_mandel_error"] < 1e-8
    assert result.metrics["max_reduced_residual_norm"] < 1e-7


def test_periodic_stiffness_lies_between_trace_bounds():
    result = homogenize_rve(nx=6, ny=6, seed=23)
    tr_reuss = np.trace(result.reuss_stiffness)
    tr_periodic = np.trace(result.periodic_stiffness)
    tr_voigt = np.trace(result.voigt_stiffness)
    assert tr_reuss <= tr_periodic <= tr_voigt
