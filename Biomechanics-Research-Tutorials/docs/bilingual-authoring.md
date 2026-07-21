[English](https://github.com/karinaurazova/Biomechanics-Research-Tutorials/blob/main/docs/bilingual-authoring.md) | [Русский](https://github.com/karinaurazova/Biomechanics-Research-Tutorials/blob/main/docs/ru/bilingual-authoring.md)

# Bilingual authoring workflow

Every new tutorial is authored as one executable project with two educational language layers.

## Recommended sequence

1. Freeze the research question, equations, parameter definitions, and evidence boundary.
2. Implement and verify the shared Python model.
3. Generate one set of numerical results and localized English/Russian figures from the same scripts.
4. Write the English teaching narrative.
5. Create the Russian narrative with equivalent scientific meaning.
6. Translate notebook Markdown and localized messages while preserving computationally equivalent code cells.
7. Create paired workshop and assessment materials.
8. Run `pytest -q` to check language parity and numerical behavior.

## Release checklist

- [ ] `README.md` and `README.ru.md` exist.
- [ ] Every chapter has an English and Russian file.
- [ ] Every exercise has an English and Russian file.
- [ ] English and Russian notebooks use the same numerical workflow.
- [ ] Instructor notes and workshop materials are paired.
- [ ] Every committed educational figure and animation has a localized pair.
- [ ] Paired visualizations are produced from identical parameters and data.
- [ ] Equations, parameter values, and evidence claims match.
- [ ] All local links resolve.
- [ ] The tutorial remains reproducible through one shared codebase.

## Translation principle

Translate ideas, not word order. Use established Russian terminology, retain standard code identifiers, and never strengthen a claim in one language version.
