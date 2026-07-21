# 01 — Motivation

Soft tissues and elastomer-like materials undergo finite, nonlinear, and often anisotropic deformation. A constitutive model converts deformation into stored energy and stress. That conversion is not unique: many models can reproduce a short segment of one experimental curve while predicting substantially different responses under another loading path.

This tutorial treats constitutive modelling as a sequence of questions:

1. Which kinematic quantities are used?
2. Which symmetries and material directions are assumed?
3. What mathematical mechanism produces strain stiffening?
4. Are fibers active in compression?
5. How is near-incompressibility represented?
6. Which experiments can identify the parameters?
7. Which numerical checks distinguish a coding error from a model limitation?

The examples are synthetic so that the mathematical mechanisms can be isolated without implying experimental validation.
