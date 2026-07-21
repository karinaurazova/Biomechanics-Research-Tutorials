[English](index.md) | [Русский](ru/index.md)

# Biomechanics Research Tutorials documentation

This documentation page is the entry point for the repository site.  The tutorials are synthetic, reproducible educational modules for computational biomechanics of soft tissues.  They are intended for teaching, workshops, independent student projects and research-method training.

## Main navigation

- [Getting started](getting-started.md)
- [How the repository works](how-the-repository-works.md)
- [Development environments](development-environments.md)
- [Learning paths](learning-paths.md)
- [Teaching guide](teaching-guide.md)
- [Workshop materials](../workshop/README.md)
- [Glossary](glossary.md)
- [Release notes v1.0.0](release-v1.0.0.md)
- [Repository visual gallery](../VISUAL_GALLERY.md)
- [Tutorial index](../TUTORIAL_INDEX.md)

## Tutorial table

| No. | Tutorial | Block | Core focus |
|---:|---|---|---|
| 01 | [Fiber Reorientation](../tutorials/01-fiber-reorientation/README.md) | Foundations | How do fibers adapt to a prescribed mechanical cue? |
| 02 | [Collagen Fiber Dispersion](../tutorials/02-collagen-fiber-dispersion/README.md) | Foundations | How do orientation and dispersion affect mechanics? |
| 03 | [Hyperelastic Constitutive Models](../tutorials/03-hyperelastic-constitutive-models/README.md) | Foundations | How do common constitutive laws differ under controlled loading? |
| 04 | [Active and Passive Stress](../tutorials/04-active-passive-stress/README.md) | Foundations | How should active contraction be separated from passive response? |
| 05 | [Structure-Tensor Orientation](../tutorials/05-structure-tensor-orientation/README.md) | Foundations | How can local axial orientation be recovered and verified from images? |
| 06 | [Mechanical Homeostasis](../tutorials/06-mechanical-homeostasis/README.md) | Growth and remodeling | When does feedback restore a mechanical target, oscillate, or fail? |
| 07 | [Growth Tensor and Multiplicative Decomposition](../tutorials/07-growth-tensor-multiplicative-decomposition/README.md) | Growth and remodeling | How are local growth and elastic accommodation separated? |
| 08 | [Stress-Driven Volumetric Growth](../tutorials/08-stress-driven-volumetric-growth/README.md) | Growth and remodeling | How do stimulus choice and boundary control alter volumetric growth? |
| 09 | [Fiber-Family Remodeling](../tutorials/09-fiber-family-remodeling/README.md) | Growth and remodeling | How do rotation, ODF evolution, recruitment, and turnover differ? |
| 10 | [Extracellular-Matrix Turnover](../tutorials/10-extracellular-matrix-turnover/README.md) | Growth and remodeling | How do synthesis, degradation, maturation, cross-links, and mechanics interact? |
| 11 | [Constrained-Mixture Toy Model](../tutorials/11-constrained-mixture-toy-model/README.md) | Growth and remodeling | How do constituent histories and natural states shape mixture mechanics? |
| 12 | [Residual Stress and Ring Opening](../tutorials/12-residual-stress-ring-opening/README.md) | Growth and remodeling | How can release geometry reveal incompatible natural configurations? |
| 13 | [Synthetic Fibrous-Tissue Generation](../tutorials/13-synthetic-fibrous-tissue-generation/README.md) | Image-informed and experimental mechanics | How can image-analysis pipelines be verified against known microstructure? |
| 14 | [Synthetic Microscopy and SEM-Like Imaging](../tutorials/14-synthetic-microscopy-sem-like-imaging/README.md) | Image-informed and experimental mechanics | How do imaging physics and artifacts alter observed microstructure? |
| 15 | [Polarization-Like Orientation Maps](../tutorials/15-polarization-like-orientation-maps/README.md) | Image-informed and experimental mechanics | How can axial orientation be recovered from angular image series? |
| 16 | [Synthetic Digital Image Correlation](../tutorials/16-synthetic-digital-image-correlation/README.md) | Image-informed and experimental mechanics | How can displacement and strain recovery be verified from exact synthetic images? |
| 17 | [Microstructure Segmentation: Classical Methods, SAM and μSAM](../tutorials/17-microstructure-segmentation-sam-usam/README.md) | Image-informed and experimental mechanics | How do classical, learnable and prompt-based methods compare under structural metrics? |
| 18 | [Orientation Distributions and Concentration Parameters](../tutorials/18-orientation-distributions-concentration/README.md) | Image-informed and experimental mechanics | How consistently is one architecture recovered from ground truth, SEM-like, polarization-like and segmented-mask modalities? |
| 19 | [Image-Informed Constitutive Parameters](../tutorials/19-image-informed-constitutive-parameters/README.md) | Image-informed and experimental mechanics | How can image-derived structure, DIC strain fields and force data identify material parameters? |
| 20 | [Multimodal Verification-Ready Synthetic Benchmark](../tutorials/20-multimodal-verification-ready-benchmark/README.md) | Image-informed and experimental mechanics | Can the full image-to-mechanics pipeline recover known masks, orientations, strains, forces and parameters? |
| 21 | [Finite-Element Growth Model](../tutorials/21-finite-element-growth-model/README.md) | Advanced computational methods | How does incompatible growth become elastic accommodation, residual stress and feedback in a finite-element model? |
| 22 | [RVE Homogenization](../tutorials/22-rve-homogenization/README.md) | Advanced computational methods | How does a heterogeneous fiber network become an effective stiffness tensor? |
| 23 | [Surrogate Modeling for Homogenized Tissue Mechanics](../tutorials/23-surrogate-modeling-homogenized-tissue-mechanics/README.md) | Advanced computational methods | How can expensive RVE/FE simulations be replaced by tested, mechanics-aware surrogate models? |
| 24 | [Physics-Informed Learning for Soft-Tissue Mechanics](../tutorials/24-physics-informed-learning-soft-tissue-mechanics/README.md) | Advanced computational methods | How can sparse data, boundary conditions and equilibrium residuals be combined in a transparent PINN-like benchmark? |
| 25 | [Sensitivity Analysis and Uncertainty Quantification](../tutorials/25-sensitivity-analysis-uncertainty-quantification/README.md) | Advanced computational methods | Which uncertain inputs actually control predicted stiffness, stress, energy and reliability? |

## Repository principles

- Synthetic data are used by default so that ground truth is known.
- Bilingual English/Russian materials share the same computations and code.
- Figures and GIF animations are localized when they contain explanatory labels.
- Each tutorial should separate verification from validation and state limitations explicitly.
- Reproducibility is part of the lesson: `reproduce.py`, tests, notebooks and saved benchmark tables are all part of the teaching material.
