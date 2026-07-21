# 03 — Scalar analytical model

Let \(L(t)>0\) denote load and \(c(t)>0\) an effective load-bearing capacity. Define the stress-like stimulus

\[
\sigma(t)=\frac{L(t)}{c(t)}.
\]

For a target \(\sigma_h\), use the multiplicative adaptation law

\[
\dot c = k c\left(\frac{\sigma}{\sigma_h}-1\right),
\qquad k\ge 0.
\]

Substitution of \(\sigma=L/c\) gives

\[
\dot c=k\left(\frac{L}{\sigma_h}-c\right).
\]

For constant load, the equilibrium is

\[
c_\infty=\frac{L}{\sigma_h},
\]

and the analytical solution is

\[
c(t)=c_\infty+(c_0-c_\infty)e^{-k(t-t_0)}.
\]

The solution exposes several properties. The equilibrium is unique and positive for positive load and target. The relaxation time is \(1/k\). Linearization gives the eigenvalue \(-k\), so the undelayed system is asymptotically stable when \(k>0\). The model also reveals why the factor \(c\) in the original law matters: it converts a relative stress error into an absolute rate of change of capacity.

This solvable case is the verification anchor for the numerical implementation. The code must recover the analytical trajectory before nonlinear feedback, noise, delay, or constituent turnover is introduced.

The variable \(c\) is intentionally abstract. Interpreting it as wall thickness, collagen mass, cross-sectional area, or effective stiffness requires a separate constitutive and geometric argument. The same scalar equation can fit multiple biological narratives; therefore a good numerical fit alone does not identify the underlying mechanism.
