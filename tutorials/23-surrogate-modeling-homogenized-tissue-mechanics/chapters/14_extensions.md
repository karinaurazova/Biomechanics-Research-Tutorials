# Extensions and research tasks


Natural extensions include replacing the synthetic forward model by Tutorial 22 RVE solves, adding finite-strain outputs, enforcing positive-definiteness of the stiffness tensor, comparing Gaussian processes with neural networks, and embedding the surrogate inside inverse FE calibration.

A more advanced version could use physics-informed losses: symmetry of the stiffness tensor, convexity constraints, energy consistency, or known monotonicity with respect to porosity and fiber fraction.  Another useful extension is multi-fidelity learning, where cheap analytical bounds and expensive RVE solves are combined.

The most important research habit is to keep the surrogate tied to the mechanics.  The goal is not to add machine learning for its own sake, but to accelerate and interrogate a mechanically meaningful forward model.
