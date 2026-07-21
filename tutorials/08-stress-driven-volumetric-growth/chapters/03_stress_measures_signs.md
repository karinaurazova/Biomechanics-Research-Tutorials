# Stress measures, invariants, and sign conventions

A stress-driven law is incomplete until the stress measure is named. This tutorial compares mean Cauchy stress, mean Mandel stress, pressure, von Mises stress, maximum principal stress and elastic energy.

Tension is taken as positive:

\[
\sigma_m=\frac13\operatorname{tr}\boldsymbol\sigma,
\qquad p=-\sigma_m.
\]

Thus positive pressure denotes compression, while positive mean stress denotes tension. Confusing these conventions reverses the predicted direction of growth.

The von Mises measure

\[
\sigma_{\mathrm{vm}}
=\sqrt{\frac32\mathbf s:\mathbf s},
\qquad
\mathbf s=\boldsymbol\sigma-\sigma_m\mathbf I,
\]

is insensitive to hydrostatic stress. Conversely, a law driven only by mean stress cannot directly remove deviatoric distortion. The Mandel stress is useful because it is work-conjugate to an intermediate-configurational growth rate, but its biological interpretation must still be justified.

The module therefore treats stimulus selection as a model comparison, not as a hidden implementation detail.
