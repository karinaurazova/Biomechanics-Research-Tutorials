# Stress-driven growth update


After solving equilibrium, the code computes two stress stimuli.  The first is a plane-stress mean stress proxy, one half of sigma_xx plus sigma_yy.  The second is fiber stress sigma_ff, obtained by projecting the stress tensor onto the local fiber direction.  These are not the only possible biological stimuli, but they are interpretable and easy to compute.

The update law changes isotropic growth and fiber growth explicitly in time.  Stress values are smoothed over neighboring elements before they affect growth.  This avoids an unrealistic checkerboard response to element-wise numerical noise and mimics the idea that biological remodeling is not infinitely local.

The update law contains targets.  If the current stress differs from the target, growth changes.  This makes the model a simple homeostatic feedback system.  The feedback is intentionally mild, bounded and explicit.  Aggressive gains can cause oscillations or clipping.  That is a useful lesson: growth laws are dynamical systems, not just algebraic corrections.

The tutorial compares frozen growth, full stress feedback and fiber-only feedback.  The differences among these scenarios reveal which parts of the stress field are controlled by isotropic growth and which parts are controlled by fiber-direction growth.  They also show that adding a feedback law does not automatically improve every metric.

In a research-grade model, the update law would be calibrated to biological turnover, cell response, constituent deposition and degradation.  Here it is a controlled numerical mechanism for learning how feedback enters a finite-element pipeline.
