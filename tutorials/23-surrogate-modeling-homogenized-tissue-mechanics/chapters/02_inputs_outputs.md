# Inputs and outputs


The input vector contains a mean fiber angle, concentration parameter, fiber fraction, porosity, connectivity and a small-strain loading state.  These variables are deliberately close to the quantities produced by Tutorials 17--22: segmentation, orientation analysis, image-informed constitutive identification and RVE homogenization.

The output vector contains six effective stiffness entries and three stress components.  Predicting both stiffness and stress makes the learning task more informative: stiffness tests whether the structure-to-material map was learned, while stress tests whether the model is mechanically useful under loading.

The workflow also separates structural descriptors from loading descriptors.  This avoids a common mistake: a surrogate may seem accurate because it memorizes a narrow set of load cases, while failing to learn the material response itself.
