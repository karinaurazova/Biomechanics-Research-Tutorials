# Tutorial 02 — Collagen Fiber Dispersion

## Research question

**How does the angular dispersion of a collagen-fiber family change its orientation tensor and its apparent mechanical response under uniaxial loading?**

This tutorial moves from a single representative fiber direction to a continuous planar orientation distribution. It introduces axial directional statistics, a π-periodic von Mises distribution, the second-order orientation tensor, angular quadrature, and a minimal tension-only hyperelastic response.

The central lesson is deliberately more subtle than “dispersion softens the tissue.” When the mean fiber direction is aligned with the loading axis, dispersion generally reduces the fraction of fibers that carry load efficiently. When the mean direction is oblique, a broader distribution can place more fibers near the loading axis and may increase the response. Dispersion must therefore be interpreted together with mean orientation and loading direction.

## Learning objectives

After completing the tutorial, the learner should be able to:

1. explain the difference between mean orientation and orientation dispersion;
2. construct and normalize a π-periodic axial probability density;
3. relate the concentration parameter to a second-order orientation parameter;
4. derive and compute the planar orientation tensor;
5. implement angular integration of a fiber strain-energy function;
6. verify normalization, tensor identities, and quadrature convergence;
7. interpret stress–stretch curves for aligned and oblique fiber families;
8. distinguish the tutorial concentration parameter from constitutive dispersion parameters used in other models;
9. design a research extension using image-derived orientation data.

## Prerequisites

- Tutorial 01 or familiarity with axial fiber angles;
- probability densities and numerical integration;
- basic tensor notation;
- strain energy and uniaxial stretch;
- elementary Python, NumPy, SciPy, and Matplotlib.

## Tutorial map

1. [Motivation](chapters/01_motivation.md)
2. [Learning objectives and assessment](chapters/02_learning_objectives.md)
3. [Biological and mechanical background](chapters/03_biological_background.md)
4. [Mathematical model](chapters/04_mathematical_model.md)
5. [Numerical method and verification](chapters/05_numerical_method.md)
6. [Computational experiments](chapters/06_computational_experiments.md)
7. [Interpretation and limitations](chapters/07_interpretation.md)
8. [Further reading](chapters/08_further_reading.md)
9. [References](chapters/09_references.md)

## Quick start

From the repository root:

```bash
pip install -e .[dev]
make tutorial-02
pytest -q
```

Or run the notebook:

```bash
jupyter notebook tutorials/02-collagen-fiber-dispersion/notebooks/02_collagen_fiber_dispersion.ipynb
```

## Included experiments

| Experiment | Main output | Methodological purpose |
|---|---|---|
| Baseline overview | `figures/baseline.png` | Connect one distribution to one mechanical response |
| Distribution gallery | `figures/distribution_gallery.png` | Connect concentration, probability density, and sampled fibers |
| Tensor verification | `figures/tensor_verification.png` | Compare analytical and quadrature-based orientation tensors |
| Aligned loading | `figures/aligned_response.png` | Show loss of directional stiffness with increasing dispersion |
| Oblique loading | `figures/oblique_response.png` | Show that dispersion can increase load-bearing when the mean is oblique |
| Anisotropy map | `figures/anisotropy_map.png` | Map the joint effect of mean angle and concentration |
| Quadrature convergence | `figures/quadrature_convergence.png` | Verify numerical angular integration |
| Population animation | `animations/dispersion_transition.gif` | Visualize a synthetic transition from uniform to aligned fibers |

## Educational model boundary

The code implements a synthetic and dimensionless constitutive demonstration. It is inspired by structural constitutive modeling, angular integration, and distributed-fiber formulations, but it is **not calibrated or validated for a specific tissue**. The distribution parameter `concentration` is the axial von Mises concentration β used in this tutorial. It is not numerically interchangeable with the dispersion parameter κ in the three-dimensional Gasser–Ogden–Holzapfel formulation.

## Assessment structure

- [Explore](exercises/explore.md) — reproduce and explain;
- [Experiment](exercises/experiment.md) — modify and compare;
- [Research Challenge](exercises/research_challenge.md) — formulate and test a new hypothesis.

## Teaching use

See [instructor notes](instructor_notes.md) and the repository-level [120-minute master-class plan](../../workshop/instructor-materials/tutorial-02-masterclass.md).
