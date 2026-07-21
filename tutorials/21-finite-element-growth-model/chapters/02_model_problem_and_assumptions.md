# Model problem and assumptions


The computational specimen is a two-dimensional rectangular patch.  It represents a generic soft-tissue region rather than a specific organ.  The patch contains a spatially heterogeneous isotropic growth variable and a fiber-direction growth variable.  The fiber angle varies smoothly through the domain, mimicking the fact that biological tissues often have regional orientation fields rather than one uniform direction.

The model is plane stress.  This means the stress component normal to the computational plane is assumed negligible.  Plane stress is a useful teaching approximation for thin samples and image-informed planar experiments, but it is not a universal assumption.  A thick organ wall, a confined hydrogel or a nearly incompressible tissue under triaxial loading would require a different formulation.

The mechanical constitutive law is linear elastic.  This is not because soft tissues are linear.  They are not.  The point is pedagogical: a linear elastic model isolates the finite-element assembly and growth-accommodation mechanism.  Nonlinear hyperelasticity would add Newton iterations, numerical quadrature details and tangent moduli.  Those are important, but they can obscure the first learning objective.

Growth enters as an eigenstrain.  The stress is not produced by total strain alone; it is produced by the difference between total strain and growth strain.  A region may have nonzero growth strain but low stress if the body can deform to accommodate it.  Conversely, a smooth growth field may produce stress near constrained boundaries or near incompatible gradients.

The model includes three scenarios.  In frozen growth, the initial growth field is solved repeatedly without updating.  In stress feedback, isotropic and fiber growth change according to stress stimuli.  In fiber-only feedback, only the fiber growth variable adapts.  These scenarios are not biological claims; they are controlled computational experiments that teach what changes when feedback is activated.
