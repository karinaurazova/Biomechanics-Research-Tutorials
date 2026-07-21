[English](06_computational_experiments.md) | [Русский](ru/06_computational_experiments.md)

# 6. Computational experiments

## Experiment A — Baseline relaxation

- Initial orientation: -50 degrees
- Target orientation: 30 degrees
- Initial axial mismatch: 80 degrees
- Remodeling rate: k = 0.35 inverse time
- Duration: 20 time units

The expected result is a monotonic decrease in axial mismatch.

## Experiment B — Analytical verification

Compare explicit Euler integration with the fixed-target analytical solution. Report the maximum axial discrepancy and repeat the comparison for several time steps.

## Experiment C — Parameter sweep

Compare several values of k. The equilibrium orientation is unchanged, but the adaptation timescale changes. The analytical expression predicts that the time to a fixed tolerance is proportional to 1/k.

## Experiment D — Changing target direction

The target changes during the simulation. This demonstrates that a first-order law introduces a lag between the cue and the structural response.

## Experiment E — Orthogonal-case diagnostic

Perturb an exactly 90-degree initial mismatch by plus or minus 0.5 degrees. The two trajectories follow different but physically equivalent branches. This experiment reveals a non-uniqueness that would be hidden if the exact orthogonal state were used as an ordinary baseline.

## Experiment F — Fiber population animation

A synthetic population is initialized with a finite angular spread. Each displayed fiber follows a common mean response while its offset decays for illustrative purposes. This animation is not a validated orientation-distribution model.
