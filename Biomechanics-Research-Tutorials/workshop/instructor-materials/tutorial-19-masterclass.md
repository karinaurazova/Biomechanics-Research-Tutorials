# Tutorial 19 master class — Image-Informed Constitutive Parameters

## Purpose

This 120-minute master class turns Tutorial 19 into a guided teaching session on identification of constitutive parameters from image-derived structure, DIC-like strain fields and force observations.  The session uses only the repository code, synthetic data and saved visualizations, so participants can reproduce every result after the workshop.

## Audience and prerequisites

The session is suitable for graduate students, early-stage researchers and instructors who know basic Python, linear algebra and continuum-mechanics notation.  No clinical or experimental dataset is required.

## Learning outcomes

By the end of the session, participants should be able to:

1. explain the modelling question addressed by Tutorial 19;
2. run the reproducible pipeline with `reproduce.py`;
3. identify which assumptions are synthetic, numerical or mechanical;
4. interpret the benchmark tables and figures without overclaiming validation;
5. modify one controlled parameter and predict the expected qualitative effect.

## 120-minute teaching plan

| Time | Segment | Instructor goal | Participant activity |
|---:|---|---|---|
| 0–10 min | Motivation | Connect the tutorial to soft-tissue biomechanics and verification. | Name the quantity that must be trusted downstream. |
| 10–25 min | Model map | Walk through README, inputs, outputs and main equations. | Mark which variables are known ground truth and which are recovered. |
| 25–45 min | Code orientation | Open `reproduce.py` and the source module. | Locate the data-generation, analysis and plotting functions. |
| 45–65 min | Live run | Execute the tutorial or selected cells from the notebook. | Record generated CSV files and the first figure to inspect. |
| 65–80 min | Visual interpretation | Compare static figures and GIF animations. | Describe one trend that is visible only across the animation. |
| 80–100 min | Metric discussion | Interpret benchmark metrics and failure modes. | Decide which metric is most relevant for mechanics. |
| 100–115 min | Controlled modification | Change one parameter or scenario. | Predict, rerun and compare the result. |
| 115–120 min | Wrap-up | Link the tutorial to neighbouring modules. | State one extension and one limitation. |

## Core classroom activities

- calibrate parameters from load-only data and then add full-field strain information.
- compare VFM-style, inverse-FE-like and Bayesian calibration results.
- identify which parameters are structural and which are mechanical.

## Demonstration order

1. Start from the conceptual diagram in the tutorial README.
2. Show the synthetic input fields before any recovered quantity.
3. Run `python tutorials/19-image-informed-constitutive-parameters/reproduce.py`.
4. Open the main benchmark CSV and ask participants to rank scenarios.
5. Use the GIF animation to discuss how the result changes across a sweep.
6. End with the limitations section and the exercises.

## Discussion prompts

- Which quantity is directly observed, and which quantity is inferred?
- Which metric would be misleading if used alone?
- Where does synthetic ground truth make verification possible?
- What would be required before making an experimental or clinical claim?
- Which later tutorial would use this output as an input?

## Common pitfalls

- Treating high visual quality as proof of mechanical correctness.
- Forgetting that synthetic benchmarks verify a workflow but do not validate a biological claim.
- Comparing scenarios without checking whether they share the same ground truth.
- Ignoring units, normalization and boundary conditions when interpreting downstream mechanics.

## Assessment suggestion

Ask participants to submit a one-page note with: the command they ran, one regenerated figure, one benchmark table row they interpret, one controlled modification, and one limitation of the model.
