# 09 Anisotropy, path dependence, and noncommutativity

Isotropic growth increments commute because each is a scalar multiple of the identity. Rotated anisotropic increments generally do not:

\[
\mathbf G_2\mathbf G_1\neq\mathbf G_1\mathbf G_2.
\]

The commutator

\[
[\mathbf G_1,\mathbf G_2]
=
\mathbf G_1\mathbf G_2-\mathbf G_2\mathbf G_1
\]

quantifies this noncommutativity. It vanishes when the increments share principal directions or are isotropic, but grows as their axes separate.

This means that the final growth tensor depends on the sequence of anisotropic events. A tissue that first grows along one fiber family and later along a rotated family need not reach the same internal state as a tissue experiencing the reverse order, even when the scalar growth magnitudes are identical.

Path dependence has practical implications. A model that stores only current mass or current principal stretches may lose information needed to reconstruct the internal architecture. Time integration must preserve the chronological order of updates. Operator splitting and large time steps can introduce artificial path errors.

The tutorial composes increments in chronological order and compares both products across a sweep of relative angles. This is a purely kinematic result; no constitutive law is needed to observe it.
