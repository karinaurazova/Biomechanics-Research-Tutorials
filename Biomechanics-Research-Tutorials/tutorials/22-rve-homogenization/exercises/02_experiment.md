# Experiment

Modify the RVE generation parameters in `reproduce.py` or call `homogenize_rve(nx=..., ny=..., seed=...)` from a notebook.

Suggested experiments:

- increase the pore fraction by modifying `generate_microstructure`;
- reduce fiber stiffness in `LocalMaterialParameters`;
- change the random seed and compare anisotropy ratios;
- increase the RVE resolution and inspect the convergence table;
- compare a strongly aligned field with a nearly random orientation field.

For each experiment, report whether the change affects stiffness magnitude, anisotropy direction, or both.
