# Growth as isotropic and fiber eigenstrain


The growth strain has two components.  The isotropic component contributes equally to epsilon_xx and epsilon_yy.  It is a simple representation of local area growth or swelling.  The fiber component acts along a unit direction a = [cos theta, sin theta].  Its tensor form is g_f a tensor a.

In vector notation the growth strain becomes [g_iso + g_f cos^2 theta, g_iso + g_f sin^2 theta, 2 g_f sin theta cos theta].  The factor 2 appears because the code stores engineering shear.  This formula is one of the most important lines in the implementation.  It connects the scalar biological variables to the mechanical strain measure.

The initial growth field is heterogeneous.  It contains a smooth lesion-like region, a band-like fiber growth region and a slowly varying fiber orientation field.  These fields are synthetic.  They are not fitted to a patient or an experiment.  The benefit is that their exact values are known and reproducible.

Interpreting growth strain requires care.  A high growth strain region is not automatically a high stress region.  Stress depends on the elastic mismatch after the body has found an equilibrium displacement.  The tutorial therefore plots both growth magnitude and stress.  Comparing the two helps students understand why the finite-element solve is necessary.

The eigenstrain formulation is also a bridge to other physics.  Thermal expansion, swelling, plastic strain and growth can all enter a linear elastic FE code through similar algebraic structures.  This analogy is useful computationally, while the biological interpretation remains different.
