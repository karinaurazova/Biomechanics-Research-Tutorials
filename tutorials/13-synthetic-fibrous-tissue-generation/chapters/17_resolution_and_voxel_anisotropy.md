# Resolution, aliasing, and voxel anisotropy

Apparent fiber diameter depends on physical radius, pixel size, blur, and threshold. Undersampling can break thin fibers or merge neighbouring ones. Therefore, a synthetic benchmark must record both geometry and acquisition grid.

In 3-D stacks, axial resolution and spacing often differ from lateral values. Tutorial 13 demonstrates axial blur and z-downsampling separately from structural dispersion. This distinction prevents an imaging artifact from being interpreted as biological anisotropy.

Resolution sweeps are also necessary before comparing segmentation algorithms: an algorithm cannot recover detail that was removed before observation.
