# Rasterization, blur, and noise

Rasterization samples each polyline segment, stamps a finite-radius kernel, and accumulates intensity and orientation moments. A Gaussian blur can represent a simple point-spread effect, and additive noise can be applied after image formation.

The image and the ground-truth mask are intentionally different arrays. Blur and noise change the observation, whereas the support accumulated before those operations defines the structural mask.

This simple imaging model is not intended to reproduce SEM, fluorescence, SHG, or polarization physics. Those modality-specific transformations are deferred to Tutorials 14 and 15.
