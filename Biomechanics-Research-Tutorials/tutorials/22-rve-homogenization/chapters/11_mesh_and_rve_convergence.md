# Mesh and RVE convergence


A single RVE result should not be trusted without a convergence check.  The tutorial includes a small resolution study in which the RVE is regenerated at several grid sizes using the same seed and field-generation logic.

The goal is not to prove asymptotic convergence in a strict mathematical sense.  The goal is to teach how to ask practical questions: does `C11` stabilize, does the anisotropy ratio stabilize, and does the Hill--Mandel error remain small?

If the effective stiffness changes strongly with grid size, the discretization may be too coarse or the microstructural pattern may require a larger representative domain.

In real applications, one should also test multiple image crops, multiple seeds or multiple anatomical regions.  RVE convergence is both a numerical and a biological sampling problem.

