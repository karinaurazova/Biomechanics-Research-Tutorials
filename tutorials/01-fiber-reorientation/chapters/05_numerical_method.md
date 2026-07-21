[English](05_numerical_method.md) | [Русский](ru/05_numerical_method.md)

# 5. Numerical method and verification

The ordinary differential equation is integrated with the explicit Euler method:

$$
\theta_{n+1}
=
\theta_n
+
\Delta t\,k\,\Delta(\theta_{t,n},\theta_n).
$$

The updated angle is wrapped back to an interval of length $\pi$.

## 5.1 Local stability and monotonicity

On a fixed branch with a constant target, the error update is

$$
e_{n+1}=(1-k\Delta t)e_n.
$$

The explicit Euler approximation is stable for

$$
0<k\Delta t<2,
$$

and its error decays without alternating sign when

$$
0<k\Delta t\le 1.
$$

The software rejects parameter sets with $k\Delta t\ge2$. Learners should still perform a time-step study because stability alone does not guarantee adequate accuracy.

## 5.2 Verification hierarchy

The tutorial includes four levels of verification:

1. **Representation tests** — axial equivalence and angle wrapping;
2. **Limiting cases** — zero remodeling rate and already-aligned states;
3. **Analytical comparison** — Euler trajectory versus exponential relaxation;
4. **Refinement study** — decreasing $\Delta t$ and measuring numerical discrepancy.

The exactly orthogonal state is tested separately as a non-unique case rather than used as the baseline.

## 5.3 Verification is not validation

Verification asks whether the equations are solved and implemented correctly. Validation asks whether the equations adequately represent a specified biological system. The automated tests in this repository address verification only.
