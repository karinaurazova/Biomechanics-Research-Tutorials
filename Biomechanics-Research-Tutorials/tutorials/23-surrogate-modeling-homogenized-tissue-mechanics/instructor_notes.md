# Instructor notes — Tutorial 23

This tutorial should be taught as a mechanics-aware machine-learning module.  Start from the fact that the expensive solver is the object being approximated.  Then make students identify inputs, outputs, units and trust regions before discussing algorithms.

Recommended teaching flow:

1. Run the reproduction script and inspect the parity plot.
2. Ask students why the quadratic model improves over the linear model.
3. Show the design-space error map and discuss extrapolation.
4. Explain bootstrap uncertainty as a practical diagnostic, not as a perfect posterior.
5. Connect active learning to expensive RVE simulations.

Common misconception: students may say that the surrogate has learned tissue mechanics.  Correct this: it has learned the mapping produced by the chosen forward model over the sampled domain.
