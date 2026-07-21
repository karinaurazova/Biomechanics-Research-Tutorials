# Skeletons and graph-like topology

A morphological skeleton reduces the binary support to a one-pixel centreline. Eight-neighbour degree identifies endpoints and potential branch pixels. Connected-component labeling provides component count and largest-component fraction.

These are lightweight image-topology metrics, not a complete geometric graph. Thick junctions may produce clusters of high-degree pixels, and crossings may be interpreted as connections even when the original fibers were unbonded.

The limitations are useful teaching examples: converting an image skeleton into a mechanical network requires junction disambiguation, edge tracing, node merging, and explicit crosslink assumptions.
