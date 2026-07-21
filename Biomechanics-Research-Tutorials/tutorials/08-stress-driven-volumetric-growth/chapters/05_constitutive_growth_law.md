# Constitutive volumetric growth law

The baseline evolution equation is

\[
\frac{d\ln J_g}{dt}=k\,\mathcal R(e),
\]

where \(k\) is an adaptation-rate parameter and \(\mathcal R\) is a nonlinear response. The implementation can include a dead zone, saturation, asymmetric gains for growth and resorption, a switch that disables resorption, and lower and upper bounds on \(J_g\).

A bounded response is represented by

\[
\mathcal R(e)=r_{\max}\tanh\left(\frac{\widetilde e}{r_{\max}}\right),
\]

where \(\widetilde e\) is the dead-zone-corrected and gain-weighted error. Saturation prevents arbitrarily large instantaneous rates but does not by itself guarantee a stable closed-loop system.

The distinction between growth and resorption is explicit. Different positive and negative gains represent different kinetics; forbidding resorption changes unloading from reversible adaptation into permanent growth.
