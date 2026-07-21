# 9. Continuous orientation-distribution evolution

A continuously distributed architecture can remodel through an orientation-space conservation equation,

\[
\frac{\partial\rho}{\partial t}
=-\frac{\partial}{\partial\theta}(v_\theta\rho)
+D_r\frac{\partial^2\rho}{\partial\theta^2}.
\]

The drift velocity aligns fibers with a target direction,

\[
v_\theta=
\frac{k_a}{2}\sin\left[2(\theta_\star-\theta)\right],
\]

while \(D_r\) represents effective rotational spreading. It can stand for unresolved variability, heterogeneous cellular actions, or stochastic remodeling; it should not be interpreted as literal Brownian rotation of mature collagen unless supported by a specific scale model.

The equation conserves total probability on the periodic axial domain. It can change the mean direction and dispersion simultaneously and can represent broad or multimodal states. Its computational cost is greater than a one-angle model, and numerical schemes must preserve non-negativity and normalization.

The tutorial uses a positivity-corrected finite-volume drift–diffusion scheme and verifies probability conservation. A parameter map demonstrates competition between alignment and diffusion.
