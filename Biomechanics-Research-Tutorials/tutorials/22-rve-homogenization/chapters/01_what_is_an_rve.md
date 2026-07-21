# What an RVE is and what it is not


An RVE is a mechanical object, not only an image crop.  It must be large enough to contain the structural heterogeneity that influences the macroscopic response, but small enough to be treated as a material point inside a larger model.

For soft tissues this distinction matters because the visible microstructure is often hierarchical.  A small crop may contain several fibers and pores, but it may not contain the orientation dispersion, connectivity, or phase balance needed to predict a stable effective stiffness.  Conversely, a very large crop may contain anatomical gradients that should not be homogenized into one local parameter.

In this tutorial the RVE is synthetic.  This is a deliberate verification choice: the true orientation, fiber fraction, porosity, local stiffness and effective response are all known or reproducible.  That makes it possible to test the homogenization procedure without mixing algorithmic error with experimental uncertainty.

The practical question is not whether the microstructure is beautiful.  The practical question is whether the chosen volume produces a repeatable macroscopic response under relevant loading modes.

