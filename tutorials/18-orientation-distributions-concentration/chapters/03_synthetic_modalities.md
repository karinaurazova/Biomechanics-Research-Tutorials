# Synthetic modalities

The module creates four views of one architecture: exact mask/orientation, SEM-like contrast, polarization-like orientation and a segmentation-derived mask. Each view loses information in a different way. SEM-like images contain gradients and shading; polarization-like maps contain angular noise and confidence; segmented masks can alter topology and thickness.

This is useful educationally because the learner can change only one degradation source and observe how the recovered ODF changes.
