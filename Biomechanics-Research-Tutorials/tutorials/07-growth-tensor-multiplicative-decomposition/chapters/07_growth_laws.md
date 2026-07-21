# 07 Growth laws, Mandel stress, and dissipation

Kinematics alone does not determine how growth evolves. A constitutive growth law is required. Define

\[
\mathbf L_g=\dot{\mathbf F}_g\mathbf F_g^{-1}.
\]

Tutorial 07 uses a transparent stress-driven prototype,

\[
\mathbf L_g
=
k\,\mathcal R\!\left(\operatorname{sym}\mathbf M-\mathbf M_h\right),
\]

where \(k\) is a rate, \(\mathbf M_h\) is a target Mandel stress, and \(\mathcal R\) may include a dead zone, saturation, projection to isotropic or diagonal modes, and suppression of resorption.

The update is performed as

\[
\mathbf F_g^{n+1}
=
\exp(\Delta t\,\mathbf L_g^n)\mathbf F_g^n.
\]

The matrix exponential preserves invertibility more reliably than the additive update \(\mathbf F_g^{n+1}=\mathbf F_g^n+\Delta t\,\dot{\mathbf F}_g\). It does not by itself guarantee that a chosen law is physically correct.

Thermodynamic admissibility requires a careful dissipation inequality. Depending on the energy convention and additional mass supply terms, the exact driving force may involve Mandel or Eshelby-type stresses. The tutorial records \(\mathbf M:\mathbf L_g\) as a diagnostic but does not claim that its sign alone proves a complete open-system thermodynamic formulation.

A homeostatic target is also not universal. Different tissues may regulate stress, strain, energy, constituent-specific tension, or combinations of biochemical and mechanical signals. The code therefore treats the target and projection mode as explicit modelling choices.
