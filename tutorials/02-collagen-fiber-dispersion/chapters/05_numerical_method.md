[English](05_numerical_method.md) | [Русский](ru/05_numerical_method.md)

# 5. Numerical method and verification

## 5.1 Angular quadrature

The interval $[-\pi/2,\pi/2]$ is discretized using an odd number of equally spaced points. Integrals are evaluated with the composite trapezoidal rule.

For smooth periodic densities, convergence is rapid, but a visually smooth curve is not evidence of sufficient resolution. The tutorial therefore compares tensor and stress results across multiple quadrature sizes.

## 5.2 Analytical checks

The implementation has several exact or near-exact verification targets:

1. $\int\rho\,d\theta=1$;
2. $\rho(\theta+\pi)=\rho(\theta)$;
3. $\operatorname{tr}\mathbf{A}=1$;
4. $\mathbf{A}=\tfrac12\mathbf{I}$ when $\beta=0$;
5. numerical and analytical orientation tensors agree;
6. $\Psi(1)=0$ and $P(1)=0$ for the chosen reference state.

## 5.3 Stress evaluation

The nominal stress is evaluated from the analytical derivative of the implemented energy rather than from noisy finite differences. A finite-difference comparison can still be used as an additional learner exercise.

## 5.4 Convergence metric

For a reference solution $P_{\mathrm{ref}}$ computed with a dense grid, define

$$
\varepsilon_N
=
\max_{\lambda}
\left|P_N(\lambda)-P_{\mathrm{ref}}(\lambda)\right|.
$$

The convergence experiment reports $\varepsilon_N$ as the number of angular points $N$ increases.

## 5.5 Verification versus validation

Passing normalization, tensor, and quadrature tests verifies that the equations are implemented consistently. It does not show that the chosen density, energy, or parameter values represent a real artery, tendon, valve, skin specimen, or myocardium sample.
