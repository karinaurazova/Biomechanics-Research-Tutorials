import numpy as np
import pytest

from biomechanics_tutorials.hyperelasticity import (
    FIBER_MODELS,
    ISOTROPIC_MODELS,
    MODEL_DEFINITIONS,
    MYOCARDIUM_MODELS,
    deformation_gradient,
    model_catalog,
    neo_hookean_uniaxial_nominal_stress,
    path_response,
    rotate_deformation,
    rotation_matrix_z,
    strain_energy,
    volumetric_energy,
)


def test_catalog_contains_sixteen_models():
    assert len(model_catalog()) == 16
    assert len(ISOTROPIC_MODELS) == 10
    assert len(FIBER_MODELS) == 3
    assert len(MYOCARDIUM_MODELS) == 3


def test_all_models_are_zero_at_reference_configuration():
    for key in MODEL_DEFINITIONS:
        assert strain_energy(key, np.eye(3)) == pytest.approx(0.0, abs=1e-12)


def test_all_models_are_objective_under_superposed_rotation():
    f = deformation_gradient("simple_shear_xy", 0.37) @ deformation_gradient("uniaxial", 1.16)
    q = rotation_matrix_z(0.73)
    for key in MODEL_DEFINITIONS:
        assert strain_energy(key, rotate_deformation(f, q)) == pytest.approx(
            strain_energy(key, f), rel=1e-11, abs=1e-12
        )


def test_neo_hookean_path_derivative_matches_analytical_nominal_stress():
    stretch = np.linspace(0.82, 1.45, 41)
    numerical = path_response("neo_hookean", stretch, relative_step=1e-5)
    analytical = neo_hookean_uniaxial_nominal_stress(stretch)
    assert np.max(np.abs(numerical - analytical)) < 2e-8


def test_gent_locking_limit_is_enforced():
    with pytest.raises(ValueError, match="locking limit"):
        strain_energy("gent", deformation_gradient("uniaxial", 4.0), {"jm": 2.0})


def test_goh_dispersion_parameter_range_is_enforced():
    with pytest.raises(ValueError, match="kappa"):
        strain_energy("goh", deformation_gradient("uniaxial", 1.2), {"kappa": 0.5})


def test_tension_only_fiber_family_does_not_add_energy_in_axial_compression():
    f = deformation_gradient("uniaxial", 0.9)
    total = strain_energy("single_fiber", f, {"fiber_angle_deg": 0.0})
    matrix = strain_energy("neo_hookean", f, {"mu": 0.2})
    assert total == pytest.approx(matrix, rel=1e-12, abs=1e-12)


def test_volumetric_penalties_vanish_at_unit_jacobian():
    for kind in ["quadratic", "logarithmic", "simo_taylor"]:
        assert float(volumetric_energy(1.0, 10.0, kind)) == pytest.approx(0.0, abs=1e-12)


def test_loading_paths_have_expected_jacobian():
    for mode in ["uniaxial", "equibiaxial", "plane_strain"]:
        assert np.linalg.det(deformation_gradient(mode, 1.23)) == pytest.approx(1.0)
    assert np.linalg.det(deformation_gradient("volumetric", 1.17)) == pytest.approx(1.17)


def test_unknown_model_and_mode_raise_clear_errors():
    with pytest.raises(KeyError):
        strain_energy("not_a_model", np.eye(3))
    with pytest.raises(KeyError):
        deformation_gradient("not_a_mode", 1.0)
