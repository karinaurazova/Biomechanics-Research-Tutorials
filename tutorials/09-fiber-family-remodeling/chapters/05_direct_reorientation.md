# 5. Direct reorientation of an existing family

A minimal direct-rotation law can be written as

\[
\dot\theta=
\frac{k_\theta}{2}
\sin\left[2(\theta_\star-\theta)\right],
\]

where \(\theta_\star\) is a selected mechanical direction. The doubled angle enforces axial periodicity. Kuhl and co-workers used a related first-order alignment concept in a finite-strain transversely isotropic network model.

This approach is attractive because it requires one internal angle per family and is straightforward to implement at a finite-element integration point. It is suitable when the research question is primarily about rotation of a preferred axis.

Its limitations are equally important:

- it rotates all pre-existing material as if fibers could reorganize without turnover;
- it does not automatically change mass, crimp, cross-linking, or natural stretch;
- an exactly orthogonal mismatch is a stationary non-unique state for the sine law;
- the target direction may be undefined when principal values are repeated;
- the result depends on whether the cue is based on stress, strain, stretch, or energy.

The tutorial includes dead-zone and rate-saturation variants and demonstrates loading-history dependence. Direct reorientation should be interpreted as a phenomenological kinematic mechanism unless additional biological evidence supports literal fiber rotation.
