# 01 — Motivation and definitions

Mechanical homeostasis is the tendency of a biological system to establish, maintain, or restore a preferred mechanical state. The word *preferred* is deliberately more careful than *constant*. A tissue can regulate a stress, strain, stiffness, energy density, pressure, traction, wall shear stress, or a combination of signals. The regulated quantity may vary by constituent, direction, spatial location, developmental stage, circadian state, or disease context.

Four concepts must be separated.

1. A **set-point** is a selected target value used by a model.
2. A **homeostatic range** is an interval in which no appreciable corrective response is triggered.
3. A **steady state** is a state whose observable variables no longer change; it need not be healthy or stable.
4. An **attractor** is a state approached by nearby trajectories. Stability is therefore a dynamical property, not a synonym for equilibrium.

In a load-bearing tissue, mechanical variables influence cell signaling, synthesis, degradation, contractility, geometry, and material properties. These changes alter the mechanics that generated the signal, closing a feedback loop. Negative feedback can restore a target. Delayed or incorrectly signed feedback can amplify a disturbance.

The tutorial uses a sequence of deliberately reduced models. The first state variable is an effective load-bearing capacity. It can be interpreted as an area-like, mass-like, or stiffness-like quantity, but it is not assigned a unique biological identity. Later, capacity is decomposed into constituents with different turnover times, and a vascular example assigns separate geometric states to radius and wall thickness.

The models are synthetic. Their purpose is to teach derivation, verification, stability analysis, and interpretation before introducing the additional complexity of finite growth, evolving natural configurations, and constrained mixtures.
