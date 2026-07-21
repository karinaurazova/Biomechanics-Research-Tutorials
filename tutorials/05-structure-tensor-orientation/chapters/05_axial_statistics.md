# 05 Axial orientation and confidence

A fiber axis has no arrow: $\theta$ and $\theta+\pi$ are equivalent. Differences must therefore be computed with doubled angles:

$$
\Delta\theta=\frac12\operatorname{atan2}
\left[\sin 2(\theta_1-\theta_2),\cos 2(\theta_1-\theta_2)\right].
$$

Coherence is defined as

$$
c=\frac{\lambda_1-\lambda_2}{\lambda_1+\lambda_2+\varepsilon}.
$$

It measures directional dominance, not biological certainty. A confidence mask should combine coherence with tensor energy, because a uniform dark region can otherwise receive a numerically unstable angle. Coverage must be reported together with error: a strict threshold can improve MAE simply by discarding difficult pixels.
