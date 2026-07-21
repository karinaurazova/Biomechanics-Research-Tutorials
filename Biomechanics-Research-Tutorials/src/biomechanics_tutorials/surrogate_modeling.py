"""Tutorial 23: surrogate modeling for homogenized soft-tissue mechanics.

The module is deliberately dependency-light.  It teaches the main ideas behind
surrogate models without hiding the workflow behind a machine-learning package:

* create a synthetic structure-to-stiffness map;
* sample it over a design space;
* fit polynomial ridge and random-feature surrogates;
* quantify interpolation and extrapolation errors;
* use an ensemble as a simple uncertainty indicator;
* run a small active-learning loop.

All numbers are synthetic and are intended for verification and education only.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np


@dataclass(frozen=True)
class SurrogateDataset:
    """Container for the synthetic surrogate-learning dataset."""

    features: np.ndarray
    targets: np.ndarray
    feature_names: tuple[str, ...]
    target_names: tuple[str, ...]


@dataclass(frozen=True)
class RidgeModel:
    """Linear model in a chosen feature basis."""

    weights: np.ndarray
    mean_x: np.ndarray
    std_x: np.ndarray
    mean_y: np.ndarray
    std_y: np.ndarray
    basis: str
    feature_names: tuple[str, ...]
    target_names: tuple[str, ...]


def latin_hypercube(n_samples: int, n_dim: int, seed: int = 0) -> np.ndarray:
    """Return a simple Latin-hypercube design in [0, 1]^n_dim."""

    rng = np.random.default_rng(seed)
    result = np.empty((n_samples, n_dim), dtype=float)
    base = (np.arange(n_samples) + rng.random(n_samples)) / n_samples
    for j in range(n_dim):
        result[:, j] = rng.permutation(base)
    return result


def sample_structural_design(n_samples: int, seed: int = 0) -> np.ndarray:
    """Sample structural descriptors and loading states.

    Columns are:
    theta_mean, kappa, rho_f, porosity, connectivity, exx, eyy, gxy.
    """

    u = latin_hypercube(n_samples, 8, seed=seed)
    theta = -0.5 * np.pi + np.pi * u[:, 0]
    kappa = 0.5 + 12.0 * u[:, 1]
    rho_f = 0.15 + 0.65 * u[:, 2]
    porosity = 0.02 + 0.28 * u[:, 3]
    connectivity = 0.25 + 0.75 * u[:, 4]
    exx = -0.035 + 0.07 * u[:, 5]
    eyy = -0.035 + 0.07 * u[:, 6]
    gxy = -0.05 + 0.10 * u[:, 7]
    return np.column_stack([theta, kappa, rho_f, porosity, connectivity, exx, eyy, gxy])


def structural_to_stiffness(x: np.ndarray) -> np.ndarray:
    """Compute a synthetic effective plane-stress stiffness for each descriptor row.

    The formula is not a validated tissue law.  It is a compact forward model
    with controlled nonlinearities, anisotropy and feature interactions.  It is
    used as a transparent stand-in for an expensive RVE solver.
    """

    x = np.asarray(x, dtype=float)
    theta, kappa, rho_f, porosity, connectivity = x[:, 0], x[:, 1], x[:, 2], x[:, 3], x[:, 4]
    c = np.cos(theta)
    s = np.sin(theta)
    order = kappa / (kappa + 2.0)
    matrix_scale = (1.0 - porosity) ** 2.2
    fiber_scale = rho_f * connectivity * (0.35 + order)
    base = 0.42 + 0.35 * matrix_scale
    fiber = 2.25 * fiber_scale
    shear_base = 0.16 + 0.12 * matrix_scale

    c4, s4 = c**4, s**4
    c2s2 = c**2 * s**2
    c3s = c**3 * s
    cs3 = c * s**3

    c11 = base + fiber * c4 + 0.12 * rho_f**2
    c22 = base + fiber * s4 + 0.10 * connectivity * rho_f
    c12 = 0.22 * base + fiber * c2s2 + 0.05 * order
    c66 = shear_base + fiber * c2s2 + 0.04 * rho_f * (1 - porosity)
    c16 = 0.55 * fiber * c3s
    c26 = 0.55 * fiber * cs3

    return np.column_stack([c11, c22, c12, c66, c16, c26])


def stiffness_to_stress(stiffness: np.ndarray, strain: np.ndarray) -> np.ndarray:
    """Map Voigt strain [exx, eyy, gxy] to stress [sxx, syy, sxy]."""

    c11, c22, c12, c66, c16, c26 = stiffness.T
    exx, eyy, gxy = strain.T
    sxx = c11 * exx + c12 * eyy + c16 * gxy
    syy = c12 * exx + c22 * eyy + c26 * gxy
    sxy = c16 * exx + c26 * eyy + c66 * gxy
    return np.column_stack([sxx, syy, sxy])


def generate_surrogate_dataset(n_samples: int = 900, seed: int = 4, noise_level: float = 0.002) -> SurrogateDataset:
    """Generate synthetic input-output pairs for surrogate learning."""

    rng = np.random.default_rng(seed)
    design = sample_structural_design(n_samples, seed=seed)
    stiffness = structural_to_stiffness(design[:, :5])
    stress = stiffness_to_stress(stiffness, design[:, 5:8])
    target = np.column_stack([stiffness, stress])
    if noise_level > 0:
        scale = np.maximum(np.std(target, axis=0, keepdims=True), 1e-8)
        target = target + rng.normal(scale=noise_level * scale, size=target.shape)
    return SurrogateDataset(
        features=design,
        targets=target,
        feature_names=("theta_mean", "kappa", "rho_f", "porosity", "connectivity", "exx", "eyy", "gxy"),
        target_names=("C11", "C22", "C12", "C66", "C16", "C26", "sxx", "syy", "sxy"),
    )


def train_test_split(n: int, train_fraction: float = 0.72, seed: int = 0) -> tuple[np.ndarray, np.ndarray]:
    """Return shuffled train/test indices."""

    rng = np.random.default_rng(seed)
    idx = rng.permutation(n)
    n_train = int(train_fraction * n)
    return idx[:n_train], idx[n_train:]



def engineered_inputs(x: np.ndarray) -> np.ndarray:
    """Return mechanics-aware inputs with axial trigonometric descriptors.

    The raw angle is periodic, so a polynomial in theta alone is a poor basis.
    We keep all original variables and append axial orientation descriptors that
    make the regression problem smoother.
    """

    x = np.asarray(x, dtype=float)
    theta = x[:, 0]
    trig = np.column_stack([
        np.cos(2.0 * theta),
        np.sin(2.0 * theta),
        np.cos(4.0 * theta),
        np.sin(4.0 * theta),
    ])
    return np.column_stack([x, trig])


def _normalize(x: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    mean = np.mean(x, axis=0)
    std = np.std(x, axis=0)
    std[std < 1e-12] = 1.0
    return (x - mean) / std, mean, std


def polynomial_basis(x: np.ndarray, degree: int = 2) -> np.ndarray:
    """Build polynomial features up to degree 3 for normalized inputs."""

    parts = [np.ones((x.shape[0], 1)), x]
    if degree >= 2:
        quad = []
        for i in range(x.shape[1]):
            for j in range(i, x.shape[1]):
                quad.append((x[:, i] * x[:, j])[:, None])
        parts.extend(quad)
    if degree >= 3:
        cubic = []
        for i in range(x.shape[1]):
            cubic.append((x[:, i] ** 3)[:, None])
        parts.extend(cubic)
    return np.hstack(parts)


def random_feature_basis(x: np.ndarray, n_features: int = 180, seed: int = 0, length_scale: float = 1.15) -> np.ndarray:
    """Random Fourier feature basis for a Gaussian-kernel-like surrogate."""

    rng = np.random.default_rng(seed)
    w = rng.normal(scale=1.0 / length_scale, size=(x.shape[1], n_features))
    b = rng.uniform(0, 2 * np.pi, size=n_features)
    z = np.sqrt(2.0 / n_features) * np.cos(x @ w + b)
    return np.hstack([np.ones((x.shape[0], 1)), x, z])


def fit_ridge_surrogate(
    x: np.ndarray,
    y: np.ndarray,
    basis: str = "quadratic",
    ridge: float = 1e-6,
    random_seed: int = 0,
) -> RidgeModel:
    """Fit a ridge surrogate in a chosen basis."""

    xe = engineered_inputs(x)
    xn, mean_x, std_x = _normalize(xe)
    yn, mean_y, std_y = _normalize(y)
    if basis == "linear":
        phi = polynomial_basis(xn, degree=1)
    elif basis == "quadratic":
        phi = polynomial_basis(xn, degree=2)
    elif basis == "cubic-lite":
        phi = polynomial_basis(xn, degree=3)
    elif basis == "random-features":
        phi = random_feature_basis(xn, seed=random_seed)
    else:
        raise ValueError(f"Unknown basis: {basis}")
    reg = ridge * np.eye(phi.shape[1])
    reg[0, 0] = 0.0
    weights = np.linalg.solve(phi.T @ phi + reg, phi.T @ yn)
    return RidgeModel(weights, mean_x, std_x, mean_y, std_y, basis, tuple(), tuple())


def predict(model: RidgeModel, x: np.ndarray) -> np.ndarray:
    """Evaluate a fitted surrogate."""

    xe = engineered_inputs(x)
    xn = (xe - model.mean_x) / model.std_x
    if model.basis == "linear":
        phi = polynomial_basis(xn, degree=1)
    elif model.basis == "quadratic":
        phi = polynomial_basis(xn, degree=2)
    elif model.basis == "cubic-lite":
        phi = polynomial_basis(xn, degree=3)
    elif model.basis == "random-features":
        phi = random_feature_basis(xn, seed=0)
    else:
        raise ValueError(f"Unknown basis: {model.basis}")
    return phi @ model.weights * model.std_y + model.mean_y


def regression_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    """Return compact multi-output regression metrics."""

    err = y_pred - y_true
    rmse = float(np.sqrt(np.mean(err**2)))
    mae = float(np.mean(np.abs(err)))
    denom = np.sum((y_true - np.mean(y_true, axis=0)) ** 2)
    r2 = float(1.0 - np.sum(err**2) / max(denom, 1e-12))
    rel = float(np.mean(np.abs(err) / np.maximum(np.abs(y_true), 1e-5)))
    return {"rmse": rmse, "mae": mae, "r2": r2, "mean_relative_error": rel}


def bootstrap_ensemble(
    x: np.ndarray,
    y: np.ndarray,
    basis: str = "quadratic",
    n_models: int = 12,
    seed: int = 0,
    ridge: float = 3e-5,
) -> list[RidgeModel]:
    """Fit bootstrap ensemble models for uncertainty indicators."""

    rng = np.random.default_rng(seed)
    models = []
    n = x.shape[0]
    for k in range(n_models):
        idx = rng.integers(0, n, size=n)
        models.append(fit_ridge_surrogate(x[idx], y[idx], basis=basis, ridge=ridge, random_seed=k))
    return models


def ensemble_predict(models: Iterable[RidgeModel], x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Return ensemble mean and standard deviation."""

    pred = np.stack([predict(m, x) for m in models], axis=0)
    return np.mean(pred, axis=0), np.std(pred, axis=0)


def learning_curve(
    dataset: SurrogateDataset,
    train_sizes: Iterable[int] = (30, 60, 120, 240, 480),
    basis: str = "quadratic",
    seed: int = 3,
) -> np.ndarray:
    """Evaluate error as a function of the number of training simulations."""

    train_idx, test_idx = train_test_split(dataset.features.shape[0], 0.7, seed=seed)
    rows = []
    for size in train_sizes:
        idx = train_idx[: min(size, len(train_idx))]
        model = fit_ridge_surrogate(dataset.features[idx], dataset.targets[idx], basis=basis, ridge=3e-5)
        pred = predict(model, dataset.features[test_idx])
        m = regression_metrics(dataset.targets[test_idx], pred)
        rows.append([len(idx), m["rmse"], m["mae"], m["r2"], m["mean_relative_error"]])
    return np.array(rows, dtype=float)


def active_learning_trace(
    pool_x: np.ndarray,
    pool_y: np.ndarray,
    initial_size: int = 35,
    batch_size: int = 25,
    n_steps: int = 7,
    seed: int = 9,
) -> np.ndarray:
    """Small uncertainty-based active-learning demonstration."""

    rng = np.random.default_rng(seed)
    remaining = list(rng.permutation(pool_x.shape[0]))
    selected = remaining[:initial_size]
    remaining = remaining[initial_size:]
    holdout = remaining[-180:]
    remaining = remaining[:-180]
    rows = []
    for step in range(n_steps + 1):
        model = fit_ridge_surrogate(pool_x[selected], pool_y[selected], basis="quadratic", ridge=5e-5)
        pred = predict(model, pool_x[holdout])
        m = regression_metrics(pool_y[holdout], pred)
        rows.append([step, len(selected), m["rmse"], m["r2"]])
        if step == n_steps or len(remaining) == 0:
            break
        ens = bootstrap_ensemble(pool_x[selected], pool_y[selected], n_models=8, seed=seed + step)
        _, sd = ensemble_predict(ens, pool_x[remaining])
        score = np.mean(sd[:, :6], axis=1)
        take_local = np.argsort(score)[-batch_size:]
        new_ids = [remaining[i] for i in take_local]
        selected.extend(new_ids)
        remaining = [r for i, r in enumerate(remaining) if i not in set(take_local)]
    return np.array(rows, dtype=float)


def extrapolation_grid(theta: float = 0.0, n: int = 70) -> np.ndarray:
    """Return a rho_f-porosity grid with fixed remaining variables."""

    rho = np.linspace(0.12, 0.85, n)
    por = np.linspace(0.00, 0.34, n)
    rr, pp = np.meshgrid(rho, por)
    x = np.column_stack([
        np.full(rr.size, theta),
        np.full(rr.size, 6.0),
        rr.ravel(),
        pp.ravel(),
        np.full(rr.size, 0.72),
        np.full(rr.size, 0.02),
        np.full(rr.size, -0.005),
        np.full(rr.size, 0.015),
    ])
    return x
