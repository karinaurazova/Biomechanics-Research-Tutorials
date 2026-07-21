# 09 — Interpretation and limitations

## What the tutorial demonstrates

- Constitutive models that look similar in one loading mode may diverge in another.
- More parameters increase flexibility but also increase identifiability demands.
- Fiber angles and dispersion can change the apparent macroscopic stiffness without changing matrix parameters.
- Myocardial shear planes contain independent information about orthotropy.
- Verification and validation are different activities.

## What the tutorial does not demonstrate

- It does not identify parameters from experimental data.
- It does not establish that one model is best for a specific tissue.
- It does not include viscoelasticity, damage, hysteresis, growth, remodeling, active contraction, or residual stress.
- It does not derive complete Cauchy or Piola stress tensors for finite-element use.
- It does not address convexity, polyconvexity, ellipticity, or global numerical robustness for every parameter set.

## Model-selection checklist

Before selecting a law, specify:

1. tissue and physiological state;
2. deformation range;
3. relevant loading modes;
4. material symmetry;
5. compressibility assumption;
6. available experimental observables;
7. parameter constraints and identifiability;
8. verification tests;
9. validation data not used for calibration;
10. intended extrapolation domain.
