# Three-dimensional fibrous volumes

The 3-D generator deposits curved centreline trajectories into a voxel grid and stores a local unit direction vector in every occupied voxel. Angular noise controls directional dispersion around a prescribed mean vector.

The current method is deliberately lightweight. It does not prevent fiber interpenetration, enforce a target pore-size distribution, or create mechanically valid crosslinks. Its role is to provide small volumetric truth sets for projection, slicing, registration, and future microscopy simulations.

Maximum-intensity projections are visual summaries only; they lose depth and may merge unrelated fibers.
