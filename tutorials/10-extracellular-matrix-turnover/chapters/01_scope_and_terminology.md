# Scope, terminology, and the central modeling question

Extracellular-matrix turnover is the continuous production, processing, deposition, maturation, damage, and removal of matrix constituents. It is not synonymous with growth. A tissue may maintain constant geometry and total collagen mass while replacing a large fraction of its matrix; conversely, mass may increase without formation of a mechanically mature network.

The central modeling question is therefore not merely “how much matrix is present?” but “which material is present, when was it deposited, in which natural state, how mature is it, how strongly is it cross-linked, and which mechanical load does it carry?” Tutorial 10 separates these questions into explicit state variables.

We distinguish **turnover** (replacement), **remodeling** (change of architecture or properties), **growth** (change of natural volume or mass), **repair** (response to injury), and **damage** (loss of load-bearing capacity). These processes can coexist but must not be collapsed into one scalar multiplier.

The implemented models are synthetic and verification-oriented. They are designed to expose assumptions, conservation laws, timescale separation, and identifiability. They do not provide tissue-specific biological rates.

## Key modeling checkpoint

State explicitly which quantities are conserved, which are constitutive assumptions, and which are experimentally observable.
