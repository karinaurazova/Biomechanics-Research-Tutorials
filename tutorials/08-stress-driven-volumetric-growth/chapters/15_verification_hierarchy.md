# Verification hierarchy

The verification sequence is deliberately layered:

1. \(\det\mathbf F_g=J_g\);
2. free growth produces \(\mathbf F_e=\mathbf I\) and zero stress;
3. exponential updates preserve \(J_g>0\);
4. fixed hydrostatic deformation relaxes the selected mean stress;
5. stress control holds the imposed stimulus and changes size;
6. isotropic growth cannot eliminate deviatoric stress in a uniaxial constraint;
7. the spatial regularisation decreases a roughness metric;
8. benchmark results are written to a machine-readable CSV file.

Verification checks whether the equations and code behave as intended. Validation would require independent biological or experimental observations. This release provides only a synthetic verification-ready benchmark.
