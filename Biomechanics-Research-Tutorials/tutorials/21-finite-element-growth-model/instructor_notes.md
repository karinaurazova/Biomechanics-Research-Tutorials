# Instructor notes — Tutorial 21

This tutorial should be taught slowly.  Students often understand growth laws as ordinary time updates but underestimate the finite-element equilibrium step.  Emphasize the separation between local preferred growth and compatible deformation.

## Suggested teaching sequence

1. Draw a one-dimensional bar with a heated middle region.  Use it as an analogy for eigenstrain.
2. Introduce the two-dimensional patch and the need for a displacement field.
3. Derive the weak form before showing code.
4. Explain the constant-strain triangle and the engineering shear convention.
5. Run the frozen-growth scenario first.
6. Add feedback only after the equilibrium residual is understood.
7. Compare trace stress and fiber stress rather than using one scalar stress measure.

## Common student misconceptions

- Growth is not displacement.
- A large growth field does not automatically imply large stress.
- A smooth displacement plot is not a verification test.
- Reactions on constrained DOFs are not numerical errors.
- The small-strain model is not a claim that tissues are linear.

## Assessment ideas

Ask students to explain one row of the assembly code and one row of the metrics table.  This tests whether they can connect equations, implementation and interpretation.
