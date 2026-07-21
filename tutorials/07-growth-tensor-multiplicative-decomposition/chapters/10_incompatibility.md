# 10 Incompatible growth fields

A tensor field is compatible if it is the gradient of a globally continuous placement. For a two-dimensional field, a necessary local condition on a simply connected domain is that each row have zero curl. Tutorial 07 computes

\[
(\operatorname{Curl}\mathbf F_g)_i
=
\frac{\partial (F_g)_{i2}}{\partial x}
-
\frac{\partial (F_g)_{i1}}{\partial y}.
\]

A constant growth tensor passes this test. A spatially varying isotropic field \(\mathbf F_g=\vartheta(x,y)\mathbf I\) generally does not, because gradients of \(\vartheta\) appear in the row-wise curls.

The row-wise curl used here is a pedagogical diagnostic. Full finite-growth compatibility is geometric and can be expressed using induced metrics and curvature. Boundary topology, defects, and three-dimensional structure require more complete analysis.

When \(\mathbf F_g\) is incompatible, it cannot be realized everywhere without an elastic correction. The actual \(\mathbf F\) must satisfy compatibility and equilibrium, while \(\mathbf F_e\) accommodates the mismatch. The resulting stress can persist after external loads are removed.

The incompatibility map in this tutorial should therefore be interpreted as a warning that a local growth prescription cannot simply be plotted as a deformed shape. A boundary-value solver is needed to determine the compatible current configuration.
