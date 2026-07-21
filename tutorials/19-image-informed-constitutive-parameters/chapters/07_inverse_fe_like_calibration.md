# 07 — Inverse-FE-like calibration loop

Production inverse finite-element calibration usually follows this loop:

1. choose a parameter vector;
2. run a forward mechanical simulation;
3. compare predicted and measured forces or displacements;
4. update the parameters;
5. repeat until the residual is acceptable.

Tutorial 19 uses the same control flow but replaces the expensive FE solve with a transparent analytical forward model. The optimizer works in log-parameter space so that stiffness parameters remain positive.

This is not a substitute for inverse FE. It is a safe educational bridge: the learner sees the inverse-loop logic without needing meshing, nonlinear solvers or contact algorithms.
