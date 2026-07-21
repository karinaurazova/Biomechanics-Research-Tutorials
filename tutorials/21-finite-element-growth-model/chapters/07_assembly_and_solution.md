# Assembly and linear solution


The global assembly loops over elements.  For each triangle it computes the B matrix, the area, the element stiffness and the equivalent growth load.  The local element degrees of freedom are mapped into the global matrix.  This is the standard finite-element assembly pattern.

Because the model is linear in displacement for a fixed growth state, each equilibrium step requires one linear solve.  The code uses dense arrays for readability.  This is acceptable for the small teaching mesh.  Larger meshes should use sparse matrices and sparse solvers.

The displacement field is stored nodally, while strain, growth strain and stress are stored element-wise.  This distinction is important.  Constant-strain triangles produce constant strain and stress inside each element.  When visualizing element fields on a grid, the code reshapes the structured two-triangle-per-cell storage.  When visualizing nodal fields, it averages element values to nodes or uses nodal displacement directly.

The equilibrium residual is computed after the full displacement vector is reconstructed.  The residual on free degrees of freedom should be near machine precision relative to the right-hand side.  The residual on fixed degrees of freedom is interpreted as the reaction force required to impose the constraints.

This chapter also explains why a visually smooth displacement field is not enough.  A wrong sign in the growth load may still produce a smooth picture, but the stress interpretation changes.  Verification metrics are therefore part of the tutorial output rather than optional debugging information.
