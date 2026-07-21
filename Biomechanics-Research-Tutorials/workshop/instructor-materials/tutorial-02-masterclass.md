# Master class 02 — Collagen Fiber Dispersion

**Duration:** 120 minutes
**Format:** concept demonstration + guided derivation + live coding + comparative investigation
**Audience:** senior undergraduate, master's, early doctoral, or interdisciplinary research trainees

## Learning outcomes

By the end, participants will be able to:

1. represent an axial orientation distribution using a π-periodic density;
2. connect concentration, order parameter, and orientation tensor;
3. implement angular integration of a tension-only fiber response;
4. verify normalization, tensor identities, and quadrature convergence;
5. explain why the mechanical effect of dispersion depends on loading-relative mean orientation;
6. distinguish implementation verification from tissue-specific validation.

## Required preparation

Instructor:

- run `make tutorial-02`;
- confirm that `pytest -q` passes;
- open `distribution_gallery.png`, `aligned_response.png`, `oblique_response.png`, and `anisotropy_map.png`;
- prepare a whiteboard sketch of an aligned and an oblique distribution;
- decide whether learners will use the completed notebook or a partially blank version.

Participants:

- repository cloned and editable package installed;
- basic knowledge of probability density, tensors, and uniaxial stretch;
- completion of Tutorial 01 is recommended but not required.

## Session plan

| Time | Activity | Instructor action | Participant evidence |
|---:|---|---|---|
| 0–10 min | Visual problem | Compare two synthetic collagen fields with the same mean but different spread | Predict whether mechanics can differ |
| 10–25 min | Axial statistics | Introduce π-periodicity and the axial von Mises density | Label μ and β correctly |
| 25–40 min | Order parameter | Derive $S=I_1/I_0$ and interpret limits | Calculate $S$ numerically for one β |
| 40–55 min | Orientation tensor | Derive the second-order tensor and trace identity | Predict the β = 0 tensor |
| 55–70 min | Verification coding | Normalize density and compare analytical/numerical tensors | Report integration and tensor error |
| 70–85 min | Mechanics bridge | Introduce $I_4(\theta)$ and tension-only fiber energy | Identify tensile orientation sectors |
| 85–100 min | Comparative experiment | Run aligned and oblique response scripts | Predict and then explain curve ordering |
| 100–112 min | Anisotropy map | Interpret the joint mean-angle/concentration map | Mark two regions with opposite effects |
| 112–118 min | Scientific caution | Discuss tensor information loss and identifiability | Give one non-identifiable parameter pair |
| 118–120 min | Exit ticket | Separate verification from validation | Submit two concise statements |

## Guided prediction prompts

Before running the aligned experiment:

> For $\mu=0^\circ$, which concentration should produce the highest stress, and why?

Before running the oblique experiment:

> For $\mu=45^\circ$, can a broader distribution place more fibers near the loading axis?

After both:

> Is “dispersion softens tissue” a valid general conclusion?

## Exit ticket

1. State one numerical result that verifies the implementation.
2. State one experiment or dataset needed to validate the model for a chosen tissue.
3. Explain in one sentence why β in this tutorial cannot be substituted directly for GOH κ.

## Assessment rubric

| Dimension | Emerging | Competent | Advanced |
|---|---|---|---|
| Axial statistics | Treats angles directionally | Uses π-periodic density | Explains doubled-angle statistics |
| Tensor reasoning | Reports matrix values | Uses trace/eigenvalue checks | Explains information loss |
| Numerical method | Produces curves | Reports quadrature error | Selects resolution from tolerance |
| Interpretation | Says “more/less stiff” | Links response to angle distribution | Identifies geometry-dependent reversal |
| Scientific caution | Implies tissue validation | States synthetic scope | Designs multimodal/image-based extension |

## Differentiation

For less experienced learners, provide the density and tensor functions and focus on interpretation. For advanced learners, remove the closed-form tensor, ask them to derive it, and add a bimodal distribution challenge.

## Reuse formats

- 45-minute lecture: distribution gallery, tensor concept, aligned-versus-oblique comparison;
- 90-minute workshop: omit the full derivation of nominal stress;
- 3-hour practical: add histogram fitting and a short uncertainty analysis;
- outreach demonstration: use the GIF, physical fiber cards, and two contrasting stress curves.
