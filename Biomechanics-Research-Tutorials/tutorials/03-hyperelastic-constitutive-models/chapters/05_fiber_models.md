# 05 — Fiber-reinforced models

A reference fiber direction \(\mathbf a_0\) defines the structural invariant

\[
\bar I_4=\mathbf a_0\cdot\bar{\mathbf C}\mathbf a_0.
\]

The corresponding fiber stretch is \(\sqrt{\bar I_4}\).

## Tension-only exponential family

The tutorial uses

\[
W_f=\frac{k_1}{2k_2}
\left[\exp\left(k_2\langle \bar I_4-1\rangle_+^2\right)-1\right],
\]

where \(\langle x\rangle_+=\max(x,0)\). This switch prevents an idealized collagen family from carrying compressive energy.

## HGO with two symmetric families

Two directions at \(+\alpha\) and \(-\alpha\) are combined with an isotropic matrix. Changing \(\alpha\) changes recruitment under a fixed loading direction.

## GOH dispersion

The dispersed measure is

\[
E_\kappa=
\kappa(\bar I_1-3)
+(1-3\kappa)(\bar I_4-1),
\qquad 0\le\kappa\le\frac13.
\]

At \(\kappa=0\), the family is perfectly aligned. At \(\kappa=1/3\), its directional contribution becomes isotropically dispersed in the second-order approximation.

The GOH parameter \(\kappa\) is not the same quantity as the axial von Mises concentration \(\beta\) used in Tutorial 02. Their ranges, definitions, and statistical interpretations differ.
