# Instructor Notes — Tutorial 13

## Suggested duration

210 minutes, divided into five blocks:

1. latent geometry and reproducibility;
2. orientation statistics and network families;
3. raster ground truth and topology;
4. 3-D volumes and resolution;
5. verification, limitations, and independent design.

## Central teaching decisions

- Keep geometry, observation, and mechanics conceptually separate.
- Repeatedly distinguish a random seed from a statistical sample.
- Do not use a tissue preset as evidence of biological realism.
- At crossings, ask learners what the requested ground truth actually is.
- Treat skeleton nodes as image-derived candidates, not automatically as physical crosslinks.
- Require every exported dataset to state that it is synthetic.

## Common misconceptions

1. **A realistic-looking image is validated.** Visual plausibility is not validation.
2. **One orientation exists at every pixel.** Crossing families violate that assumption.
3. **Porosity determines mechanics.** Connectivity, orientation, crimp, and junction rules also matter.
4. **A skeleton is a mechanical graph.** Crossings and thick junctions require interpretation.
5. **More pixels mean more physical information.** Upsampling cannot restore removed detail.
6. **A seed is a parameter of the material.** It indexes a realization.

## Assessment evidence

Ask students to submit:

- a generator configuration;
- an exported NPZ dataset;
- a table of structural metrics over multiple seeds;
- one failure case for an orientation or segmentation method;
- a short statement separating verification from validation.
