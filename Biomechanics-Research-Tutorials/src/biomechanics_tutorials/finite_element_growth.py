"""Finite-element growth model for Tutorial 21.

The implementation is intentionally compact and dependency-light.  It is not a
replacement for a production finite-element package.  Its purpose is to make the
complete chain transparent:

1. create a structured triangular mesh;
2. assemble the small-strain plane-stress stiffness matrix;
3. represent growth as an incompatible eigenstrain field;
4. solve mechanical equilibrium with essential boundary conditions;
5. update growth variables from mechanical stimuli;
6. compute verification metrics and reproducible figures.

The mathematical model used here is a pedagogical linearized growth analogue of
finite-strain growth mechanics.  The exact finite-growth split F = F_e F_g is
introduced in the tutorial chapters.  In code we use the small-strain analogue

    sigma = C : (epsilon(u) - epsilon_g),

where epsilon_g is the prescribed or evolved growth strain.  This keeps the
implementation short enough to inspect line by line while retaining the central
idea: incompatible growth generates elastic accommodation, residual stress, and
stress-driven feedback.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
from numpy.typing import ArrayLike
from scipy import ndimage
from scipy.linalg import solve


@dataclass(frozen=True)
class Mesh:
    """Structured 2-D triangular mesh on a rectangle."""

    nodes: np.ndarray
    elements: np.ndarray
    nx: int
    ny: int
    length: float
    height: float

    @property
    def n_nodes(self) -> int:
        return int(self.nodes.shape[0])

    @property
    def n_elements(self) -> int:
        return int(self.elements.shape[0])

    @property
    def n_dofs(self) -> int:
        return 2 * self.n_nodes


@dataclass(frozen=True)
class Material:
    """Linear elastic plane-stress material."""

    young_modulus: float = 80.0
    poisson_ratio: float = 0.35
    thickness: float = 1.0

    def stiffness_matrix(self) -> np.ndarray:
        """Return the 3x3 plane-stress matrix for [exx, eyy, gamma_xy]."""
        E = float(self.young_modulus)
        nu = float(self.poisson_ratio)
        if E <= 0:
            raise ValueError("Young's modulus must be positive.")
        if not (-1.0 < nu < 0.5):
            raise ValueError("Poisson's ratio must lie between -1 and 0.5.")
        factor = E / (1.0 - nu**2)
        return factor * np.array(
            [[1.0, nu, 0.0], [nu, 1.0, 0.0], [0.0, 0.0, (1.0 - nu) / 2.0]],
            dtype=float,
        )


@dataclass(frozen=True)
class GrowthState:
    """Element-wise growth variables and fiber orientation."""

    isotropic: np.ndarray
    fiber: np.ndarray
    theta: np.ndarray
    stimulus_history: np.ndarray


@dataclass(frozen=True)
class EquilibriumResult:
    """Mechanical solution for one growth state."""

    displacement: np.ndarray
    element_strain: np.ndarray
    growth_strain: np.ndarray
    elastic_strain: np.ndarray
    stress: np.ndarray
    energy_density: np.ndarray
    residual_norm: float
    reaction_norm: float
    fixed_dofs: np.ndarray


@dataclass(frozen=True)
class GrowthHistory:
    """Complete result of a stress-driven growth simulation."""

    mesh: Mesh
    material: Material
    states: list[GrowthState]
    equilibrium: list[EquilibriumResult]
    metrics: list[dict[str, float]]


@dataclass(frozen=True)
class ScenarioResult:
    """Named finite-element growth scenario."""

    name: str
    history: GrowthHistory


def create_rectangular_tri_mesh(
    nx: int = 18,
    ny: int = 12,
    length: float = 1.6,
    height: float = 1.0,
) -> Mesh:
    """Create a structured triangular mesh with two triangles per cell."""
    if nx < 2 or ny < 2:
        raise ValueError("Use at least nx=2 and ny=2 cells.")
    xs = np.linspace(0.0, length, nx + 1)
    ys = np.linspace(0.0, height, ny + 1)
    xx, yy = np.meshgrid(xs, ys, indexing="xy")
    nodes = np.column_stack([xx.ravel(), yy.ravel()])
    elements: list[list[int]] = []
    for j in range(ny):
        for i in range(nx):
            n00 = j * (nx + 1) + i
            n10 = n00 + 1
            n01 = n00 + (nx + 1)
            n11 = n01 + 1
            elements.append([n00, n10, n11])
            elements.append([n00, n11, n01])
    return Mesh(nodes=np.asarray(nodes, dtype=float), elements=np.asarray(elements, dtype=int), nx=nx, ny=ny, length=length, height=height)


def element_centroids(mesh: Mesh) -> np.ndarray:
    """Return centroid coordinates for every triangular element."""
    return mesh.nodes[mesh.elements].mean(axis=1)


def triangle_B_matrix(coords: ArrayLike) -> tuple[np.ndarray, float]:
    """Return CST strain-displacement matrix and area for a triangle.

    The strain vector is [epsilon_xx, epsilon_yy, gamma_xy].  The engineering
    shear strain gamma_xy = du_x/dy + du_y/dx is used, matching the material
    matrix returned by :meth:`Material.stiffness_matrix`.
    """
    xy = np.asarray(coords, dtype=float)
    if xy.shape != (3, 2):
        raise ValueError("coords must have shape (3, 2).")
    x1, y1 = xy[0]
    x2, y2 = xy[1]
    x3, y3 = xy[2]
    twice_area = (x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)
    area = 0.5 * abs(twice_area)
    if area <= 1e-14:
        raise ValueError("Degenerate triangle encountered.")
    b = np.array([y2 - y3, y3 - y1, y1 - y2], dtype=float) / twice_area
    c = np.array([x3 - x2, x1 - x3, x2 - x1], dtype=float) / twice_area
    B = np.zeros((3, 6), dtype=float)
    B[0, 0::2] = b
    B[1, 1::2] = c
    B[2, 0::2] = c
    B[2, 1::2] = b
    return B, area


def default_boundary_conditions(mesh: Mesh) -> np.ndarray:
    """Return essential boundary conditions that remove rigid-body modes.

    The left edge is fixed horizontally.  One lower-left node is fixed vertically.
    This resembles a strip attached to a rigid support while remaining free to
    expand or contract vertically except at the anchor point.
    """
    x = mesh.nodes[:, 0]
    y = mesh.nodes[:, 1]
    left_nodes = np.where(np.isclose(x, 0.0))[0]
    bottom_left = int(np.argmin(x**2 + y**2))
    fixed = [2 * n for n in left_nodes]
    fixed.append(2 * bottom_left + 1)
    return np.unique(np.asarray(fixed, dtype=int))


def growth_strain_from_state(state: GrowthState) -> np.ndarray:
    """Convert scalar growth variables into element strain vectors.

    ``isotropic`` contributes equally to epsilon_xx and epsilon_yy.  ``fiber``
    contributes along the local fiber direction a = [cos(theta), sin(theta)].
    The shear component is stored as engineering gamma_xy.
    """
    g_iso = np.asarray(state.isotropic, dtype=float)
    g_f = np.asarray(state.fiber, dtype=float)
    theta = np.asarray(state.theta, dtype=float)
    c = np.cos(theta)
    s = np.sin(theta)
    return np.column_stack(
        [
            g_iso + g_f * c**2,
            g_iso + g_f * s**2,
            2.0 * g_f * s * c,
        ]
    )


def assemble_system(
    mesh: Mesh,
    material: Material,
    growth_strain: np.ndarray,
    body_force: tuple[float, float] = (0.0, 0.0),
) -> tuple[np.ndarray, np.ndarray, list[np.ndarray], np.ndarray]:
    """Assemble global stiffness and equivalent growth load vector."""
    D = material.stiffness_matrix()
    K = np.zeros((mesh.n_dofs, mesh.n_dofs), dtype=float)
    rhs = np.zeros(mesh.n_dofs, dtype=float)
    B_mats: list[np.ndarray] = []
    areas = np.zeros(mesh.n_elements, dtype=float)
    for e, conn in enumerate(mesh.elements):
        coords = mesh.nodes[conn]
        B, area = triangle_B_matrix(coords)
        B_mats.append(B)
        areas[e] = area
        dofs = np.array([2 * conn[0], 2 * conn[0] + 1, 2 * conn[1], 2 * conn[1] + 1, 2 * conn[2], 2 * conn[2] + 1])
        Ke = material.thickness * area * (B.T @ D @ B)
        fe_growth = material.thickness * area * (B.T @ D @ growth_strain[e])
        fx, fy = body_force
        fe_body = material.thickness * area / 3.0 * np.array([fx, fy, fx, fy, fx, fy], dtype=float)
        K[np.ix_(dofs, dofs)] += Ke
        rhs[dofs] += fe_growth + fe_body
    return K, rhs, B_mats, areas


def solve_equilibrium(
    mesh: Mesh,
    material: Material,
    state: GrowthState,
    fixed_dofs: ArrayLike | None = None,
) -> EquilibriumResult:
    """Solve K u = f_g for a prescribed growth state."""
    if fixed_dofs is None:
        fixed = default_boundary_conditions(mesh)
    else:
        fixed = np.asarray(fixed_dofs, dtype=int)
    growth_strain = growth_strain_from_state(state)
    K, rhs, B_mats, areas = assemble_system(mesh, material, growth_strain)
    all_dofs = np.arange(mesh.n_dofs)
    free = np.setdiff1d(all_dofs, fixed)
    u = np.zeros(mesh.n_dofs, dtype=float)
    u[free] = solve(K[np.ix_(free, free)], rhs[free], assume_a="sym")

    D = material.stiffness_matrix()
    strain = np.zeros_like(growth_strain)
    stress = np.zeros_like(growth_strain)
    energy = np.zeros(mesh.n_elements, dtype=float)
    for e, conn in enumerate(mesh.elements):
        dofs = np.array([2 * conn[0], 2 * conn[0] + 1, 2 * conn[1], 2 * conn[1] + 1, 2 * conn[2], 2 * conn[2] + 1])
        eps = B_mats[e] @ u[dofs]
        elastic = eps - growth_strain[e]
        sig = D @ elastic
        strain[e] = eps
        stress[e] = sig
        energy[e] = 0.5 * float(elastic @ sig)
    residual = K @ u - rhs
    residual_norm = float(np.linalg.norm(residual[free]) / max(np.linalg.norm(rhs[free]), 1e-12))
    reaction_norm = float(np.linalg.norm(residual[fixed]))
    return EquilibriumResult(
        displacement=u.reshape((-1, 2)),
        element_strain=strain,
        growth_strain=growth_strain,
        elastic_strain=strain - growth_strain,
        stress=stress,
        energy_density=energy,
        residual_norm=residual_norm,
        reaction_norm=reaction_norm,
        fixed_dofs=fixed,
    )


def initial_growth_state(mesh: Mesh, seed: int = 21, amplitude: float = 0.014) -> GrowthState:
    """Create a spatially heterogeneous starting growth field."""
    rng = np.random.default_rng(seed)
    centroids = element_centroids(mesh)
    x = centroids[:, 0] / mesh.length
    y = centroids[:, 1] / mesh.height
    theta = np.deg2rad(18.0 + 55.0 * (y - 0.5) + 12.0 * np.sin(2.0 * np.pi * x))
    lesion = np.exp(-((x - 0.68) ** 2 / 0.035 + (y - 0.48) ** 2 / 0.055))
    band = np.exp(-((y - 0.55 - 0.12 * np.sin(2 * np.pi * x)) ** 2) / 0.055)
    noise = ndimage.gaussian_filter(rng.normal(size=(mesh.ny, mesh.nx * 2)), sigma=1.0).ravel()
    noise = (noise - noise.mean()) / max(noise.std(), 1e-12)
    isotropic = amplitude * (0.25 + 0.55 * lesion + 0.15 * noise[: mesh.n_elements])
    fiber = amplitude * (0.40 + 0.60 * band + 0.10 * noise[: mesh.n_elements])
    stimulus_history = np.zeros(mesh.n_elements, dtype=float)
    return GrowthState(isotropic=isotropic, fiber=fiber, theta=np.mod(theta, np.pi), stimulus_history=stimulus_history)


def fiber_stress(stress: np.ndarray, theta: ArrayLike) -> np.ndarray:
    """Return sigma_ff = a · sigma · a for element stress vectors."""
    theta = np.asarray(theta, dtype=float)
    c = np.cos(theta)
    s = np.sin(theta)
    sxx = stress[:, 0]
    syy = stress[:, 1]
    txy = stress[:, 2]
    return sxx * c**2 + syy * s**2 + 2.0 * txy * s * c


def mean_stress(stress: np.ndarray) -> np.ndarray:
    """Return a plane-stress mean stress proxy."""
    return 0.5 * (stress[:, 0] + stress[:, 1])


def smooth_element_field(mesh: Mesh, values: ArrayLike, sigma: float = 0.9) -> np.ndarray:
    """Smooth element values by reshaping the structured two-triangle grid."""
    arr = np.asarray(values, dtype=float).reshape(mesh.ny, mesh.nx * 2)
    return ndimage.gaussian_filter(arr, sigma=sigma, mode="nearest").ravel()


def update_growth_state(
    mesh: Mesh,
    state: GrowthState,
    result: EquilibriumResult,
    dt: float = 0.18,
    isotropic_gain: float = 4.5e-4,
    fiber_gain: float = 6.5e-4,
    target_mean_stress: float = -0.35,
    target_fiber_stress: float = -0.20,
    memory: float = 0.82,
    lower: float = -0.025,
    upper: float = 0.050,
) -> GrowthState:
    """Explicit stress-driven update of isotropic and fiber growth variables."""
    m = mean_stress(result.stress)
    ff = fiber_stress(result.stress, state.theta)
    stimulus = 0.55 * (m - target_mean_stress) + 0.45 * (ff - target_fiber_stress)
    filtered = memory * state.stimulus_history + (1.0 - memory) * smooth_element_field(mesh, stimulus, sigma=0.9)
    new_iso = state.isotropic + dt * isotropic_gain * filtered
    new_fiber = state.fiber + dt * fiber_gain * smooth_element_field(mesh, ff - target_fiber_stress, sigma=1.1)
    new_iso = np.clip(new_iso, lower, upper)
    new_fiber = np.clip(new_fiber, lower, upper)
    return GrowthState(isotropic=new_iso, fiber=new_fiber, theta=state.theta, stimulus_history=filtered)


def history_metrics(mesh: Mesh, state: GrowthState, result: EquilibriumResult, step: int) -> dict[str, float]:
    """Summarize one time step with scalar diagnostics."""
    displacement_norm = np.linalg.norm(result.displacement, axis=1)
    ff = fiber_stress(result.stress, state.theta)
    trace = result.stress[:, 0] + result.stress[:, 1]
    growth_magnitude = np.linalg.norm(result.growth_strain, axis=1)
    elastic_magnitude = np.linalg.norm(result.elastic_strain, axis=1)
    return {
        "step": float(step),
        "mean_isotropic_growth": float(np.mean(state.isotropic)),
        "mean_fiber_growth": float(np.mean(state.fiber)),
        "max_displacement": float(np.max(displacement_norm)),
        "mean_energy_density": float(np.mean(result.energy_density)),
        "mean_trace_stress": float(np.mean(trace)),
        "mean_fiber_stress": float(np.mean(ff)),
        "stress_std": float(np.std(trace)),
        "mean_growth_magnitude": float(np.mean(growth_magnitude)),
        "mean_elastic_mismatch": float(np.mean(elastic_magnitude)),
        "residual_norm": float(result.residual_norm),
        "reaction_norm": float(result.reaction_norm),
    }


def simulate_growth(
    mesh: Mesh | None = None,
    material: Material | None = None,
    n_steps: int = 16,
    seed: int = 21,
    dt: float = 0.18,
    scenario: str = "stress_feedback",
) -> GrowthHistory:
    """Run a reproducible finite-element growth simulation."""
    mesh = mesh if mesh is not None else create_rectangular_tri_mesh()
    material = material if material is not None else Material()
    state = initial_growth_state(mesh, seed=seed)
    states: list[GrowthState] = []
    equilibrium: list[EquilibriumResult] = []
    metrics: list[dict[str, float]] = []
    fixed = default_boundary_conditions(mesh)
    for step in range(n_steps + 1):
        result = solve_equilibrium(mesh, material, state, fixed_dofs=fixed)
        states.append(state)
        equilibrium.append(result)
        metrics.append(history_metrics(mesh, state, result, step))
        if step == n_steps:
            break
        if scenario == "frozen_growth":
            state = GrowthState(state.isotropic.copy(), state.fiber.copy(), state.theta.copy(), state.stimulus_history.copy())
        elif scenario == "stress_feedback":
            state = update_growth_state(mesh, state, result, dt=dt)
        elif scenario == "fiber_only_feedback":
            updated = update_growth_state(mesh, state, result, dt=dt, isotropic_gain=0.0, fiber_gain=8.0e-4)
            state = updated
        else:
            raise ValueError(f"Unknown scenario: {scenario}")
    return GrowthHistory(mesh=mesh, material=material, states=states, equilibrium=equilibrium, metrics=metrics)


def run_scenarios() -> list[ScenarioResult]:
    """Run three comparison scenarios used by the tutorial figures."""
    mesh = create_rectangular_tri_mesh(nx=18, ny=12, length=1.6, height=1.0)
    material = Material(young_modulus=80.0, poisson_ratio=0.35, thickness=1.0)
    return [
        ScenarioResult("frozen_growth", simulate_growth(mesh, material, scenario="frozen_growth", n_steps=16, seed=21)),
        ScenarioResult("stress_feedback", simulate_growth(mesh, material, scenario="stress_feedback", n_steps=16, seed=21)),
        ScenarioResult("fiber_only_feedback", simulate_growth(mesh, material, scenario="fiber_only_feedback", n_steps=16, seed=21)),
    ]


def element_to_node_average(mesh: Mesh, values: ArrayLike) -> np.ndarray:
    """Average element values to nodes for plotting."""
    vals = np.asarray(values, dtype=float)
    acc = np.zeros(mesh.n_nodes, dtype=float)
    count = np.zeros(mesh.n_nodes, dtype=float)
    for e, conn in enumerate(mesh.elements):
        acc[conn] += vals[e]
        count[conn] += 1.0
    return acc / np.maximum(count, 1.0)


def nodal_field_grid(mesh: Mesh, nodal_values: ArrayLike) -> np.ndarray:
    """Reshape nodal values to a regular grid."""
    return np.asarray(nodal_values, dtype=float).reshape(mesh.ny + 1, mesh.nx + 1)


def element_field_grid(mesh: Mesh, element_values: ArrayLike) -> np.ndarray:
    """Reshape element values to the structured two-triangle grid."""
    return np.asarray(element_values, dtype=float).reshape(mesh.ny, mesh.nx * 2)


def scenario_summary_rows(scenarios: Iterable[ScenarioResult]) -> list[dict[str, float | str]]:
    """Create a compact scenario comparison table."""
    rows: list[dict[str, float | str]] = []
    for scenario in scenarios:
        first = scenario.history.metrics[0]
        last = scenario.history.metrics[-1]
        rows.append(
            {
                "scenario": scenario.name,
                "initial_mean_trace_stress": first["mean_trace_stress"],
                "final_mean_trace_stress": last["mean_trace_stress"],
                "initial_mean_fiber_stress": first["mean_fiber_stress"],
                "final_mean_fiber_stress": last["mean_fiber_stress"],
                "final_mean_isotropic_growth": last["mean_isotropic_growth"],
                "final_mean_fiber_growth": last["mean_fiber_growth"],
                "final_mean_energy_density": last["mean_energy_density"],
                "final_residual_norm": last["residual_norm"],
            }
        )
    return rows


def compute_identifiability_table(history: GrowthHistory) -> list[dict[str, float]]:
    """Return numerical diagnostics that connect the FE model to verification."""
    rows: list[dict[str, float]] = []
    for step, (state, result) in enumerate(zip(history.states, history.equilibrium)):
        growth = result.growth_strain
        elastic = result.elastic_strain
        stress = result.stress
        # A simple element-wise design matrix: elastic strain components predict stress.
        A = np.column_stack([elastic[:, 0], elastic[:, 1], elastic[:, 2]])
        svals = np.linalg.svd(A, compute_uv=False)
        cond = float(svals[0] / max(svals[-1], 1e-12)) if svals.size else float("nan")
        rows.append(
            {
                "step": float(step),
                "growth_std": float(np.std(np.linalg.norm(growth, axis=1))),
                "elastic_std": float(np.std(np.linalg.norm(elastic, axis=1))),
                "stress_std": float(np.std(np.linalg.norm(stress, axis=1))),
                "strain_design_condition_number": cond,
                "residual_norm": result.residual_norm,
            }
        )
    return rows


def save_csv(path: str | Path, rows: list[dict[str, float | str]]) -> None:
    """Write list-of-dicts data to CSV without adding a pandas dependency."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    keys = list(rows[0].keys())
    lines = [",".join(keys)]
    for row in rows:
        fields = []
        for key in keys:
            value = row[key]
            if isinstance(value, str):
                fields.append(value)
            else:
                fields.append(f"{float(value):.10g}")
        lines.append(",".join(fields))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
