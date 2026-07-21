# 01 Motivation and scope

Growth changes mass, local natural dimensions, composition, and often material architecture. A purely elastic model can describe a body that deforms and returns to the same natural state, but it cannot represent a persistent change of that state. Finite-growth mechanics therefore introduces an internal map that records how an infinitesimal material neighbourhood would change if it could grow without being forced to fit its neighbours.

The central distinction is between **observable shape change** and **local natural-state change**. The deformation gradient \(\mathbf F\) is obtained from the compatible motion of the body. The growth tensor \(\mathbf F_g\), by contrast, is generally not the gradient of a globally realizable deformation. It describes a local stress-free change. The elastic tensor \(\mathbf F_e\) restores compatibility and is the part used by the elastic constitutive law.

This framework was introduced for soft tissues in the classical finite-growth formulation of Rodriguez, Hoger, and McCulloch. It has since been used in cardiac growth, vascular adaptation, morphogenesis, tumour growth, surface wrinkling, and many other systems. The breadth of applications does not remove the need for caution: a multiplicative split is a modelling hypothesis, not a directly measured fact.

Tutorial 07 focuses on the kinematic and computational foundations required before a full boundary-value problem is attempted. The model is homogeneous where possible, spatial only where incompatibility must be demonstrated, and deliberately synthetic. The objective is to make every identity, stress transformation, and numerical update testable.

The tutorial does not yet solve a three-dimensional finite-element equilibrium problem. That extension is reserved for Tutorial 18. It also does not replace constituent turnover or constrained-mixture theory. Instead, it establishes a precise morphoelastic language that later modules can compare with mixture-based descriptions.
