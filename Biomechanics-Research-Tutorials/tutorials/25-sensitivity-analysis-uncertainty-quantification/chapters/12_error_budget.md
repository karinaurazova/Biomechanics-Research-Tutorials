# Error budget across the modeling pipeline

An error budget asks where uncertainty enters the pipeline: segmentation, orientation recovery, material calibration, boundary conditions, loading or surrogate approximation. The tutorial uses parameter-level diagnostics as a first step toward a full pipeline-level budget.

## Implementation notes

The corresponding code is in `src/biomechanics_tutorials/sensitivity_uncertainty.py`. Run `reproduce.py` to regenerate the tables, figures and GIF animations used in this chapter. The chapter should be read together with the CSV files in `data/`, because the goal is not only to view a plot but to understand exactly which assumptions produced it.

## What to check

- Are the parameter ranges physically plausible for the intended educational problem?
- Does the output uncertainty come from one dominant parameter or from interactions?
- Would the conclusion change if the prior range or mechanical limit were modified?
