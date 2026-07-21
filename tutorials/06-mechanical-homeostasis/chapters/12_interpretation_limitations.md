# 12 — Interpretation, limitations, and extensions

The tutorial supports several defensible conclusions:

- negative feedback can restore a preferred mechanical state;
- recovery time depends on adaptation gain and feedback nonlinearities;
- dead zones create a homeostatic range but permit residual error;
- filters reduce noise while adding lag;
- bias can regulate the wrong true state;
- delay can destabilize an otherwise valid equilibrium;
- constant mass can coexist with active turnover;
- constituent time scales create memory;
- multiple mechanical stimuli can regulate different state variables.

It does **not** establish that a specific tissue senses stress rather than strain, that a chosen target is physiological, or that the synthetic parameter values correspond to an organism. It does not model molecular signaling, finite-element stress heterogeneity, evolving reference configurations, damage, inflammation, or experimental uncertainty in a tissue-specific way.

Important extensions include:

1. finite growth through \(\mathbf F=\mathbf F_e\mathbf F_g\);
2. tensor-valued homeostatic stress and anisotropic growth;
3. deposition cohorts and constituent natural configurations;
4. spatially varying stimuli coupled to finite elements;
5. active contraction and tone;
6. biochemical signaling networks;
7. Bayesian parameter inference and uncertainty propagation;
8. experimental protocol design for identifiability;
9. data-driven or physics-informed surrogate models.

The next tutorial introduces the growth tensor and multiplicative decomposition. Tutorial 06 provides the feedback logic that will drive that kinematic model.
