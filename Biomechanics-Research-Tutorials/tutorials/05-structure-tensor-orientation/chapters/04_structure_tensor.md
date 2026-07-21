# 04 Structure-tensor formulation

Let $I(x,y)$ be a grayscale image. Gaussian derivatives provide $I_x$ and $I_y$. Their products are averaged with an integration kernel:

$$
\mathbf J = G_{\sigma_i} *
\begin{bmatrix}
I_x^2 & I_x I_y \\
I_x I_y & I_y^2
\end{bmatrix}.
$$

The eigenvalues are

$$
\lambda_{1,2}=\frac{J_{xx}+J_{yy}\pm
\sqrt{(J_{xx}-J_{yy})^2+4J_{xy}^2}}{2}.
$$

The major-gradient angle is

$$
\phi_g=\frac12\operatorname{atan2}(2J_{xy},J_{xx}-J_{yy}),
$$

and the ridge tangent is $\theta=\phi_g+\pi/2$, wrapped to an axial interval.
