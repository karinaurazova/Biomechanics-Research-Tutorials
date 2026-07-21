# Synthetic forward model


The forward model creates an anisotropic plane-stress stiffness tensor from structural descriptors.  Fiber orientation controls the direction of reinforcement, concentration controls the degree of alignment, fiber fraction controls the reinforcement magnitude, and porosity reduces the matrix contribution.

The formula is intentionally synthetic.  It should not be reported as a validated constitutive law.  Its purpose is educational: it creates nonlinear, coupled, anisotropic data with known ground truth.  That makes it possible to test whether surrogate diagnostics detect interpolation, extrapolation and uncertainty problems.

A real version of this module would replace the synthetic formula by calls to an RVE solver from Tutorial 22, a finite-element code, or an experimentally calibrated forward model.
