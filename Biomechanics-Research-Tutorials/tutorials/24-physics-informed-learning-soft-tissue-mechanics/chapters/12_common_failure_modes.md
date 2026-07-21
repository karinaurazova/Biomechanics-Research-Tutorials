# Common failure modes

Common failures include over-weighting physics, under-weighting boundary conditions, using a biased stiffness prior, placing too few observations near high-gradient regions, and interpreting a flat inverse objective as a successful calibration.

Another subtle failure is residual masking: a model can have a small average residual while concentrating errors near boundaries or material transitions. Always inspect residual fields, not only scalar averages.

For multidimensional tissue mechanics these failures become more severe because loads, clamps, anisotropy and incompressibility introduce additional uncertainty.
