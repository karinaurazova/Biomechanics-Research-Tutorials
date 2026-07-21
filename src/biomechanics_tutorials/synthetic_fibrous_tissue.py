"""Synthetic fibrous-tissue geometry with explicit ground truth.

Tutorial 13 uses deterministic, parameter-controlled generators rather than
photorealistic black-box synthesis.  The output is intended for verification of
image analysis, segmentation, orientation extraction, and multiscale mechanics.
All coordinates are dimensionless unless a caller assigns a physical scale.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import json
import math
from typing import Sequence

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy import ndimage
from scipy.spatial import Voronoi

FloatArray = NDArray[np.float64]
IntArray = NDArray[np.int32]
BoolArray = NDArray[np.bool_]


def axial_wrap(angle: ArrayLike) -> FloatArray:
    """Wrap axial angles to ``[-pi/2, pi/2)``."""
    values = np.asarray(angle, dtype=float)
    return (values + np.pi / 2.0) % np.pi - np.pi / 2.0


def axial_difference(a: ArrayLike, b: ArrayLike) -> FloatArray:
    """Shortest signed difference between axial angles."""
    return 0.5 * np.arctan2(
        np.sin(2.0 * (np.asarray(a, dtype=float) - np.asarray(b, dtype=float))),
        np.cos(2.0 * (np.asarray(a, dtype=float) - np.asarray(b, dtype=float))),
    )


def axial_mean(angles: ArrayLike, weights: ArrayLike | None = None) -> float:
    """Weighted axial mean angle."""
    values = np.asarray(angles, dtype=float)
    if values.size == 0:
        return float("nan")
    w = np.ones_like(values) if weights is None else np.asarray(weights, dtype=float)
    total = float(np.sum(w))
    if total <= 0.0:
        return float("nan")
    c = float(np.sum(w * np.cos(2.0 * values)) / total)
    s = float(np.sum(w * np.sin(2.0 * values)) / total)
    return float(0.5 * np.arctan2(s, c))


def axial_order_parameter(angles: ArrayLike, weights: ArrayLike | None = None) -> float:
    """Return the magnitude of the second angular moment in ``[0, 1]``."""
    values = np.asarray(angles, dtype=float)
    if values.size == 0:
        return float("nan")
    w = np.ones_like(values) if weights is None else np.asarray(weights, dtype=float)
    total = float(np.sum(w))
    if total <= 0.0:
        return float("nan")
    c = float(np.sum(w * np.cos(2.0 * values)) / total)
    s = float(np.sum(w * np.sin(2.0 * values)) / total)
    return float(np.hypot(c, s))


def sample_axial_von_mises(
    mean_angle: float,
    concentration: float,
    size: int,
    rng: np.random.Generator,
) -> FloatArray:
    """Sample an axial von Mises distribution using doubled angles."""
    if size < 0:
        raise ValueError("size must be non-negative")
    if concentration < 0.0:
        raise ValueError("concentration must be non-negative")
    doubled = rng.vonmises(2.0 * mean_angle, concentration, size=size)
    return axial_wrap(0.5 * doubled)


@dataclass(frozen=True)
class Fiber2D:
    """Polyline representation of one planar fiber."""

    points: FloatArray
    radius: float = 1.5
    family: int = 0
    identifier: int = 0
    metadata: dict[str, float | int | str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        pts = np.asarray(self.points, dtype=float)
        if pts.ndim != 2 or pts.shape[1] != 2 or pts.shape[0] < 2:
            raise ValueError("points must have shape (n>=2, 2)")
        if self.radius <= 0.0:
            raise ValueError("radius must be positive")
        object.__setattr__(self, "points", pts)


@dataclass
class FiberNetwork2D:
    """A collection of planar fibers and generation metadata."""

    fibers: list[Fiber2D]
    domain: tuple[float, float] = (1.0, 1.0)
    seed: int = 0
    name: str = "synthetic-network"
    metadata: dict[str, float | int | str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.domain[0] <= 0.0 or self.domain[1] <= 0.0:
            raise ValueError("domain dimensions must be positive")


@dataclass(frozen=True)
class RasterizedNetwork2D:
    """Raster representation and pixel-wise ground truth."""

    image: FloatArray
    mask: BoolArray
    orientation: FloatArray
    coherence: FloatArray
    count: IntArray
    family: IntArray
    thickness: FloatArray


@dataclass(frozen=True)
class FiberVolume3D:
    """Voxelized 3-D fiber volume with orientation ground truth."""

    volume: BoolArray
    orientation: FloatArray
    count: IntArray
    seed: int
    metadata: dict[str, float | int | str]


def _polyline_from_parameters(
    center: Sequence[float],
    angle: float,
    length: float,
    waviness: float,
    wavelength: float,
    phase: float,
    points: int,
    curvature: float = 0.0,
) -> FloatArray:
    s = np.linspace(-0.5 * length, 0.5 * length, max(points, 2))
    tangent = np.array([math.cos(angle), math.sin(angle)])
    normal = np.array([-math.sin(angle), math.cos(angle)])
    wave = waviness * np.sin(2.0 * np.pi * s / max(wavelength, 1e-12) + phase)
    bend = 0.5 * curvature * s**2 / max(length, 1e-12)
    return np.asarray(center, dtype=float) + s[:, None] * tangent + (wave + bend)[:, None] * normal


def _random_center(rng: np.random.Generator, domain: tuple[float, float], margin: float = 0.0) -> FloatArray:
    width, height = domain
    return np.array(
        [rng.uniform(-margin, width + margin), rng.uniform(-margin, height + margin)],
        dtype=float,
    )


def generate_mikado_network(
    n_fibers: int = 80,
    domain: tuple[float, float] = (1.0, 1.0),
    mean_angle: float = 0.0,
    concentration: float = 0.0,
    length: float | tuple[float, float] = (0.45, 1.15),
    radius: float | tuple[float, float] = (0.006, 0.012),
    waviness: float = 0.0,
    wavelength: float = 0.18,
    seed: int = 0,
    family: int = 0,
) -> FiberNetwork2D:
    """Generate a 2-D Mikado-like network of finite fibers."""
    if n_fibers < 1:
        raise ValueError("n_fibers must be positive")
    rng = np.random.default_rng(seed)
    angles = sample_axial_von_mises(mean_angle, concentration, n_fibers, rng)
    lengths = (
        np.full(n_fibers, float(length))
        if np.isscalar(length)
        else rng.uniform(float(length[0]), float(length[1]), n_fibers)
    )
    radii = (
        np.full(n_fibers, float(radius))
        if np.isscalar(radius)
        else rng.uniform(float(radius[0]), float(radius[1]), n_fibers)
    )
    fibers: list[Fiber2D] = []
    for index, (angle, fiber_length, fiber_radius) in enumerate(zip(angles, lengths, radii)):
        center = _random_center(rng, domain, margin=0.15 * float(fiber_length))
        n_points = max(12, int(70 * float(fiber_length) / max(domain)))
        points = _polyline_from_parameters(
            center,
            float(angle),
            float(fiber_length),
            waviness,
            wavelength,
            rng.uniform(0.0, 2.0 * np.pi),
            n_points,
        )
        fibers.append(
            Fiber2D(
                points=points,
                radius=float(fiber_radius),
                family=family,
                identifier=index,
                metadata={"mean_angle": float(mean_angle), "concentration": float(concentration)},
            )
        )
    return FiberNetwork2D(
        fibers=fibers,
        domain=domain,
        seed=seed,
        name="mikado",
        metadata={"n_fibers": n_fibers, "concentration": float(concentration)},
    )


def generate_parallel_bundle(
    n_fibers: int = 24,
    domain: tuple[float, float] = (1.0, 1.0),
    angle: float = 0.0,
    spacing_jitter: float = 0.15,
    waviness: float = 0.02,
    wavelength: float = 0.18,
    radius: float = 0.008,
    seed: int = 0,
    family: int = 0,
) -> FiberNetwork2D:
    """Generate a nearly parallel bundle spanning the domain."""
    rng = np.random.default_rng(seed)
    width, height = domain
    diagonal = float(np.hypot(width, height) * 1.5)
    normal = np.array([-math.sin(angle), math.cos(angle)])
    center = np.array([0.5 * width, 0.5 * height])
    extent = abs(normal[0]) * width + abs(normal[1]) * height
    offsets = np.linspace(-0.55 * extent, 0.55 * extent, n_fibers)
    if n_fibers > 1:
        spacing = float(np.mean(np.diff(offsets)))
        offsets += rng.normal(0.0, abs(spacing) * spacing_jitter, n_fibers)
    fibers = []
    for index, offset in enumerate(offsets):
        local_angle = angle + rng.normal(0.0, 0.015)
        points = _polyline_from_parameters(
            center + offset * normal,
            local_angle,
            diagonal,
            waviness * rng.uniform(0.7, 1.3),
            wavelength * rng.uniform(0.8, 1.2),
            rng.uniform(0.0, 2.0 * np.pi),
            120,
        )
        fibers.append(Fiber2D(points, radius, family, index))
    return FiberNetwork2D(fibers, domain, seed, "parallel-bundle")


def generate_crossing_families(
    angles: tuple[float, float] = (-np.pi / 4.0, np.pi / 4.0),
    n_per_family: int = 24,
    domain: tuple[float, float] = (1.0, 1.0),
    radius: float = 0.007,
    waviness: float = 0.012,
    seed: int = 0,
) -> FiberNetwork2D:
    """Generate two labeled crossing fiber families."""
    networks = [
        generate_parallel_bundle(
            n_fibers=n_per_family,
            domain=domain,
            angle=angle,
            waviness=waviness,
            radius=radius,
            seed=seed + 101 * family,
            family=family,
        )
        for family, angle in enumerate(angles)
    ]
    fibers: list[Fiber2D] = []
    identifier = 0
    for network in networks:
        for fiber in network.fibers:
            fibers.append(
                Fiber2D(fiber.points, fiber.radius, fiber.family, identifier, fiber.metadata)
            )
            identifier += 1
    return FiberNetwork2D(fibers, domain, seed, "crossing-families", {"angles": str(angles)})


def generate_spatial_gradient_network(
    n_fibers: int = 60,
    domain: tuple[float, float] = (1.0, 1.0),
    angle_left: float = -np.pi / 3.0,
    angle_right: float = np.pi / 3.0,
    radius: float = 0.007,
    seed: int = 0,
) -> FiberNetwork2D:
    """Generate curved fibers whose orientation varies across the domain."""
    rng = np.random.default_rng(seed)
    width, height = domain
    fibers: list[Fiber2D] = []
    for index in range(n_fibers):
        y0 = rng.uniform(0.0, height)
        x = np.linspace(-0.1 * width, 1.1 * width, 140)
        fraction = np.clip(x / width, 0.0, 1.0)
        angle = angle_left + fraction * axial_difference(angle_right, angle_left)
        dx = np.gradient(x)
        dy = np.tan(angle) * dx
        y = y0 + np.cumsum(dy - np.mean(dy))
        y += 0.015 * np.sin(2.0 * np.pi * x / width + rng.uniform(0.0, 2.0 * np.pi))
        fibers.append(Fiber2D(np.column_stack([x, y]), radius, 0, index))
    return FiberNetwork2D(
        fibers,
        domain,
        seed,
        "orientation-gradient",
        {"angle_left": float(angle_left), "angle_right": float(angle_right)},
    )


def generate_layered_network(
    layer_angles: Sequence[float] = (-np.pi / 4.0, 0.0, np.pi / 4.0),
    fibers_per_layer: int = 18,
    domain: tuple[float, float] = (1.0, 1.0),
    radius: float = 0.006,
    seed: int = 0,
) -> FiberNetwork2D:
    """Generate horizontal layers with different preferred directions."""
    rng = np.random.default_rng(seed)
    width, height = domain
    n_layers = len(layer_angles)
    fibers: list[Fiber2D] = []
    identifier = 0
    for family, angle in enumerate(layer_angles):
        y_min = family * height / n_layers
        y_max = (family + 1) * height / n_layers
        diagonal = float(np.hypot(width, height) * 1.25)
        normal = np.array([-math.sin(angle), math.cos(angle)])
        tangent = np.array([math.cos(angle), math.sin(angle)])
        for local in range(fibers_per_layer):
            center = np.array([rng.uniform(0.0, width), rng.uniform(y_min, y_max)])
            s = np.linspace(-0.5 * diagonal, 0.5 * diagonal, 100)
            points = center + s[:, None] * tangent
            points += (
                0.01
                * np.sin(2.0 * np.pi * s / 0.2 + rng.uniform(0.0, 2.0 * np.pi))[:, None]
                * normal
            )
            # Keep only points in a padded layer to preserve local architecture.
            keep = (points[:, 1] >= y_min - 0.04) & (points[:, 1] <= y_max + 0.04)
            if np.count_nonzero(keep) >= 2:
                fibers.append(Fiber2D(points[keep], radius, family, identifier))
                identifier += 1
    return FiberNetwork2D(fibers, domain, seed, "layered", {"layers": n_layers})


def generate_voronoi_network(
    n_seeds: int = 45,
    domain: tuple[float, float] = (1.0, 1.0),
    radius: float = 0.006,
    seed: int = 0,
) -> FiberNetwork2D:
    """Generate a cellular network from finite Voronoi ridges."""
    if n_seeds < 5:
        raise ValueError("n_seeds must be at least five")
    rng = np.random.default_rng(seed)
    width, height = domain
    points = np.column_stack([rng.uniform(0.0, width, n_seeds), rng.uniform(0.0, height, n_seeds)])
    # Guard points make most central ridges finite.
    guard = np.array(
        [
            [-width, -height],
            [2.0 * width, -height],
            [-width, 2.0 * height],
            [2.0 * width, 2.0 * height],
        ]
    )
    voronoi = Voronoi(np.vstack([points, guard]))
    fibers: list[Fiber2D] = []
    identifier = 0
    for ridge in voronoi.ridge_vertices:
        if len(ridge) != 2 or min(ridge) < 0:
            continue
        p0, p1 = voronoi.vertices[ridge]
        if (
            -0.1 * width <= p0[0] <= 1.1 * width
            and -0.1 * height <= p0[1] <= 1.1 * height
            and -0.1 * width <= p1[0] <= 1.1 * width
            and -0.1 * height <= p1[1] <= 1.1 * height
        ):
            fibers.append(Fiber2D(np.vstack([p0, p1]), radius, 0, identifier))
            identifier += 1
    return FiberNetwork2D(fibers, domain, seed, "voronoi", {"n_seeds": n_seeds})


def add_branches(
    network: FiberNetwork2D,
    branch_probability: float = 0.25,
    branch_length: float = 0.18,
    branch_angle: float = np.pi / 3.0,
    seed: int | None = None,
) -> FiberNetwork2D:
    """Add labeled side branches to an existing network."""
    if not 0.0 <= branch_probability <= 1.0:
        raise ValueError("branch_probability must lie in [0, 1]")
    rng = np.random.default_rng(network.seed + 701 if seed is None else seed)
    fibers = list(network.fibers)
    identifier = max((fiber.identifier for fiber in fibers), default=-1) + 1
    for fiber in network.fibers:
        if rng.random() > branch_probability or len(fiber.points) < 5:
            continue
        index = int(rng.integers(2, len(fiber.points) - 2))
        origin = fiber.points[index]
        tangent = fiber.points[index + 1] - fiber.points[index - 1]
        theta = math.atan2(tangent[1], tangent[0])
        theta += rng.choice([-1.0, 1.0]) * branch_angle * rng.uniform(0.75, 1.25)
        points = _polyline_from_parameters(
            origin + 0.5 * branch_length * np.array([math.cos(theta), math.sin(theta)]),
            theta,
            branch_length,
            0.01,
            max(branch_length, 0.05),
            rng.uniform(0.0, 2.0 * np.pi),
            30,
        )
        fibers.append(
            Fiber2D(points, 0.8 * fiber.radius, fiber.family, identifier, {"branch": 1})
        )
        identifier += 1
    return FiberNetwork2D(
        fibers,
        network.domain,
        network.seed,
        f"{network.name}-branched",
        {**network.metadata, "branch_probability": branch_probability},
    )


def apply_defects(
    network: FiberNetwork2D,
    deletion_fraction: float = 0.1,
    gap_probability: float = 0.2,
    seed: int | None = None,
) -> FiberNetwork2D:
    """Delete fibers and introduce internal gaps without changing other parameters."""
    if not 0.0 <= deletion_fraction < 1.0:
        raise ValueError("deletion_fraction must lie in [0, 1)")
    if not 0.0 <= gap_probability <= 1.0:
        raise ValueError("gap_probability must lie in [0, 1]")
    rng = np.random.default_rng(network.seed + 991 if seed is None else seed)
    fibers: list[Fiber2D] = []
    for fiber in network.fibers:
        if rng.random() < deletion_fraction:
            continue
        if rng.random() < gap_probability and len(fiber.points) >= 12:
            midpoint = int(rng.integers(4, len(fiber.points) - 4))
            gap = max(2, len(fiber.points) // 12)
            left = fiber.points[: midpoint - gap]
            right = fiber.points[midpoint + gap :]
            if len(left) >= 2:
                fibers.append(Fiber2D(left, fiber.radius, fiber.family, fiber.identifier, {"gapped": 1}))
            if len(right) >= 2:
                fibers.append(
                    Fiber2D(right, fiber.radius, fiber.family, fiber.identifier + 100000, {"gapped": 1})
                )
        else:
            fibers.append(fiber)
    return FiberNetwork2D(
        fibers,
        network.domain,
        network.seed,
        f"{network.name}-defective",
        {**network.metadata, "deletion_fraction": deletion_fraction, "gap_probability": gap_probability},
    )


def _stamp_disk(
    shape: tuple[int, int],
    row: float,
    column: float,
    radius: float,
) -> tuple[NDArray[np.intp], NDArray[np.intp], FloatArray]:
    r0 = max(int(np.floor(row - radius - 1)), 0)
    r1 = min(int(np.ceil(row + radius + 1)), shape[0] - 1)
    c0 = max(int(np.floor(column - radius - 1)), 0)
    c1 = min(int(np.ceil(column + radius + 1)), shape[1] - 1)
    if r1 < r0 or c1 < c0:
        empty = np.array([], dtype=int)
        return empty, empty, np.array([], dtype=float)
    rr, cc = np.mgrid[r0 : r1 + 1, c0 : c1 + 1]
    distance = np.hypot(rr - row, cc - column)
    keep = distance <= radius + 0.75
    weights = np.exp(-0.5 * (distance[keep] / max(radius * 0.65, 0.55)) ** 2)
    return rr[keep], cc[keep], weights


def rasterize_network(
    network: FiberNetwork2D,
    shape: tuple[int, int] = (256, 256),
    background: float = 0.05,
    foreground: float = 0.95,
    noise_std: float = 0.0,
    blur_sigma: float = 0.7,
    seed: int | None = None,
) -> RasterizedNetwork2D:
    """Rasterize fibers and accumulate orientation/family ground truth."""
    height_px, width_px = shape
    width, height = network.domain
    intensity = np.zeros(shape, dtype=float)
    c2 = np.zeros(shape, dtype=float)
    s2 = np.zeros(shape, dtype=float)
    orientation_weight = np.zeros(shape, dtype=float)
    count = np.zeros(shape, dtype=np.int32)
    family_votes: dict[int, FloatArray] = {}

    for fiber in network.fibers:
        pts = fiber.points
        if fiber.family not in family_votes:
            family_votes[fiber.family] = np.zeros(shape, dtype=float)
        for p0, p1 in zip(pts[:-1], pts[1:]):
            delta = p1 - p0
            segment_length = float(np.linalg.norm(delta))
            if segment_length <= 1e-14:
                continue
            angle = math.atan2(delta[1], delta[0])
            pixel_length = segment_length * max(width_px / width, height_px / height)
            samples = max(1, int(np.ceil(pixel_length * 0.28)))
            radius_px = max(fiber.radius * 0.5 * (width_px / width + height_px / height), 0.55)
            for fraction in np.linspace(0.0, 1.0, samples, endpoint=False):
                point = (1.0 - fraction) * p0 + fraction * p1
                column = point[0] / width * (width_px - 1)
                row = point[1] / height * (height_px - 1)
                rr, cc, weights = _stamp_disk(shape, row, column, radius_px)
                if weights.size == 0:
                    continue
                intensity[rr, cc] += weights
                c2[rr, cc] += weights * math.cos(2.0 * angle)
                s2[rr, cc] += weights * math.sin(2.0 * angle)
                orientation_weight[rr, cc] += weights
                count[rr, cc] += 1
                family_votes[fiber.family][rr, cc] += weights

    maximum = float(np.max(intensity))
    normalized = intensity / maximum if maximum > 0.0 else intensity
    image = background + (foreground - background) * np.clip(normalized, 0.0, 1.0)
    if blur_sigma > 0.0:
        image = ndimage.gaussian_filter(image, blur_sigma)
    if noise_std > 0.0:
        rng = np.random.default_rng(network.seed + 313 if seed is None else seed)
        image = image + rng.normal(0.0, noise_std, shape)
    image = np.clip(image, 0.0, 1.0)
    mask = orientation_weight > 0.05
    orientation = np.full(shape, np.nan, dtype=float)
    orientation[mask] = 0.5 * np.arctan2(s2[mask], c2[mask])
    coherence = np.zeros(shape, dtype=float)
    coherence[mask] = np.hypot(c2[mask], s2[mask]) / np.maximum(orientation_weight[mask], 1e-12)
    family = np.full(shape, -1, dtype=np.int32)
    if family_votes:
        labels = sorted(family_votes)
        stack = np.stack([family_votes[label] for label in labels], axis=0)
        winner = np.argmax(stack, axis=0)
        family[mask] = np.asarray(labels, dtype=np.int32)[winner[mask]]
    thickness = 2.0 * ndimage.distance_transform_edt(mask)
    return RasterizedNetwork2D(image, mask, orientation, coherence, count, family, thickness)


def morphological_skeleton(mask: ArrayLike) -> BoolArray:
    """Morphological skeleton using iterative erosions and openings."""
    binary = np.asarray(mask, dtype=bool)
    skeleton = np.zeros_like(binary)
    structure = ndimage.generate_binary_structure(2, 1)
    current = binary.copy()
    while np.any(current):
        eroded = ndimage.binary_erosion(current, structure=structure)
        opened = ndimage.binary_dilation(eroded, structure=structure)
        skeleton |= current & ~opened
        current = eroded
    return skeleton


def skeleton_degrees(skeleton: ArrayLike) -> IntArray:
    """Return the number of 8-connected skeleton neighbors per pixel."""
    binary = np.asarray(skeleton, dtype=bool)
    kernel = np.ones((3, 3), dtype=int)
    kernel[1, 1] = 0
    return ndimage.convolve(binary.astype(int), kernel, mode="constant", cval=0).astype(np.int32)


def skeleton_graph_metrics(skeleton: ArrayLike) -> dict[str, float | int]:
    """Compute lightweight graph-like topology metrics from a skeleton."""
    binary = np.asarray(skeleton, dtype=bool)
    degree = skeleton_degrees(binary)
    labeled, components = ndimage.label(binary, structure=np.ones((3, 3), dtype=int))
    endpoints = int(np.count_nonzero(binary & (degree == 1)))
    branchpoints = int(np.count_nonzero(binary & (degree >= 3)))
    nodes = endpoints + branchpoints
    skeleton_length = int(np.count_nonzero(binary))
    largest = 0
    if components:
        sizes = np.bincount(labeled.ravel())[1:]
        largest = int(np.max(sizes)) if sizes.size else 0
    return {
        "components": int(components),
        "endpoints": endpoints,
        "branchpoints": branchpoints,
        "nodes": nodes,
        "skeleton_pixels": skeleton_length,
        "largest_component_pixels": largest,
        "largest_component_fraction": float(largest / max(skeleton_length, 1)),
    }


def network_metrics(network: FiberNetwork2D, raster: RasterizedNetwork2D) -> dict[str, float | int]:
    """Return structural summary metrics for a generated network."""
    lengths = []
    segment_angles = []
    segment_weights = []
    for fiber in network.fibers:
        delta = np.diff(fiber.points, axis=0)
        segment_length = np.linalg.norm(delta, axis=1)
        valid = segment_length > 1e-14
        lengths.append(float(np.sum(segment_length)))
        segment_angles.extend(np.arctan2(delta[valid, 1], delta[valid, 0]))
        segment_weights.extend(segment_length[valid])
    skeleton = morphological_skeleton(raster.mask)
    topology = skeleton_graph_metrics(skeleton)
    return {
        "fiber_count": len(network.fibers),
        "total_fiber_length": float(np.sum(lengths)),
        "mean_fiber_length": float(np.mean(lengths)) if lengths else 0.0,
        "area_fraction": float(np.mean(raster.mask)),
        "porosity": float(1.0 - np.mean(raster.mask)),
        "mean_orientation_rad": axial_mean(segment_angles, segment_weights),
        "order_parameter": axial_order_parameter(segment_angles, segment_weights),
        "mean_thickness_px": float(np.mean(raster.thickness[raster.mask])) if np.any(raster.mask) else 0.0,
        **topology,
    }


def generate_fiber_volume(
    shape: tuple[int, int, int] = (64, 96, 96),
    n_fibers: int = 36,
    mean_direction: Sequence[float] = (1.0, 0.0, 0.0),
    angular_noise: float = 0.25,
    radius: float = 1.4,
    waviness: float = 1.5,
    seed: int = 0,
) -> FiberVolume3D:
    """Generate a voxelized 3-D fiber volume with local direction vectors."""
    if n_fibers < 1:
        raise ValueError("n_fibers must be positive")
    rng = np.random.default_rng(seed)
    direction = np.asarray(mean_direction, dtype=float)
    norm = float(np.linalg.norm(direction))
    if norm <= 0.0:
        raise ValueError("mean_direction must be non-zero")
    direction /= norm
    volume = np.zeros(shape, dtype=bool)
    orientation_sum = np.zeros(shape + (3,), dtype=float)
    count = np.zeros(shape, dtype=np.int32)
    zmax, ymax, xmax = np.asarray(shape, dtype=float) - 1.0
    max_length = float(np.linalg.norm([zmax, ymax, xmax]) * 1.4)

    for _ in range(n_fibers):
        local = direction + rng.normal(0.0, angular_noise, 3)
        local /= max(np.linalg.norm(local), 1e-12)
        center = np.array([rng.uniform(0.0, zmax), rng.uniform(0.0, ymax), rng.uniform(0.0, xmax)])
        helper = np.array([0.0, 0.0, 1.0]) if abs(local[2]) < 0.85 else np.array([0.0, 1.0, 0.0])
        normal1 = np.cross(local, helper)
        normal1 /= max(np.linalg.norm(normal1), 1e-12)
        normal2 = np.cross(local, normal1)
        s = np.linspace(-0.5 * max_length, 0.5 * max_length, 220)
        phase = rng.uniform(0.0, 2.0 * np.pi)
        points = center + s[:, None] * local
        points += waviness * np.sin(2.0 * np.pi * s / 24.0 + phase)[:, None] * normal1
        points += 0.5 * waviness * np.cos(2.0 * np.pi * s / 31.0 + phase)[:, None] * normal2
        for point in points:
            z, y, x = point
            z0, z1 = max(int(z - radius - 1), 0), min(int(z + radius + 1), shape[0] - 1)
            y0, y1 = max(int(y - radius - 1), 0), min(int(y + radius + 1), shape[1] - 1)
            x0, x1 = max(int(x - radius - 1), 0), min(int(x + radius + 1), shape[2] - 1)
            if z1 < z0 or y1 < y0 or x1 < x0:
                continue
            zz, yy, xx = np.mgrid[z0 : z1 + 1, y0 : y1 + 1, x0 : x1 + 1]
            keep = np.sqrt((zz - z) ** 2 + (yy - y) ** 2 + (xx - x) ** 2) <= radius
            zi, yi, xi = zz[keep], yy[keep], xx[keep]
            volume[zi, yi, xi] = True
            orientation_sum[zi, yi, xi] += local
            count[zi, yi, xi] += 1

    orientation = np.zeros_like(orientation_sum)
    occupied = count > 0
    norms = np.linalg.norm(orientation_sum[occupied], axis=1)
    orientation[occupied] = orientation_sum[occupied] / np.maximum(norms[:, None], 1e-12)
    return FiberVolume3D(
        volume=volume,
        orientation=orientation,
        count=count,
        seed=seed,
        metadata={
            "n_fibers": n_fibers,
            "radius_voxels": float(radius),
            "angular_noise": float(angular_noise),
        },
    )


def tissue_preset(name: str, seed: int = 0) -> FiberNetwork2D:
    """Return a generic educational preset, not a calibrated tissue model."""
    key = name.strip().lower().replace("_", "-")
    if key in {"tendon", "ligament", "aligned-bundle"}:
        return generate_parallel_bundle(34, angle=0.05, waviness=0.028, radius=0.007, seed=seed)
    if key in {"skin", "dermis", "crossed"}:
        return generate_crossing_families((-0.7, 0.7), 22, radius=0.006, waviness=0.018, seed=seed)
    if key in {"artery", "vessel", "layered-wall"}:
        return generate_layered_network((-0.9, 0.0, 0.9), 16, radius=0.006, seed=seed)
    if key in {"myocardium", "rotating-wall", "orientation-gradient"}:
        return generate_spatial_gradient_network(56, angle_left=-0.9, angle_right=0.9, seed=seed)
    if key in {"valve", "membrane", "two-family"}:
        return generate_crossing_families((-0.45, 0.45), 26, radius=0.006, waviness=0.012, seed=seed)
    if key in {"lung", "alveolar", "cellular"}:
        return generate_voronoi_network(55, radius=0.005, seed=seed)
    if key in {"scaffold", "nonwoven", "mikado"}:
        return generate_mikado_network(110, concentration=0.4, waviness=0.008, seed=seed)
    raise ValueError(f"unknown preset: {name}")


def export_network_dataset(
    path: str | Path,
    network: FiberNetwork2D,
    raster: RasterizedNetwork2D,
    metrics: dict[str, float | int] | None = None,
) -> None:
    """Export a compact synthetic dataset with explicit provenance."""
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    metadata = {
        "name": network.name,
        "seed": network.seed,
        "domain": list(network.domain),
        "generator_metadata": network.metadata,
        "metrics": metrics or network_metrics(network, raster),
        "synthetic": True,
        "experimental_validation": False,
    }
    np.savez_compressed(
        destination,
        image=raster.image,
        mask=raster.mask,
        orientation=raster.orientation,
        coherence=raster.coherence,
        count=raster.count,
        family=raster.family,
        thickness=raster.thickness,
        metadata_json=np.array(json.dumps(metadata, ensure_ascii=False)),
    )


def read_dataset_metadata(path: str | Path) -> dict:
    """Read metadata without interpreting the numerical arrays."""
    with np.load(Path(path), allow_pickle=False) as data:
        return json.loads(str(data["metadata_json"]))
