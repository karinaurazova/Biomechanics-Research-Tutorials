# Motivation and scientific scope

Stress-driven volumetric growth is often summarized by the phrase “tissue grows when stress is high.” That statement is not yet a constitutive model. A reproducible model must define the kinematics, the stress measure, the configuration in which the signal is evaluated, the homeostatic target, the response function, the admissible range of growth and resorption, and the mechanical boundary conditions.

This tutorial restricts the growth tensor to

\[
\mathbf F_g=J_g^{1/3}\mathbf I,
\]

so the internal state is the positive scalar growth-volume ratio \(J_g\). This restriction isolates volumetric adaptation from directional remodeling. It is therefore appropriate for studying mass-volume bookkeeping, hydrostatic feedback, numerical integration and mechanobiological stability before moving to fiber-family remodeling.

The module is verification-oriented. Every parameter and dataset is synthetic. The examples are not calibrated to myocardium, artery, tumor, skin or any other specific tissue. The goal is to make assumptions visible and testable.
