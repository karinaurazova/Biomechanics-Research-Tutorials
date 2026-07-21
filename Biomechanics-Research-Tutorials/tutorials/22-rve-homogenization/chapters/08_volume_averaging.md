# Volume averaging of strain, stress and energy


After solving a periodic case, the code computes element strain, stress and energy density.  These quantities are averaged using element areas as weights.

The effective stress is the volume average of microscopic stress.  The effective stiffness column is obtained by applying a unit macroscopic strain and recording the averaged stress response.

The tutorial solves three independent strain cases: unit `exx`, unit `eyy` and unit engineering shear `gamma_xy`.  The three average stress vectors become the three columns of the effective 3-by-3 stiffness matrix.

The same idea works for nonlinear materials, but then the effective tangent depends on the current macroscopic deformation and must be recomputed along the loading path.

