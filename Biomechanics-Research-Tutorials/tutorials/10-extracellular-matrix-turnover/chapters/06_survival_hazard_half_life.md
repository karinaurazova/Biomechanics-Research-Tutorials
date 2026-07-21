# Survival functions, hazard, and half-life

A cohort deposited at time $\tau$ contributes at later time $t$ through a survival function $q(t-\tau)$. For exponential survival,

$$q(a)=\exp(-\lambda a),\qquad \lambda=\frac{\ln2}{t_{1/2}}.$$

The corresponding hazard is constant. This memoryless assumption is computationally convenient and yields an exact connection to a first-order homogenized turnover equation.

A Weibull survival law,

$$q(a)=\exp[-(a/\eta)^k],$$

allows the hazard to decrease or increase with age. Thus, the same half-life can coexist with very different age distributions and early-versus-late removal behavior.

Half-life alone is therefore insufficient to specify turnover. The model must state the full survival law or hazard. Tutorial 10 compares exponential and Weibull cases and shows their different pulse–chase curves.

## Key modeling checkpoint

State explicitly which quantities are conserved, which are constitutive assumptions, and which are experimentally observable.
