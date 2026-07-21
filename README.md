> “Above law there can only be love; above right, only mercy; above justice, only forgiveness. Much in this world has limits, but mercy has no limit.”
> — Patriarch Alexy II
[English](README.md) | [Русский](README.ru.md)

# Biomechanics Research Tutorials

**Biomechanics Research Tutorials** is a reproducible educational repository on computational biomechanics of soft tissues.  It contains 25 self-contained tutorials that connect biological motivation, mathematical models, numerical methods, Python implementations, tests, synthetic data, figures and bilingual teaching notes.

## What this repository is for

The repository is designed as a teaching and research-training resource.  Each tutorial can be used as a short lesson, a workshop unit, a reproducible mini-study, or a starting point for a student project.  The modules are intentionally universal: they are not tied to one thesis topic, one tissue type or one dataset.

All generated data are synthetic unless a tutorial explicitly says otherwise.  Synthetic examples are used so that masks, orientations, material parameters, deformation fields and benchmark targets can be known exactly.

## Start here

New users should begin with [START_HERE.md](START_HERE.md).  The shortest path is:

```bash
python3 scripts/setup_venv.py
python scripts/verify_repository.py --strict
python scripts/run_reproduce_selected.py 01 13 17 22 25
```

For Anaconda, VS Code, Visual Studio, Windows, Linux and macOS setup instructions, see [docs/development-environments.md](docs/development-environments.md).

## Repository structure

```text
Biomechanics-Research-Tutorials/
├── tutorials/              # 25 independent tutorial modules
├── src/biomechanics_tutorials/
├── tests/                  # repository-level tests
├── docs/                   # English documentation
├── docs/ru/                # Russian documentation
├── assets/shared-figures/  # release-level overview figures and GIFs
└── scripts/                # setup, verification and reproduction helpers
```

The package `biomechanics_tutorials` is local to this repository.  It is not an external dependency.

## Tutorial map

| No. | Tutorial | Section | Main question |
|---:|---|---|---|
| 01 | [Fiber Reorientation](tutorials/01-fiber-reorientation/README.md) | Foundations | How do fibers adapt to a prescribed mechanical cue? |
| 02 | [Collagen Fiber Dispersion](tutorials/02-collagen-fiber-dispersion/README.md) | Foundations | How do orientation and dispersion affect mechanics? |
| 03 | [Hyperelastic Constitutive Models](tutorials/03-hyperelastic-constitutive-models/README.md) | Foundations | How do common constitutive laws differ under controlled loading? |
| 04 | [Active and Passive Stress](tutorials/04-active-passive-stress/README.md) | Foundations | How should active contraction be separated from passive response? |
| 05 | [Structure-Tensor Orientation](tutorials/05-structure-tensor-orientation/README.md) | Foundations | How can local axial orientation be recovered and verified from images? |
| 06 | [Mechanical Homeostasis](tutorials/06-mechanical-homeostasis/README.md) | Growth and remodeling | When does feedback restore a mechanical target, oscillate, or fail? |
| 07 | [Growth Tensor and Multiplicative Decomposition](tutorials/07-growth-tensor-multiplicative-decomposition/README.md) | Growth and remodeling | How are local growth and elastic accommodation separated? |
| 08 | [Stress-Driven Volumetric Growth](tutorials/08-stress-driven-volumetric-growth/README.md) | Growth and remodeling | How do stimulus choice and boundary control alter volumetric growth? |
| 09 | [Fiber-Family Remodeling](tutorials/09-fiber-family-remodeling/README.md) | Growth and remodeling | How do rotation, ODF evolution, recruitment, and turnover differ? |
| 10 | [Extracellular-Matrix Turnover](tutorials/10-extracellular-matrix-turnover/README.md) | Growth and remodeling | How do synthesis, degradation, maturation, cross-links, and mechanics interact? |
| 11 | [Constrained-Mixture Toy Model](tutorials/11-constrained-mixture-toy-model/README.md) | Growth and remodeling | How do constituent histories and natural states shape mixture mechanics? |
| 12 | [Residual Stress and Ring Opening](tutorials/12-residual-stress-ring-opening/README.md) | Growth and remodeling | How can release geometry reveal incompatible natural configurations? |
| 13 | [Synthetic Fibrous-Tissue Generation](tutorials/13-synthetic-fibrous-tissue-generation/README.md) | Image-informed and experimental mechanics | How can image-analysis pipelines be verified against known microstructure? |
| 14 | [Synthetic Microscopy and SEM-Like Imaging](tutorials/14-synthetic-microscopy-sem-like-imaging/README.md) | Image-informed and experimental mechanics | How do imaging physics and artifacts alter observed microstructure? |
| 15 | [Polarization-Like Orientation Maps](tutorials/15-polarization-like-orientation-maps/README.md) | Image-informed and experimental mechanics | How can axial orientation be recovered from angular image series? |
| 16 | [Synthetic Digital Image Correlation](tutorials/16-synthetic-digital-image-correlation/README.md) | Image-informed and experimental mechanics | How can displacement and strain recovery be verified from exact synthetic images? |
| 17 | [Microstructure Segmentation: Classical Methods, SAM and μSAM](tutorials/17-microstructure-segmentation-sam-usam/README.md) | Image-informed and experimental mechanics | How do classical, learnable and prompt-based methods compare under structural metrics? |
| 18 | [Orientation Distributions and Concentration Parameters](tutorials/18-orientation-distributions-concentration/README.md) | Image-informed and experimental mechanics | How consistently is one architecture recovered from ground truth, SEM-like, polarization-like and segmented-mask modalities? |
| 19 | [Image-Informed Constitutive Parameters](tutorials/19-image-informed-constitutive-parameters/README.md) | Image-informed and experimental mechanics | How can image-derived structure, DIC strain fields and force data identify material parameters? |
| 20 | [Multimodal Verification-Ready Synthetic Benchmark](tutorials/20-multimodal-verification-ready-benchmark/README.md) | Image-informed and experimental mechanics | Can the full image-to-mechanics pipeline recover known masks, orientations, strains, forces and parameters? |
| 21 | [Finite-Element Growth Model](tutorials/21-finite-element-growth-model/README.md) | Advanced computational methods | How does incompatible growth become elastic accommodation, residual stress and feedback in a finite-element model? |
| 22 | [RVE Homogenization](tutorials/22-rve-homogenization/README.md) | Advanced computational methods | How does a heterogeneous fiber network become an effective stiffness tensor? |
| 23 | [Surrogate Modeling for Homogenized Tissue Mechanics](tutorials/23-surrogate-modeling-homogenized-tissue-mechanics/README.md) | Advanced computational methods | How can expensive RVE/FE simulations be replaced by tested, mechanics-aware surrogate models? |
| 24 | [Physics-Informed Learning for Soft-Tissue Mechanics](tutorials/24-physics-informed-learning-soft-tissue-mechanics/README.md) | Advanced computational methods | How can sparse data, boundary conditions and equilibrium residuals be combined in a transparent PINN-like benchmark? |
| 25 | [Sensitivity Analysis and Uncertainty Quantification](tutorials/25-sensitivity-analysis-uncertainty-quantification/README.md) | Advanced computational methods | Which uncertain inputs actually control predicted stiffness, stress, energy and reliability? |

## Visual and language policy

The repository is bilingual.  English and Russian materials share the same computations, code and numerical results.  See [LANGUAGE_POLICY.md](LANGUAGE_POLICY.md)

## Learning paths

The 25 tutorials are grouped into four learning blocks:

| Tutorials | Block | Purpose |
|---|---|---|
| 01–05 | Foundations | orientation, dispersion, hyperelasticity, active stress and structure tensors |
| 06–12 | Growth and remodeling | homeostasis, growth tensors, remodeling, turnover, mixtures and residual stress |
| 13–20 | Image-informed and experimental mechanics | synthetic images, DIC, segmentation, ODFs, image-informed parameters and multimodal verification |
| 21–25 | Advanced computational methods | FE growth, RVE homogenization, surrogates, physics-informed learning and uncertainty quantification |

Detailed routes are given in [docs/learning-paths.md](docs/learning-paths.md).

## Reproducibility policy

Every tutorial is expected to provide:

- a clear mathematical model and assumptions;
- a reproducible Python implementation;
- synthetic data or explicit data-generation code;
- saved figures and tables regenerated by `reproduce.py`;
- tests or numerical sanity checks;
- English and Russian teaching materials.

Tutorial outputs are educational computational demonstrations.  They must not be presented as experimental or clinical validation unless a future module explicitly includes such validation.

## Core reference files

- [START_HERE.md](START_HERE.md) — first steps for new users.
- [TUTORIAL_INDEX.md](TUTORIAL_INDEX.md) — compact index of all tutorials.
- [ROADMAP.md](ROADMAP.md) — educational roadmap.
- [RELEASE_NOTES_v1.0.0.md](RELEASE_NOTES_v1.0.0.md) — public release notes.
- [workshop/README.md](workshop/README.md) — reusable master-class materials.


## Citation and license

Citation metadata are provided in [CITATION.cff](CITATION.cff).  Code and educational materials are released under the MIT License unless otherwise stated.
