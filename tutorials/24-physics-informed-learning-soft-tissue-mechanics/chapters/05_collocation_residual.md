# Collocation residual

The PDE is enforced at grid points called collocation points. The code builds a finite-difference derivative matrix and applies it to every basis function. This creates a residual design matrix. Multiplying that matrix by the unknown weights gives the residual field.

This construction is a discrete analogue of automatic differentiation in standard PINNs. In a deep-learning implementation, derivatives of the network output are obtained through autodiff. Here finite differences are used so that the residual can be inspected directly.

The residual is not a decorative metric. It controls whether the reconstructed field can be used to compute stress and strain in a mechanically meaningful way.
