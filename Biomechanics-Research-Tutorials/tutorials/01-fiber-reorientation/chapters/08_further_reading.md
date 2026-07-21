[English](08_further_reading.md) | [Русский](ru/08_further_reading.md)

# 8. Further reading and extensions

The recommended progression is to introduce one additional modeling assumption at a time.

## Mechanical coupling

Compute the target from a stress or strain tensor rather than prescribing it. Driessen and co-workers developed computational frameworks in which collagen architecture adapts to loading-related preferred directions in cardiovascular tissues. Hariton and co-workers proposed a stress-driven remodeling formulation for arterial walls.

## Distributed orientations

Replace one angle with an orientation distribution or orientation tensor. This is required when tissue contains a broad family of directions rather than one effective axis.

## Stress-dependent kinetics

Allow the rate to depend on stimulus magnitude, but define the stimulus, reference state, units, and calibration procedure explicitly.

## Threshold behavior

Suppress remodeling below a homeostatic or activation threshold. Investigate whether the added threshold creates multiple steady states or sensitivity to measurement noise.

## Turnover-based remodeling

Model directional deposition and degradation rather than effective rotation. This changes the biological interpretation and usually introduces constituent mass or density variables.

## Three-dimensional orientation

Represent orientation with unit vectors, structural tensors, or spherical distributions and preserve objectivity under rigid-body rotations.

## Reading strategy

Use the annotated [References](09_references.md) to distinguish:

- experimental motivation;
- computational precedent;
- concepts deliberately simplified in this tutorial.
