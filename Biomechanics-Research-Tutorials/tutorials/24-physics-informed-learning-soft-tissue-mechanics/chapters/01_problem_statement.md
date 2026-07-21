# Problem statement

Physics-informed learning is introduced here as a constrained reconstruction problem. We know a few noisy displacement values, we know the differential equation that should hold inside the tissue, and we know part of the boundary loading. The learner is not allowed to be only an interpolator. It must produce a field whose derivative and stress are mechanically plausible.

The benchmark is a one-dimensional bar because the mechanics can be checked exactly. This is not a limitation of the concept; it is a teaching choice. In a 2D or 3D PINN the same ideas appear, but the notation and computational cost can hide the central mechanism. Here every term in the loss has a visible mechanical meaning.

The governing equilibrium equation is `d/dx(E(x) du/dx)=0`. The stiffness field `E(x)` is not constant. It is obtained from synthetic fibre descriptors, so the tutorial connects image-informed modelling with physics-informed learning.
