# 09 — Spatial material maps

Once global parameters are calibrated, the image-derived fields convert them into spatial maps:

```text
matrix_modulus(x) = p0 + p1 rho_f(x)
```

```text
fiber_modulus(x) = p2 rho_f(x) order(x) + p3 connectivity(x) order(x)
```

These maps are not experimental material-property measurements. They are model-dependent fields produced by a chosen constitutive hypothesis.

The distinction matters. The image informs the spatial distribution, but the mechanical experiment calibrates the scale. Without force or displacement data, a bright fibre region can suggest stronger material response, but it cannot determine the stiffness magnitude by itself.
