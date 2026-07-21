import numpy as np

from biomechanics_tutorials.finite_element_growth import (
    Material,
    create_rectangular_tri_mesh,
    initial_growth_state,
    run_scenarios,
    solve_equilibrium,
    triangle_B_matrix,
)


def test_mesh_counts_and_triangle_area():
    mesh = create_rectangular_tri_mesh(nx=4, ny=3)
    assert mesh.n_nodes == 20
    assert mesh.n_elements == 24
    B, area = triangle_B_matrix(mesh.nodes[mesh.elements[0]])
    assert B.shape == (3, 6)
    assert area > 0


def test_equilibrium_residual_is_small():
    mesh = create_rectangular_tri_mesh(nx=6, ny=4)
    state = initial_growth_state(mesh, seed=21)
    result = solve_equilibrium(mesh, Material(), state)
    assert result.displacement.shape == (mesh.n_nodes, 2)
    assert result.stress.shape == (mesh.n_elements, 3)
    assert result.residual_norm < 1e-9
    assert np.isfinite(result.energy_density).all()


def test_growth_scenarios_are_distinct_and_finite():
    scenarios = run_scenarios()
    names = {scenario.name for scenario in scenarios}
    assert names == {"frozen_growth", "stress_feedback", "fiber_only_feedback"}
    finals = {scenario.name: scenario.history.metrics[-1] for scenario in scenarios}
    assert finals["stress_feedback"]["residual_norm"] < 1e-9
    assert finals["frozen_growth"]["mean_isotropic_growth"] != finals["stress_feedback"]["mean_isotropic_growth"]
    assert np.isfinite(finals["fiber_only_feedback"]["final_mean_energy_density"] if "final_mean_energy_density" in finals["fiber_only_feedback"] else finals["fiber_only_feedback"]["mean_energy_density"])
