# Verification metrics


The tutorial saves several scalar diagnostics for every time step.  The residual norm checks whether the linear equilibrium system was solved correctly.  The reaction norm measures the force required to enforce boundary conditions.  The mean energy density summarizes elastic accommodation.  The mean growth magnitude and elastic mismatch quantify how much growth is present and how much of it cannot be accommodated stress-free.

The stress statistics are not validation metrics.  They are internal consistency metrics.  They help compare scenarios and detect numerical mistakes.  For example, if frozen growth and stress feedback produce identical histories, the update law is not being applied.  If the residual norm grows large, the equilibrium solve is not trustworthy.  If stress values explode, the update gains or boundary conditions may be inappropriate.

The tutorial also computes a simple identifiability-style table.  It looks at the singular values of an element-wise strain design matrix.  This is not a full inverse problem.  It is a bridge to later tutorials: mechanical parameters cannot be identified from uninformative strain states.  If the strain field lacks diversity, different parameter combinations can explain the same data.

Verification is intentionally separated from interpretation.  A simulation can be numerically verified and still biologically unrealistic.  Conversely, a biologically plausible idea can be implemented incorrectly.  The workflow in this tutorial asks learners to establish numerical correctness before drawing mechanobiological conclusions.

The saved CSV files make the checks reproducible.  They can be inspected without opening the notebook, compared across runs or used in continuous integration tests.
