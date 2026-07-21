# 04 Isotropic and anisotropic growth tensors

An isotropic growth tensor has one scalar stretch:

\[
\mathbf F_g=\vartheta\mathbf I.
\]

A transversely isotropic tensor with reference fiber direction \(\mathbf a_0\) is

\[
\mathbf F_g=
\vartheta_f\,\mathbf a_0\otimes\mathbf a_0
+
\vartheta_t\left(\mathbf I-\mathbf a_0\otimes\mathbf a_0\right).
\]

Here \(\vartheta_f\) controls growth along the fiber and \(\vartheta_t\) controls the transverse plane. The special cases \(\vartheta_t=1\) and \(\vartheta_f=1\) represent purely longitudinal and purely transverse growth.

For an orthonormal material basis \(\mathbf Q=[\mathbf f_0\;\mathbf s_0\;\mathbf n_0]\), orthotropic growth is

\[
\mathbf F_g=
\mathbf Q
\operatorname{diag}(\vartheta_f,\vartheta_s,\vartheta_n)
\mathbf Q^T.
\]

This form is useful for myocardium, where fiber, sheet, and sheet-normal directions provide a natural local basis. It can represent eccentric-like and concentric-like growth patterns, but the labels should not be interpreted clinically unless parameters and stimuli are connected to data.

The determinant is the product of the principal growth stretches. An apparently volume-preserving change may still be strongly anisotropic. Conversely, equal principal growth stretches imply isotropy only in the selected configuration.

The tensor must remain positive definite in the symmetric growth models used here. The code updates growth through a matrix exponential and clips singular values only as a numerical safety bound. Such clipping must be reported because it changes the evolution law when a bound becomes active.
