# 02 Three configurations

The multiplicative theory distinguishes three configurations.

1. The **reference configuration** labels material points before the modelled interval.
2. The **local grown configuration** is obtained by applying \(\mathbf F_g\). It represents the natural state that each neighbourhood would prefer after growth.
3. The **current configuration** is compatible in physical space and is reached after the elastic accommodation \(\mathbf F_e\).

The relation is

\[
\mathbf F=\mathbf F_e\mathbf F_g.
\]

The intermediate grown configuration is usually virtual. If \(\mathbf F_g\) varies spatially, neighbouring grown elements may not fit together. Consequently, there may be no global placement whose gradient equals \(\mathbf F_g\). This is the source of residual stress: the body must elastically distort the locally preferred grown states to recover a continuous configuration.

The order of multiplication matters. Vectors are first mapped by \(\mathbf F_g\) and then by \(\mathbf F_e\). Writing \(\mathbf F=\mathbf F_g\mathbf F_e\) would define a different theory. In anisotropic problems the two products are not interchangeable.

The intermediate configuration also has a gauge-like ambiguity. A change of internal basis may alter the matrix representations of \(\mathbf F_e\) and \(\mathbf F_g\) while leaving \(\mathbf F\) unchanged. Constitutive assumptions, material directions, evolution laws, and initialization are therefore needed to give the split physical meaning.

A useful modelling discipline is to state, for every variable, the configuration in which it lives. Reference fiber directions belong to the reference configuration; growth stretches are defined through \(\mathbf F_g\); elastic invariants are computed from \(\mathbf F_e\); current stresses act in the current configuration.
