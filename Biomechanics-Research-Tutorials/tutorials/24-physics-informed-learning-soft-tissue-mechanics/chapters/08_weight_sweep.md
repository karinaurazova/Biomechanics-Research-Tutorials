# Physics-loss weight sweep

The sweep over `lambda_PDE` demonstrates the trade-off between fitting data and satisfying the governing equation. At very small weights the result resembles interpolation. At very large weights the physics term dominates and can suppress useful measurement information.

The best region is usually a plateau rather than a single magical number. In real studies, the choice should be justified using noise estimates, cross-validation, residual diagnostics and independent mechanical checks.

The GIF animation visualizes how errors move as the physics weight changes.
