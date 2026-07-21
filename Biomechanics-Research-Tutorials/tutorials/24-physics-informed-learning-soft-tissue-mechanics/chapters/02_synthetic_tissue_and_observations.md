# Synthetic tissue and observations

The hidden tissue contains fields for fibre angle, fibre fraction, orientation concentration and connectivity. These descriptors define a true axial stiffness. A second stiffness field is produced by adding bias and smoothing, mimicking an imperfect image-processing pipeline.

The true displacement is computed from constant nominal stress: if the end traction is known, strain is `T/E(x)`, and displacement is its integral. Sparse noisy samples of this displacement represent a simplified DIC measurement. They are intentionally insufficient for a stable derivative-based reconstruction without additional mechanical information.

This design gives three levels of truth: hidden structural truth, imperfect image-derived prior, and sparse measurement data. The learner must negotiate between all three.
