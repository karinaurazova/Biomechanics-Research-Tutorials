# Tutorial 24 workbook — Physics-Informed Learning for Soft-Tissue Mechanics

## Before you start

Open the tutorial folder:

```bash
cd tutorials/24-physics-informed-learning-soft-tissue-mechanics
```

Read `README.md` and identify the input data, recovered quantities and benchmark outputs.

## Task 1 — Run the baseline

```bash
python reproduce.py
```

Record:

- the main dataset file in `data/`;
- the main benchmark table in `data/`;
- two figures from `figures/`;
- one animation from `animations/`, if present.

## Task 2 — Interpret the pipeline

Write three short statements:

1. What is known exactly because the data are synthetic?
2. What is estimated by the method?
3. Which output would affect a downstream mechanics calculation?

## Task 3 — Compare scenarios

Use the benchmark table and figures to answer:

- Which scenario gives the best numerical metric?
- Which scenario gives the most mechanically useful result?
- Are those two answers the same?  Explain why or why not.

## Task 4 — Controlled modification

Change one documented parameter, rerun the tutorial and compare the result.  Do not change several parameters at once.

Suggested report table:

| Quantity | Baseline | Modified run | Interpretation |
|---|---:|---:|---|
| Primary error metric |  |  |  |
| Main structural/mechanical metric |  |  |  |
| Most visible figure change |  |  |  |

## Reflection

Finish with one paragraph: what does this tutorial verify, and what does it not validate?
