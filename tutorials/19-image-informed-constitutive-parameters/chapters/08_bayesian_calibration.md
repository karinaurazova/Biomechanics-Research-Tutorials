# 08 — Bayesian calibration and uncertainty

Point estimates can hide uncertainty. A parameter vector may fit the data well, but some components may still be weakly identified.

The tutorial therefore includes a Gaussian linear posterior:

```text
posterior precision = A^T R^{-1} A + P_0^{-1}
```

where `R` is the observation-noise covariance and `P_0` is the prior covariance. The posterior gives mean values, standard deviations and approximate 95% intervals.

The posterior is most useful when interpreted together with singular values and parameter correlations. A narrow interval usually means the data constrain that parameter. A wide interval means the parameter remains uncertain under the available load cases and image-derived fields.
