# Mixture stress and energy

Mixture stress is the sum of consistently normalized constituent stresses. This apparently simple statement depends on whether constituent energies are per unit mass, constituent reference volume, mixture reference volume, or current volume.

The code uses one explicit convention and tests that component stresses sum to the reported total. Learners are asked to change the convention and identify every place where Jacobians or density factors must change.

A constituent may carry little mass but large stress because of stiffness or prestretch. Mass fraction and load fraction are therefore distinct diagnostics.
