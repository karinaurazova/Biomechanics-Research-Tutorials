# Parity plots and residuals


A parity plot compares predicted and true values.  Points close to the diagonal indicate good agreement.  Systematic curvature or fan-shaped residuals indicate model bias or heteroscedastic error.

For mechanics, parity plots should be read together with physical interpretation.  If C11 is well predicted but C66 is poor, the surrogate may be acceptable for uniaxial tests but unsafe for shear-dominated problems.  If stress predictions fail for mixed loading, the model may not have learned coupling terms.

Residual plots are also useful for debugging the training data.  Outliers may correspond to high porosity, low connectivity, or orientations near a coordinate singularity.
