# Boundary conditions and rigid-body modes


A finite-element stiffness matrix for an unconstrained elastic body has rigid-body modes.  In two dimensions these are two translations and one rotation.  If the boundary conditions do not remove them, the linear system is singular or nearly singular.  A solver may fail or return a meaningless displacement field.

The tutorial uses a minimal but interpretable set of essential boundary conditions.  The left edge is fixed horizontally, and one lower-left node is fixed vertically.  This prevents rigid translation and rotation while allowing much of the tissue patch to expand or contract naturally.  The model resembles a strip attached to a rigid support rather than a fully clamped specimen.

Boundary conditions matter strongly in growth problems.  The same growth field can produce different stress fields under free, supported or clamped conditions.  A region that would be stress-free if isolated may become stressed when attached to a less-grown region or to a constrained boundary.  Therefore boundary conditions are not just numerical details; they are part of the biological and experimental interpretation.

The code stores the fixed degrees of freedom and uses the free degrees of freedom to solve the reduced system.  Reactions are then computed from the full residual K u - f.  A small residual on the free degrees of freedom and finite reactions on the fixed degrees of freedom are expected.  A large free residual is a numerical error.

For research use, boundary conditions should come from the experimental setup, organ geometry or physiological constraints.  For teaching use, it is useful to compare several boundary-condition choices.  That extension is included in the exercises.
