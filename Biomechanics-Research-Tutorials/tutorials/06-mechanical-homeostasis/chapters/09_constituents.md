# 09 — Multiple constituents and the constrained-mixture bridge

Soft tissues contain constituents with different turnover times, preferred stretches, orientations, and mechanical roles. The tutorial assigns each constituent

- a homeostatic mass;
- a half-life;
- production and removal sensitivities;
- a deposition-stretch metadata value.

For constituent \(\alpha\),

\[
\dot m^\alpha=\dot m^\alpha_{\mathrm{prod}}-\dot m^\alpha_{\mathrm{rem}}.
\]

Different half-lives cause different transient responses even under the same stimulus. A rapidly turning-over ground matrix may adapt quickly, while collagen-like material retains a longer memory of past deposition.

This construction is a bridge to constrained-mixture theory, not a full constrained-mixture model. A complete formulation may track deposition time, survival, constituent-specific natural configurations, deposition stretches, constituent stresses, and the shared mixture motion. The current module stores deposition stretch as metadata but does not use it to calculate cohort stress.

The distinction matters. Summing constituent masses is not equivalent to summing constituent mechanical stresses. A constituent can be present but unloaded, pre-stretched, damaged, or oriented differently. Tutorial 06 therefore stops at turnover bookkeeping. Later tutorials can add evolving natural configurations, residual stress, and finite-deformation mixture mechanics.

The component experiment is designed to teach interpretation: curves with different time scales should be read as consequences of specified half-lives and sensitivities, not as fitted values for collagen, smooth muscle, or matrix in a particular tissue.
