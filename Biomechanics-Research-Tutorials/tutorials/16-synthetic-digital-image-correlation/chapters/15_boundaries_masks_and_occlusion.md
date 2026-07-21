# Boundaries, masks, and occlusion

A subset needs support in both images and throughout its search region. Measurements are therefore unavailable near image boundaries, specimen edges, holes, grips, and masked regions. Deformation can also move surface points out of view.

A robust workflow propagates region-of-interest masks through the deformation, distinguishes missing data from zero displacement, and reports coverage. Extrapolating a smooth field across an unmeasured boundary can create physically misleading strain.
