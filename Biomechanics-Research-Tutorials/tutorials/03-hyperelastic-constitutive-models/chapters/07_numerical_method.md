# 07 — Numerical method and verification

For a scalar path parameter \(q\), the generalized response is

\[
R(q)=\frac{d}{dq}W(\mathbf F(q)).
\]

The implementation uses a centred finite difference:

\[
R(q)\approx
\frac{W(\mathbf F(q+h))-W(\mathbf F(q-h))}{2h}.
\]

## Verification

For the incompressible Neo-Hookean uniaxial path,

\[
P(\lambda)=\mu\left(\lambda-\lambda^{-2}\right).
\]

The numerical derivative is compared with this analytical expression over a range of stretches and finite-difference steps.

## Objectivity

A superposed spatial rigid rotation \(\mathbf Q\) gives

\[
\mathbf F^*=\mathbf Q\mathbf F,
\qquad
\mathbf C^*=\mathbf F^{*T}\mathbf F^*=\mathbf C.
\]

Therefore an objective hyperelastic energy must satisfy

\[
W(\mathbf Q\mathbf F)=W(\mathbf F).
\]

The repository checks this property numerically for all sixteen models.

## Volumetric penalties

The distortional energies use \(\bar{\mathbf C}\). Volume change is studied separately with:

\[
U_q=\frac{K}{2}(J-1)^2,
\]

\[
U_{\log}=\frac{K}{2}(\ln J)^2,
\]

\[
U_{ST}=\frac{K}{4}(J^2-1-2\ln J).
\]

Large \(K\) approximates near-incompressibility but can also create numerical conditioning difficulties in finite-element formulations.
