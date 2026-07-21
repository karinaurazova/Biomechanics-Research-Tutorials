# Reproducibility and testing


The repository treats this finite-element module as a reproducible computational experiment.  The random seed, mesh size, material constants, time-step count and update gains are fixed in the baseline reproduction script.  Running the script should recreate the same benchmark tables and figures.

The tests do not check for one exact visual appearance.  They check properties that should remain true if the code is refactored: the mesh has the correct number of elements and degrees of freedom, the triangle B matrix has positive area, the equilibrium residual is small, the stress arrays have the expected shape, the scenario runner returns named scenarios and the saved CSV files contain meaningful metrics.

This style of testing is important for educational scientific code.  A student should be able to improve plotting or reorganize functions without breaking the core checks.  At the same time, accidental changes to mechanics should be caught early.

The reproduction script also writes a JSON summary.  This makes it easy to inspect the final state without importing Python.  Continuous integration can use such files to confirm that the tutorial remains runnable on different operating systems.

Reproducibility does not imply realism.  It means that the computational claim can be regenerated exactly.  Biological interpretation still requires model validation, sensitivity analysis and comparison with experiments.  Those topics are intentionally separated into future advanced tutorials.
