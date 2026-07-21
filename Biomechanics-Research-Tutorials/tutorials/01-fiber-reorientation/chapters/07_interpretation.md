[English](07_interpretation.md) | [Русский](ru/07_interpretation.md)

# 7. Interpretation and limitations

The model demonstrates five useful ideas:

1. orientation variables require periodic mathematics appropriate for axes;
2. a first-order kinetic law creates a characteristic adaptation time;
3. analytical solutions can be used to verify numerical code;
4. a moving cue produces a delayed structural response;
5. seemingly harmless initial conditions can expose non-uniqueness.

However, the model does not identify a real biological remodeling rate. It also does not distinguish between rotation, deposition, degradation, cell-mediated matrix contraction, or deformation-induced apparent reorientation.

## What would be required for validation?

A validation study would need:

- a clearly defined tissue, cell population, and loading protocol;
- time-resolved measurements of orientation or an orientation distribution;
- a rule for extracting the mechanical cue from measured or simulated fields;
- independent parameter estimation;
- an error metric and uncertainty analysis;
- comparison against alternative remodeling hypotheses;
- evidence that remodeling is separated from instantaneous deformation.

## Interpretation checklist

Before describing a simulation result, ask:

1. Is the output a direction, an axis, or a distribution?
2. Was the mechanical cue prescribed or computed?
3. Is the reported timescale dimensional and experimentally calibrated?
4. Does the model resolve a mechanism or only an effective response?
5. Was the result verified numerically?
6. What observation could falsify the hypothesis?

The present tutorial is best described as a transparent educational model and a reproducible synthetic benchmark.
