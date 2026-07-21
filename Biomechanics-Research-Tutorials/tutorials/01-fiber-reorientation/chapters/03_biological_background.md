[English](03_biological_background.md) | [Русский](ru/03_biological_background.md)

# 3. Biological and mechanical background

Many soft tissues are anisotropic because their microstructure contains preferred directions. Collagen networks, cardiomyocyte bundles, tendon fascicles, and vascular fiber families are common examples.

The word *reorientation* can describe several distinct processes:

- rotation or rearrangement of existing structural elements;
- cell-mediated contraction and reorganization of a matrix;
- degradation of fibers in one direction and deposition in another;
- apparent change in orientation caused by elastic deformation;
- evolution of the statistical distribution of many fibers.

These mechanisms should not be collapsed into a single biological statement. For example, fibroblasts can generate coordinated rearrangement of collagen gels, and loading combined with boundary constraints can produce different cell and collagen alignment patterns. Long-term cyclic loading has also been used to regulate cellular orientation and the anisotropy of deposited collagen matrix. The cited experiments motivate the general concept of mechanically coupled architecture, but they do not identify the specific rate law used in this tutorial.

## Mechanical cue

The target direction may later be defined from:

- the maximum principal stress direction;
- the maximum principal strain direction;
- a preferred stretch direction;
- a prescribed loading axis;
- a direction inferred from an image or experiment.

Computational studies of cardiovascular tissues have used stress- or strain-related preferred directions and, for biaxial loading, directions between the principal loading axes. Some models evolve a single direction; others evolve a continuous angular distribution and fiber content.

In this first tutorial, the target direction is prescribed explicitly. This is a deliberate abstraction: it allows the orientation update to be studied independently from constitutive mechanics.

## Evidence boundary

The tutorial makes only the following evidence-based claim:

> Mechanical environment, cell activity, and constraints can influence fibrous architecture, and several computational frameworks have represented this coupling through evolving orientations or distributions.

It does **not** claim that real collagen fibers universally rotate toward the maximum principal stress or strain direction.

See [References](09_references.md) for the source map and the role of each paper.
