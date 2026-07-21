[English](04_mathematical_model.md) | [Русский](ru/04_mathematical_model.md)

# 4. Mathematical model

## 4.1 Axial orientation density

Let the planar fiber direction be

$$
\mathbf{a}(\theta)=
\begin{bmatrix}
\cos\theta\\
\sin\theta
\end{bmatrix},
$$

where $\theta$ and $\theta+\pi$ describe the same physical axis. On one axial period, $\theta\in[-\pi/2,\pi/2)$, define

$$
\rho(\theta;\mu,\beta)
=
\frac{\exp\left[\beta\cos 2(\theta-\mu)\right]}
{\pi I_0(\beta)}.
$$

Here:

- $\mu$ is the mean axial orientation;
- $\beta\ge0$ is the concentration;
- $I_0$ is the modified Bessel function of the first kind.

At $\beta=0$, $\rho=1/\pi$ and the planar distribution is uniform. Increasing $\beta$ narrows the distribution around $\mu$.

## 4.2 Axial order parameter

The second-order parameter is

$$
S=\left\langle\cos 2(\theta-\mu)\right\rangle
=\frac{I_1(\beta)}{I_0(\beta)}.
$$

Thus $S=0$ for a uniform planar distribution and approaches one for perfect alignment. For teaching, we also define

$$
D=1-S,
$$

where larger $D$ means greater dispersion. This $D$ is a tutorial summary index, not a universal constitutive parameter.

## 4.3 Orientation tensor

The planar second-order orientation tensor is

$$
\mathbf{A}
=
\int_{-\pi/2}^{\pi/2}
\rho(\theta)\,\mathbf{a}(\theta)\otimes\mathbf{a}(\theta)\,d\theta.
$$

For the axial von Mises density,

$$
\mathbf{A}
=
\frac{1}{2}
\begin{bmatrix}
1+S\cos2\mu & S\sin2\mu\\
S\sin2\mu & 1-S\cos2\mu
\end{bmatrix}.
$$

Its trace equals one and its eigenvalues are $(1+S)/2$ and $(1-S)/2$. The principal eigenvector identifies the mean axis when $S>0$.

## 4.4 Kinematics

A three-dimensional incompressible uniaxial deformation is prescribed:

$$
\mathbf{F}=\operatorname{diag}(\lambda,\lambda^{-1/2},\lambda^{-1/2}).
$$

For an in-plane fiber, the squared stretch invariant is

$$
I_4(\theta)
=
\lambda^2\cos^2\theta
+
\lambda^{-1}\sin^2\theta.
$$

## 4.5 Tension-only fiber energy

The educational fiber energy is

$$
\psi_f(I_4)
=
\frac{k_1}{2k_2}
\left[
\exp\left(k_2\langle I_4-1\rangle_+^2\right)-1
\right],
$$

where $\langle x\rangle_+=\max(x,0)$. Excluding compressed fibers is an explicit assumption. It avoids assigning compressive stiffness to idealized collagen fibers but does not model buckling, crimp recruitment, or interactions between fibers.

The distributed contribution is evaluated by angular integration:

$$
\Psi_f(\lambda)
=
\int_{-\pi/2}^{\pi/2}
\rho(\theta)\,\psi_f(I_4(\theta))\,d\theta.
$$

A neo-Hookean matrix term is added:

$$
\Psi_m
=
\frac{\mu_m}{2}
\left(\lambda^2+2\lambda^{-1}-3\right).
$$

The nominal stress is

$$
P(\lambda)=\frac{d}{d\lambda}\left(\Psi_m+\Psi_f\right).
$$

## 4.6 Scope and nomenclature

The parameters $\mu_m$, $k_1$, and $k_2$ are dimensionless demonstration values. The concentration $\beta$ describes the π-periodic von Mises density used here. It must not be confused with:

- the dispersion parameter $\kappa$ in the Gasser–Ogden–Holzapfel model;
- a concentration parameter extracted by another fitting convention;
- the dispersity variable used in a remodeling paper.

Parameter symbols are model-specific. Comparisons require matching definitions, dimensions, and normalization.
