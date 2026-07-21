# Tutorial 13 — Synthetic Fibrous-Tissue Generation

[English](README.md) | [Русский](README.ru.md)

A universal, fully synthetic foundation for imaging-informed biomechanics. The tutorial creates reproducible 2-D and 3-D fibrous architectures together with synchronized ground truth for geometry, orientation, thickness, family identity, overlap, skeleton topology, and provenance.

> All tissue names are qualitative educational analogies. No preset is experimentally calibrated, patient-specific, or clinically validated.

## Learning objectives

After completing the tutorial, a learner should be able to:

1. distinguish latent fiber geometry from a raster or voxel observation;
2. generate aligned, dispersed, crossed, layered, gradient, Mikado, Voronoi-like, branched, and defective networks;
3. use axial statistics correctly for undirected fibers;
4. create synchronized image, mask, orientation, coherence, count, family, and thickness arrays;
5. skeletonize a binary network and interpret endpoints, branch pixels, connected components, and their limitations;
6. generate compact 3-D voxel volumes with local direction vectors;
7. study sensitivity to density, radius, waviness, orientation concentration, resolution, and random seed;
8. export a portable dataset with explicit metadata and synthetic-data provenance;
9. formulate verification tests without claiming experimental validation;
10. prepare ground-truth structures for synthetic microscopy, polarization, DIC, segmentation, SAM/μSAM, inverse mechanics, and RVE tutorials.

## Model families

| Generator | Controlled features | Typical educational use |
|---|---|---|
| Parallel bundle | mean axis, spacing, crimp, radius | aligned tissues and orientation verification |
| Axial Mikado network | density, length, dispersion, radius | disordered ECM and nonwoven scaffolds |
| Crossing families | two axes, family labels, relative overlap | ambiguity and multi-family segmentation |
| Layered network | depth-dependent family angle | laminated walls and interfaces |
| Spatial gradient | continuously varying tangent field | field-valued orientation ground truth |
| Voronoi-like network | cellular topology and seed density | pore and connectivity studies |
| Branched/defective network | branches, deletion, gaps | robustness and topology benchmarks |
| 3-D voxel network | mean 3-D direction, dispersion, radius | volume imaging and anisotropic voxels |

## Core data model

A planar fiber is stored as a polyline with radius, family identifier, and metadata. Rasterization produces:

- `image` — blurred/noisy synthetic observation;
- `mask` — geometric support before observational noise;
- `orientation` — local axial angle in radians;
- `coherence` — magnitude of the local doubled-angle moment;
- `count` — number of deposited samples contributing to each pixel;
- `family` — dominant family identifier;
- `thickness` — distance-transform-derived local thickness.

A 3-D volume stores a binary voxel mask, local unit direction vectors, overlap count, random seed, and generation metadata.

## Chapters

1. [Scope and synthetic-data philosophy](chapters/01_scope_and_synthetic_data.md)
2. [Representations, coordinates, and units](chapters/02_representations_and_coordinates.md)
3. [Randomness and reproducibility](chapters/03_randomness_and_reproducibility.md)
4. [Axial orientation statistics](chapters/04_axial_orientation_statistics.md)
5. [Polyline fibers, radius, and curvature](chapters/05_polyline_fibers.md)
6. [Mikado and deposited-line networks](chapters/06_mikado_networks.md)
7. [Aligned bundles, crimp, and tortuosity](chapters/07_aligned_bundles_and_crimp.md)
8. [Multiple families, crossings, and ambiguity](chapters/08_multiple_families.md)
9. [Layers and spatial orientation gradients](chapters/09_layers_and_gradients.md)
10. [Cellular and Voronoi-like architectures](chapters/10_cellular_voronoi.md)
11. [Branches, gaps, and controlled defects](chapters/11_branches_gaps_and_defects.md)
12. [Rasterization, blur, and noise](chapters/12_rasterization.md)
13. [Synchronized ground-truth layers](chapters/13_ground_truth_layers.md)
14. [Skeletons and graph-like topology](chapters/14_skeleton_and_graphs.md)
15. [Porosity, thickness, connectivity, and descriptors](chapters/15_structural_metrics.md)
16. [Three-dimensional fibrous volumes](chapters/16_three_dimensional_volumes.md)
17. [Resolution, aliasing, and voxel anisotropy](chapters/17_resolution_and_voxel_anisotropy.md)
18. [Presets and universal educational scope](chapters/18_presets_and_universality.md)
19. [Verification and dataset schema](chapters/19_verification_and_dataset_schema.md)
20. [Limitations and connection to later tutorials](chapters/20_limitations_and_next_steps.md)

## Reproduce the tutorial

From the repository root:

```bash
python tutorials/13-synthetic-fibrous-tissue-generation/reproduce.py
```

Or run the notebook:

```text
notebooks/13_synthetic_fibrous_tissue_generation.ipynb
```

## Main outputs

- [Preset gallery](figures/preset_gallery.png)
- [Synchronized ground-truth layers](figures/ground_truth_layers.png)
- [Density and topology](figures/density_porosity.png)
- [Resolution and apparent thickness](figures/thickness_resolution.png)
- [Orientation concentration](figures/concentration_order.png)
- [Crossing-family ambiguity](figures/crossing_families.png)
- [Crimp and waviness](figures/crimp_waviness.png)
- [Spatial orientation gradient](figures/spatial_gradient.png)
- [Layered architecture](figures/layered_architecture.png)
- [Mikado topology](figures/mikado_topology.png)
- [Voronoi-like architecture](figures/voronoi_cellular.png)
- [Branches and defects](figures/branches_defects.png)
- [Skeleton and graph degree](figures/skeleton_graph.png)
- [3-D volume projections](figures/volume_3d.png)
- [Voxel anisotropy](figures/voxel_anisotropy.png)
- [Seed reproducibility](figures/seed_reproducibility.png)
- [Parameter sensitivity](figures/parameter_sensitivity.png)
- [Dataset export](figures/dataset_export.png)
- [Synthetic verification summary](figures/benchmark_summary.png)
- [Sequential network deposition](animations/network_deposition.gif)

## Independent work

- [Explore](exercises/explore.md)
- [Experiment](exercises/experiment.md)
- [Research Challenge](exercises/research_challenge.md)

## Scientific interpretation

The generators are transparent, parametric test objects. They provide known latent structure for algorithmic verification and method comparison. They do not prove that the selected distributions, radii, crosslinks, or presets reproduce a biological population. Experimental calibration and validation would require modality-specific data and independent measurements.
