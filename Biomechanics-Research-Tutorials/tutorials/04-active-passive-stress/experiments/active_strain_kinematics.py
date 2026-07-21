"""Visualize active strain principal stretches and determinant."""

import matplotlib.pyplot as plt
import numpy as np
from common import save_figure, title
from biomechanics_tutorials.active_mechanics import active_strain_tensor


def main():
    la = np.linspace(0.65, 1.0, 250)
    axial = []
    transverse = []
    determinant = []
    for value in la:
        fa = active_strain_tensor(value)
        axial.append(fa[0, 0])
        transverse.append(fa[1, 1])
        determinant.append(np.linalg.det(fa))
    for language in ("en", "ru"):
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(
            la,
            axial,
            lw=2.3,
            label="Fiber stretch" if language == "en" else "Растяжение вдоль волокна",
        )
        ax.plot(
            la,
            transverse,
            lw=2.3,
            label="Transverse stretch" if language == "en" else "Поперечное растяжение",
        )
        ax.plot(la, determinant, lw=2.3, ls="--", label="det(Fa)")
        ax.set(
            xlabel="Active fiber stretch λa"
            if language == "en"
            else "Активное растяжение волокна λa",
            ylabel="Kinematic quantity" if language == "en" else "Кинематическая величина",
            title=title("active_strain_kinematics", language),
        )
        ax.legend()
        ax.grid(alpha=0.25)
        save_figure(fig, "active_strain_kinematics", language)


if __name__ == "__main__":
    main()
