# 1. Scope and terminology

Fiber-family remodeling is the time-dependent change of the load-bearing architecture of a fibrous tissue. The phrase can refer to several distinct processes:

- rotation or sliding of fibers that already exist;
- deposition of new fibers in a mechanically selected direction;
- selective degradation of poorly loaded or damaged fibers;
- changes in angular dispersion without a change in mean direction;
- changes in collagen mass fraction, crimp, recruitment stretch, cross-link density, or deposition prestretch;
- replacement of one constituent population by another.

These mechanisms cannot be represented faithfully by one angle alone. A constitutive model must state which internal variables evolve and which biological statement each variable represents.

This tutorial separates four model classes:

1. **direct reorientation**, in which an existing director rotates toward a mechanical cue;
2. **structure-tensor closure**, in which a mean direction and a dispersion parameter summarize an orientation distribution;
3. **continuous orientation-distribution evolution**, in which probability mass moves through angle space;
4. **cohort turnover**, in which old fibers survive or disappear while new fibers are deposited with their own direction and natural stretch.

The module does not claim that one class is universally superior. The correct level depends on the question, data, time scale, and computational budget. Taber's broad biomechanics framework emphasizes that growth, remodeling, and morphogenesis are coupled but conceptually distinct. Lanir's structural theory shows how tissue response can be assembled from directional constituents. Holzapfel and colleagues provide efficient anisotropic continuum closures. Humphrey and Rajagopal introduce constituent-specific production, removal, and natural configurations. The tutorial places these approaches in one computational comparison.
