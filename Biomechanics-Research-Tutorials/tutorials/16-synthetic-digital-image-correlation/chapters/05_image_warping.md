# Image warping and interpolation

The deformed image is evaluated at the inverse material coordinates. For a prescribed reference displacement field, the inverse map is approximated by fixed-point iteration and sampled with spline interpolation. This avoids holes that would arise from simply pushing pixels forward.

Interpolation order changes the synthetic benchmark itself. High-order interpolation generally preserves subpixel texture better, but no interpolation is exact for an arbitrary sampled image. Therefore synthetic verification should document the interpolation model and avoid treating a generated image as an independent experimental truth.
