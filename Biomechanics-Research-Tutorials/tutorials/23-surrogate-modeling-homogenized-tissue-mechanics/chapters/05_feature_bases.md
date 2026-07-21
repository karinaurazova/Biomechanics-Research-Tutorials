# Feature bases


The tutorial compares linear, quadratic and random-feature bases.  A linear model is interpretable but cannot capture most nonlinear interactions.  A quadratic model can represent pairwise interactions such as fiber fraction times connectivity.  Random Fourier features approximate a Gaussian-kernel-like model while keeping the training problem as a linear ridge regression.

This distinction is useful pedagogically because it separates two questions.  First, what basis is used to represent the response surface?  Second, how are the coefficients fitted?  Here all models use ridge regression after constructing different feature maps.

The regularization parameter controls the trade-off between fitting the training data and keeping coefficients stable.  In small or noisy datasets, this can matter more than the apparent sophistication of the basis.
