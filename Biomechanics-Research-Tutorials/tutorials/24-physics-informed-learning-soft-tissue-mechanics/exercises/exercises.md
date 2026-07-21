# Exercises

1. Increase the observation noise and rerun `reproduce.py`. Which metric degrades first: displacement error, strain error or PDE residual?
2. Remove the traction term by setting `lambda_traction=0`. Explain why the stress scale becomes less reliable.
3. Replace the image-derived stiffness by a constant stiffness. Compare the residual and strain fields.
4. Change the number of random features. When does the model become too flexible?
5. Repeat the inverse scale sweep with fewer observations. Does the objective remain identifiable?
6. Add an artificial body force term and modify the residual operator accordingly.
7. Design a 2D extension: what would replace `E(x) du/dx` in plane stress?
