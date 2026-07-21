# Scenario interpretation


The frozen-growth scenario is the baseline.  It asks what stress field is produced by the initial incompatible growth pattern under the chosen boundary conditions.  Because the growth field is not updated, the time history should remain essentially constant.  This scenario verifies that the solver is deterministic.

The stress-feedback scenario allows both isotropic and fiber growth to evolve.  If the gains are moderate, the response changes smoothly.  Some stress measures may move toward their targets, while other measures may not.  This is expected because one feedback law cannot control every local stress component independently.

The fiber-only scenario isolates the effect of anisotropic growth.  It changes the growth strain mainly along the local fiber direction.  This can reduce or redistribute fiber stress but may leave mean stress or boundary reactions relatively high.  The comparison illustrates why isotropic and anisotropic remodeling should not be collapsed into one scalar variable.

Interpreting the figures requires comparing fields rather than reading a single color map.  Growth magnitude, displacement magnitude, trace stress, fiber stress and energy density answer different questions.  A high displacement region may have low stress if it moves freely.  A low-displacement region near a support may store high elastic energy.

The main conceptual result is that growth is not equivalent to deformation.  Deformation is the compatible displacement solution.  Growth is the local preferred change.  Stress measures the mismatch between the two after equilibrium has been enforced.
