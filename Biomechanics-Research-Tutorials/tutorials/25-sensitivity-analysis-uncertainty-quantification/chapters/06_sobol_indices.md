# Sobol variance-based sensitivity

Sobol indices decompose output variance into parameter contributions. First-order indices estimate direct effects; total indices also include interactions. In biomechanics this distinction is important because fibre fraction, connectivity and orientation often act together rather than independently.

## Implementation notes

The corresponding code is in `src/biomechanics_tutorials/sensitivity_uncertainty.py`. Run `reproduce.py` to regenerate the tables, figures and GIF animations used in this chapter. The chapter should be read together with the CSV files in `data/`, because the goal is not only to view a plot but to understand exactly which assumptions produced it.

## What to check

- Are the parameter ranges physically plausible for the intended educational problem?
- Does the output uncertainty come from one dominant parameter or from interactions?
- Would the conclusion change if the prior range or mechanical limit were modified?
