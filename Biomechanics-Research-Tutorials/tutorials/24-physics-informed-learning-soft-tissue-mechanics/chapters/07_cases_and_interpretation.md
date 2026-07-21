# Cases and interpretation

Four cases are compared. The data-only case fits observations but does not know equilibrium. The physics-only case knows equilibrium and boundary conditions but ignores interior measurements. The data+physics case combines sparse DIC-like data with an image-derived stiffness prior. The oracle case uses the true stiffness field and is included only as a verification reference.

The comparison shows why a low displacement error is not enough. A curve can pass near all measurements and still have a large residual or poor strain estimate. For biomechanics, derivative-based quantities often matter more than the displacement itself.

The figures should be read together: displacement, residual, traction error and strain error tell different parts of the story.
