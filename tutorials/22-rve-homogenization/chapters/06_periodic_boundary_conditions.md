# Periodic boundary conditions


Periodic boundary conditions decompose microscopic displacement into an affine macroscopic part and a periodic fluctuation.  Opposite boundaries are allowed to move relative to each other according to the imposed macroscopic strain, but their fluctuations must match.

This is different from simply fixing all boundary nodes to the affine displacement.  Affine displacement boundary conditions suppress microscopic relaxation and tend to be too stiff.  Periodic boundary conditions allow internal compatibility while keeping the RVE representative of a repeating medium.

The implementation creates one fluctuation unknown for each periodic node class.  Nodes on the left and right boundaries share the same fluctuation.  Nodes on the bottom and top boundaries also share the same fluctuation.  One fluctuation class is fixed to remove arbitrary translation.

This explicit reduction-matrix approach is not the most scalable method, but it is excellent for education because the constraint logic is visible.

