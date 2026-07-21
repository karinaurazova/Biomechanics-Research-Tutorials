# 17. Verification hierarchy

Before a tissue-specific application, a fiber-remodeling implementation should pass a hierarchy of synthetic checks.

**Geometry and statistics**

- axial wrapping is \(\pi\)-periodic;
- orientation density integrates to one;
- the orientation tensor has unit trace;
- mean direction and order parameter recover known distributions.

**Evolution laws**

- direct reorientation reduces mismatch except at explicitly documented degenerate states;
- continuous ODF evolution conserves probability and remains non-negative;
- rotational diffusion broadens a concentrated distribution;
- survival reaches one half at the specified half-life.

**Mechanics**

- fiber stretch matches analytical deformation modes;
- angular quadrature converges with increasing resolution;
- aligned structure-tensor and discrete-family limits agree;
- recruitment is monotone and tension-only.

**Coupling**

- family-specific loading changes mass in the expected direction;
- cohort replacement and direct rotation are distinguishable by hidden state variables;
- fitting one loading mode does not guarantee predictive agreement in another.

The committed CSV benchmark records quantitative tolerances for selected checks.
