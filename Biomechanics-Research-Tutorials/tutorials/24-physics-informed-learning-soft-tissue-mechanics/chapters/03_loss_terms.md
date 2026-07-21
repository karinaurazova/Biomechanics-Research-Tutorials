# Loss terms

The tutorial separates the loss into four blocks. The data term fits measured displacements. The boundary term enforces `u(0)=0`. The traction term enforces the stress boundary at the loaded end. The physics term penalizes the interior residual of the equilibrium equation.

This separation matters because different applications trust different information. A high-quality DIC experiment may justify a strong data term. A carefully controlled mechanical test may justify strong boundary terms. A segmentation-derived stiffness field may be useful but biased, so physics and data should be balanced rather than blindly trusted.

The loss-weight sweep is included because there is rarely a universal best value for the PDE weight. Too little physics gives a smooth interpolator; too much physics can ignore data or amplify errors in an imperfect constitutive prior.
