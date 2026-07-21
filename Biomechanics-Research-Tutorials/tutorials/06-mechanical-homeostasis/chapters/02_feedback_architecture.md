# 02 — Feedback architecture and set-points

A homeostatic model contains at least five maps:

1. **loading:** an external history produces forces, pressures, flows, or kinematic constraints;
2. **mechanics:** the current tissue state converts loading into a mechanical stimulus;
3. **sensing:** cells or an abstract sensor estimate that stimulus;
4. **response:** the sensed deviation generates production, removal, contraction, growth, or remodeling;
5. **state update:** the response changes the tissue and therefore the next mechanical stimulus.

Let the mechanical stimulus be \(q(t)\) and the target be \(q_h(t)\). The dimensionless homeostatic error is

\[
e(t)=\frac{q(t)}{q_h(t)}-1.
\]

This normalization allows errors from different quantities to be compared, but it does not make them biologically equivalent. A 10% deviation in wall shear stress and a 10% deviation in intramural stress can activate different pathways and time scales.

The simplest negative-feedback response is proportional:

\[
r(e)=e.
\]

A more realistic educational response can include a dead zone \(\delta\) and a maximum magnitude \(r_{\max}\):

\[
r(e)=r_{\max}\tanh\!\left(
\frac{\operatorname{sign}(e)\max(|e|-\delta,0)}{r_{\max}}
\right).
\]

The dead zone represents a homeostatic range or limited sensitivity. Saturation represents finite biosynthetic or degradative capacity. These additions change both transient and long-time behavior.

A valid feedback diagram must show where delay, noise, bias, and physical limits enter. A sensor bias shifts the regulated *true* state even when the *measured* error becomes zero. A state bound can make the nominal target unreachable. A biological offset, such as a persistent inflammatory signal in a reduced model, can drive remodeling despite a mechanically normal stimulus.
