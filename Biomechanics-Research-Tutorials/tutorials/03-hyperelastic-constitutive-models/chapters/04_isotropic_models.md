# 04 — Isotropic models

For isotropic materials, the energy depends on invariants or principal stretches and is unchanged by rigid rotation.

## Neo-Hookean

\[
W=\frac{\mu}{2}(\bar I_1-3).
\]

It is the simplest baseline and has a constant small-strain shear modulus.

## Mooney–Rivlin

\[
W=C_{10}(\bar I_1-3)+C_{01}(\bar I_2-3).
\]

The second invariant allows more flexibility across different deformation modes.

## Yeoh

\[
W=C_1X+C_2X^2+C_3X^3,
\qquad X=\bar I_1-3.
\]

The model uses only the first invariant but introduces higher-order nonlinearity.

## Second-order Rivlin polynomial

\[
W=C_{10}X+C_{01}Y+C_{20}X^2+C_{11}XY+C_{02}Y^2,
\]

where \(Y=\bar I_2-3\).

## Gent

\[
W=-\frac{\mu J_m}{2}
\ln\left(1-\frac{\bar I_1-3}{J_m}\right).
\]

The energy diverges when \(\bar I_1-3\to J_m\), representing limiting extensibility.

## Arruda–Boyce

The eight-chain model is represented here by a five-term series in \(\bar I_1\). The chain parameter controls the onset of finite-chain stiffening. The tutorial explicitly labels this implementation as a truncated approximation.

## Ogden

\[
W=\sum_{p=1}^{N}\frac{2\mu_p}{\alpha_p^2}
\left(\bar\lambda_1^{\alpha_p}+
\bar\lambda_2^{\alpha_p}+
\bar\lambda_3^{\alpha_p}-3\right).
\]

The exponents \(\alpha_p\) strongly influence tension–compression asymmetry and curvature.

## Demiray

\[
W=\frac{a}{2b}\left[\exp\left(b(\bar I_1-3)\right)-1\right].
\]

This exponential form produces progressive stiffening with one invariant.

## Veronda–Westmann

\[
W=C_1\left[\exp(C_2(\bar I_1-3))-1\right]
-\frac{C_1C_2}{2}(\bar I_2-3).
\]

The model combines an exponential first-invariant term with a second-invariant correction.

No model in this list is universally superior. Their usefulness depends on loading modes, parameter range, tissue structure, and the intended simulation.
