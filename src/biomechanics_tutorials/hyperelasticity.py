"""Educational hyperelastic constitutive models for Tutorial 03.

The implementations in this module are designed for transparent comparison,
verification, and teaching.  Parameters are synthetic and dimensionless.  The
functions are not a substitute for tissue-specific parameter identification or
finite-element material routines.

All distortional models use the isochoric part of the deformation.  Volumetric
penalties are provided separately so that the effects of shape change and
volume change can be studied independently.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import numpy as np
from numpy.typing import ArrayLike, NDArray


FloatArray = NDArray[np.float64]


@dataclass(frozen=True)
class ModelDefinition:
    """Metadata and synthetic default parameters for one constitutive model."""

    key: str
    name: str
    category: str
    parameters: Mapping[str, float]
    reference: str


MODEL_DEFINITIONS: dict[str, ModelDefinition] = {
    "neo_hookean": ModelDefinition(
        "neo_hookean", "Neo-Hookean", "isotropic", {"mu": 1.0}, "Treloar / Rivlin",
    ),
    "mooney_rivlin": ModelDefinition(
        "mooney_rivlin", "Mooney-Rivlin", "isotropic",
        {"c10": 0.35, "c01": 0.15}, "Mooney (1940); Rivlin (1948)",
    ),
    "yeoh": ModelDefinition(
        "yeoh", "Yeoh", "isotropic",
        {"c1": 0.50, "c2": 0.08, "c3": 0.015}, "Yeoh (1990)",
    ),
    "rivlin_polynomial_2": ModelDefinition(
        "rivlin_polynomial_2", "Rivlin polynomial (order 2)", "isotropic",
        {"c10": 0.32, "c01": 0.18, "c20": 0.025, "c11": 0.015, "c02": 0.008},
        "Rivlin (1948)",
    ),
    "gent": ModelDefinition(
        "gent", "Gent", "isotropic", {"mu": 1.0, "jm": 18.0}, "Gent (1996)",
    ),
    "arruda_boyce": ModelDefinition(
        "arruda_boyce", "Arruda-Boyce (truncated)", "isotropic",
        {"mu": 1.0, "chain_parameter": 8.0}, "Arruda & Boyce (1993)",
    ),
    "ogden_1": ModelDefinition(
        "ogden_1", "Ogden, one term", "isotropic",
        {"mu1": 1.0, "alpha1": 2.0}, "Ogden (1972)",
    ),
    "ogden_2": ModelDefinition(
        "ogden_2", "Ogden, two terms", "isotropic",
        {"mu1": 0.65, "alpha1": 1.3, "mu2": 0.35, "alpha2": 5.0},
        "Ogden (1972)",
    ),
    "demiray": ModelDefinition(
        "demiray", "Demiray exponential", "isotropic",
        {"a": 1.0, "b": 2.0}, "Demiray (1972)",
    ),
    "veronda_westmann": ModelDefinition(
        "veronda_westmann", "Veronda-Westmann", "isotropic",
        {"c1": 1.0 / 3.0, "c2": 3.0}, "Veronda & Westmann (1970)",
    ),
    "single_fiber": ModelDefinition(
        "single_fiber", "Single exponential fiber family", "fiber",
        {"matrix_mu": 0.20, "k1": 1.0, "k2": 5.0, "fiber_angle_deg": 0.0},
        "structural invariant model",
    ),
    "hgo": ModelDefinition(
        "hgo", "HGO, two fiber families", "fiber",
        {"matrix_mu": 0.20, "k1": 0.65, "k2": 5.0, "fiber_angle_deg": 30.0},
        "Holzapfel et al. (2000); Gasser et al. (2006)",
    ),
    "goh": ModelDefinition(
        "goh", "GOH with fiber dispersion", "fiber",
        {
            "matrix_mu": 0.20,
            "k1": 0.65,
            "k2": 5.0,
            "fiber_angle_deg": 30.0,
            "kappa": 0.15,
        },
        "Gasser, Ogden & Holzapfel (2006)",
    ),
    "guccione": ModelDefinition(
        "guccione", "Guccione myocardium", "myocardium",
        {"c": 0.18, "bf": 18.0, "bt": 3.0, "bfs": 7.0},
        "Guccione, McCulloch & Waldman (1991)",
    ),
    "costa": ModelDefinition(
        "costa", "Costa orthotropic myocardium", "myocardium",
        {
            "c": 0.10,
            "bff": 18.0,
            "bss": 3.0,
            "bnn": 3.0,
            "bfs": 7.0,
            "bfn": 4.0,
            "bsn": 2.0,
        },
        "Costa, Holmes & McCulloch (2001)",
    ),
    "holzapfel_ogden": ModelDefinition(
        "holzapfel_ogden", "Holzapfel-Ogden myocardium", "myocardium",
        {
            "a": 0.18,
            "b": 2.5,
            "af": 0.35,
            "bf": 8.0,
            "as": 0.12,
            "bs": 5.0,
            "afs": 0.08,
            "bfs": 4.0,
        },
        "Holzapfel & Ogden (2009)",
    ),
}

ISOTROPIC_MODELS = tuple(
    key for key, definition in MODEL_DEFINITIONS.items() if definition.category == "isotropic"
)
FIBER_MODELS = tuple(
    key for key, definition in MODEL_DEFINITIONS.items() if definition.category == "fiber"
)
MYOCARDIUM_MODELS = tuple(
    key for key, definition in MODEL_DEFINITIONS.items() if definition.category == "myocardium"
)


def _as_deformation_gradient(deformation_gradient: ArrayLike) -> FloatArray:
    f = np.asarray(deformation_gradient, dtype=float)
    if f.shape != (3, 3):
        raise ValueError("deformation_gradient must have shape (3, 3)")
    determinant = float(np.linalg.det(f))
    if determinant <= 0.0:
        raise ValueError("deformation_gradient must have positive determinant")
    return f


def kinematic_state(deformation_gradient: ArrayLike) -> dict[str, FloatArray | float]:
    """Return finite-strain kinematics and isochoric invariants."""
    f = _as_deformation_gradient(deformation_gradient)
    j = float(np.linalg.det(f))
    c = f.T @ f
    c_bar = j ** (-2.0 / 3.0) * c
    i1 = float(np.trace(c_bar))
    i2 = float(0.5 * (i1**2 - np.trace(c_bar @ c_bar)))
    stretches = np.linalg.svd(f, compute_uv=False)
    stretches_bar = j ** (-1.0 / 3.0) * stretches
    return {
        "F": f,
        "J": j,
        "C": c,
        "C_bar": c_bar,
        "I1_bar": i1,
        "I2_bar": i2,
        "principal_stretches_bar": stretches_bar,
    }


def rotation_matrix_z(angle_rad: float) -> FloatArray:
    """Return a right-handed rotation about the third coordinate axis."""
    c = float(np.cos(angle_rad))
    s = float(np.sin(angle_rad))
    return np.array([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]])


def fiber_direction(angle_deg: float) -> FloatArray:
    """Return an in-plane unit fiber direction."""
    angle = np.deg2rad(float(angle_deg))
    return np.array([np.cos(angle), np.sin(angle), 0.0], dtype=float)


def _positive(value: float) -> float:
    return max(float(value), 0.0)


def _exp_fiber_energy(strain_measure: float, k1: float, k2: float) -> float:
    positive = _positive(strain_measure)
    if k1 < 0.0 or k2 <= 0.0:
        raise ValueError("fiber parameters require k1 >= 0 and k2 > 0")
    return float(k1 / (2.0 * k2) * np.expm1(k2 * positive**2))


def _parameters(model_key: str, overrides: Mapping[str, float] | None) -> dict[str, float]:
    try:
        definition = MODEL_DEFINITIONS[model_key]
    except KeyError as exc:
        raise KeyError(f"unknown hyperelastic model: {model_key}") from exc
    parameters = dict(definition.parameters)
    if overrides:
        parameters.update({key: float(value) for key, value in overrides.items()})
    return parameters


def strain_energy(
    model_key: str,
    deformation_gradient: ArrayLike,
    parameters: Mapping[str, float] | None = None,
) -> float:
    """Evaluate one distortional strain-energy density.

    The result is dimensionless because all parameters in the tutorial are
    synthetic.  Volumetric energy is deliberately excluded.
    """
    state = kinematic_state(deformation_gradient)
    i1 = float(state["I1_bar"])
    i2 = float(state["I2_bar"])
    c_bar = np.asarray(state["C_bar"], dtype=float)
    stretches = np.asarray(state["principal_stretches_bar"], dtype=float)
    p = _parameters(model_key, parameters)
    x = i1 - 3.0
    y = i2 - 3.0

    if model_key == "neo_hookean":
        return 0.5 * p["mu"] * x
    if model_key == "mooney_rivlin":
        return p["c10"] * x + p["c01"] * y
    if model_key == "yeoh":
        return p["c1"] * x + p["c2"] * x**2 + p["c3"] * x**3
    if model_key == "rivlin_polynomial_2":
        return (
            p["c10"] * x
            + p["c01"] * y
            + p["c20"] * x**2
            + p["c11"] * x * y
            + p["c02"] * y**2
        )
    if model_key == "gent":
        if p["jm"] <= 0.0:
            raise ValueError("jm must be positive")
        argument = 1.0 - x / p["jm"]
        if argument <= 0.0:
            raise ValueError("Gent locking limit reached")
        return -0.5 * p["mu"] * p["jm"] * float(np.log(argument))
    if model_key == "arruda_boyce":
        n = p["chain_parameter"]
        if n <= 0.0:
            raise ValueError("chain_parameter must be positive")
        # Five-term series approximation of the eight-chain energy.
        coefficients = (
            (0.5, 1),
            (1.0 / (20.0 * n), 2),
            (11.0 / (1050.0 * n**2), 3),
            (19.0 / (7000.0 * n**3), 4),
            (519.0 / (673750.0 * n**4), 5),
        )
        return float(
            p["mu"]
            * sum(coefficient * (i1**power - 3.0**power) for coefficient, power in coefficients)
        )
    if model_key == "ogden_1":
        alpha = p["alpha1"]
        if abs(alpha) < 1e-12:
            raise ValueError("Ogden exponent must be non-zero")
        return float(2.0 * p["mu1"] / alpha**2 * (np.sum(stretches**alpha) - 3.0))
    if model_key == "ogden_2":
        energy = 0.0
        for index in (1, 2):
            alpha = p[f"alpha{index}"]
            if abs(alpha) < 1e-12:
                raise ValueError("Ogden exponent must be non-zero")
            energy += 2.0 * p[f"mu{index}"] / alpha**2 * (
                float(np.sum(stretches**alpha)) - 3.0
            )
        return float(energy)
    if model_key == "demiray":
        if p["b"] <= 0.0:
            raise ValueError("b must be positive")
        return float(p["a"] / (2.0 * p["b"]) * np.expm1(p["b"] * x))
    if model_key == "veronda_westmann":
        if p["c2"] <= 0.0:
            raise ValueError("c2 must be positive")
        return float(p["c1"] * np.expm1(p["c2"] * x) - 0.5 * p["c1"] * p["c2"] * y)

    if model_key in FIBER_MODELS:
        matrix = 0.5 * p["matrix_mu"] * x
        angle = p["fiber_angle_deg"]
        directions = [fiber_direction(angle)]
        if model_key in {"hgo", "goh"}:
            directions = [fiber_direction(angle), fiber_direction(-angle)]
        fiber_energy = 0.0
        for direction in directions:
            i4 = float(direction @ c_bar @ direction)
            if model_key == "goh":
                kappa = p["kappa"]
                if not 0.0 <= kappa <= 1.0 / 3.0:
                    raise ValueError("GOH kappa must lie in [0, 1/3]")
                measure = kappa * x + (1.0 - 3.0 * kappa) * (i4 - 1.0)
            else:
                measure = i4 - 1.0
            fiber_energy += _exp_fiber_energy(measure, p["k1"], p["k2"])
        return float(matrix + fiber_energy)

    # Local orthonormal material basis: fiber, sheet, sheet-normal.
    f0 = np.array([1.0, 0.0, 0.0])
    s0 = np.array([0.0, 1.0, 0.0])
    n0 = np.array([0.0, 0.0, 1.0])
    e = 0.5 * (c_bar - np.eye(3))

    def component(a: FloatArray, b: FloatArray) -> float:
        return float(a @ e @ b)

    eff = component(f0, f0)
    ess = component(s0, s0)
    enn = component(n0, n0)
    efs = component(f0, s0)
    efn = component(f0, n0)
    esn = component(s0, n0)

    if model_key == "guccione":
        q = (
            p["bf"] * eff**2
            + p["bt"] * (ess**2 + enn**2 + 2.0 * esn**2)
            + p["bfs"] * 2.0 * (efs**2 + efn**2)
        )
        return float(0.5 * p["c"] * np.expm1(q))
    if model_key == "costa":
        q = (
            p["bff"] * eff**2
            + p["bss"] * ess**2
            + p["bnn"] * enn**2
            + 2.0 * p["bfs"] * efs**2
            + 2.0 * p["bfn"] * efn**2
            + 2.0 * p["bsn"] * esn**2
        )
        return float(0.5 * p["c"] * np.expm1(q))
    if model_key == "holzapfel_ogden":
        i4f = float(f0 @ c_bar @ f0)
        i4s = float(s0 @ c_bar @ s0)
        i8fs = float(f0 @ c_bar @ s0)
        energy = p["a"] / (2.0 * p["b"]) * np.expm1(p["b"] * x)
        energy += p["af"] / (2.0 * p["bf"]) * np.expm1(
            p["bf"] * _positive(i4f - 1.0) ** 2
        )
        energy += p["as"] / (2.0 * p["bs"]) * np.expm1(
            p["bs"] * _positive(i4s - 1.0) ** 2
        )
        energy += p["afs"] / (2.0 * p["bfs"]) * np.expm1(p["bfs"] * i8fs**2)
        return float(energy)

    raise KeyError(f"unknown hyperelastic model: {model_key}")


def volumetric_energy(jacobian: ArrayLike, bulk_modulus: float, kind: str = "quadratic") -> FloatArray:
    """Evaluate one of three educational volumetric penalty functions."""
    j = np.asarray(jacobian, dtype=float)
    if np.any(j <= 0.0):
        raise ValueError("jacobian must be positive")
    if bulk_modulus < 0.0:
        raise ValueError("bulk_modulus must be non-negative")
    if kind == "quadratic":
        return 0.5 * bulk_modulus * (j - 1.0) ** 2
    if kind == "logarithmic":
        return 0.5 * bulk_modulus * np.log(j) ** 2
    if kind == "simo_taylor":
        return 0.25 * bulk_modulus * (j**2 - 1.0 - 2.0 * np.log(j))
    raise KeyError(f"unknown volumetric energy: {kind}")


def deformation_gradient(mode: str, amount: float) -> FloatArray:
    """Construct a standard homogeneous loading path."""
    value = float(amount)
    if mode in {"uniaxial", "equibiaxial", "plane_strain", "volumetric"} and value <= 0.0:
        raise ValueError("stretch or volume ratio must be positive")
    if mode == "uniaxial":
        return np.diag([value, value ** (-0.5), value ** (-0.5)])
    if mode == "equibiaxial":
        return np.diag([value, value, value ** (-2.0)])
    if mode == "plane_strain":
        return np.diag([value, 1.0, value ** (-1.0)])
    if mode == "simple_shear_xy":
        f = np.eye(3)
        f[0, 1] = value
        return f
    if mode == "simple_shear_xz":
        f = np.eye(3)
        f[0, 2] = value
        return f
    if mode == "simple_shear_yz":
        f = np.eye(3)
        f[1, 2] = value
        return f
    if mode == "volumetric":
        return value ** (1.0 / 3.0) * np.eye(3)
    raise KeyError(f"unknown loading mode: {mode}")


def path_energy(
    model_key: str,
    amounts: ArrayLike,
    mode: str = "uniaxial",
    parameters: Mapping[str, float] | None = None,
) -> FloatArray:
    """Evaluate energy along a homogeneous loading path."""
    values = np.asarray(amounts, dtype=float)
    result = np.full(values.shape, np.nan, dtype=float)
    for index, amount in np.ndenumerate(values):
        try:
            result[index] = strain_energy(
                model_key,
                deformation_gradient(mode, float(amount)),
                parameters,
            )
        except (ValueError, FloatingPointError, OverflowError):
            result[index] = np.nan
    return result


def path_response(
    model_key: str,
    amounts: ArrayLike,
    mode: str = "uniaxial",
    parameters: Mapping[str, float] | None = None,
    relative_step: float = 1e-5,
) -> FloatArray:
    """Return the generalized force ``dW/dq`` along a loading path.

    For the incompressible uniaxial path this is the work-conjugate nominal
    response.  For shear it is the generalized shear response.  The derivative
    is intentionally computed numerically so the same transparent procedure can
    be applied to all sixteen models.
    """
    values = np.asarray(amounts, dtype=float)
    result = np.full(values.shape, np.nan, dtype=float)
    for index, amount in np.ndenumerate(values):
        q = float(amount)
        step = relative_step * max(1.0, abs(q))
        if mode in {"uniaxial", "equibiaxial", "plane_strain", "volumetric"}:
            step = min(step, 0.25 * q)
        try:
            plus = strain_energy(model_key, deformation_gradient(mode, q + step), parameters)
            minus = strain_energy(model_key, deformation_gradient(mode, q - step), parameters)
            result[index] = (plus - minus) / (2.0 * step)
        except (ValueError, FloatingPointError, OverflowError):
            result[index] = np.nan
    return result


def neo_hookean_uniaxial_nominal_stress(stretch: ArrayLike, mu: float = 1.0) -> FloatArray:
    """Analytical nominal stress for the incompressible Neo-Hookean path."""
    lam = np.asarray(stretch, dtype=float)
    if np.any(lam <= 0.0):
        raise ValueError("stretch must be positive")
    return mu * (lam - lam ** (-2.0))


def rotate_deformation(deformation_gradient_value: ArrayLike, rotation: ArrayLike) -> FloatArray:
    """Superpose a spatial rigid rotation on a deformation gradient."""
    f = _as_deformation_gradient(deformation_gradient_value)
    q = np.asarray(rotation, dtype=float)
    if q.shape != (3, 3) or not np.allclose(q.T @ q, np.eye(3), atol=1e-10):
        raise ValueError("rotation must be an orthogonal 3x3 matrix")
    return q @ f


def model_catalog() -> tuple[ModelDefinition, ...]:
    """Return model definitions in publication order."""
    return tuple(MODEL_DEFINITIONS.values())
