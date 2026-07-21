# Degradation, MMPs, and TIMPs

Matrix degradation depends on enzyme activation, inhibitor availability, accessibility of cleavage sites, mechanical state, and matrix architecture. Tutorial 10 introduces a transparent MMP–TIMP activity proxy,

$$a_e=\frac{\mathrm{MMP}}{1+\mathrm{TIMP}/K_I}.$$

This is not a detailed binding model; it is a bounded way to separate enzyme abundance from effective activity. Increasing TIMP can reduce activity even if MMP remains elevated.

Immature and mature collagen are assigned different degradation rates. This reflects the general possibility that newly synthesized material is removed rapidly, whereas mature, cross-linked fibrils may be more persistent. The direction of cross-link effects on degradability can be context dependent, so the tutorial treats those dependencies as explicit model choices.

Mechanical loading may modify degradation by changing enzyme transport, cleavage-site exposure, or fibril strain. The implementation uses a synthetic stress-dependent multiplier and documents that its sign and form must be experimentally justified.

## Key modeling checkpoint

State explicitly which quantities are conserved, which are constitutive assumptions, and which are experimentally observable.
