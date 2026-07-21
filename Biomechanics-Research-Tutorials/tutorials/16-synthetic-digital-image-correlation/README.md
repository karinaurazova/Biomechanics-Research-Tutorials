# Tutorial 16 — Synthetic Digital Image Correlation

This tutorial develops a transparent synthetic 2D digital image correlation pipeline with exact ground truth. It generates reference textures, prescribes displacement fields, warps images, estimates local displacement by subset correlation, performs subpixel and affine refinement, recovers strain fields, and quantifies uncertainty and failure modes.

## Learning goals

- distinguish image formation, displacement estimation, interpolation, and strain recovery;
- generate controlled speckle and natural-texture surrogates;
- implement ZNCC/ZNSSD subset matching and subpixel peak refinement;
- compare translation and affine subset kinematics;
- verify small-strain and Green–Lagrange measures;
- study subset size, step, speckle scale, noise, blur, boundaries, and discontinuities;
- export synthetic DIC datasets with exact displacement fields and explicit provenance.

## Scientific scope

The implementation is an educational local 2D baseline. It is not a replacement for Ncorr, OpenCorr, μDIC, stereo-DIC, or digital volume correlation. All images, displacement fields, parameters, and benchmarks are synthetic. No experimental, clinical, or material validation is claimed.

## Reproduce

```bash
python tutorials/16-synthetic-digital-image-correlation/reproduce.py
```

## Contents

The tutorial contains 22 bilingual chapters, 25 paired static figures, two GIF animations, an executed EN/RU notebook pair, a synthetic NPZ dataset, a six-case verification benchmark, exercises, instructor notes, and workshop materials.
