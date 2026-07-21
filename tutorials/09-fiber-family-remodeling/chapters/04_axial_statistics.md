# 4. Axial directional statistics

A collagen fiber is an axis rather than an oriented arrow. Thus \(\theta\) and \(\theta+\pi\) describe the same family. Ordinary circular statistics with period \(2\pi\) are therefore inappropriate.

The second circular moment is

\[
m_2=\int \rho(\theta)e^{2i\theta}\,d\theta.
\]

The mean axial angle and order parameter are

\[
\bar\theta=\frac12\arg(m_2),
\qquad
S=|m_2|.
\]

Here \(S=1\) denotes perfect alignment and \(S=0\) denotes in-plane isotropy or a balanced multimodal distribution. This ambiguity matters: a uniform distribution and two equally weighted orthogonal families can have the same second moment. Higher moments or the full orientation distribution may be required.

The tutorial uses an axial von Mises density

\[
\rho(\theta)=\frac{
\exp\left[\kappa\cos 2(\theta-\mu)\right]
}{\pi I_0(\kappa)}.
\]

The concentration \(\kappa\) controls dispersion, but it does not describe arbitrary skewed, truncated, or multimodal populations. Reporting a mean angle and one concentration parameter is therefore a modelling assumption, not a neutral summary of all available structural information.
