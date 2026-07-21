# Kinematics and the scalar growth state

The finite-growth split remains

\[
\mathbf F=\mathbf F_e\mathbf F_g,
\qquad
\mathbf F_e=\mathbf F\mathbf F_g^{-1}.
\]

For isotropic volumetric growth,

\[
\mathbf F_g=g\mathbf I,
\qquad g=J_g^{1/3},
\qquad \det\mathbf F_g=J_g>0.
\]

The observable deformation \(\mathbf F\) and the internal growth state \(J_g\) play different roles. If \(\mathbf F=\mathbf F_g\), then \(\mathbf F_e=\mathbf I\) and homogeneous free growth is stress-free. If the body is constrained so that \(\mathbf F\neq\mathbf F_g\), elastic accommodation stores energy.

Using \(x=\ln J_g\) as the evolution variable is advantageous because any finite value of \(x\) corresponds to a positive volume ratio. The isotropic growth velocity gradient is

\[
\mathbf L_g=\dot{\mathbf F}_g\mathbf F_g^{-1}
=\frac{1}{3}\frac{d\ln J_g}{dt}\mathbf I.
\]

This identity is explicitly tested in the code.
