# 7. Lanir-type structural integration

Lanir's structural theory treats fibrous tissue as a composite whose macroscopic response emerges from directional constituents and their statistical distributions. In a planar reduction,

\[
\Psi_f(\mathbf F)=
\int_{-\pi/2}^{\pi/2}
\rho(\theta)\,
\psi_f\!\left(\sqrt{\mathbf a_0(\theta)\cdot\mathbf C\mathbf a_0(\theta)}\right)
\,d\theta.
\]

This formulation has several advantages:

- multimodal distributions can be represented explicitly;
- tension-only activation is applied direction by direction;
- image-derived orientation histograms can enter the model directly;
- changes in the distribution can be separated from changes in fiber material properties.

The cost is angular quadrature and a larger internal state if the distribution evolves. Numerical accuracy depends on angular resolution, especially for sharply concentrated distributions and near recruitment thresholds.

The tutorial compares full angular integration with discrete families and with a generalized structure-tensor closure. It shows that the latter can be efficient but may not reproduce every distribution shape or directional activation pattern.
