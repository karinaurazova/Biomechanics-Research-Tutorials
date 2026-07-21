# Subset size, step, and search radius

Subset size controls the amount of texture and the spatial averaging scale. Step size controls the density of reported points, not the information contained in each subset. Search radius controls the range of initial translations. These three parameters have different roles and should not be conflated.

Small subsets improve nominal spatial resolution but become noisy or ambiguous. Large subsets are robust but smooth gradients and cross discontinuities. A small step creates highly overlapping measurements and increases cost without restoring information lost by a large subset.
