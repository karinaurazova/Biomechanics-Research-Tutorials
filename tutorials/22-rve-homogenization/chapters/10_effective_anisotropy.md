# Effective anisotropy and directional stiffness


The effective stiffness matrix contains more information than `C11` and `C22`.  A heterogeneous fiber network may produce coupling terms and directional stiffness that are not obvious from visual inspection of the microstructure.

The tutorial computes directional Young modulus by applying a unit uniaxial stress direction and using the effective compliance matrix.  The ratio between maximum and minimum directional modulus gives a compact anisotropy index.

This index is useful when comparing different segmentation or orientation-recovery pipelines.  Two masks may have similar Dice scores but produce different anisotropy because their connectivity or orientation distribution differs.

For biomechanics, this is one of the main lessons: geometric error becomes mechanically relevant only after being propagated through a constitutive or homogenization model.

