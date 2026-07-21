# 6. Mechanical cue selection and degeneracy

Common target directions include maximum principal stress, maximum principal strain, maximum principal stretch, or a weighted combination of principal directions. These choices are not interchangeable in anisotropic, incompressible, actively contracting, or residually stressed tissues.

A principal direction becomes ill-conditioned when the associated eigenvalue gap approaches zero. Near an equibiaxial state, an arbitrarily small perturbation can rotate the computed eigenvector by a large angle. The problem is mathematical, not numerical: the physical state genuinely lacks a unique preferred principal direction.

A robust remodeling model should therefore record at least one confidence measure, such as

\[
\chi=
\frac{|\lambda_1-\lambda_2|}
{|\lambda_1|+|\lambda_2|+\varepsilon}.
\]

Possible responses to low confidence include freezing the direction, retaining the previous direction, blending several cues, evolving a distribution rather than one axis, or declaring the state non-identifiable.

Taber's vascular growth models illustrate that distinct stimuli may regulate different aspects of adaptation, for example fluid shear and fiber stress. Hariton and co-workers proposed stress-driven preferred directions in arterial walls. Such models must state how multiple principal stresses are converted into one or more collagen-family directions.
