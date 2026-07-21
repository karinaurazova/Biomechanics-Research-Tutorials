# 03 Synthetic fiber images

The generators use periodic Gaussian ridges. For a straight family with tangent angle $\theta$, the ridge phase is measured along the normal

$$
q(x,y)=-x\sin\theta+y\cos\theta.
$$

The distance to the nearest periodic centerline is converted into intensity with a Gaussian profile. Curved fields use an analytical phase function, allowing the tangent orientation to be obtained from its derivative. Piecewise fields, radial fans, uneven illumination, noise, and two superposed families are added as controlled complications.

Synthetic truth is not a substitute for experimental validation. It is a way to test whether the implementation recovers what was deliberately encoded.
