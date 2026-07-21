# Verification and dataset schema

The benchmark verifies deterministic reproduction, target orientation, aligned order, normalization of 3-D direction vectors, and provenance flags. These checks are intentionally lightweight and run during continuous testing.

The NPZ schema stores numerical arrays and one JSON metadata field. It is compact, portable, and readable without a custom database. A production dataset may later add TIFF, Zarr, HDF5, or NIfTI export, but the synthetic truth must remain synchronized.

Verification asks whether the code generated what its equations and parameters prescribe. Validation would ask whether those prescriptions represent an experimental population; Tutorial 13 does not make that claim.
