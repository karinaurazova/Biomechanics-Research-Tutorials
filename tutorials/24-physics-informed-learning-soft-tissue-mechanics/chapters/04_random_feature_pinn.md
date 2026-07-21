# Random-feature PINN-like model

A conventional PINN uses a neural network and gradient-based optimization. This tutorial uses a random-feature model instead. The displacement field is represented as `u(x)=Phi(x)w`, where `Phi` is fixed and only the linear weights `w` are fitted.

Because the PDE residual is linear in `u`, every loss term becomes a row block in one least-squares system. This makes the implementation transparent and reproducible. It also shows that the core of physics-informed learning is not the neural-network library; the core is the coupling of data, boundary conditions and differential-equation residuals.

The same structure can later be replaced by a trainable MLP, Fourier network or operator-learning model.
