[English](07_interpretation.md) | [Русский](ru/07_interpretation.md)

# 7. Interpretation and limitations

## 7.1 Main interpretation

Dispersion changes how many fibers are favorably oriented for a given deformation. Its mechanical effect is conditional:

- for a mean family parallel to loading, increasing dispersion usually reduces directional reinforcement;
- for a mean family oblique to loading, increasing dispersion can recruit a subset of fibers closer to the loading axis;
- for a uniform planar distribution, the response becomes independent of the chosen mean angle.

The phrase “more dispersed means softer” is therefore incomplete.

## 7.2 What the orientation tensor preserves

The second-order tensor preserves mean axial direction and second-order alignment. It does not uniquely preserve multimodality, skewness, tails, or higher-order structure. Different densities can share the same second-order tensor while producing different nonlinear angular integrals.

## 7.3 Model limitations

1. The distribution is planar, symmetric, and unimodal.
2. Fibers do not interact, rotate, recruit gradually, fail, or remodel.
3. The matrix is isotropic and incompressible.
4. All fibers share identical material parameters.
5. Out-of-plane dispersion is omitted.
6. Compressed fibers are removed using a simple positive-part rule.
7. Parameter values are synthetic and dimensionless.
8. The model has not been fitted to mechanical or imaging data.

## 7.4 Identifiability warning

A stress–stretch curve may be reproduced by different combinations of concentration, mean angle, fiber stiffness, and nonlinearity. Mechanical data alone may not identify microstructure uniquely. Imaging data can reduce this ambiguity, but measurement and fitting uncertainty must still be quantified.

## 7.5 Connection to later tutorials

This module provides inputs for:

- image-derived orientation distributions;
- structure-tensor analysis;
- coupled mean-direction and dispersion remodeling;
- constitutive parameter estimation;
- uncertainty propagation from microscopy to mechanics.
