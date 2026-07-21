# Local constitutive law


Each element receives a plane-stress matrix contribution and a fiber reinforcement contribution.  The matrix part is isotropic.  The fiber part is anisotropic and depends on the local orientation angle.

The fiber strain is the axial strain along the unit fiber direction.  In small strain it can be written as a linear form of `[exx, eyy, gamma_xy]`.  The fiber energy is then a quadratic penalty on this scalar strain.  This produces a rank-one stiffness term aligned with the fiber direction.

This model is intentionally simple.  It does not include finite stretch, fiber recruitment, damage, viscoelasticity or active contraction.  Its purpose is to isolate the homogenization procedure.  Once the homogenization workflow is understood, the local law can be replaced by a more realistic hyperelastic law.

The important point is that local stiffness is no longer a constant material matrix.  It is a field that depends on image-informed structural variables.

