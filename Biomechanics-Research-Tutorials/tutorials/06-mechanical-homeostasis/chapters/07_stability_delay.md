# 07 — Delays and mechanobiological stability

Adaptation is distributed across signaling, transcription, translation, matrix assembly, degradation, and geometric reorganization. A reduced model can represent the aggregate lag as a delay \(\tau_d\):

\[
\dot c(t)=k c(t) r\bigl(e(t-\tau_d)\bigr).
\]

Delay changes the mathematical character of the system. The current state responds to an earlier error, so the corrective action can continue after the target has already been crossed. Increasing gain or delay can produce overshoot, sustained oscillation, or divergence toward imposed bounds.

The tutorial constructs a numerical gain–delay map. Each point is classified by a late-time error metric rather than by visual inspection alone. The map illustrates a central principle of mechanobiological stability: a homeostatic equilibrium may exist algebraically while the biological feedback is dynamically unable to approach it.

The map is numerical and model-specific. It is not a universal physiological stability diagram. Its role is to teach a workflow:

1. identify an equilibrium;
2. perturb the system;
3. vary feedback parameters;
4. quantify late-time behavior;
5. test sensitivity to integration step and observation window;
6. separate slow convergence from genuine instability.

Wrong-sign feedback is the clearest failure. If an elevated stress causes loss rather than gain of load-bearing capacity, stress increases further and the loop becomes positive feedback. More subtle failure can arise from correct-sign but excessive delayed gain.
