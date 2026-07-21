# 06 — Virtual-field-style equations

Full-field strain data should not be reduced immediately to one global number. The virtual fields method uses weighted forms of equilibrium to extract additional information from spatially varying strain fields.

The tutorial uses smooth virtual weights over the left, right, top, bottom and central regions. For each weight and load case, a weighted stress observation is assembled:

```text
weighted observation = average(w(x) sigma(x)).
```

In a real VFM experiment, the right-hand side comes from measured boundary work and chosen virtual displacement fields. In this synthetic tutorial, the right-hand side is generated from the known model and perturbed with noise. This allows the inverse pipeline to be verified while keeping the code short.

The important idea is identifiability: spatial weighting can separate parameters that look similar in global averages.
