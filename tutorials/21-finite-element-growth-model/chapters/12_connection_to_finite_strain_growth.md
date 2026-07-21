# Connection to finite-strain growth mechanics


The finite-strain growth framework uses F = Fe Fg.  The growth tensor Fg maps a local reference neighborhood into its grown natural configuration.  The elastic tensor Fe maps that grown neighborhood into the current compatible placement.  Stress is derived from the elastic part, not from total deformation alone.

The small-strain model in this tutorial is the linearized analogue.  The total strain epsilon(u) is split into elastic strain and growth strain.  The stress uses only the elastic difference.  This is why the code is useful as a bridge: it preserves the conceptual separation while avoiding nonlinear solve machinery.

Moving from this tutorial to a finite-strain implementation requires several changes.  The displacement gradient must be replaced by the deformation gradient.  The constitutive law must be formulated through a strain-energy function.  The residual must be nonlinear in the displacement.  Newton iterations and consistent tangent matrices become necessary.  Incompressibility may require mixed displacement-pressure elements or stabilization.

Boundary conditions and growth laws also become more delicate.  The order of tensor multiplication matters.  Fiber growth, volume growth and remodeling of structural directions may not commute.  Updating Fg must preserve physical constraints such as positive determinant and meaningful fiber architecture.

For these reasons the tutorial stops at a linearized model but explains exactly where finite-strain generalization enters.  Learners should leave with a clear map: the finite-element pipeline remains, but the strain measure, constitutive law, residual and solver become nonlinear.
