# Scope and learning goals

Digital image correlation (DIC) estimates displacement by matching image texture between a reference state and one or more deformed states. This tutorial treats DIC as a measurement chain rather than as a single correlation coefficient. The chain contains specimen texture, illumination, camera sampling, image interpolation, subset kinematics, optimization, field interpolation, differentiation, uncertainty assessment, and reporting.

All examples are synthetic and retain exact ground truth. This makes it possible to separate implementation verification from experimental validation. The tutorial implements a transparent local 2D baseline; production studies should compare results with established packages and follow current good-practice guidance.
