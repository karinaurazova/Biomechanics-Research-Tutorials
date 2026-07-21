# Master class 01 — Fiber Reorientation

**Duration:** 120 minutes
**Format:** short lecture + guided derivation + live coding + paired interpretation
**Audience:** senior undergraduate, master's, early doctoral, or interdisciplinary research trainees

## Learning outcomes

By the end, participants will be able to:

1. represent an undirected fiber orientation correctly;
2. derive and implement a first-order adaptation law;
3. verify a numerical solution against an analytical solution;
4. diagnose non-uniqueness at a 90-degree mismatch;
5. distinguish computational verification from biological validation.

## Required preparation

Instructor:

- install the package and run `make tutorial-01`;
- confirm that `pytest -q` passes;
- open the baseline and orthogonal-case figures;
- prepare one blank notebook or coding environment.

Participants:

- Python environment with NumPy and Matplotlib;
- basic familiarity with ODEs and trigonometry;
- repository cloned before the session where possible.

## Session plan

| Time | Activity | Instructor action | Participant evidence |
|---:|---|---|---|
| 0–10 min | Biological motivation | Contrast matrix reorganization, turnover, and apparent rotation | Identify two possible mechanisms |
| 10–25 min | Axial orientation | Demonstrate 10° = 190° and naive subtraction failure | Compute three axial differences |
| 25–40 min | Model derivation | Introduce doubled-angle difference and first-order law | Annotate variables and units |
| 40–55 min | Analytical solution | Derive exponential relaxation and time-to-tolerance | Calculate one adaptation time |
| 55–75 min | Live coding | Implement wrapper, mismatch, and Euler loop | Run baseline simulation |
| 75–90 min | Verification | Compare Euler and analytical trajectories; discuss kΔt | Record numerical discrepancy |
| 90–105 min | Non-uniqueness | Run orthogonal-case experiment | Explain branch selection |
| 105–115 min | Mini investigation | Pairs vary k or Δt and interpret results | One figure + one claim |
| 115–120 min | Exit ticket | Separate verification and validation | Submit two-sentence response |

## Exit ticket

1. Give one statement showing that the code is verified.
2. Give one statement explaining why the biological law is not validated.

## Differentiation

For less experienced participants, provide the Euler loop and ask them to complete the angle function. For advanced participants, ask them to compute the target direction from a symmetric 2D stress tensor and discuss eigenvector sign ambiguity.

## Assessment rubric

| Dimension | Emerging | Competent | Advanced |
|---|---|---|---|
| Axial representation | Uses directed subtraction | Uses doubled-angle mismatch | Explains topology and non-uniqueness |
| Numerical method | Runs code | Performs analytical comparison | Quantifies convergence order |
| Interpretation | Describes graph | Links behavior to parameters | Proposes a falsifiable extension |
| Scientific caution | Implies validation | States limitations | Designs a validation dataset |

## Reuse formats

- 45-minute lecture: omit live coding and use prepared figures;
- 90-minute workshop: omit the changing-target experiment;
- 3-hour practical: add the Research Challenge and short presentations;
- outreach demonstration: retain the animation, axial-angle puzzle, and parameter slider concept.
