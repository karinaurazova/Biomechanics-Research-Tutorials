# 06 Numerical implementation

The implementation uses `scipy.ndimage.gaussian_filter` both for Gaussian derivatives and for integration of gradient products. Reflective boundaries avoid artificial zero padding, but they do not remove boundary bias; the tutorial therefore measures error versus border distance and supports explicit border exclusion.

Two scales must be separated:

- $\sigma_g$ controls derivative regularization and the smallest visible feature;
- $\sigma_i$ controls the neighborhood over which one dominant orientation is assumed.

Increasing $\sigma_i$ reduces random noise but blends nearby domains and rapidly changing curvature. Parameter selection is therefore a multi-objective decision involving error, coverage, and spatial resolution.
