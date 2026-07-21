# Synthetic microstructure fields


The RVE contains four cell-wise structural fields: fiber orientation, fiber density, pore indicator and connectivity.  These fields play the same role as image-derived quantities in later image-informed mechanics workflows.

The orientation field controls the direction in which fiber reinforcement is strongest.  The density field controls how much fiber contribution is present.  The pore field locally softens the tissue.  The connectivity field is a simple proxy for whether fibers form a continuous load-bearing network.

The fields are smooth but heterogeneous.  They are not meant to represent one specific tissue.  Instead, they create a controlled test case where structure varies enough to make homogenization non-trivial.

A useful exercise is to modify the random seed or the smoothing length and observe whether the effective stiffness changes smoothly or erratically.  Erratic changes indicate that the RVE may be too small for the structural pattern being modeled.

