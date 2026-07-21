# Biomechanical interpretation


A surrogate is useful only if its outputs are interpretable in the mechanical problem.  Predicting an effective stiffness tensor means that errors affect stress, energy, wave speed, stability and inverse parameter estimates.  Small numerical errors can become important if they occur in the wrong tensor component.

The tutorial therefore keeps the link between structural variables and stiffness visible.  Fiber fraction should generally increase reinforcement, porosity should generally reduce matrix support, and connectivity should amplify fiber contribution.  A surrogate that violates these trends may still score well statistically but behave poorly in simulation.

Mechanics-aware diagnostics are therefore essential: directional stiffness, coupling terms, energy consistency and load-case-specific errors.
