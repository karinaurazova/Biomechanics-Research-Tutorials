# Verification and validation hierarchy

Verification asks whether the equations are solved correctly. Tutorial 10 checks half-life identities, mass-balance closure, cohort–ODE equivalence under constant hazard, non-negativity, bounded cross-links, and localized spatial degradation.

Validation asks whether model assumptions represent a particular biological system. That requires independent data for turnover rates, maturation, enzyme regulation, cross-links, deposition stretch, and mechanics. No such tissue-specific validation is claimed here.

A recommended hierarchy is: unit tests; analytical limits; synthetic benchmark; temporal convergence; cohort-versus-homogenized comparison; parameter-recovery tests; then independent experimental validation.

Every reported figure should be traceable to a script and parameter set. The results manifest and benchmark CSV provide this provenance.

## Key modeling checkpoint

State explicitly which quantities are conserved, which are constitutive assumptions, and which are experimentally observable.
