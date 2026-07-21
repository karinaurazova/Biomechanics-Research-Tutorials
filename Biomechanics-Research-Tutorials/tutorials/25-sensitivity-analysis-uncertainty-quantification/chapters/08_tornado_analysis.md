# Tornado plots and one-at-a-time checks

Tornado analysis changes one parameter at a time between its lower and upper bounds. It is not a substitute for global sensitivity analysis, because it ignores interactions, but it is easy to explain and useful for debugging signs, units and dominant directions of influence.

## Implementation notes

The corresponding code is in `src/biomechanics_tutorials/sensitivity_uncertainty.py`. Run `reproduce.py` to regenerate the tables, figures and GIF animations used in this chapter. The chapter should be read together with the CSV files in `data/`, because the goal is not only to view a plot but to understand exactly which assumptions produced it.

## What to check

- Are the parameter ranges physically plausible for the intended educational problem?
- Does the output uncertainty come from one dominant parameter or from interactions?
- Would the conclusion change if the prior range or mechanical limit were modified?
