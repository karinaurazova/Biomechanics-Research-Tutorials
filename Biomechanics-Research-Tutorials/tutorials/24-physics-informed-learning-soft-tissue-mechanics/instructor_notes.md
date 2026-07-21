# Instructor notes

This tutorial is designed as a bridge between inverse mechanics and PINNs.  Start from the data-only case and ask students why the displacement curve can look good while the strain field is unreliable.  Then introduce the PDE residual as a mechanical regularizer.  The random-feature implementation is intentionally less fashionable than a deep-learning framework, but it is much easier to inspect.

Suggested 90-minute class:

1. 15 min: review 1D equilibrium and boundary conditions.
2. 20 min: inspect the dataset and stiffness prior.
3. 20 min: derive the least-squares block system.
4. 20 min: run the case suite and interpret residual fields.
5. 15 min: discuss inverse calibration and identifiability.

Emphasize that a low physics residual is not experimental validation.  It only means that the learned field is consistent with the assumed physics.
