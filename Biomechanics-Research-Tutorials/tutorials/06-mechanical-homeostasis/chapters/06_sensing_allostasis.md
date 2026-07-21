# 06 — Sensing, noise, filtering, bias, and allostasis

The true mechanical stimulus is rarely the same as the signal used by the adaptation law. The tutorial distinguishes

- true stimulus;
- noisy measurement;
- filtered sensed signal;
- delayed signal;
- target used for comparison.

A first-order low-pass filter is represented by

\[
\tau_s \dot q_s = q_m-q_s,
\]

where \(q_m\) is the measured signal and \(q_s\) is the sensed signal. Filtering reduces high-frequency noise but creates phase lag. Thus the same operation that stabilizes a noisy controller can destabilize a fast delayed one.

A multiplicative sensor bias is modeled as

\[
q_m=(1+b)q+\eta(t).
\]

At measured equilibrium, \(q_m=q_h\), so the true regulated stimulus is \(q_h/(1+b)\). Zero perceived error does not imply zero true error.

The target can also change with time. A moving target is used here as a minimal representation of allostatic regulation. The code accepts a target history \(q_h(t)\), allowing separation of two questions: can the state restore a fixed target, and can it track a target that itself evolves?

Noise, bias, filter time constant, and target evolution are not interchangeable. Similar-looking trajectories can result from different combinations, creating a parameter-identification problem. Independent measurements of the sensor or signaling dynamics are needed to distinguish them.
