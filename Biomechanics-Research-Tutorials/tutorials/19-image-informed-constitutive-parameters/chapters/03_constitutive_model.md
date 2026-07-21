# 03 — Image-informed constitutive model

The model is a small-strain anisotropic law with a matrix part and a fibre part. It is written in Voigt notation:

```text
sigma = [sigma_xx, sigma_yy, sigma_xy]
```

The matrix response is isotropic plane stress per unit modulus. The fibre response acts along the local axial direction `n = [cos(theta), sin(theta)]`.

The local fibre strain is

```text
e_f = n_x^2 epsilon_xx + n_y^2 epsilon_yy + n_x n_y gamma_xy.
```

The fibre stress contribution is proportional to

```text
e_f [n_x^2, n_y^2, n_x n_y].
```

The image-informed parameter vector is

```text
p = [matrix_base, matrix_density_gain, fiber_scale, connectivity_scale].
```

The model can be written as

```text
sigma(x) = B(x, epsilon, theta, kappa, rho_f, connectivity) p.
```

This is the central design choice. The model is linear in unknown parameters, but nonlinear in the image-derived fields. It is therefore simple enough for exact verification while still demonstrating the coupling between structure and mechanics.
