# Spatial heterogeneity and regularisation

A local growth law applied pointwise can generate sharp or noisy fields of \(J_g\). The tutorial uses a one-dimensional material line with heterogeneous homeostatic targets. Every point shares the same prescribed total deformation, so the example isolates constitutive heterogeneity from mechanical equilibrium.

A transparent regularized law adds

\[
D\,\frac{\partial^2\ln J_g}{\partial X^2}
\]

with zero-flux boundary conditions. The coefficient \(D\) suppresses small-scale oscillations but broadens interfaces and introduces a length scale.

This term is pedagogical. It can represent nonlocal signaling or serve as numerical regularisation, but those interpretations are not equivalent. A finite-element model should not add smoothing merely to hide mesh dependence; the physical or mathematical origin of the length scale must be stated.
