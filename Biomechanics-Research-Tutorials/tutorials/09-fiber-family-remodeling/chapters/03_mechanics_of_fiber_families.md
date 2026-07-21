# 3. Mechanics of fiber families

For a planar fiber direction

\[
\mathbf a_0(\theta)=
\begin{bmatrix}
\cos\theta\\
\sin\theta
\end{bmatrix},
\]

the affine fiber stretch is

\[
\lambda_f(\theta)=\sqrt{\mathbf a_0\cdot\mathbf C\mathbf a_0},
\qquad
\mathbf C=\mathbf F^T\mathbf F.
\]

Collagen is commonly idealized as carrying tensile load but negligible compressive load. The tutorial therefore uses a tension-only exponential energy. The exact parameter values are synthetic; the purpose is to expose the structural role of direction and recruitment.

A discrete-family model writes

\[
\Psi_f=\sum_{i=1}^{N_f}\phi_i\,\psi_f(\lambda_{f,i}),
\]

where \(\phi_i\) is a family weight or mass fraction. A continuously distributed model writes

\[
\Psi_f=\int_{-\pi/2}^{\pi/2}
\rho(\theta)\,\psi_f(\lambda_f(\theta))\,d\theta.
\]

The two expressions become close when the discrete quadrature resolves the orientation density. They are not automatically equivalent when only two families are retained, when the distribution is multimodal, or when tension-only activation creates sharp directional transitions.

Mechanically, remodeling can change at least five independent features: mean direction, angular dispersion, total fiber mass, slack-stretch distribution, and deposition stretch. Each affects the stress–stretch curve differently. This is why one uniaxial curve rarely identifies all remodeling variables uniquely.
