# Full-history cohort algorithm

The full-history algorithm creates cohorts at each deposition time, ages them, removes the non-surviving fraction, evaluates cohort-specific elastic stretch, and sums mass and stress.

Its advantages are explicit age structure, transparent prestress memory, and direct access to deposition history. Its cost grows with the number of time steps, constituents, and spatial integration points.

The tutorial includes history truncation and convergence tests. Truncation is acceptable only when the discarded cohorts make a demonstrably negligible contribution.
