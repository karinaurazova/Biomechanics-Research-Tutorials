[English](instructor_notes.md) | [Русский](instructor_notes.ru.md)

# Instructor notes

## Central misconceptions

1. **A fiber angle is a directed vector angle.** Use 10 degrees and 190 degrees to demonstrate axial equivalence.
2. **The target direction is measured biology.** In this tutorial it is prescribed; later modules may compute it from stress or strain.
3. **A smooth graph validates the model.** The graph only shows the behavior of the chosen equation.
4. **The 90-degree case is ordinary.** It is non-unique unless an extra selection rule is supplied.
5. **A stable time step is automatically accurate.** Require a refinement comparison.

## Recommended live-coding sequence

1. Plot a naive angular difference.
2. Show its failure near the 180-degree boundary.
3. Introduce the doubled-angle difference.
4. Derive the exponential fixed-target solution.
5. Implement explicit Euler.
6. Verify the zero-rate and axial-equivalence cases.
7. Compare numerical and analytical trajectories.
8. Reveal the orthogonal-case ambiguity.
9. Run the parameter sweep.
10. Close with the evidence boundary and validation discussion.

## Formative assessment checkpoints

- Minute 25: learners calculate an axial difference by hand.
- Minute 55: learners predict the sign of the Euler update.
- Minute 80: learners estimate the adaptation time before running code.
- Minute 105: learners write one verification statement and one validation limitation.
