# From growth kinematics to finite elements


Growth mechanics often begins with a conceptual statement: biological tissue may add mass, remove mass, reorient structural constituents or change its local natural configuration.  In a finite-dimensional model this sounds simple.  In a continuum model it becomes difficult because growth is spatially distributed and may be incompatible.

Compatibility is the key word.  If every material point could grow freely according to its own local rule, there would be no elastic stress.  Each small neighborhood would simply adopt its new natural shape.  A connected body cannot usually do that.  Neighboring regions must still fit together.  The finite-element model computes the displacement field that best accommodates the imposed growth field while satisfying equilibrium and boundary conditions.

The finite-growth literature expresses this idea with the split F = Fe Fg.  Fg describes the local grown configuration and Fe describes the elastic correction required to place the grown neighborhoods into one continuous body.  This tutorial keeps the same interpretation but uses the small-strain analogue epsilon = epsilon_e + epsilon_g.  The finite-element equilibrium problem is then built from the elastic strain epsilon_e = epsilon(u) - epsilon_g.

This is the first advanced tutorial because it changes the computational object.  Earlier modules could be solved by pointwise updates, image processing, one-dimensional constitutive curves or small inverse problems.  Here the unknown is a displacement field over a mesh.  The model must assemble element contributions into a global system, impose constraints, solve a linear algebra problem and interpret the resulting stress field.

The module remains synthetic and verification-oriented.  We know the growth field, the mesh, the material parameters and the update law.  This allows us to check residuals, reactions, stress magnitudes, energy changes and scenario differences.  Those checks are more important than the visual beauty of the displacement field.
