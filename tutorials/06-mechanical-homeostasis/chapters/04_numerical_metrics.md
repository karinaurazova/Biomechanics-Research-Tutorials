# 04 — Numerical method and recovery metrics

The tutorial integrates the state with an explicit Euler update:

\[
c_{n+1}=c_n+\Delta t\,k c_n r(e_n).
\]

The state is clipped only when an experiment explicitly imposes physical bounds. For the analytical verification case, a sufficiently small time step must reduce the difference between numerical and exact solutions. This is a verification test, not validation against biology.

A homeostatic trajectory should not be summarized by the final value alone. The tutorial reports:

- peak absolute error;
- final absolute error;
- root-mean-square error;
- integrated absolute error,
  \[\mathrm{IAE}=\int |e(t)|\,dt;\]
- settling time, defined here as the last time the error lies outside a selected tolerance.

Different metrics answer different questions. Final error detects persistent bias but ignores a dangerous transient. Peak error captures the largest excursion but ignores duration. IAE penalizes both amplitude and persistence. Settling time is intuitive but depends on the selected tolerance and observation window.

Disturbance design is part of verification. A step tests regulation after a permanent change. A pulse tests recovery after a temporary insult. A ramp tests tracking of a changing environment. A cyclic load tests whether adaptation follows the mean, oscillates with the forcing, or accumulates drift.

Numerical robustness requires checking time-step sensitivity, positivity, state bounds, deterministic random seeds, and reproducibility of every stored figure. The committed CSV benchmark provides machine-readable recovery metrics for several failure modes.
