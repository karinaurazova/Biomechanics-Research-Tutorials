# Subpixel peak refinement

After the integer maximum is found, a parabola is fitted independently through the neighboring horizontal and vertical samples. The peak of this parabola provides a simple subpixel estimate. It is computationally inexpensive and effective for smooth, well-sampled correlation surfaces.

The method is not equivalent to a full iterative interpolation-based DIC solver. Peak locking, interpolation bias, asymmetric surfaces, and large deformation gradients can limit its accuracy. The tutorial therefore reports error against exact fractional translations.
