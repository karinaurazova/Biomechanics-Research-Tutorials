# 02 — From images to structural fields

The computational input of Tutorial 19 is not a raw image. It is a set of fields that could come from the previous image-informed modules:

- `theta(x)` — local axial fibre direction;
- `kappa(x)` — concentration or alignment strength;
- `rho_f(x)` — fibre-fraction proxy;
- `connectivity(x)` — connectedness proxy;
- `mask(x)` — region of interest.

A real workflow may obtain these fields from different sources. A SEM-like image can support masks, skeletons and diameter distributions. A polarization-like image can support orientation and retardance. A segmented mask can support connected components and graph metrics. A DIC image pair can support strain fields.

The tutorial starts from already-recovered fields because the aim is the mechanics. This is important pedagogically: the material model should not know whether `theta(x)` came from SEM, polarimetry, fluorescence or manual annotation. It only receives structural descriptors and their uncertainty.

## Structural order

The concentration parameter is mapped to a bounded order proxy:

```text
order(x) = kappa(x) / (kappa(x) + 2)
```

This monotone proxy is not intended to replace full orientation-distribution integration. It is used to demonstrate how stronger alignment can increase the anisotropic fibre contribution.
