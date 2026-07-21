# 04 — Synthetic DIC and force data

The synthetic experiment contains several load cases:

- low and high uniaxial extension in `x`;
- uniaxial extension in `y`;
- biaxial loading;
- shear;
- a spatially graded strain field.

Each load case contains full-field strain components:

```text
epsilon_xx(x), epsilon_yy(x), gamma_xy(x)
```

and a global reaction-like force vector obtained by averaging the stress over the tissue region. Small noise is added to mimic measurement uncertainty.

This setup reflects the logic of DIC-based mechanics: images provide a displacement/strain field, while a load cell provides boundary force information. The inverse problem tries to find material parameters that make both data sources consistent.
