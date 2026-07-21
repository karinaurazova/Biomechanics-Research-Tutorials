# Training, validation and metrics


The module reports RMSE, MAE, coefficient of determination and mean relative error.  No single metric is sufficient.  RMSE emphasizes large errors, MAE is easier to interpret, R² measures explained variance, and relative error reveals whether small-magnitude targets are being treated poorly.

Multi-output regression also requires care.  A model can be accurate for large stiffness entries and poor for coupling terms such as C16 or C26.  For anisotropic materials these coupling terms can be mechanically important even when their absolute value is smaller.

The figures therefore include parity plots, residual summaries and error maps.  This is more informative than one scalar score.
