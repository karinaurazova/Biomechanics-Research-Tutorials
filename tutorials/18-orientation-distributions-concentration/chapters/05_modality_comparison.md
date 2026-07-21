# Modality comparison

The benchmark compares ODFs using Jensen-Shannon divergence and pixelwise orientation mean absolute error. Confidence weighting is included for polarization-like and SEM-like estimates because low-confidence regions should not influence the ODF as strongly as reliable regions.

The comparison is intentionally transparent. It does not rank real microscopes or real segmentation models; it shows how an image-to-ODF pipeline can be verified when the hidden truth is known.
