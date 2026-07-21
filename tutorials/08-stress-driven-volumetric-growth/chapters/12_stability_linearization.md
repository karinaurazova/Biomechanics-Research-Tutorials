# Closed-loop stability and linearisation

Let \(x=\ln J_g\) and \(\dot x=f(x)\) under fixed total deformation. At an equilibrium \(x_h\), local stability is governed by

\[
\lambda_{\mathrm{lin}}=\left.\frac{df}{dx}\right|_{x_h}.
\]

A negative value indicates local asymptotic stability in the scalar continuous-time problem. The code estimates this derivative by centered finite differences and tests the hydrostatic equilibrium.

The numerical map additionally depends on the time step. Even when the continuous system is stable, a coarse explicit discretization can oscillate or fail to settle. The gain–time-step map separates monotone convergence, oscillatory convergence and unresolved trajectories.

This analysis complements, but does not replace, the mechanobiological stability concepts introduced in Tutorial 06. Spatial mechanics and multiple internal variables can introduce additional eigenmodes.
