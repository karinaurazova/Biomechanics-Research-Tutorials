# Age-structured cohorts and hereditary memory

An explicit cohort model records birth time, deposited mass, deposition stretch, and material properties for every generation. The current mass is

$$m(t)=\sum_\alpha m_\alpha(\tau_\alpha)q_\alpha(t-\tau_\alpha).$$

Age structure carries information that is absent from total mass. Two tissues can have identical collagen mass but different mean age, fraction of original material, cross-link maturity, and stress contribution.

Cohorts also provide a natural representation of hereditary mechanics. A newly deposited fiber can have its own natural configuration and prestretch, whereas old cohorts retain the state assigned at deposition unless a separate remodeling mechanism is introduced.

The cost is state growth: each time step creates a new cohort. Practical constrained-mixture implementations therefore use history compression, quadrature, adaptive integration, or homogenized approximations.

## Key modeling checkpoint

State explicitly which quantities are conserved, which are constitutive assumptions, and which are experimentally observable.
