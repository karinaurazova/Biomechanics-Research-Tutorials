# Subset correlation criteria

Local DIC assumes that a small reference window can be mapped into the deformed image by a low-dimensional shape function. This tutorial implements zero-normalized cross-correlation (ZNCC) and zero-normalized sum of squared differences (ZNSSD). Zero normalization removes sensitivity to an ideal linear gain and offset.

The correlation criterion is only one part of the estimator. Its result depends on subset texture, search region, interpolation, deformation gradients, masks, and optimization. A high ZNCC value is a similarity diagnostic, not a universal uncertainty measure.
