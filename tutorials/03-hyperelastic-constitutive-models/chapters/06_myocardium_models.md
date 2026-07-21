# 06 — Myocardial models

Myocardium is described in a local orthonormal basis:

\[
\mathbf f_0,\qquad \mathbf s_0,\qquad \mathbf n_0,
\]

representing fiber, sheet, and sheet-normal directions.

## Guccione

The Green strain components in the material basis enter an exponential quadratic form:

\[
W=\frac{C}{2}\left(\exp Q-1\right).
\]

The parameters group fiber strain, transverse normal/shear strains, and fiber-transverse shear strains.

## Costa

The Costa form gives separate coefficients to the normal and shear components:

\[
Q=b_{ff}E_{ff}^2+b_{ss}E_{ss}^2+b_{nn}E_{nn}^2
+2b_{fs}E_{fs}^2+2b_{fn}E_{fn}^2+2b_{sn}E_{sn}^2.
\]

It is therefore more flexible but requires more information for parameter identification.

## Holzapfel–Ogden

A common structural form combines:

- an isotropic exponential matrix term;
- a fiber term based on \(I_{4f}\);
- a sheet term based on \(I_{4s}\);
- a fiber–sheet interaction based on \(I_{8fs}\).

The tutorial compares all three myocardial models in the \(f\!s\), \(f\!n\), and \(s\!n\) shear planes. These tests reveal anisotropic information that cannot be recovered from a single extension curve.
