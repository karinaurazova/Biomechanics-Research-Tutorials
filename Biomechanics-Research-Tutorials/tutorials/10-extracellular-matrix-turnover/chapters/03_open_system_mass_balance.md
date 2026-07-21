# Open-system mass balance

For a constituent with mass-like state variable $m$, the minimal balance is

$$\dot m = \dot m_{\mathrm{prod}}-\dot m_{\mathrm{rem}}.$$

This equation is deceptively simple. Production and removal are fluxes, whereas $m$ is a stock. A stationary mass requires equality of the fluxes, not their disappearance:

$$\dot m=0,\qquad \dot m_{\mathrm{prod}}=\dot m_{\mathrm{rem}}\ne0.$$

The model must also specify the configuration or volume to which the mass is referred. In constrained-mixture theories, constituent mass production is commonly written per unit reference mixture volume, while stresses and natural configurations remain constituent specific.

A numerical implementation should report cumulative production, cumulative removal, and the residual of the integrated balance. Tutorial 10 includes this residual as a verification quantity. A visually plausible mass curve is not enough if the discrete mass balance does not close.

## Key modeling checkpoint

State explicitly which quantities are conserved, which are constitutive assumptions, and which are experimentally observable.
