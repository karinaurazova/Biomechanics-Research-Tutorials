# Polyline fibers, radius, and curvature

A fiber is represented by ordered points. Segment tangents define local orientation; the radius defines the geometric support after rasterization. Waviness is introduced in the normal direction by a sinusoidal perturbation, while curvature can be added independently.

This representation is deliberately transparent. It supports finite fibers, long bundles, gaps, branches, and spatially varying tangent directions without requiring a mesh generator. The cost is that crosslinks and contact are not yet mechanical entities; they become topology descriptors only.

Polyline sampling must be fine enough for rasterization but not confused with material discretization. A denser polyline changes numerical smoothness, whereas a larger physical radius changes the actual synthetic structure.
