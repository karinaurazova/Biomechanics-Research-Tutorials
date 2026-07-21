# From expensive simulations to reusable surrogates


A surrogate model is a fast approximation of a slower forward model.  In this tutorial the slow model is represented by a synthetic homogenization law: microstructural descriptors and loading states are mapped to effective stiffness and stress.  In a real project the same role could be played by a periodic RVE solve, a nonlinear finite-element simulation, or a patient-specific inverse model.

The important point is that the surrogate is not a new constitutive theory by itself.  It is a numerical approximation of a chosen forward model over a chosen domain.  Therefore every surrogate statement must specify three things: the input variables, the output variables, and the domain where training data were available.

For biomechanics this is especially important because image-derived descriptors are not abstract features.  Fiber fraction, orientation concentration, porosity and connectivity all carry mechanical meaning.  A useful surrogate must preserve this meaning instead of only minimizing a black-box loss.
