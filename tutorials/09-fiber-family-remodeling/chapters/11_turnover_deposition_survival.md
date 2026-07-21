# 11. Deposition, survival, and cohort history

A turnover model distinguishes existing constituents from newly deposited material. A cohort deposited at time \(\tau\) carries a birth mass, deposition direction, deposition stretch, and survival function.

For exponential survival,

\[
q(t-\tau)=
2^{-(t-\tau)/t_{1/2}}.
\]

The current mass is the sum of surviving cohorts. The current orientation distribution is a mass-weighted mixture of cohort directions. Remodeling can therefore occur without rotating any existing fiber: old directions disappear and new directions are deposited.

Deposition stretch is especially important. Two tissues can have the same observed orientation and total mass yet different residual or homeostatic prestress because their cohorts were deposited at different natural stretches.

The tutorial implements a transparent cohort ledger. It tracks total mass, mean axial orientation, order parameter, production rate, and mean cohort age. This model is still a reduction: it does not resolve molecular collagen synthesis, fibrillogenesis, enzymatic degradation, or cross-link chemistry.
