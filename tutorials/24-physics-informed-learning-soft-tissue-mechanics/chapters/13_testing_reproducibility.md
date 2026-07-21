# Testing and reproducibility

The tests check dataset generation, stiffness positivity, residual reduction, weight-sweep output and inverse calibration. They are not meant to prove biological truth. They prove that the computational experiment is internally consistent and reproducible.

The reproduce script regenerates all major tables and figures from a fixed seed. This makes the tutorial suitable for classroom use and for GitHub-based regression testing.

Students are encouraged to modify the noise level, observation density and image-prior bias to see when the method becomes unstable.
