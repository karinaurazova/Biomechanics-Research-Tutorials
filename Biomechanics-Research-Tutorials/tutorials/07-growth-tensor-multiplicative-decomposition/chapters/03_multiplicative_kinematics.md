# 03 Multiplicative kinematics

Given \(\mathbf F\) and an internal growth tensor with positive determinant,

\[
\mathbf F_e=\mathbf F\mathbf F_g^{-1}.
\]

The determinants satisfy

\[
J=\det\mathbf F,
\qquad
J_e=\det\mathbf F_e,
\qquad
J_g=\det\mathbf F_g,
\qquad
J=J_eJ_g.
\]

This identity is a first-line verification test. It should hold pointwise to machine precision. It also clarifies interpretation. \(J_g\) describes the local change of natural volume in the selected growth model. \(J_e\) describes elastic volume change needed for compatibility and loading. The observed volume ratio \(J\) contains both.

For isotropic linear growth \(\vartheta\),

\[
\mathbf F_g=\vartheta\mathbf I,
\qquad
J_g=\vartheta^3.
\]

It is often safer to prescribe \(J_g\) and set \(\vartheta=J_g^{1/3}\), because this prevents confusion between linear and volumetric growth factors.

A material direction \(\mathbf a_0\) is pushed forward by a map \(\mathbf A\) as

\[
\mathbf a=\frac{\mathbf A\mathbf a_0}{\|\mathbf A\mathbf a_0\|}.
\]

Applying this formula separately to \(\mathbf F_g\) and \(\mathbf F\) reveals that growth-induced reorientation and final observed reorientation need not coincide. Elastic accommodation may rotate directions further.

All admissible tensors must preserve orientation: \(\det\mathbf F>0\), \(\det\mathbf F_g>0\), and \(\det\mathbf F_e>0\). The implementation rejects reflections and singular states rather than allowing an inverse to fail later in the calculation.
