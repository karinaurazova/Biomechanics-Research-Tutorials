# 12 Verification hierarchy

A finite-growth implementation should be verified from algebraic identities upward.

**Level 1 — tensor construction**

- positive determinant of every growth tensor;
- orthonormality of material bases;
- exact principal stretches for rotated tensors.

**Level 2 — kinematic identities**

- \(\mathbf F=\mathbf F_e\mathbf F_g\);
- \(J=J_eJ_g\);
- free growth gives \(\mathbf F_e=\mathbf I\).

**Level 3 — constitutive checks**

- zero stress in the elastic reference state;
- frame indifference;
- finite-difference agreement between \(\partial\Psi/\partial\mathbf F\) and \(\mathbf P\).

**Level 4 — evolution checks**

- zero driving force leaves \(\mathbf F_g\) unchanged;
- exponential updates preserve positive determinant;
- time-step refinement gives convergent trajectories;
- bounds are detected and reported.

**Level 5 — spatial checks**

- compatible fields have negligible curl diagnostic;
- reduced strips balance force and moment;
- mesh refinement will later be required for finite-element problems.

The synthetic CSV benchmark records numerical errors and tolerances. Passing it establishes internal consistency, not biological validity.
