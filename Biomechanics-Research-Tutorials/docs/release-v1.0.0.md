# Release notes — v1.0.0

**Biomechanics Research Tutorials v1.0.0** is the first complete 25-module release of the repository.

## What is included

- **25 reproducible tutorials** in computational biomechanics.
- Bilingual English/Russian educational materials.
- Synthetic-only datasets and benchmarks suitable for verification, teaching and method comparison.
- Source modules in `src/biomechanics_tutorials/`.
- Per-tutorial `reproduce.py` entry points.
- Figures, GIF animations, notebooks, exercises, instructor notes and references.
- Public documentation: tutorial index, visual gallery, language policy, teaching guide and workshop materials.

## Tutorial blocks

| Range | Block | Description |
|---|---|---|
| 01–05 | Foundations | fiber mechanics, structure tensors, active/passive stress |
| 06–12 | Growth and remodeling | homeostasis, growth tensors, ECM turnover, residual stress |
| 13–20 | Image-informed and experimental mechanics | synthetic microscopy, DIC, segmentation, multimodal benchmarks |
| 21–25 | Advanced computational methods | FE growth, RVE, surrogates, physics-informed learning, UQ |


## Release statistics

- Tutorials: **25**
- PNG figures: **674**
- GIF animations: **72**
- English chapters: **359**
- Russian chapters: **359**

## Synthetic-data position

This release does **not** claim experimental validation. All datasets are synthetic, reproducible and intended for verification-ready workflows, method comparison and education.

## Recommended first commands

```bash
python scripts/diagnose_environment.py
python scripts/verify_repository.py
python tutorials/25-sensitivity-analysis-uncertainty-quantification/reproduce.py
```

## Known limitations

- Full `pytest` can be slow because many tutorials regenerate figures and synthetic datasets.
- SAM and μSAM are represented through benchmark logic and prompt/failure-case abstractions; the repository does not require large external model weights.
- The finite-element, RVE, PINN-like and UQ modules are educational implementations, not production solvers.
