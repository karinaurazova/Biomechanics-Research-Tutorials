# Finite-element discretization


The RVE is discretized using constant-strain triangular elements.  Each rectangular cell is split into two triangles.  The local material matrix is assigned from the cell-wise microstructure field.

For each element the code computes the strain-displacement matrix, element area and element stiffness.  The global stiffness matrix is assembled in the same way as in the finite-element growth tutorial, but here the element material matrix changes from element to element.

The microscopic unknown is not the full displacement field.  It is the periodic fluctuation field.  The affine part is known from the prescribed macroscopic strain.  Solving the reduced system gives the fluctuation that minimizes microscopic elastic energy subject to periodicity.

This gives students a concrete link between finite elements and homogenization: homogenization is not a separate numerical universe, it is a boundary-value problem with special boundary conditions and special post-processing.

