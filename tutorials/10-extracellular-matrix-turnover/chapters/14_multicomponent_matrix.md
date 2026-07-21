# Multicomponent ECM turnover

A tissue-level ECM model should allow constituent-specific kinetics. Tutorial 10 includes elastin, collagen I, collagen III, and proteoglycan-like components with distinct half-lives, production gains, degradation gains, stiffnesses, and deposition stretches.

The total mass and effective stiffness are weighted sums only in this reduced model. Real interactions are nonlinear: proteoglycans influence hydration and fibril spacing, collagen III affects collagen I fibrillogenesis, and elastin damage changes load sharing.

Component-specific timescales produce history dependence. A short overload may alter proteoglycans and collagen III before slowly turning-over elastin changes appreciably.

This section prepares the transition from a single collagen variable to the constrained-mixture model of Tutorial 11.

## Key modeling checkpoint

State explicitly which quantities are conserved, which are constitutive assumptions, and which are experimentally observable.
