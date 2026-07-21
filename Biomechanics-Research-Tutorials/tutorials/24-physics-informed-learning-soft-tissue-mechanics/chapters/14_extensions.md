# Extensions

Natural extensions include a 2D plane-stress PINN, incompressibility constraints, finite-strain kinematics, unknown boundary tractions, spatial parameter fields and Bayesian physics-informed inference.

A direct continuation is to replace the random-feature model with a trainable neural network. Another continuation is to couple this module with Tutorial 22 and Tutorial 23: RVE generates effective constitutive response, a surrogate accelerates it, and a physics-informed learner uses it inside an inverse mechanical problem.

The important rule is to preserve diagnostics. More complex networks should not mean less transparent mechanics.
