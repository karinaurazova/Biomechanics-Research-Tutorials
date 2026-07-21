# Dataset schema, provenance, and reproducibility

The NPZ export stores all ground-truth arrays, every modality, and JSON metadata. Required provenance flags are `synthetic=true` and `experimental_validation=false`. Seeds and acquisition parameters are part of the sample, making exact regeneration and controlled train/test domain splits possible.
