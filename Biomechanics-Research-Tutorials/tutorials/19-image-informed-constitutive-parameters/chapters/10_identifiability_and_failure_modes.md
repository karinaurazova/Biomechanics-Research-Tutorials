# 10 — Identifiability and failure modes

The same load curve can often be reproduced by several parameter combinations. This is a structural inverse-problem issue, not merely a numerical inconvenience.

Tutorial 19 reports singular values of the design matrix. A very small singular value means that at least one parameter direction has weak influence on the observations. The corresponding singular vector indicates which combination of parameters is hard to distinguish.

Common failure modes include:

- too few loading modes;
- loading that does not excite the fibre direction;
- nearly uniform orientation fields;
- segmentation bias in fibre fraction;
- overconfident priors;
- calibrating too many parameters from too few observations;
- using Dice or IoU as the only image metric while ignoring mechanical sensitivity.
