# 01 — Problem statement and three identification levels

Image-informed mechanics becomes meaningful only when the image is connected to a mechanical observable. A segmentation mask or an orientation map is not yet a material model. It becomes mechanically useful when it changes the predicted stress, strain energy, stiffness, damage risk or remodelling stimulus.

This tutorial separates three tasks that are often mixed together.

## 1. Structural identification

Structural identification estimates descriptors from images:

```text
image -> theta(x), kappa(x), rho_f(x), connectivity(x), diameter(x), pore size(x)
```

Examples are fibre orientation, orientation concentration, fibre fraction, skeleton connectivity, pore-size distribution and graph topology. These quantities can be obtained from SEM-like images, polarization-like maps, fluorescence images, segmented masks or skeletons.

Structural identification is not yet a mechanical inverse problem. It answers: what structure is present?

## 2. Mechanical identification

Mechanical identification estimates parameters from mechanical data:

```text
DIC strain field + force/load data -> constitutive parameters
```

The image may be absent. A homogeneous model can be calibrated from stress-stretch curves, biaxial tests or full-field DIC data. The main difficulty is that different parameter combinations may produce very similar load responses.

## 3. Joint image-informed identification

Joint identification uses both:

```text
microstructure + DIC + force data -> spatial material model
```

The image provides spatial structure and priors. The mechanical data determine the numerical values that make the model reproduce measured forces or boundary work.

The tutorial uses synthetic data so that the true structure, true strain fields, true forces and true parameters are known. That makes it possible to quantify identifiability and bias at every stage.
