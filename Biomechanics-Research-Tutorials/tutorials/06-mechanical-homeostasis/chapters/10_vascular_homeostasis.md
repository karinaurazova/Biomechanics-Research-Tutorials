# 10 — Two-stimulus vascular homeostasis

An idealized artery provides a useful example because flow and pressure generate different mechanical cues. Let \(r\) be radius and \(h\) wall thickness. In normalized form, the tutorial uses

\[
\frac{\tau_w}{\tau_{w,h}}
=\frac{Q}{Q_h}\left(\frac{r_h}{r}\right)^3,
\]

and a thin-wall scaling

\[
\frac{\sigma_\theta}{\sigma_{\theta,h}}
=\frac{P}{P_h}\frac{r}{r_h}\frac{h_h}{h}.
\]

Radius adapts to wall shear error and thickness adapts to circumferential stress error:

\[
\frac{\dot r}{r}=k_r r_\tau,
\qquad
\frac{\dot h}{h}=k_h r_\sigma.
\]

For new constant pressure and flow, simultaneous restoration of both normalized stimuli gives

\[
r_\infty=r_h\left(\frac{Q}{Q_h}\right)^{1/3},
\]

\[
h_\infty=h_h\frac{P}{P_h}\frac{r_\infty}{r_h}.
\]

These expressions provide an analytical equilibrium check. The numerical trajectory is then plotted in radius–thickness state space together with a vector field. Multiple initial conditions approach the same attractor when the chosen feedback is stable.

The model omits axial stress, nonlinear wall mechanics, residual stress, active tone, layered structure, pulsatility, and constituent-specific turnover. It should therefore be interpreted as a dimensional and dynamical teaching model, not as an arterial predictor.
