# Uncertain parameters and admissible ranges

The benchmark uses eight bounded parameters: matrix modulus, fibre gain, fibre fraction, orientation, concentration, connectivity, load scale and boundary compliance. The ranges are deliberately explicit. A reader can decide whether a reported conclusion depends on a narrow calibration assumption or on a robust mechanical trend.

## Implementation notes

The corresponding code is in `src/biomechanics_tutorials/sensitivity_uncertainty.py`. Run `reproduce.py` to regenerate the tables, figures and GIF animations used in this chapter. The chapter should be read together with the CSV files in `data/`, because the goal is not only to view a plot but to understand exactly which assumptions produced it.

## What to check

- Are the parameter ranges physically plausible for the intended educational problem?
- Does the output uncertainty come from one dominant parameter or from interactions?
- Would the conclusion change if the prior range or mechanical limit were modified?
