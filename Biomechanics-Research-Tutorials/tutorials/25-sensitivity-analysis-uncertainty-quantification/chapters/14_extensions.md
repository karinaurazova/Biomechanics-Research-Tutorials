# Extensions and research tasks

Natural extensions include correlated priors, hierarchical Bayesian calibration, uncertainty in geometry, mesh-dependent numerical error, surrogate-model uncertainty and patient- or specimen-specific inverse problems. The included exercises move from simple parameter changes to research-level redesigns.

## Implementation notes

The corresponding code is in `src/biomechanics_tutorials/sensitivity_uncertainty.py`. Run `reproduce.py` to regenerate the tables, figures and GIF animations used in this chapter. The chapter should be read together with the CSV files in `data/`, because the goal is not only to view a plot but to understand exactly which assumptions produced it.

## What to check

- Are the parameter ranges physically plausible for the intended educational problem?
- Does the output uncertainty come from one dominant parameter or from interactions?
- Would the conclusion change if the prior range or mechanical limit were modified?
