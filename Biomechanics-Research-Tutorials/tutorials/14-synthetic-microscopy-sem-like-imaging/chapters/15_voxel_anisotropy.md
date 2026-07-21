# Voxel anisotropy and resampling

A voxel array has meaning only together with physical spacing. Resampling from thick slices to isotropic voxels changes apparent continuity and smoothness but does not create missing information. Linear interpolation is suitable for continuous intensity, whereas nearest-neighbor interpolation is generally required for categorical labels.
