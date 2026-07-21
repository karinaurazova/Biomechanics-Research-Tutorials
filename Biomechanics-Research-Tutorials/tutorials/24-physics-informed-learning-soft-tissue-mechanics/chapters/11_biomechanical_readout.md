# Biomechanical readout

The useful output of the model is not only `u(x)`. The downstream readout includes strain, stress, residual, energy and calibrated stiffness scale. These quantities are closer to the questions asked in soft-tissue mechanics.

A visually good displacement curve can still produce an unstable strain field if it oscillates between observations. The physics residual acts as a regularizer against such behaviour. However, it should not be interpreted as validation against real tissue unless the experimental assumptions are independently checked.

The synthetic benchmark is verification-ready, not an experimental validation dataset.
