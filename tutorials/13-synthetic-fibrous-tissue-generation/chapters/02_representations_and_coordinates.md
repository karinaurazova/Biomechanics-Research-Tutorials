# Representations, coordinates, and units

The implementation separates vector geometry from raster and voxel representations. A planar fiber is stored as a polyline in a rectangular domain. Its radius, family identifier, and provenance remain attached to the geometry. Rasterization converts this vector object into pixel arrays without deleting the original representation.

Coordinates are dimensionless by default. A caller may later assign millimetres, micrometres, or voxel dimensions, but that scale must be recorded explicitly. Mixing a dimensionless radius with a pixel diameter is a common source of silent errors, so the code performs the coordinate-to-pixel conversion only inside the rasterizer.

For axial fibers, directions separated by 180 degrees are equivalent. Orientation is therefore wrapped to the interval [-90°, 90°), and all means and differences use doubled-angle statistics.
