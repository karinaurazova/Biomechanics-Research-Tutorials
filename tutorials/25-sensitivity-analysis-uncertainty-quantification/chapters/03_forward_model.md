# Forward structure-mechanics map

The forward model is a compact anisotropic small-strain surrogate. Fibre terms depend on direction, concentration and connectivity; matrix terms provide a baseline stiffness. The model is not intended as a clinical constitutive law. Its role is to provide a transparent map where uncertainty methods can be inspected line by line.

## Implementation notes

The corresponding code is in `src/biomechanics_tutorials/sensitivity_uncertainty.py`. Run `reproduce.py` to regenerate the tables, figures and GIF animations used in this chapter. The chapter should be read together with the CSV files in `data/`, because the goal is not only to view a plot but to understand exactly which assumptions produced it.

## What to check

- Are the parameter ranges physically plausible for the intended educational problem?
- Does the output uncertainty come from one dominant parameter or from interactions?
- Would the conclusion change if the prior range or mechanical limit were modified?
