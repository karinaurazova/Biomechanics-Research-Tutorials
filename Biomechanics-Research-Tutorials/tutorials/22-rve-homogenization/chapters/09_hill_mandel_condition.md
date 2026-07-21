# Hill--Mandel consistency


The Hill--Mandel condition states that macroscopic stress power should equal the volume average of microscopic stress power for admissible microfluctuations.  In the small-strain linear setting, this becomes an energy consistency check.

The code compares the macroscopic energy density computed from average stress and imposed macro strain with the average microscopic energy density.  For a well-solved periodic fluctuation problem the relative error should be very small.

This check is important because an effective stiffness tensor can look reasonable while the micro-macro energy relation is wrong.  That may happen if boundary constraints are inconsistent, shear conventions are mixed, or averaging weights are incorrect.

In a research code, Hill--Mandel consistency is not optional.  It is one of the basic sanity checks for computational homogenization.

