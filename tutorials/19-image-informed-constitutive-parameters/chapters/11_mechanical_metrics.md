# 11 — Mechanical metrics beyond image similarity

The output of an image-informed workflow should be evaluated through mechanics-aware metrics:

- parameter error;
- stress prediction error;
- stiffness-index error;
- uncertainty interval width;
- condition number;
- parameter correlation;
- sensitivity to segmentation perturbations;
- sensitivity to missing load cases;
- downstream RVE or FE response error.

A segmentation with high Dice can still be mechanically poor if it breaks connected fibres or biases orientation. Conversely, a mask with moderate pixel error may be mechanically acceptable if the errors occur in regions with low strain sensitivity.

This is why Tutorial 19 is placed after segmentation, ODF and DIC modules: the final quality criterion is not only visual similarity, but mechanically relevant prediction.
