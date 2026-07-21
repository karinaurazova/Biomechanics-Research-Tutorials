import numpy as np

from biomechanics_tutorials.physics_informed_learning import (
    evaluate_prediction,
    fit_physics_informed_model,
    generate_bar_dataset,
    inverse_stiffness_scale_sweep,
    run_case_suite,
    run_weight_sweep,
    stiffness_from_structure,
)


def test_dataset_has_positive_stiffness_and_observations():
    data = generate_bar_dataset(n_grid=81, n_observations=9)
    assert np.all(data.stiffness_true > 0)
    assert np.all(data.stiffness_image > 0)
    assert len(data.obs_x) == 9
    assert data.displacement_true[0] == 0


def test_stiffness_from_structure_increases_with_fiber_fraction():
    theta = np.zeros(5)
    kappa = np.ones(5) * 0.5
    conn = np.ones(5)
    low = stiffness_from_structure(theta, np.ones(5)*0.1, kappa, conn)
    high = stiffness_from_structure(theta, np.ones(5)*0.7, kappa, conn)
    assert np.all(high > low)


def test_physics_model_returns_finite_metrics():
    data = generate_bar_dataset(n_grid=101, n_observations=12)
    pred = fit_physics_informed_model(data, n_features=32, lambda_pde=1.0)
    metrics = evaluate_prediction(data, pred)
    assert metrics['u_mae'] < 0.05
    assert np.isfinite(metrics['pde_residual_rms'])


def test_case_suite_contains_expected_cases():
    data = generate_bar_dataset(n_grid=101, n_observations=12)
    cases = run_case_suite(data)
    assert set(cases) == {'data_only', 'physics_only', 'data_plus_physics_image_E', 'oracle_physics_true_E'}


def test_weight_sweep_and_inverse_sweep_have_rows():
    data = generate_bar_dataset(n_grid=81, n_observations=10)
    sweep = run_weight_sweep(data, lambdas=np.array([1e-2, 1.0, 1e2]))
    inv = inverse_stiffness_scale_sweep(data, alpha_values=np.array([0.8, 1.0, 1.2]))
    assert len(sweep) == 3
    assert len(inv) == 3
    assert all('objective' in row for row in inv)
