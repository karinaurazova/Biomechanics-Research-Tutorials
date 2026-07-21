# Sampling design


The tutorial uses a Latin-hypercube design.  This is not because Latin hypercubes are universally optimal, but because they give a simple way to cover each coordinate range without placing all points on a regular grid.  Regular grids become inefficient very quickly as the number of variables grows.

In image-informed biomechanics the sampling plan should reflect expected biological and experimental variability.  For example, porosity and fiber fraction may not vary independently in real tissue, but independent sampling is useful in a verification benchmark because it tests the solver over a wider controlled range.

The main lesson is that a surrogate is only as reliable as the simulation campaign used to train it.  Adding a more complex model cannot compensate for missing regions of design space.
