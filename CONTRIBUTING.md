[English](CONTRIBUTING.md) | [Русский](CONTRIBUTING.ru.md)

# Contributing

Contributions should preserve the educational and scientific consistency of the repository.

## Required tutorial elements

Each new tutorial should include:

- a clearly formulated biological or mechanical question;
- learning objectives written with observable verbs;
- explicit assumptions and limitations;
- equations with definitions of all variables and parameters;
- a reproducible baseline experiment;
- at least one parameter study;
- lightweight automated tests;
- exercises at the Explore, Experiment, and Research Challenge levels;
- a distinction between verification, validation, and demonstration.
- equivalent English and Russian educational content;
- localized visual outputs generated from the same numerical scripts and data;

## Code style

- Python 3.10 or newer;
- type hints for public functions;
- NumPy-style docstrings;
- deterministic examples where randomness is used;
- generated outputs should not be committed unless they are part of the tutorial narrative.

## Scientific language

Avoid claims of biological realism beyond the assumptions of the model. A toy model may be useful and insightful without being experimentally validated.
