# Tutorial 15 — Polarization-Like Orientation Maps

This tutorial develops a transparent synthetic forward-and-inverse pipeline for orientation-sensitive polarization imaging. Known fiber orientation, retardance, thickness, amplitude, illumination, blur, depolarization-like mixing, and noise are converted into angular image series and then recovered with a harmonic inverse model.

## Learning goals

- distinguish optical-axis orientation, birefringence, thickness, retardance, and observed intensity;
- derive and implement a reduced crossed-polarizer forward model;
- recover axial orientation, modulation, confidence, and residual maps;
- understand axial ambiguity, branch ambiguity, multilayer non-commutativity, and overlapping families;
- quantify the effects of angular sampling, noise, blur, illumination bias, and depolarization;
- export synthetic datasets with explicit provenance and known ground truth.

## Scientific scope

The reduced model uses a fourth-harmonic crossed-polarizer response and ideal Jones matrices for selected multilayer demonstrations. It is not a calibrated Mueller-matrix instrument model. Circular retardance, diattenuation, multiple scattering, depth mixing, and depolarization are represented only through controlled educational perturbations. All images and parameters are synthetic; no experimental or clinical validation is claimed.

## Reproduce

```bash
python tutorials/15-polarization-like-orientation-maps/reproduce.py
```

## Contents

The tutorial contains 20 bilingual chapters, 23 paired static figures, two GIF animations, an executed EN/RU notebook pair, an exported NPZ dataset, a synthetic verification benchmark, exercises, instructor notes, and workshop materials.
