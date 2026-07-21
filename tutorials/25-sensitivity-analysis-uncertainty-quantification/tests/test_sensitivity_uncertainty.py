from __future__ import annotations

import numpy as np

from biomechanics_tutorials.sensitivity_uncertainty import (
    PARAMETERS,
    evaluate_tissue_model,
    likelihood_update,
    monte_carlo,
    morris_screening,
    nominal_parameter_vector,
    sample_parameters,
    sobol_pick_freeze,
    tornado_analysis,
    unit_cube_to_parameters,
)


def test_unit_cube_mapping_bounds():
    x0 = unit_cube_to_parameters(np.zeros(len(PARAMETERS)))
    x1 = unit_cube_to_parameters(np.ones(len(PARAMETERS)))
    assert np.allclose(x0, [p.lower for p in PARAMETERS])
    assert np.allclose(x1, [p.upper for p in PARAMETERS])


def test_forward_model_positive_outputs():
    out = evaluate_tissue_model(nominal_parameter_vector())
    assert out["C11"] > 0
    assert out["C22"] > 0
    assert out["peak_stress"] > 0
    assert out["strain_energy"] > 0


def test_monte_carlo_shapes_and_summary():
    samples, outputs, summary = monte_carlo(n=256, seed=10)
    assert samples.shape == (256, len(PARAMETERS))
    assert outputs["peak_stress"].shape == (256,)
    assert summary["peak_stress"]["q95"] > summary["peak_stress"]["q05"]


def test_sobol_and_morris_return_all_parameters():
    sob = sobol_pick_freeze(n=128, seed=11)
    mor = morris_screening(r=5, seed=12)
    assert set(sob) == {p.name for p in PARAMETERS}
    assert set(mor) == {p.name for p in PARAMETERS}
    assert all(v["ST"] >= 0 for v in sob.values())
    assert all(v["mu_star"] >= 0 for v in mor.values())


def test_tornado_and_likelihood_update():
    tor = tornado_analysis()
    assert set(tor) == {p.name for p in PARAMETERS}
    samples = sample_parameters(200, seed=13)
    outputs = evaluate_tissue_model(samples)
    like = likelihood_update(samples, outputs)
    weights = like["weights"]
    assert np.isclose(np.sum(weights), 1.0)
    assert like["effective_sample_size"][0] > 1
