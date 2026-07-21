# 03 — Finite-strain kinematics

The deformation gradient is

\[
\mathbf F=\frac{\partial \mathbf x}{\partial \mathbf X},
\qquad J=\det\mathbf F>0.
\]

The right Cauchy–Green tensor is

\[
\mathbf C=\mathbf F^T\mathbf F.
\]

To separate distortional and volumetric effects, the tutorial uses

\[
\bar{\mathbf C}=J^{-2/3}\mathbf C,
\]

with invariants

\[
\bar I_1=\operatorname{tr}\bar{\mathbf C},
\qquad
\bar I_2=\frac12\left[(\operatorname{tr}\bar{\mathbf C})^2-
\operatorname{tr}(\bar{\mathbf C}^2)\right].
\]

The isochoric principal stretches satisfy

\[
\bar\lambda_i=J^{-1/3}\lambda_i,
\qquad
\bar\lambda_1\bar\lambda_2\bar\lambda_3=1.
\]

## Loading paths

The repository includes the following homogeneous paths:

- incompressible uniaxial stretch
  \(\mathbf F=\operatorname{diag}(\lambda,\lambda^{-1/2},\lambda^{-1/2})\);
- equibiaxial stretch
  \(\mathbf F=\operatorname{diag}(\lambda,\lambda,\lambda^{-2})\);
- plane strain
  \(\mathbf F=\operatorname{diag}(\lambda,1,\lambda^{-1})\);
- simple shear in the \(xy\), \(xz\), or \(yz\) plane;
- volumetric dilation
  \(\mathbf F=J^{1/3}\mathbf I\).

These paths are not complete boundary-value problems. They are controlled kinematic probes used to expose differences among energy functions.
