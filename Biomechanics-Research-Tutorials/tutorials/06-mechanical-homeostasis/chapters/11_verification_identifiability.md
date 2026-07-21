# 11 — Verification benchmark and identifiability

Verification asks whether the equations are solved correctly. Validation asks whether the equations adequately represent observations. Tutorial 06 performs verification only.

The verification ladder is:

1. algebraic checks of error and equilibrium definitions;
2. analytical comparison for the constant-load scalar model;
3. convergence with decreasing time step;
4. exact turnover balance at zero stimulus error;
5. half-life check of the survival function;
6. analytical vascular equilibrium check;
7. positivity and bounds;
8. deterministic reproduction with fixed random seeds;
9. bilingual figure generation from identical numerical data;
10. automated tests and a machine-readable benchmark CSV.

The benchmark compares baseline regulation with slow response, dead zone, saturation, delay, sensor bias, and limited capacity. Reporting several metrics prevents one failure mode from appearing acceptable because of a favorable single number.

Identifiability remains limited. A slow trajectory may result from a small adaptation gain, a long sensing time constant, a delay, saturation, or a long constituent half-life. A nonzero final error may result from a dead zone, sensor bias, biological bias, or a state bound. Similar outputs do not imply similar mechanisms.

A parameter study should therefore be accompanied by an observation map: which quantities would have to be measured to distinguish the alternatives? Time-resolved mechanical stimuli, geometry, mass, production markers, degradation markers, and signaling variables provide different constraints.
