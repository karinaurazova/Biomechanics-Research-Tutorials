# Numerical integration and positivity

The evolution variable is updated by

\[
J_g^{n+1}=J_g^n\exp(\Delta t\,r^n),
\qquad r=\frac{d\ln J_g}{dt}.
\]

This exponential update preserves positivity for any finite time step. In contrast, naive Euler integration,

\[
J_g^{n+1}=J_g^n(1+\Delta t\,r^n),
\]

can produce negative volume ratios during rapid resorption.

Positivity does not guarantee accuracy or closed-loop stability. Large time steps can still overshoot a homeostatic target, create artificial oscillations or activate numerical clipping. The tutorial therefore compares gain and time step jointly and treats bound activation as a warning, not a successful physiological prediction.
