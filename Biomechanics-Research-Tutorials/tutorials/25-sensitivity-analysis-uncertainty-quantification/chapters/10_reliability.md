# Probability of exceeding a mechanical limit

A reliability calculation converts an output distribution into a probability of exceeding a chosen mechanical limit. The limit in this tutorial is synthetic, but the logic is the same for verification studies: define the limit, propagate uncertainty, and report the probability together with assumptions.

## Implementation notes

The corresponding code is in `src/biomechanics_tutorials/sensitivity_uncertainty.py`. Run `reproduce.py` to regenerate the tables, figures and GIF animations used in this chapter. The chapter should be read together with the CSV files in `data/`, because the goal is not only to view a plot but to understand exactly which assumptions produced it.

## What to check

- Are the parameter ranges physically plausible for the intended educational problem?
- Does the output uncertainty come from one dominant parameter or from interactions?
- Would the conclusion change if the prior range or mechanical limit were modified?
