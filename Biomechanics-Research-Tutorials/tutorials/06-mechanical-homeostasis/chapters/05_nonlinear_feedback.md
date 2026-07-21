# 05 — Nonlinear feedback: dead zones and saturation

Real adaptive systems need not respond linearly to every small deviation. A dead zone

\[
|e|\le\delta \quad\Rightarrow\quad r(e)=0
\]

creates a homeostatic range. It suppresses unnecessary activity and noise amplification, but it also permits residual error. The system can stop changing before the exact set-point is recovered.

Saturation limits the maximum response. It can represent finite synthesis, degradation, migration, contractility, or signaling capacity. Saturation is especially important after large disturbances: the early response becomes approximately rate-limited, so recovery time grows more than predicted by the linear model.

Combining a dead zone and saturation creates three regimes:

1. an inactive central interval;
2. a responsive intermediate region;
3. a rate-limited outer region.

The shape of the feedback function is therefore a constitutive assumption for adaptation. It should be documented with the same care as a stress–strain law.

Physical bounds add another nonlinearity. If capacity cannot exceed \(c_{\max}\), a load increase may make the target stress unattainable. The resulting residual error is not necessarily a numerical failure; it is a model prediction that the adaptive reserve has been exhausted. Conversely, an unrealistically generous bound can hide this failure mode.
