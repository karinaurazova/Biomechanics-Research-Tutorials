# Constrained-mixture interpretation

The constrained-mixture framework treats the tissue as a mixture of constituents that share the observed motion but possess constituent-specific natural configurations, production rates, survival functions, and constitutive responses. This is the conceptual foundation of Humphrey–Rajagopal-type models.

A constituent deposited at time $\tau$ contributes stress at time $t$ according to its surviving mass and elastic deformation relative to its deposition configuration. The total mixture stress is the sum of constituent contributions. Consequently, turnover is coupled to mechanics through both mass and prestretch.

This approach distinguishes production from growth kinematics: adding collagen mass is not equivalent to multiplying the whole tissue by an isotropic growth tensor. It also allows slowly turning-over elastin and rapidly adapting collagen families to coexist.

Tutorial 10 implements only a reduced cohort analogue. The purpose is to teach the bookkeeping and verification logic before the full constrained-mixture toy model in Tutorial 11.

## Key modeling checkpoint

State explicitly which quantities are conserved, which are constitutive assumptions, and which are experimentally observable.
