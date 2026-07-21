import numpy as np

from biomechanics_tutorials.surrogate_modeling import (
    bootstrap_ensemble,
    ensemble_predict,
    fit_ridge_surrogate,
    generate_surrogate_dataset,
    predict,
    regression_metrics,
    structural_to_stiffness,
    train_test_split,
)


def test_dataset_shapes():
    d = generate_surrogate_dataset(120, seed=1, noise_level=0.0)
    assert d.features.shape == (120, 8)
    assert d.targets.shape == (120, 9)


def test_fiber_fraction_increases_c11_for_zero_angle():
    x_low = np.array([[0.0, 5.0, 0.2, 0.08, 0.8]])
    x_high = np.array([[0.0, 5.0, 0.7, 0.08, 0.8]])
    assert structural_to_stiffness(x_high)[0, 0] > structural_to_stiffness(x_low)[0, 0]


def test_quadratic_surrogate_is_reasonably_accurate():
    d = generate_surrogate_dataset(260, seed=3, noise_level=0.0)
    tr, te = train_test_split(d.features.shape[0], seed=4)
    model = fit_ridge_surrogate(d.features[tr], d.targets[tr], basis='quadratic')
    m = regression_metrics(d.targets[te], predict(model, d.features[te]))
    assert m['r2'] > 0.92


def test_bootstrap_ensemble_shapes():
    d = generate_surrogate_dataset(160, seed=5, noise_level=0.0)
    models = bootstrap_ensemble(d.features, d.targets, n_models=5, seed=2)
    mean, sd = ensemble_predict(models, d.features[:10])
    assert mean.shape == (10, 9)
    assert sd.shape == (10, 9)
    assert np.all(sd >= 0)
