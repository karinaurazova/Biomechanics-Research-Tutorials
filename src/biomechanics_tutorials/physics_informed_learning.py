"""Tutorial 24: physics-informed learning for soft-tissue mechanics.

The module intentionally avoids deep-learning frameworks.  It implements a
lightweight physics-informed surrogate with random Fourier features and linear
least-squares fitting.  This keeps the tutorial reproducible on a plain
scientific-Python stack while preserving the main PINN ideas: data misfit,
boundary-condition penalties, PDE residuals, constitutive priors and inverse
calibration.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class BarDataset:
    """Synthetic one-dimensional tissue strip used in the tutorial."""

    x: np.ndarray
    theta: np.ndarray
    rho_f: np.ndarray
    kappa: np.ndarray
    connectivity: np.ndarray
    stiffness_true: np.ndarray
    stiffness_image: np.ndarray
    displacement_true: np.ndarray
    strain_true: np.ndarray
    stress_true: np.ndarray
    obs_x: np.ndarray
    obs_u: np.ndarray
    traction: float


def stiffness_from_structure(
    theta: np.ndarray,
    rho_f: np.ndarray,
    kappa: np.ndarray,
    connectivity: np.ndarray,
    matrix_stiffness: float = 1.0,
    fiber_gain: float = 4.0,
    concentration_gain: float = 0.55,
) -> np.ndarray:
    """Map image-derived structural descriptors to a scalar axial stiffness.

    The map is deliberately simple.  Fibres aligned with the loading axis
    increase axial stiffness through ``cos(theta)^2``.  Fibre fraction, angular
    concentration and connectivity modulate the strength of this reinforcement.
    """

    alignment = np.cos(theta) ** 2
    reinforcement = fiber_gain * rho_f * (0.25 + concentration_gain * kappa) * connectivity * alignment
    return matrix_stiffness * (1.0 + reinforcement)


def generate_bar_dataset(
    n_grid: int = 161,
    n_observations: int = 18,
    noise_level: float = 0.002,
    seed: int = 24,
) -> BarDataset:
    """Generate a synthetic image-informed bar equilibrium benchmark.

    The hidden truth is a heterogeneous stiffness field derived from synthetic
    microstructural descriptors.  The measured data are sparse noisy DIC-like
    displacement observations.
    """

    rng = np.random.default_rng(seed)
    x = np.linspace(0.0, 1.0, n_grid)
    theta = 0.15 * np.pi + 0.28 * np.pi * x + 0.10 * np.pi * np.sin(2 * np.pi * x)
    rho_f = 0.30 + 0.22 * np.exp(-((x - 0.30) / 0.18) ** 2) + 0.10 * np.exp(-((x - 0.78) / 0.12) ** 2)
    rho_f = np.clip(rho_f, 0.05, 0.85)
    kappa = 0.35 + 0.45 * np.exp(-((x - 0.55) / 0.25) ** 2)
    connectivity = 0.72 + 0.22 * np.sin(np.pi * x) ** 2
    stiffness_true = stiffness_from_structure(theta, rho_f, kappa, connectivity)

    # Image-derived stiffness is deliberately biased and smoothed: it mimics an
    # imperfect segmentation/orientation pipeline rather than an oracle field.
    bias = 1.0 + 0.08 * np.sin(3 * np.pi * x + 0.4)
    stiffness_image = np.clip(stiffness_true * bias + rng.normal(0.0, 0.035, n_grid), 0.35, None)
    stiffness_image = moving_average(stiffness_image, 7)

    traction = 0.18
    strain_true = traction / stiffness_true
    # u(0)=0 and constant nominal stress because d/dx(E u')=0.
    displacement_true = cumulative_trapezoid(strain_true, x)
    stress_true = stiffness_true * strain_true

    obs_idx = np.linspace(0, n_grid - 1, n_observations).astype(int)
    obs_x = x[obs_idx]
    obs_u = displacement_true[obs_idx] + rng.normal(0.0, noise_level, n_observations)
    obs_u[0] = 0.0
    return BarDataset(
        x=x,
        theta=theta,
        rho_f=rho_f,
        kappa=kappa,
        connectivity=connectivity,
        stiffness_true=stiffness_true,
        stiffness_image=stiffness_image,
        displacement_true=displacement_true,
        strain_true=strain_true,
        stress_true=stress_true,
        obs_x=obs_x,
        obs_u=obs_u,
        traction=float(traction),
    )


def moving_average(y: np.ndarray, width: int) -> np.ndarray:
    """Centered moving average with edge padding."""
    width = max(1, int(width))
    pad = width // 2
    yp = np.pad(y, pad, mode="edge")
    kernel = np.ones(width) / width
    return np.convolve(yp, kernel, mode="valid")[: len(y)]


def cumulative_trapezoid(y: np.ndarray, x: np.ndarray) -> np.ndarray:
    """Cumulative trapezoidal integral with zero initial value."""
    out = np.zeros_like(y, dtype=float)
    dx = np.diff(x)
    out[1:] = np.cumsum(0.5 * (y[:-1] + y[1:]) * dx)
    return out


def random_fourier_features(x: np.ndarray, n_features: int = 64, seed: int = 0) -> np.ndarray:
    """Random Fourier feature design matrix for one-dimensional inputs."""
    rng = np.random.default_rng(seed)
    frequencies = rng.normal(0.0, 3.0, n_features)
    phases = rng.uniform(0.0, 2 * np.pi, n_features)
    X = x[:, None]
    phi = np.sqrt(2.0 / n_features) * np.cos(2 * np.pi * X * frequencies[None, :] + phases[None, :])
    return np.column_stack([np.ones(len(x)), x, phi])


def finite_difference_matrix(x: np.ndarray) -> np.ndarray:
    """First-derivative matrix on a nonperiodic one-dimensional grid."""
    n = len(x)
    D = np.zeros((n, n), dtype=float)
    dx = np.diff(x)
    for i in range(1, n - 1):
        h0 = x[i] - x[i - 1]
        h1 = x[i + 1] - x[i]
        D[i, i - 1] = -h1 / (h0 * (h0 + h1))
        D[i, i] = (h1 - h0) / (h0 * h1)
        D[i, i + 1] = h0 / (h1 * (h0 + h1))
    D[0, 0] = -1.0 / dx[0]
    D[0, 1] = 1.0 / dx[0]
    D[-1, -2] = -1.0 / dx[-1]
    D[-1, -1] = 1.0 / dx[-1]
    return D


def physics_operator(x: np.ndarray, stiffness: np.ndarray, basis: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Return PDE residual and strain design matrices for ``u = basis @ w``.

    For equilibrium in a heterogeneous bar the governing equation is
    ``d/dx(E(x) du/dx) = 0``.  Applying finite differences to every basis column
    gives a linear residual operator in the unknown weights.
    """
    D = finite_difference_matrix(x)
    strain_basis = D @ basis
    residual_basis = D @ (stiffness[:, None] * strain_basis)
    return residual_basis, strain_basis


def interpolate_rows(x_grid: np.ndarray, basis: np.ndarray, x_query: np.ndarray) -> np.ndarray:
    """Linearly interpolate every basis column to query coordinates."""
    return np.column_stack([np.interp(x_query, x_grid, basis[:, j]) for j in range(basis.shape[1])])


def fit_physics_informed_model(
    data: BarDataset,
    stiffness: np.ndarray | None = None,
    n_features: int = 48,
    lambda_data: float = 1.0,
    lambda_pde: float = 1.0,
    lambda_bc: float = 100.0,
    lambda_traction: float = 50.0,
    ridge: float = 1e-8,
    seed: int = 7,
) -> dict[str, np.ndarray | float]:
    """Fit a lightweight physics-informed random-feature surrogate.

    The least-squares system combines sparse displacement data, a displacement
    boundary condition at x=0, a traction boundary condition at x=1, and the PDE
    residual at interior collocation points.
    """
    x = data.x
    E = data.stiffness_image if stiffness is None else np.asarray(stiffness)
    basis = random_fourier_features(x, n_features=n_features, seed=seed)
    obs_basis = interpolate_rows(x, basis, data.obs_x)
    residual_basis, strain_basis = physics_operator(x, E, basis)

    blocks = []
    targets = []
    if lambda_data > 0:
        blocks.append(np.sqrt(lambda_data) * obs_basis)
        targets.append(np.sqrt(lambda_data) * data.obs_u)
    if lambda_pde > 0:
        blocks.append(np.sqrt(lambda_pde) * residual_basis[1:-1])
        targets.append(np.zeros(len(x) - 2))
    if lambda_bc > 0:
        blocks.append(np.sqrt(lambda_bc) * basis[[0], :])
        targets.append(np.array([0.0]) * np.sqrt(lambda_bc))
    if lambda_traction > 0:
        traction_row = E[-1] * strain_basis[[-1], :]
        blocks.append(np.sqrt(lambda_traction) * traction_row)
        targets.append(np.array([data.traction]) * np.sqrt(lambda_traction))

    A = np.vstack(blocks)
    b = np.concatenate(targets)
    if ridge > 0:
        A = np.vstack([A, np.sqrt(ridge) * np.eye(A.shape[1])])
        b = np.concatenate([b, np.zeros(A.shape[1])])
    weights, *_ = np.linalg.lstsq(A, b, rcond=None)
    u = basis @ weights
    strain = strain_basis @ weights
    stress = E * strain
    residual = residual_basis @ weights
    return {
        "weights": weights,
        "x": x,
        "stiffness_used": E,
        "displacement": u,
        "strain": strain,
        "stress": stress,
        "residual": residual,
        "basis": basis,
        "condition_number": float(np.linalg.cond(A.T @ A + ridge * np.eye(A.shape[1]))),
    }


def evaluate_prediction(data: BarDataset, pred: dict[str, np.ndarray | float]) -> dict[str, float]:
    """Evaluate displacement, strain, residual and boundary errors."""
    u = np.asarray(pred["displacement"])
    strain = np.asarray(pred["strain"])
    stress = np.asarray(pred["stress"])
    residual = np.asarray(pred["residual"])
    return {
        "u_mae": float(np.mean(np.abs(u - data.displacement_true))),
        "u_rmse": float(np.sqrt(np.mean((u - data.displacement_true) ** 2))),
        "strain_mae": float(np.mean(np.abs(strain - data.strain_true))),
        "stress_mae": float(np.mean(np.abs(stress - data.stress_true))),
        "pde_residual_rms": float(np.sqrt(np.mean(residual[1:-1] ** 2))),
        "left_bc_error": float(abs(u[0])),
        "traction_error": float(abs(stress[-1] - data.traction)),
        "energy_error": float(abs(np.trapz(stress * strain, data.x) - np.trapz(data.stress_true * data.strain_true, data.x))),
    }


def run_weight_sweep(data: BarDataset, lambdas: np.ndarray | None = None) -> list[dict[str, float]]:
    """Sweep the PDE residual weight and return error diagnostics."""
    if lambdas is None:
        lambdas = np.logspace(-4, 4, 11)
    out = []
    for lam in lambdas:
        pred = fit_physics_informed_model(data, lambda_pde=float(lam), lambda_data=1.0, seed=11)
        metrics = evaluate_prediction(data, pred)
        metrics["lambda_pde"] = float(lam)
        out.append(metrics)
    return out


def run_case_suite(data: BarDataset) -> dict[str, dict[str, np.ndarray | float]]:
    """Fit several instructive cases used throughout the tutorial."""
    cases = {
        "data_only": dict(lambda_data=1.0, lambda_pde=0.0, lambda_bc=100.0, lambda_traction=0.0, stiffness=data.stiffness_image),
        "physics_only": dict(lambda_data=0.0, lambda_pde=1.0, lambda_bc=100.0, lambda_traction=80.0, stiffness=data.stiffness_image),
        "data_plus_physics_image_E": dict(lambda_data=1.0, lambda_pde=10.0, lambda_bc=100.0, lambda_traction=80.0, stiffness=data.stiffness_image),
        "oracle_physics_true_E": dict(lambda_data=1.0, lambda_pde=10.0, lambda_bc=100.0, lambda_traction=80.0, stiffness=data.stiffness_true),
    }
    return {name: fit_physics_informed_model(data, **kwargs, seed=13) for name, kwargs in cases.items()}


def inverse_stiffness_scale_sweep(
    data: BarDataset,
    alpha_values: np.ndarray | None = None,
) -> list[dict[str, float]]:
    """Simple inverse problem: calibrate a scale factor for image-derived stiffness."""
    if alpha_values is None:
        alpha_values = np.linspace(0.65, 1.35, 21)
    rows = []
    for alpha in alpha_values:
        E = alpha * data.stiffness_image
        pred = fit_physics_informed_model(
            data,
            stiffness=E,
            lambda_data=1.0,
            lambda_pde=20.0,
            lambda_bc=100.0,
            lambda_traction=80.0,
            seed=17,
        )
        metrics = evaluate_prediction(data, pred)
        obs_pred = np.interp(data.obs_x, data.x, np.asarray(pred["displacement"]))
        objective = float(np.mean((obs_pred - data.obs_u) ** 2) + 0.1 * metrics["pde_residual_rms"] ** 2)
        rows.append({"alpha": float(alpha), "objective": objective, **metrics})
    return rows


def make_learning_history(data: BarDataset, n_steps: int = 24) -> list[dict[str, float]]:
    """Create a deterministic pseudo-training history for visualization.

    The model is refit with an increasing PDE weight.  The sequence mimics the
    common curriculum strategy: start with data fit, then progressively enforce
    equilibrium more strongly.
    """
    lam_values = np.logspace(-4, 2, n_steps)
    history = []
    for step, lam in enumerate(lam_values):
        pred = fit_physics_informed_model(data, lambda_data=1.0, lambda_pde=float(lam), lambda_bc=100.0, lambda_traction=80.0, seed=23)
        metrics = evaluate_prediction(data, pred)
        history.append({"step": step, "lambda_pde": float(lam), **metrics})
    return history
