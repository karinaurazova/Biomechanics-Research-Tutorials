# Common failure modes


The most common error is mixing tensor shear strain and engineering shear strain.  This tutorial consistently uses engineering shear `gamma_xy` in the strain vector and `sigma_xy` in the stress vector.

Another common error is imposing affine displacement on all boundary nodes and calling the result periodic.  That is not periodic homogenization; it is a kinematic upper-bound calculation.

A third error is averaging stiffness directly and assuming that the result is the RVE solution.  Direct stiffness averaging gives the Voigt estimate, not the relaxed periodic response.

Finally, image-derived fields can be mechanically misleading.  A mask with correct area fraction but broken fiber connectivity may strongly underpredict stiffness along the load-bearing direction.  That is why Tutorial 22 should be read together with Tutorials 17--20.

