# Scale separation and local material points


Homogenization assumes that the microstructural length scale is smaller than the macroscopic scale on which boundary conditions, geometry and loads vary.  This does not require infinite separation, but it does require a useful gap between the scale of fibers or pores and the scale at which the effective material law is used.

In a computational model, one macroscopic integration point may be associated with one RVE.  The macroscopic solver sends a deformation or strain measure to the RVE.  The RVE solves a microscopic boundary-value problem and returns an averaged stress and tangent stiffness.

The simplified implementation here uses small strain.  The macroscopic strain is the vector `[exx, eyy, gamma_xy]`.  The RVE computes the corresponding average stress vector `[sigma_xx, sigma_yy, sigma_xy]`.  Repeating this for independent strain cases gives the columns of the effective stiffness matrix.

The same idea extends to finite strain, but then the RVE receives a deformation gradient and returns a first Piola or Cauchy stress together with a consistent tangent.

