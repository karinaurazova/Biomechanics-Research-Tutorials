# Randomness and reproducibility

Random placement is useful only when it is reproducible. Every public generator accepts an explicit integer seed and creates a local NumPy random generator. Re-running the same generator with the same parameters and seed must produce identical fibers and arrays.

A seed identifies one realization, not a population. Scientific conclusions about stochastic architectures require multiple independent seeds, distribution summaries, and convergence with respect to sample size. Tutorial 13 therefore distinguishes parameter sweeps from realization sweeps.

The exported NPZ files include the seed, domain, generator name, metrics, and a declaration that the data are synthetic and not experimentally validated.
