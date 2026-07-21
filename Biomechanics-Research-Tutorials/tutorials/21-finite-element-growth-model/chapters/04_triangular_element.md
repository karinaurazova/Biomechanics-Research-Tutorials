# The constant-strain triangular element


The implementation uses a constant-strain triangular element.  Each triangle has three nodes and two displacement degrees of freedom at every node.  The element displacement is interpolated linearly from the nodal values.  Because the interpolation is linear, the strain is constant inside the triangle.

This element is not the most accurate finite element.  It can be too stiff in bending-dominated problems and it represents gradients coarsely.  Its advantage is transparency.  The strain-displacement matrix B can be written explicitly from the triangle coordinates.  The element stiffness is area times B transpose C B.  A student can print the matrix and understand where every term came from.

The element strain vector is stored as [epsilon_xx, epsilon_yy, gamma_xy].  The shear component is the engineering shear gamma_xy = du_x/dy + du_y/dx.  The material matrix is written consistently with that convention.  Mixing tensor shear and engineering shear is a common source of factor-of-two errors in finite-element codes.

The equivalent growth load is area times B transpose C epsilon_g.  The sign convention follows from the model sigma = C(epsilon - epsilon_g).  With the algebraic system written as K u = f_g, the growth term appears on the right-hand side.  This makes growth mathematically similar to a thermal strain load in linear thermoelasticity.

The mesh is structured, but the assembly is written as a general element loop.  This makes the code easy to extend to unstructured meshes later.  The tutorial deliberately keeps the element routine separate from the global assembly so learners can test the triangle formula independently.
