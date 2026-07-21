
"""Tutorial 25: sensitivity analysis and uncertainty quantification.

The functions in this module are intentionally lightweight and transparent.  They
implement a synthetic soft-tissue benchmark that maps uncertain structural and
mechanical parameters to effective stiffness, stress and energy readouts.  The
module includes Monte Carlo propagation, Sobol pick-freeze indices, Morris
screening, tornado analysis, simple likelihood-based posterior updating and
reliability metrics.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple

import numpy as np


@dataclass(frozen=True)
class ParameterSpec:
    """Description of one uncertain input parameter.

    Parameters are sampled from bounded uniform ranges.  This choice is
    pedagogical rather than universal: it keeps inverse transforms transparent
    and avoids hiding the UQ logic behind a distribution library.
    """

    name: str
    nominal: float
    lower: float
    upper: float
    unit: str
    description: str


PARAMETERS: Tuple[ParameterSpec, ...] = (
    ParameterSpec("matrix_modulus", 42.0, 30.0, 58.0, "kPa", "matrix-dominated small-strain modulus"),
    ParameterSpec("fibre_gain", 4.2, 2.4, 6.8, "-", "multiplicative stiffness gain produced by aligned fibres"),
    ParameterSpec("fibre_fraction", 0.44, 0.22, 0.66, "-", "area or volume fraction occupied by load-bearing fibres"),
    ParameterSpec("orientation_deg", 26.0, -10.0, 62.0, "deg", "dominant fibre direction measured from the loading axis"),
    ParameterSpec("concentration", 5.0, 1.1, 12.0, "-", "orientation concentration parameter; larger means less dispersion"),
    ParameterSpec("connectivity", 0.72, 0.35, 0.96, "-", "dimensionless continuity of the fibre network"),
    ParameterSpec("load_scale", 1.0, 0.72, 1.28, "-", "multiplicative uncertainty in the applied macroscopic strain"),
    ParameterSpec("boundary_compliance", 0.08, 0.00, 0.22, "-", "loss of effective strain due to compliant grips or boundary error"),
)

OUTPUT_NAMES: Tuple[str, ...] = (
    "C11", "C22", "C12", "C66", "peak_stress", "strain_energy", "anisotropy_ratio", "growth_stimulus"
)


def parameter_table() -> np.ndarray:
    """Return nominal/lower/upper parameter values as an array."""
    return np.array([[p.nominal, p.lower, p.upper] for p in PARAMETERS], dtype=float)


def nominal_parameter_vector() -> np.ndarray:
    return np.array([p.nominal for p in PARAMETERS], dtype=float)


def unit_cube_to_parameters(u: np.ndarray) -> np.ndarray:
    """Map samples from [0, 1]^d to physical parameter ranges."""
    u = np.asarray(u, dtype=float)
    one_dim = u.ndim == 1
    if one_dim:
        u = u[None, :]
    lows = np.array([p.lower for p in PARAMETERS])
    highs = np.array([p.upper for p in PARAMETERS])
    x = lows + np.clip(u, 0.0, 1.0) * (highs - lows)
    return x[0] if one_dim else x


def parameters_to_unit_cube(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    one_dim = x.ndim == 1
    if one_dim:
        x = x[None, :]
    lows = np.array([p.lower for p in PARAMETERS])
    highs = np.array([p.upper for p in PARAMETERS])
    u = (x - lows) / (highs - lows)
    return u[0] if one_dim else u


def latin_hypercube(n: int, d: int, seed: int = 0) -> np.ndarray:
    """Generate a simple Latin hypercube design in the unit cube."""
    rng = np.random.default_rng(seed)
    result = np.zeros((n, d), dtype=float)
    for j in range(d):
        perm = rng.permutation(n)
        result[:, j] = (perm + rng.random(n)) / n
    return result


def sample_parameters(n: int, seed: int = 0, method: str = "lhs") -> np.ndarray:
    """Sample uncertain parameters."""
    if method == "lhs":
        u = latin_hypercube(n, len(PARAMETERS), seed=seed)
    elif method == "random":
        u = np.random.default_rng(seed).random((n, len(PARAMETERS)))
    else:
        raise ValueError("method must be 'lhs' or 'random'")
    return unit_cube_to_parameters(u)


def evaluate_tissue_model(samples: np.ndarray) -> Dict[str, np.ndarray]:
    """Evaluate the synthetic structure-mechanics benchmark.

    The model is not a clinical constitutive law.  It is a controlled forward
    map for uncertainty propagation.  Its terms mimic common dependencies in
    anisotropic soft-tissue mechanics: matrix stiffness, fibre fraction,
    orientation, concentration, connectivity and loading uncertainty.
    """
    x = np.asarray(samples, dtype=float)
    one_dim = x.ndim == 1
    if one_dim:
        x = x[None, :]
    Em, kg, rho, theta_deg, kappa, conn, load_scale, bc = x.T
    theta = np.deg2rad(theta_deg)
    c = np.cos(theta)
    s = np.sin(theta)
    # Axial order factor from [0, 1). It behaves like a concentration-to-alignment proxy.
    order = kappa / (kappa + 2.0)
    fibre_strength = kg * rho * conn * order
    # Mild porosity-like matrix weakening when fibre fraction is low and boundary compliance is high.
    matrix_factor = 1.0 - 0.18 * (1.0 - rho) - 0.08 * bc
    base = Em * matrix_factor
    C11 = base * (1.00 + fibre_strength * (0.20 + c**4))
    C22 = base * (0.86 + fibre_strength * (0.15 + s**4))
    C12 = base * (0.30 + 0.20 * fibre_strength * (s * c) ** 2)
    C66 = base * (0.23 + 0.55 * fibre_strength * (s * c) ** 2 + 0.05 * conn)
    # A macroscopic loading program with uncertain amplitude and boundary compliance.
    exx = 0.075 * load_scale * (1.0 - 0.42 * bc)
    eyy = -0.020 * load_scale * (1.0 - 0.15 * bc)
    gxy = 0.026 * load_scale * np.sin(2 * theta) * (0.35 + 0.65 * conn)
    sxx = C11 * exx + C12 * eyy
    syy = C12 * exx + C22 * eyy
    sxy = C66 * gxy
    peak = np.sqrt(sxx**2 + syy**2 + 2.0 * sxy**2)
    energy = 0.5 * (sxx * exx + syy * eyy + sxy * gxy)
    anis = C11 / np.maximum(C22, 1e-12)
    # A toy growth/remodeling stimulus: stress departure amplified by structural order.
    growth_stimulus = (peak - 3.2) * (0.55 + 0.45 * order) + 0.25 * (rho - 0.44)
    out = {
        "C11": C11,
        "C22": C22,
        "C12": C12,
        "C66": C66,
        "peak_stress": peak,
        "strain_energy": energy,
        "anisotropy_ratio": anis,
        "growth_stimulus": growth_stimulus,
        "sxx": sxx,
        "syy": syy,
        "sxy": sxy,
        "exx": exx,
        "eyy": eyy,
        "gxy": gxy,
        "order": order,
    }
    if one_dim:
        return {k: np.asarray(v)[0] for k, v in out.items()}
    return out


def summarize_outputs(outputs: Dict[str, np.ndarray]) -> Dict[str, Dict[str, float]]:
    """Return mean, standard deviation and quantiles for model outputs."""
    summary: Dict[str, Dict[str, float]] = {}
    for name in OUTPUT_NAMES:
        y = np.asarray(outputs[name], dtype=float)
        summary[name] = {
            "mean": float(np.mean(y)),
            "std": float(np.std(y, ddof=1)),
            "q05": float(np.quantile(y, 0.05)),
            "q50": float(np.quantile(y, 0.50)),
            "q95": float(np.quantile(y, 0.95)),
        }
    return summary


def monte_carlo(n: int = 4096, seed: int = 1) -> Tuple[np.ndarray, Dict[str, np.ndarray], Dict[str, Dict[str, float]]]:
    samples = sample_parameters(n, seed=seed, method="lhs")
    outputs = evaluate_tissue_model(samples)
    return samples, outputs, summarize_outputs(outputs)


def sobol_pick_freeze(n: int = 2048, seed: int = 2, output: str = "peak_stress") -> Dict[str, Dict[str, float]]:
    """Estimate first-order and total Sobol indices using a pick-freeze design."""
    rng = np.random.default_rng(seed)
    d = len(PARAMETERS)
    A = rng.random((n, d))
    B = rng.random((n, d))
    XA = unit_cube_to_parameters(A)
    XB = unit_cube_to_parameters(B)
    YA = evaluate_tissue_model(XA)[output]
    YB = evaluate_tissue_model(XB)[output]
    var_y = np.var(np.concatenate([YA, YB]), ddof=1)
    if var_y <= 1e-14:
        var_y = 1e-14
    indices: Dict[str, Dict[str, float]] = {}
    for i, p in enumerate(PARAMETERS):
        ABi = A.copy()
        ABi[:, i] = B[:, i]
        YAB = evaluate_tissue_model(unit_cube_to_parameters(ABi))[output]
        # Saltelli-style estimators. Values are clipped only for readability in noisy finite samples.
        s1 = np.mean(YB * (YAB - YA)) / var_y
        st = 0.5 * np.mean((YA - YAB) ** 2) / var_y
        indices[p.name] = {"S1": float(np.clip(s1, -0.1, 1.1)), "ST": float(np.clip(st, 0.0, 1.2))}
    return indices


def morris_screening(r: int = 28, levels: int = 6, seed: int = 3, output: str = "peak_stress") -> Dict[str, Dict[str, float]]:
    """Compute Morris elementary effects for one output."""
    rng = np.random.default_rng(seed)
    d = len(PARAMETERS)
    delta = levels / (2.0 * (levels - 1.0))
    effects = {p.name: [] for p in PARAMETERS}
    grid = np.linspace(0.0, 1.0 - delta, levels // 2)
    for _ in range(r):
        x = rng.choice(grid, size=d)
        order = rng.permutation(d)
        y0 = evaluate_tissue_model(unit_cube_to_parameters(x))[output]
        for j in order:
            x_next = x.copy()
            x_next[j] = min(1.0, x_next[j] + delta)
            y1 = evaluate_tissue_model(unit_cube_to_parameters(x_next))[output]
            effects[PARAMETERS[j].name].append((y1 - y0) / delta)
            x = x_next
            y0 = y1
    result: Dict[str, Dict[str, float]] = {}
    for name, vals in effects.items():
        ee = np.asarray(vals, dtype=float)
        result[name] = {
            "mu": float(np.mean(ee)),
            "mu_star": float(np.mean(np.abs(ee))),
            "sigma": float(np.std(ee, ddof=1)),
        }
    return result


def tornado_analysis(output: str = "peak_stress") -> Dict[str, Dict[str, float]]:
    """One-at-a-time lower/upper variation around the nominal point."""
    x0 = nominal_parameter_vector()
    base = float(evaluate_tissue_model(x0)[output])
    result: Dict[str, Dict[str, float]] = {}
    for i, p in enumerate(PARAMETERS):
        xl = x0.copy(); xu = x0.copy()
        xl[i] = p.lower; xu[i] = p.upper
        yl = float(evaluate_tissue_model(xl)[output])
        yu = float(evaluate_tissue_model(xu)[output])
        result[p.name] = {
            "baseline": base,
            "lower_value": yl,
            "upper_value": yu,
            "range": float(abs(yu - yl)),
            "signed_change_low": float(yl - base),
            "signed_change_high": float(yu - base),
        }
    return result


def reliability_metrics(outputs: Dict[str, np.ndarray], stress_limit: float = 4.2, anisotropy_limit: float = 2.6) -> Dict[str, float]:
    peak = np.asarray(outputs["peak_stress"], dtype=float)
    anis = np.asarray(outputs["anisotropy_ratio"], dtype=float)
    stimulus = np.asarray(outputs["growth_stimulus"], dtype=float)
    fail_stress = peak > stress_limit
    fail_anis = anis > anisotropy_limit
    fail_any = np.logical_or(fail_stress, fail_anis)
    return {
        "stress_limit": float(stress_limit),
        "anisotropy_limit": float(anisotropy_limit),
        "p_peak_stress_exceeds_limit": float(np.mean(fail_stress)),
        "p_anisotropy_exceeds_limit": float(np.mean(fail_anis)),
        "p_any_failure": float(np.mean(fail_any)),
        "mean_positive_growth_stimulus": float(np.mean(np.maximum(stimulus, 0.0))),
    }


def likelihood_update(samples: np.ndarray, outputs: Dict[str, np.ndarray], observation: Dict[str, float] | None = None,
                      sigma: Dict[str, float] | None = None) -> Dict[str, np.ndarray]:
    """Simple likelihood weighting from synthetic observations.

    This is not a replacement for full Bayesian inverse modeling.  It is a
    compact demonstration of how prior samples can be reweighted when a small
    set of measured readouts is available.
    """
    if observation is None:
        nominal_outputs = evaluate_tissue_model(nominal_parameter_vector())
        observation = {
            "peak_stress": float(nominal_outputs["peak_stress"] * 1.03),
            "anisotropy_ratio": float(nominal_outputs["anisotropy_ratio"] * 0.98),
            "strain_energy": float(nominal_outputs["strain_energy"] * 1.04),
        }
    if sigma is None:
        sigma = {"peak_stress": 0.16, "anisotropy_ratio": 0.08, "strain_energy": 0.006}
    logw = np.zeros(samples.shape[0], dtype=float)
    for name, obs in observation.items():
        sd = sigma[name]
        residual = (np.asarray(outputs[name]) - obs) / sd
        logw += -0.5 * residual**2
    logw -= np.max(logw)
    w = np.exp(logw)
    w /= np.sum(w)
    ess = 1.0 / np.sum(w**2)
    return {"weights": w, "effective_sample_size": np.array([ess]), "observation_names": np.array(list(observation.keys()), dtype=object)}


def weighted_quantile(values: np.ndarray, weights: np.ndarray, qs: Iterable[float]) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    weights = np.asarray(weights, dtype=float)
    sorter = np.argsort(values)
    v = values[sorter]
    w = weights[sorter]
    cw = np.cumsum(w)
    cw /= cw[-1]
    return np.interp(list(qs), cw, v)


def posterior_summary(samples: np.ndarray, weights: np.ndarray) -> Dict[str, Dict[str, float]]:
    result: Dict[str, Dict[str, float]] = {}
    for j, p in enumerate(PARAMETERS):
        vals = samples[:, j]
        q05, q50, q95 = weighted_quantile(vals, weights, [0.05, 0.50, 0.95])
        result[p.name] = {
            "prior_mean": float(0.5 * (p.lower + p.upper)),
            "posterior_mean": float(np.sum(weights * vals)),
            "posterior_q05": float(q05),
            "posterior_q50": float(q50),
            "posterior_q95": float(q95),
        }
    return result


def convergence_trace(output_values: np.ndarray, checkpoints: Iterable[int]) -> Dict[str, np.ndarray]:
    y = np.asarray(output_values, dtype=float)
    ns, means, q05s, q95s = [], [], [], []
    for n in checkpoints:
        n = int(min(max(2, n), len(y)))
        ns.append(n)
        means.append(np.mean(y[:n]))
        q05s.append(np.quantile(y[:n], 0.05))
        q95s.append(np.quantile(y[:n], 0.95))
    return {"n": np.asarray(ns), "mean": np.asarray(means), "q05": np.asarray(q05s), "q95": np.asarray(q95s)}


def run_full_uq(seed: int = 25, n_mc: int = 4096, n_sobol: int = 1536) -> Dict[str, object]:
    samples, outputs, mc_summary = monte_carlo(n=n_mc, seed=seed)
    sobol_peak = sobol_pick_freeze(n=n_sobol, seed=seed + 1, output="peak_stress")
    sobol_energy = sobol_pick_freeze(n=n_sobol, seed=seed + 2, output="strain_energy")
    morris_peak = morris_screening(r=32, seed=seed + 3, output="peak_stress")
    tornado_peak = tornado_analysis(output="peak_stress")
    reliability = reliability_metrics(outputs)
    like = likelihood_update(samples, outputs)
    post = posterior_summary(samples, like["weights"])
    checkpoints = np.unique(np.geomspace(32, n_mc, 18).astype(int))
    conv = convergence_trace(outputs["peak_stress"], checkpoints)
    return {
        "samples": samples,
        "outputs": outputs,
        "monte_carlo_summary": mc_summary,
        "sobol_peak_stress": sobol_peak,
        "sobol_strain_energy": sobol_energy,
        "morris_peak_stress": morris_peak,
        "tornado_peak_stress": tornado_peak,
        "reliability": reliability,
        "likelihood": like,
        "posterior_summary": post,
        "convergence": conv,
    }
