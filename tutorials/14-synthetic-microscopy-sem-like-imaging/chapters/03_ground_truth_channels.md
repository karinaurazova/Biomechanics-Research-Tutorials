# Ground-truth channels and coordinate systems

A single binary mask is insufficient for microscopy benchmarks. The dataset stores mask, local orientation, family label, thickness, emitter amplitude, composition, and three-dimensional occupancy. Pixel coordinates, physical coordinates, voxel spacing, and slice order are written explicitly so that later resampling or registration does not silently change scale.
