[English](01_motivation.md) | [Русский](ru/01_motivation.md)

# 1. Motivation

Fibrous biological tissues derive much of their directional mechanical behavior from the organization of collagen fibers, muscle cells, or other elongated structural components. When loading conditions change over sufficiently long times, the internal architecture may also change.

Experimental systems show that cell-generated forces, tissue constraints, and cyclic loading can reorganize collagen networks or alter the alignment of cells and newly deposited matrix. These observations do not imply one universal alignment rule: the resulting direction depends on the tissue, loading mode, boundary constraints, timescale, and biological mechanism.

A computational model of reorientation therefore needs at least two ingredients:

1. a mechanical cue that identifies one or more preferred directions;
2. an evolution law that describes how the current architecture responds over time.

The first tutorial deliberately separates these ingredients. The preferred direction is prescribed rather than computed from a full stress analysis. This keeps the focus on orientation kinematics, angular periodicity, verification, and model interpretation.

## Guiding question

If a fiber family starts at $-50^\circ$ and the preferred mechanical direction is $30^\circ$, how does the orientation evolve, and how does the response change when the remodeling rate is varied?

## Why the baseline is not exactly orthogonal

An earlier draft used $-60^\circ$ and $30^\circ$. Those axes differ by exactly $90^\circ$. At that state, clockwise and counter-clockwise rotation are equally short, so the minimal law cannot choose a unique branch. The revised baseline uses an $80^\circ$ mismatch, while the orthogonal state is retained as a separate diagnostic experiment.
