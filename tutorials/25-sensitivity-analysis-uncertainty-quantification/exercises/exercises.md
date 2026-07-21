# Exercises — Tutorial 25

## Explore

1. Change the range of `fibre_fraction` and rerun the Monte Carlo study. Which output interval changes most?
2. Increase `boundary_compliance` and inspect the reliability curve.
3. Compare the tornado ranking with the Sobol total-index ranking.

## Experiment

1. Replace the uniform prior for one parameter by a triangular or normal prior.
2. Add a correlation between `fibre_fraction` and `connectivity`.
3. Repeat Sobol analysis for `anisotropy_ratio` and compare it with `peak_stress`.

## Research challenge

Design a pipeline-level error budget in which segmentation error changes fibre fraction, orientation error changes `orientation_deg`, and DIC noise changes the loading scale. Compare the resulting uncertainty with the parameter-level benchmark used here.
