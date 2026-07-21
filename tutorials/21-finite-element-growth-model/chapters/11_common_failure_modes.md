# Common failure modes


Finite-element growth models can fail in several ways.  The first is a boundary-condition failure.  If rigid modes are not removed, the system is singular.  If too many nodes are fixed, the model may produce artificial stress.  The tutorial chooses a minimal support, but exercises ask learners to compare it with clamped and freer alternatives.

The second failure is a sign convention error.  The growth strain should reduce elastic strain when the displacement accommodates growth.  If the equivalent growth load sign is reversed, the solution may still look plausible but the stress field has the wrong interpretation.  This is why the tutorial explains the weak form and tests the residual.

The third failure is overinterpreting a small-strain model.  Linearized growth is useful for learning, but large biological growth requires finite kinematics.  When growth variables become large, the small-strain approximation becomes a limitation.  The code clips growth variables to keep the demonstration within a safe range.

The fourth failure is mistaking feedback for calibration.  A stress-driven update law can produce interesting dynamics without being experimentally identified.  The tutorial labels the law as synthetic and pedagogical.  In real tissue modeling, turnover rates, stress targets and constituent-specific responses require independent evidence.

The fifth failure is ignoring mesh dependence.  A CST mesh can be sufficient for a first demonstration but not for quantitative predictions.  Mesh refinement, element choice and quadrature matter.  Tutorial 21 prepares the ground for later RVE and surrogate-modeling modules where these numerical choices become even more important.
