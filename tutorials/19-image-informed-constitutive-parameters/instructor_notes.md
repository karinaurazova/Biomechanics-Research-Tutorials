# Instructor notes — Tutorial 19

Suggested teaching sequence:

1. Begin by asking students why an accurate segmentation may still be mechanically insufficient.
2. Review the distinction between structural, mechanical and joint identification.
3. Derive the linear-in-parameters stress basis on the board.
4. Run the baseline script and inspect `parameter_estimates.csv`.
5. Compare load-only and virtual-field-style systems through singular values.
6. Discuss why the Bayesian posterior is not decorative: it reports what the data did not identify.
7. End with the bridge to Tutorial 20 and the idea of full pipeline error propagation.

Common misconception: students may think image-derived stiffness maps are measured material properties. Emphasize that they are model-dependent maps calibrated by mechanical data.
