# Affine subset kinematics

A translation-only subset cannot represent local stretch, shear, or rotation. The six-parameter affine shape function adds four displacement gradients to the two center translations. Nonlinear least squares then minimizes the normalized intensity residual.

Affine parameters are local approximations. They do not imply that the entire specimen deforms affinely, and they can become biased when gradients vary substantially across the subset. Higher-order shape functions increase flexibility but also require more texture and more stable optimization.
