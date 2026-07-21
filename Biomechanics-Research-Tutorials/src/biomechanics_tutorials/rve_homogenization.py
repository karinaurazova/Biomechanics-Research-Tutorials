"""RVE homogenization tools for Tutorial 22.

The module implements a compact, inspectable homogenization workflow for a
heterogeneous fiber-reinforced representative volume element (RVE).  It is not
intended to replace production finite-element or FFT homogenization software.
Instead, it keeps every step visible:

1. generate a synthetic heterogeneous microstructure with fiber density,
   orientation, pores and connectivity;
2. assign an anisotropic small-strain stiffness matrix to every finite element;
3. compute Voigt and Reuss bounds;
4. solve a periodic fluctuation problem for three macroscopic strain cases;
5. assemble the effective stiffness tensor from volume-averaged stresses;
6. report Hill--Mandel consistency, anisotropy and mesh-convergence diagnostics.

The mechanical model is small-strain plane stress.  The local strain vector is
``[epsilon_xx, epsilon_yy, gamma_xy]`` and the stress vector is
``[sigma_xx, sigma_yy, sigma_xy]``.  Fiber reinforcement is introduced through a
quadratic energy penalty on the axial fiber strain.
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
class RVEMesh:
    """Structured triangular mesh for a rectangular periodic RVE."""

    nodes: np.ndarray
    elements: np.ndarray
    cell_ids: np.ndarray
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
class LocalMaterialParameters:
    """Parameters used to convert image-like structure into local stiffness."""

    matrix_young: float = 35.0
    matrix_poisson: float = 0.35
    fiber_stiffness: float = 190.0
    density_gain: float = 0.45
    pore_softening: float = 0.08
    connectivity_gain: float = 0.35


@dataclass(frozen=True)
class Microstructure:
    """Cell-wise synthetic RVE fields."""

    theta: np.ndarray
    rho_f: np.ndarray
    pore: np.ndarray
    connectivity: np.ndarray
    phase: np.ndarray
    seed: int
    length: float
    height: float

    @property
    def nx(self) -> int:
        return int(self.theta.shape[1])

    @property
    def ny(self) -> int:
        return int(self.theta.shape[0])


@dataclass(frozen=True)
class PeriodicCaseResult:
    """Solution of one periodic macroscopic strain case."""

    name: str
    macro_strain: np.ndarray
    displacement: np.ndarray
    element_strain: np.ndarray
    element_stress: np.ndarray
    element_energy: np.ndarray
    average_strain: np.ndarray
    average_stress: np.ndarray
    hill_mandel_error: float
    reduced_residual_norm: float


@dataclass(frozen=True)
class HomogenizationResult:
    """Complete homogenization result for one RVE."""

    mesh: RVEMesh
    microstructure: Microstructure
    local_stiffness: np.ndarray
    local_areas: np.ndarray
    voigt_stiffness: np.ndarray
    reuss_stiffness: np.ndarray
    periodic_stiffness: np.ndarray
    cases: list[PeriodicCaseResult]
    metrics: dict[str, float]


def plane_stress_isotropic(E: float, nu: float) -> np.ndarray:
    """Return the 3x3 plane-stress stiffness matrix."""
    E = float(E)
    nu = float(nu)
    if E <= 0:
        raise ValueError("Young's modulus must be positive.")
    if not (-1.0 < nu < 0.5):
        raise ValueError("Poisson's ratio must lie between -1 and 0.5.")
    factor = E / (1.0 - nu**2)
    return factor * np.array(
        [[1.0, nu, 0.0], [nu, 1.0, 0.0], [0.0, 0.0, (1.0 - nu) / 2.0]],
        dtype=float,
    )


def fiber_projector(theta: ArrayLike) -> np.ndarray:
    """Return q(theta) such that fiber strain is q dot [exx, eyy, gamma_xy]."""
    th = np.asarray(theta, dtype=float)
    c = np.cos(th)
    s = np.sin(th)
    return np.stack([c * c, s * s, s * c], axis=-1)


def fiber_reinforced_stiffness(
    theta: float,
    rho_f: float,
    pore: float,
    connectivity: float,
    parameters: LocalMaterialParameters | None = None,
) -> np.ndarray:
    """Convert local image-derived fields into a positive local stiffness matrix.

    The model is deliberately modest.  The matrix contribution is isotropic and
    scaled by density/connectivity/porosity.  The fiber contribution is a rank-one
    stiffness term associated with the axial strain along the local fiber axis.
    This is sufficient for a transparent RVE tutorial because it creates a clear
    link between orientation fields and effective anisotropy.
    """
    p = parameters or LocalMaterialParameters()
    matrix_scale = (1.0 + p.density_gain * float(rho_f)) * (1.0 - p.pore_softening * float(pore))
    matrix_scale *= 1.0 + p.connectivity_gain * float(connectivity)
    C = matrix_scale * plane_stress_isotropic(p.matrix_young, p.matrix_poisson)
    q = fiber_projector(float(theta))
    fiber_scale = p.fiber_stiffness * float(rho_f) * (1.0 - 0.75 * float(pore)) * (0.35 + 0.65 * float(connectivity))
    C = C + max(fiber_scale, 0.0) * np.outer(q, q)
    return 0.5 * (C + C.T)


def create_periodic_tri_mesh(nx: int = 14, ny: int = 14, length: float = 1.0, height: float = 1.0) -> RVEMesh:
    """Create a structured triangular mesh with two triangles per rectangular cell."""
    if nx < 2 or ny < 2:
        raise ValueError("nx and ny must be at least 2.")
    xs = np.linspace(0.0, float(length), nx + 1)
    ys = np.linspace(0.0, float(height), ny + 1)
    xx, yy = np.meshgrid(xs, ys, indexing="xy")
    nodes = np.column_stack([xx.ravel(), yy.ravel()])
    elements: list[list[int]] = []
    cell_ids: list[int] = []
    for j in range(ny):
        for i in range(nx):
            n00 = j * (nx + 1) + i
            n10 = n00 + 1
            n01 = n00 + (nx + 1)
            n11 = n01 + 1
            cid = j * nx + i
            elements.append([n00, n10, n11])
            elements.append([n00, n11, n01])
            cell_ids.extend([cid, cid])
    return RVEMesh(
        nodes=np.asarray(nodes, dtype=float),
        elements=np.asarray(elements, dtype=int),
        cell_ids=np.asarray(cell_ids, dtype=int),
        nx=int(nx),
        ny=int(ny),
        length=float(length),
        height=float(height),
    )


def triangle_B_matrix(coords: ArrayLike) -> tuple[np.ndarray, float]:
    """Return CST strain-displacement matrix and triangle area."""
    xy = np.asarray(coords, dtype=float)
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


def generate_microstructure(
    nx: int = 14,
    ny: int = 14,
    seed: int = 22,
    length: float = 1.0,
    height: float = 1.0,
) -> Microstructure:
    """Generate a smooth synthetic heterogeneous RVE.

    The returned fields mimic what an image-informed pipeline might provide:
    orientation, fiber density, pores, and a simple connectivity proxy.  All
    fields are synthetic and exactly reproducible.
    """
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[0:ny, 0:nx]
    x = (x + 0.5) / nx
    y = (y + 0.5) / ny

    angle_noise = ndimage.gaussian_filter(rng.normal(size=(ny, nx)), sigma=max(nx, ny) / 9.0, mode="wrap")
    theta = 0.20 * np.pi + 0.34 * np.sin(2.0 * np.pi * y) + 0.18 * np.cos(2.0 * np.pi * x) + 0.18 * angle_noise
    theta = np.mod(theta, np.pi)

    density_noise = ndimage.gaussian_filter(rng.normal(size=(ny, nx)), sigma=max(nx, ny) / 12.0, mode="wrap")
    rho_f = 0.50 + 0.20 * np.sin(2.0 * np.pi * (x + 0.15)) + 0.15 * np.cos(2.0 * np.pi * (y - 0.1)) + 0.12 * density_noise
    rho_f = np.clip(rho_f, 0.12, 0.92)

    pore_score = ndimage.gaussian_filter(rng.normal(size=(ny, nx)), sigma=max(nx, ny) / 16.0, mode="wrap")
    pore = (pore_score > np.quantile(pore_score, 0.78)).astype(float)
    pore = ndimage.binary_dilation(pore.astype(bool), iterations=1).astype(float)
    pore = np.clip(pore, 0.0, 1.0)

    gx = ndimage.sobel(rho_f, axis=1, mode="wrap")
    gy = ndimage.sobel(rho_f, axis=0, mode="wrap")
    grad = np.sqrt(gx * gx + gy * gy)
    connectivity = 1.0 - grad / (np.percentile(grad, 95) + 1e-12)
    connectivity = np.clip(0.25 + 0.75 * connectivity, 0.05, 1.0)
    connectivity *= 1.0 - 0.45 * pore

    phase = np.where(pore > 0.5, 0, np.where(rho_f > np.median(rho_f), 2, 1))
    return Microstructure(theta=theta, rho_f=rho_f, pore=pore, connectivity=connectivity, phase=phase, seed=int(seed), length=float(length), height=float(height))


def local_stiffness_for_mesh(
    mesh: RVEMesh,
    microstructure: Microstructure,
    parameters: LocalMaterialParameters | None = None,
) -> np.ndarray:
    """Return one 3x3 material matrix per triangular element."""
    flat_theta = microstructure.theta.ravel()
    flat_rho = microstructure.rho_f.ravel()
    flat_pore = microstructure.pore.ravel()
    flat_conn = microstructure.connectivity.ravel()
    mats = []
    for cid in mesh.cell_ids:
        mats.append(
            fiber_reinforced_stiffness(
                flat_theta[cid], flat_rho[cid], flat_pore[cid], flat_conn[cid], parameters
            )
        )
    return np.asarray(mats, dtype=float)


def element_geometry(mesh: RVEMesh) -> tuple[list[np.ndarray], np.ndarray]:
    """Return B matrices and element areas."""
    B_mats: list[np.ndarray] = []
    areas = np.zeros(mesh.n_elements, dtype=float)
    for e, conn in enumerate(mesh.elements):
        B, area = triangle_B_matrix(mesh.nodes[conn])
        B_mats.append(B)
        areas[e] = area
    return B_mats, areas


def assemble_global_stiffness(mesh: RVEMesh, local_stiffness: np.ndarray) -> tuple[np.ndarray, np.ndarray, list[np.ndarray]]:
    """Assemble the global small-strain FE stiffness matrix."""
    B_mats, areas = element_geometry(mesh)
    K = np.zeros((mesh.n_dofs, mesh.n_dofs), dtype=float)
    for e, conn in enumerate(mesh.elements):
        dofs = np.ravel(np.column_stack([2 * conn, 2 * conn + 1]))
        ke = B_mats[e].T @ local_stiffness[e] @ B_mats[e] * areas[e]
        K[np.ix_(dofs, dofs)] += ke
    return 0.5 * (K + K.T), areas, B_mats


def periodic_reduction_matrix(mesh: RVEMesh) -> tuple[np.ndarray, dict[tuple[int, int, int], int]]:
    """Return a dense reduction matrix enforcing periodic fluctuation DOFs.

    Nodes on opposite boundaries share the same fluctuation unknown.  The class
    at the lower-left periodic corner is fixed in both components to remove the
    arbitrary constant translation of the fluctuation field.
    """
    n_classes = mesh.nx * mesh.ny
    unknown_index: dict[tuple[int, int, int], int] = {}
    counter = 0
    for cls in range(n_classes):
        if cls == 0:
            continue
        for comp in range(2):
            i = cls % mesh.nx
            j = cls // mesh.nx
            unknown_index[(i, j, comp)] = counter
            counter += 1
    P = np.zeros((mesh.n_dofs, counter), dtype=float)
    for j in range(mesh.ny + 1):
        for i in range(mesh.nx + 1):
            node = j * (mesh.nx + 1) + i
            ii = i % mesh.nx
            jj = j % mesh.ny
            for comp in range(2):
                key = (ii, jj, comp)
                if key in unknown_index:
                    P[2 * node + comp, unknown_index[key]] = 1.0
    return P, unknown_index


def affine_displacement(mesh: RVEMesh, macro_strain: ArrayLike) -> np.ndarray:
    """Return nodal displacement for a constant macroscopic strain."""
    E = np.asarray(macro_strain, dtype=float)
    if E.shape != (3,):
        raise ValueError("macro_strain must be [exx, eyy, gamma_xy].")
    x = mesh.nodes[:, 0]
    y = mesh.nodes[:, 1]
    u = np.zeros((mesh.n_nodes, 2), dtype=float)
    u[:, 0] = E[0] * x + 0.5 * E[2] * y
    u[:, 1] = E[1] * y + 0.5 * E[2] * x
    return u


def solve_periodic_case(
    mesh: RVEMesh,
    local_stiffness: np.ndarray,
    macro_strain: ArrayLike,
    name: str = "case",
) -> PeriodicCaseResult:
    """Solve the periodic displacement-fluctuation problem for one strain case."""
    K, areas, B_mats = assemble_global_stiffness(mesh, local_stiffness)
    P, _ = periodic_reduction_matrix(mesh)
    u_aff = affine_displacement(mesh, macro_strain).reshape(-1)
    K_red = P.T @ K @ P
    rhs = -P.T @ K @ u_aff
    q = solve(K_red + 1e-12 * np.eye(K_red.shape[0]), rhs, assume_a="sym")
    u = u_aff + P @ q
    residual = P.T @ K @ u

    strains = np.zeros((mesh.n_elements, 3), dtype=float)
    stresses = np.zeros((mesh.n_elements, 3), dtype=float)
    energy = np.zeros(mesh.n_elements, dtype=float)
    for e, conn in enumerate(mesh.elements):
        dofs = np.ravel(np.column_stack([2 * conn, 2 * conn + 1]))
        strains[e] = B_mats[e] @ u[dofs]
        stresses[e] = local_stiffness[e] @ strains[e]
        energy[e] = 0.5 * float(strains[e] @ stresses[e])
    total_area = float(np.sum(areas))
    avg_strain = np.average(strains, axis=0, weights=areas)
    avg_stress = np.average(stresses, axis=0, weights=areas)
    macro = np.asarray(macro_strain, dtype=float)
    macro_energy = 0.5 * float(macro @ avg_stress)
    average_energy = float(np.average(energy, weights=areas))
    hm_error = abs(macro_energy - average_energy) / (abs(macro_energy) + 1e-12)
    return PeriodicCaseResult(
        name=str(name),
        macro_strain=macro,
        displacement=u.reshape(mesh.n_nodes, 2),
        element_strain=strains,
        element_stress=stresses,
        element_energy=energy,
        average_strain=avg_strain,
        average_stress=avg_stress,
        hill_mandel_error=float(hm_error),
        reduced_residual_norm=float(np.linalg.norm(residual)),
    )


def voigt_bound(local_stiffness: np.ndarray, areas: ArrayLike) -> np.ndarray:
    """Uniform-strain upper bound for the effective stiffness."""
    a = np.asarray(areas, dtype=float)
    return np.average(local_stiffness, axis=0, weights=a)


def reuss_bound(local_stiffness: np.ndarray, areas: ArrayLike) -> np.ndarray:
    """Uniform-stress lower bound for the effective stiffness."""
    a = np.asarray(areas, dtype=float)
    compliance = np.asarray([np.linalg.inv(C) for C in local_stiffness])
    S_avg = np.average(compliance, axis=0, weights=a)
    return np.linalg.inv(S_avg)


def directional_young_modulus(C: np.ndarray, angles: ArrayLike | None = None) -> tuple[np.ndarray, np.ndarray]:
    """Return directional Young modulus for plane-stress stiffness C."""
    if angles is None:
        angles = np.linspace(0.0, np.pi, 181)
    phi = np.asarray(angles, dtype=float)
    S = np.linalg.inv(C)
    out = np.zeros_like(phi)
    for k, th in enumerate(phi):
        q = fiber_projector(th)
        compliance = float(q @ S @ q)
        out[k] = 1.0 / max(compliance, 1e-12)
    return phi, out


def stiffness_summary(C: np.ndarray, label: str) -> dict[str, float | str]:
    """Return scalar summary metrics for an effective stiffness tensor."""
    angles, E_dir = directional_young_modulus(C)
    eig = np.linalg.eigvalsh(0.5 * (C + C.T))
    return {
        "method": label,
        "C11": float(C[0, 0]),
        "C22": float(C[1, 1]),
        "C12": float(C[0, 1]),
        "C66": float(C[2, 2]),
        "C16": float(C[0, 2]),
        "C26": float(C[1, 2]),
        "min_eigenvalue": float(np.min(eig)),
        "condition_number": float(np.max(eig) / max(np.min(eig), 1e-12)),
        "E_min": float(np.min(E_dir)),
        "E_max": float(np.max(E_dir)),
        "anisotropy_ratio": float(np.max(E_dir) / max(np.min(E_dir), 1e-12)),
        "angle_E_max_deg": float(np.rad2deg(angles[int(np.argmax(E_dir))])),
    }


def homogenize_rve(
    nx: int = 14,
    ny: int = 14,
    seed: int = 22,
    parameters: LocalMaterialParameters | None = None,
) -> HomogenizationResult:
    """Run Voigt/Reuss/periodic homogenization for one synthetic RVE."""
    mesh = create_periodic_tri_mesh(nx=nx, ny=ny)
    micro = generate_microstructure(nx=nx, ny=ny, seed=seed, length=mesh.length, height=mesh.height)
    C_local = local_stiffness_for_mesh(mesh, micro, parameters)
    _, areas, _ = assemble_global_stiffness(mesh, C_local)
    cases = [
        solve_periodic_case(mesh, C_local, np.array([1.0, 0.0, 0.0]), "exx"),
        solve_periodic_case(mesh, C_local, np.array([0.0, 1.0, 0.0]), "eyy"),
        solve_periodic_case(mesh, C_local, np.array([0.0, 0.0, 1.0]), "gxy"),
    ]
    C_periodic = np.column_stack([case.average_stress for case in cases])
    C_periodic = 0.5 * (C_periodic + C_periodic.T)
    C_voigt = voigt_bound(C_local, areas)
    C_reuss = reuss_bound(C_local, areas)
    metrics = {
        "mean_hill_mandel_error": float(np.mean([c.hill_mandel_error for c in cases])),
        "max_hill_mandel_error": float(np.max([c.hill_mandel_error for c in cases])),
        "max_reduced_residual_norm": float(np.max([c.reduced_residual_norm for c in cases])),
        "fiber_volume_fraction": float(np.mean(micro.rho_f * (1.0 - micro.pore))),
        "pore_fraction": float(np.mean(micro.pore)),
        "mean_connectivity": float(np.mean(micro.connectivity)),
    }
    metrics.update({f"periodic_{k}": v for k, v in stiffness_summary(C_periodic, "periodic").items() if k != "method"})
    return HomogenizationResult(
        mesh=mesh,
        microstructure=micro,
        local_stiffness=C_local,
        local_areas=areas,
        voigt_stiffness=C_voigt,
        reuss_stiffness=C_reuss,
        periodic_stiffness=C_periodic,
        cases=cases,
        metrics=metrics,
    )


def convergence_study(sizes: Iterable[int] = (6, 8, 10, 12, 14), seed: int = 22) -> list[dict[str, float]]:
    """Compute effective stiffness summaries for several RVE resolutions."""
    rows: list[dict[str, float]] = []
    for n in sizes:
        result = homogenize_rve(nx=int(n), ny=int(n), seed=seed)
        row = {"nx": float(n), "ny": float(n), **result.metrics}
        row.update({f"C_{key}": float(value) for key, value in stiffness_summary(result.periodic_stiffness, "periodic").items() if isinstance(value, (int, float, np.floating))})
        rows.append(row)
    return rows


def element_field_to_grid(mesh: RVEMesh, element_values: ArrayLike) -> np.ndarray:
    """Average two triangular element values back to an ny-by-nx cell grid."""
    values = np.asarray(element_values, dtype=float)
    if values.ndim != 1 or values.size != mesh.n_elements:
        raise ValueError("element_values must be a one-dimensional element field.")
    accum = np.zeros(mesh.nx * mesh.ny, dtype=float)
    counts = np.zeros(mesh.nx * mesh.ny, dtype=float)
    for e, cid in enumerate(mesh.cell_ids):
        accum[cid] += values[e]
        counts[cid] += 1.0
    return (accum / np.maximum(counts, 1.0)).reshape(mesh.ny, mesh.nx)


def save_csv(path: str | Path, rows: list[dict[str, object]]) -> None:
    """Save list-of-dict rows to a small CSV file without pandas."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    columns = list(rows[0].keys())
    lines = [",".join(columns)]
    for row in rows:
        lines.append(",".join(str(row.get(col, "")) for col in columns))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def export_rve_dataset(result: HomogenizationResult, path: str | Path) -> None:
    """Save the central arrays needed to reproduce the tutorial results."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        path,
        nodes=result.mesh.nodes,
        elements=result.mesh.elements,
        cell_ids=result.mesh.cell_ids,
        theta=result.microstructure.theta,
        rho_f=result.microstructure.rho_f,
        pore=result.microstructure.pore,
        connectivity=result.microstructure.connectivity,
        phase=result.microstructure.phase,
        local_stiffness=result.local_stiffness,
        voigt_stiffness=result.voigt_stiffness,
        reuss_stiffness=result.reuss_stiffness,
        periodic_stiffness=result.periodic_stiffness,
        exx_displacement=result.cases[0].displacement,
        exx_strain=result.cases[0].element_strain,
        exx_stress=result.cases[0].element_stress,
    )
