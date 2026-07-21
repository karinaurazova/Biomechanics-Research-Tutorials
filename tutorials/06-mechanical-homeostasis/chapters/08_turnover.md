# 08 — Turnover as dynamic equilibrium

A tissue can maintain constant mass while its constituents are continuously produced and removed. For a constituent mass \(m\),

\[
\dot m = \dot m_{\mathrm{prod}}-\dot m_{\mathrm{rem}}.
\]

Homeostasis requires equality of the rates, not that both rates vanish:

\[
\dot m_{\mathrm{prod}}=\dot m_{\mathrm{rem}}>0,
\qquad \dot m=0.
\]

The tutorial uses first-order removal. If the half-life is \(T_{1/2}\), the survival function of a cohort of age \(a\) is

\[
S(a)=\exp\left(-\frac{\ln 2}{T_{1/2}}a\right).
\]

The baseline production rate is chosen to balance removal at the homeostatic mass. A positive mechanical error increases production through an exponential sensitivity. This choice keeps production positive and makes the response transparent, but it is only one possible constitutive law.

Turnover introduces memory. Current mass is the accumulated result of past production and survival. Two tissues with the same present mass can have different age distributions and therefore different future responses. The reduced implementation tracks total mass rather than individual deposition cohorts; the survival function is provided to make the missing cohort structure explicit.

A zero net mass rate must not be interpreted as biological inactivity. Likewise, an increase in total mass does not specify whether it arose from increased production, decreased removal, or both.
