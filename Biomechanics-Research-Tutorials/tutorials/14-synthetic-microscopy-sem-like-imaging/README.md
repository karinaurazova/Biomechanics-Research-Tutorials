# Tutorial 14 — Synthetic Microscopy and SEM-Like Imaging

This tutorial turns explicit synthetic fibrous microstructure into synchronized virtual observations: bright-field-like transmission, wide-field fluorescence, confocal-like stacks, orientation-sensitive SHG-like images, SEM-like topographic/compositional contrast, and FIB-SEM-like serial sections.

## Learning goals

- distinguish latent structure from the observation process;
- model PSF blur, photon/read noise, background, saturation, and bleaching;
- compare optical and electron-microscopy-inspired contrast mechanisms;
- generate 2-D and 3-D acquisition artifacts with exact ground truth;
- design calibration targets, domain shifts, and verification metrics;
- export synchronized multimodal datasets for segmentation, DIC, and inverse mechanics.

## Scientific scope

The optical models use transparent Gaussian-PSF and Poisson–Gaussian approximations. The SEM renderer is phenomenological: it combines surface-normal shading, edges, composition, charging-like brightness, blur, and noise. It is **not** a Monte Carlo electron–solid interaction solver. All datasets and parameters are synthetic and no experimental validation is claimed.

## Reproduce

```bash
python tutorials/14-synthetic-microscopy-sem-like-imaging/reproduce.py
```

## Contents

The tutorial includes 20 bilingual chapters, 22 paired static figures, four animations, an executed EN/RU notebook pair, a compressed multimodal NPZ dataset, a benchmark CSV, exercises, instructor notes, and workshop materials.
