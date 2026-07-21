# Constitutive assumptions

Residual stress cannot be reconstructed from geometry alone. The sector problem requires a constitutive law for the elastic accommodation. The core implementation uses incompressible neo-Hookean response with optional tension-only circumferential reinforcement.

Alternative choices include Mooney–Rivlin, Fung-type exponentials, Holzapfel–Gasser–Ogden dispersion, Lanir angular integration, viscoelasticity, active tone, damage, and compressible formulations. The inferred stress field can be highly model dependent.

Constitutive parameters, units, fiber configuration, recruitment threshold, and compression treatment must be reported together with the opening angle.
