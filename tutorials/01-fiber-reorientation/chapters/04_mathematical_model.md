[English](04_mathematical_model.md) | [Русский](ru/04_mathematical_model.md)

# 4. Mathematical model

## 4.1 State variable

Let $\theta(t)$ denote the orientation of an undirected fiber axis in a two-dimensional plane. Because an axis has no arrowhead,

$$
\theta \equiv \theta + \pi.
$$

A naive difference $\theta_t-\theta$ can therefore be incorrect near an angular boundary. The model uses the shortest signed axial difference

$$
\Delta(\theta_t,\theta)
=
\frac{1}{2}\operatorname{atan2}
\left(
\sin[2(\theta_t-\theta)],
\cos[2(\theta_t-\theta)]
\right).
$$

The doubled angle converts an axial variable with period $\pi$ into a directional variable with period $2\pi$.

## 4.2 Evolution equation

The minimal first-order law is

$$
\frac{d\theta}{dt}=k\,\Delta(\theta_t,\theta),
$$

where:

- $\theta$ is the current orientation;
- $\theta_t$ is the target direction;
- $k\ge 0$ is a remodeling rate with dimensions of inverse time.

This law is a didactic relaxation model. It is not presented as the exact evolution equation from any cited experiment or computational paper.

## 4.3 Fixed-target analytical solution

For a constant target and an initial axial mismatch strictly smaller than $90^\circ$, define

$$
e(t)=\Delta(\theta_t,\theta(t)).
$$

On a fixed angular branch,

$$
\frac{de}{dt}=-ke,
\qquad
 e(t)=e_0 e^{-kt}.
$$

Therefore, the characteristic adaptation time is $\tau=1/k$. The time required to reach a tolerance $\varepsilon$ is

$$
t_\varepsilon=
\frac{1}{k}\ln\left(\frac{|e_0|}{\varepsilon}\right),
\qquad |e_0|>\varepsilon.
$$

This analytical result provides a direct verification target for the numerical implementation.

## 4.4 The exactly orthogonal state

When $|\Delta|=90^\circ$, the two possible rotation directions have equal angular length. The model does not supply an additional rule to choose between them. Floating-point roundoff can therefore select a branch accidentally.

This is not merely a coding inconvenience. It is a statement about model incompleteness. A unique prediction would require an additional ingredient, such as:

- a small perturbation or measured bias;
- a history-dependent rule;
- a second mechanical cue;
- stochastic dynamics;
- a distribution-based formulation.

## 4.5 Alignment index

For visualization, the tutorial uses

$$
A=\cos^2\Delta.
$$

Then $A=1$ denotes aligned axes and $A=0$ denotes an orthogonal mismatch. This is an educational summary measure, not a constitutive material parameter.

## 4.6 Assumptions

1. A single effective fiber family is represented.
2. The problem is two-dimensional.
3. The target direction is known and prescribed.
4. The remodeling rate is constant.
5. No threshold, delay, damage, turnover, or stochasticity is included.
6. The law changes orientation only; it does not change stiffness or mass.
7. Elastic rotation caused by instantaneous deformation is not separated from structural remodeling.
