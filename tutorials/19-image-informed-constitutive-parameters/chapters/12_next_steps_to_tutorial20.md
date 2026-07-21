# 12 — Next steps toward the multimodal benchmark

Tutorial 19 identifies image-informed constitutive parameters from synthetic structure, DIC strain fields and force data. Tutorial 20 will connect the full chain:

```text
ground-truth microstructure
-> SEM-like, polarization-like and fluorescence-like images
-> segmentation / SAM / μSAM
-> orientation and structure recovery
-> mechanical simulation
-> synthetic DIC images
-> recovered strain field
-> inverse parameter estimation
```

That final benchmark will make it possible to test how an error introduced early in the imaging pipeline propagates to the final mechanical parameter estimate.

The key lesson is methodological: verification requires known truth at every stage. Synthetic data make that possible before any claim is made about experimental or clinical validity.
