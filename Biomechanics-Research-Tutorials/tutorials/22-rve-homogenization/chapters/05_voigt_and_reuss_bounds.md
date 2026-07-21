# Voigt and Reuss bounds


The Voigt estimate assumes that every microscopic point experiences the same strain.  It is therefore a uniform-strain estimate and usually gives an upper bound for stiffness.  In code it is just the volume average of the local stiffness matrices.

The Reuss estimate assumes that every microscopic point experiences the same stress.  It is therefore a uniform-stress estimate and usually gives a lower bound.  In code it is obtained by averaging local compliance matrices and inverting the result.

These bounds are useful because they catch mistakes.  A periodic homogenized stiffness should usually lie between these idealized extremes in an energy sense.  If it is far outside the bounds, the implementation, units, boundary conditions or material matrices should be checked.

The tutorial reports all three estimates because students should not treat one homogenized tensor as a black box.  Bounds help interpret whether the RVE response is matrix-dominated, fiber-dominated or strongly affected by heterogeneity.

