[English](02_learning_objectives.md) | [Русский](ru/02_learning_objectives.md)

# 2. Learning objectives and assessment

## 2.1 Intended learning outcomes

The tutorial uses an explain–derive–implement–verify–evaluate sequence.

| Level | Learner action | Evidence |
|---|---|---|
| Explain | Distinguish alignment, mean angle, dispersion, and isotropy | Annotated distribution plot |
| Derive | Obtain normalization and orientation-tensor expressions | Short derivation |
| Implement | Evaluate density, tensor, energy, and stress | Executable notebook |
| Verify | Test normalization, trace, analytical tensor, and quadrature | Numerical table or plot |
| Analyse | Compare aligned and oblique loading | Stress–stretch figures |
| Evaluate | State model limitations and parameter ambiguity | Research memo |
| Create | Replace the synthetic density with image-derived data | Research Challenge |

## 2.2 Success criteria

A complete submission should:

- preserve π-periodicity of axial orientations;
- demonstrate that the density integrates to one;
- show that the orientation tensor has unit trace;
- recover an isotropic planar tensor for zero concentration;
- report quadrature error rather than only display smooth curves;
- explain why the sign of a dispersion effect depends on loading geometry;
- avoid treating β as a tissue-specific biomarker without calibration.

## 2.3 Formative questions

1. Can two distributions have the same mean angle but different mechanical responses?
2. What does the tensor lose compared with the complete probability density?
3. Why do fibers under compression require an explicit modeling decision?
4. Which statements in this tutorial are verification claims, and which would require validation data?
