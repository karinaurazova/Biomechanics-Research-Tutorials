# Tutorial 01 — Fiber Reorientation

## Research question

**How does an initially misaligned fiber family adapt toward a prescribed mechanical direction, and how does the remodeling rate control the adaptation time?**

This tutorial introduces a minimal evolution law for fiber orientation. It is intentionally simple enough to derive, implement, verify, and extend in one teaching session, while still exposing an important modeling issue: a fiber is an **axis**, not an arrow. Therefore, orientations separated by 180 degrees are physically equivalent.

## Learning objectives

After completing the tutorial, the learner should be able to:

1. explain why fiber orientation is represented as an axial quantity;
2. distinguish a target mechanical direction from an experimentally measured fiber direction;
3. formulate a first-order reorientation law;
4. implement the law using a periodic angular difference;
5. verify limiting cases and numerical behavior;
6. conduct a parameter study of the remodeling rate;
7. interpret the model's scope and limitations;
8. propose a research-level extension.

## Prerequisites

- basic trigonometry;
- first-order ordinary differential equations;
- elementary Python and NumPy;
- basic understanding of anisotropy.

## Tutorial map

1. [Motivation](chapters/01_motivation.md)
2. [Learning objectives and assessment](chapters/02_learning_objectives.md)
3. [Biological and mechanical background](chapters/03_biological_background.md)
4. [Mathematical model](chapters/04_mathematical_model.md)
5. [Numerical method and verification](chapters/05_numerical_method.md)
6. [Computational experiments](chapters/06_computational_experiments.md)
7. [Interpretation and limitations](chapters/07_interpretation.md)
8. [Further reading and extensions](chapters/08_further_reading.md)

## Run the baseline

From the repository root:

```bash
pip install -e .[dev]
python tutorials/01-fiber-reorientation/experiments/baseline.py
```

Run the full tutorial experiment set:

```bash
make tutorial-01
```

Run verification tests:

```bash
pytest -q
```

## Model summary

The evolution law is

\[
\dot{\theta}=k\,\Delta(\theta_\mathrm{target},\theta),
\]

where \(\theta\) is the current fiber orientation, \(k\) is the remodeling rate, and \(\Delta\) is the shortest signed **axial** angle.

The axial angle difference is evaluated through the doubled-angle representation:

\[
\Delta(\theta_t,\theta)
=
\frac{1}{2}\operatorname{atan2}
\left[
\sin 2(\theta_t-\theta),
\cos 2(\theta_t-\theta)
\right].
\]

This choice enforces the physical equivalence \(\theta\equiv\theta+\pi\).

## Outputs

The scripts generate:

- orientation versus time;
- angular error versus time;
- alignment index versus time;
- comparison of multiple remodeling rates;
- response to a changing target direction;
- an animation of a synthetic fiber population.

## Exercise levels

- [Explore](exercises/explore.md): reproduce and inspect the baseline;
- [Experiment](exercises/experiment.md): formulate and analyse a parameter study;
- [Research Challenge](exercises/research_challenge.md): extend the remodeling hypothesis.

## Scientific status

This is a **didactic toy model** and a **verification-oriented synthetic demonstration**. It does not constitute experimental validation of a biological remodeling law.
