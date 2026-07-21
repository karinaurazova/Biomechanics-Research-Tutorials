# Bootstrap uncertainty


The tutorial fits an ensemble of surrogate models on bootstrap resamples of the training data.  The standard deviation of ensemble predictions is not a full Bayesian posterior, but it is a practical indicator of model instability.

If many bootstrap models agree, the prediction is likely supported by the available training set.  If they disagree, the point may be in a sparse or difficult region of the design space.  This uncertainty is especially useful for active learning.

The key limitation is that bootstrap uncertainty can underestimate errors caused by a wrong feature basis.  If all models share the same biased basis, they may agree with each other and still be wrong.
