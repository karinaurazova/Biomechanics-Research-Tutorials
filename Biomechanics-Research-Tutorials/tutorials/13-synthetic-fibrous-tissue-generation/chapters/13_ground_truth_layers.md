# Synchronized ground-truth layers

The rasterizer outputs image, binary mask, axial orientation, coherence, overlap count, dominant family, and local thickness. All layers share the same pixel grid and provenance.

Orientation is undefined outside the mask and stored as NaN. This prevents background pixels from silently contributing a zero-degree direction. Coherence is zero outside the support and decreases where distinct directions overlap.

A benchmark should select the ground-truth layer appropriate to the task. Binary Dice is not an orientation metric; orientation error is not a topology metric; family classification is not equivalent to reconstructing all crossing directions.
