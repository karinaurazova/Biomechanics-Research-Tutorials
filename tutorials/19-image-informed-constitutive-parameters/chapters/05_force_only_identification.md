# 05 — Force-only identification

The simplest calibration uses only global force components. For each load case the model predicts

```text
y_i = average(sigma_i) = average(B_i) p.
```

Stacking all load cases gives a linear system:

```text
A p ≈ y.
```

The tutorial solves this with non-negative least squares. The non-negativity constraint is not a universal law, but it prevents unphysical negative stiffnesses in this demonstration.

Force-only calibration is useful but limited. It can recover parameters when the load cases are diverse, but it may be poorly conditioned when the observations are insensitive to one parameter or when two parameters compensate for each other.
