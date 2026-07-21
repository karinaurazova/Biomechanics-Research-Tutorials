# 05 Elastic response and stress measures

The elastic constitutive law is evaluated using \(\mathbf F_e\), not the total \(\mathbf F\). Tutorial 07 uses a compressible neo-Hookean energy per unit grown stress-free volume,

\[
W(\mathbf F_e)=
\frac{\mu}{2}
\left(I_{1e}-3-2\ln J_e\right)
+
\frac{\kappa}{2}(\ln J_e)^2.
\]

To express energy per original reference volume, the tutorial adopts

\[
\Psi(\mathbf F,\mathbf F_g)=J_g W(\mathbf F_e).
\]

This convention produces

\[
\mathbf P=J_g\mathbf P_e\mathbf F_g^{-T},
\]

where \(\mathbf P_e=\partial W/\partial\mathbf F_e\). Other growth formulations use different reference-volume conventions. A code base must state its choice explicitly because the resulting nominal stress changes.

The Cauchy stress follows from the elastic response,

\[
\boldsymbol\sigma=rac{1}{J_e}\mathbf P_e\mathbf F_e^T.
\]

The Mandel stress is

\[
\mathbf M=\mathbf F_e^T\mathbf P_e.
\]

It is work-conjugate to a growth velocity gradient in many thermodynamic derivations and is therefore a natural driver for stress-mediated growth.

Two verification tests are essential. First, superposing a rigid rotation on the current configuration must not change the stored energy. Second, a finite-difference derivative of \(\Psi\) with respect to \(\mathbf F\) must agree with the implemented \(\mathbf P\). Both tests are automated in this repository.
