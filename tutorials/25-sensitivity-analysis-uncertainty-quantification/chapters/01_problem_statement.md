# Problem statement: uncertainty after model building

After a model can be solved, the next question is not only whether it runs, but whether its predictions are stable under uncertain inputs. Soft-tissue simulations contain structural parameters, loading parameters, boundary-condition assumptions and measurement noise. This tutorial treats those quantities as uncertain and propagates them to stiffness, stress, strain energy and a growth stimulus.

## Implementation notes

The corresponding code is in `src/biomechanics_tutorials/sensitivity_uncertainty.py`. Run `reproduce.py` to regenerate the tables, figures and GIF animations used in this chapter. The chapter should be read together with the CSV files in `data/`, because the goal is not only to view a plot but to understand exactly which assumptions produced it.

## What to check

- Are the parameter ranges physically plausible for the intended educational problem?
- Does the output uncertainty come from one dominant parameter or from interactions?
- Would the conclusion change if the prior range or mechanical limit were modified?
