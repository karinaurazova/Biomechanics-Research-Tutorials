"""Animate the Gent locking parameter."""

from __future__ import annotations

from matplotlib import animation
import matplotlib.pyplot as plt
import numpy as np

from common import output_path, tr
from biomechanics_tutorials.hyperelasticity import path_response


def main() -> None:
    stretches = np.linspace(1.0, 2.05, 280)
    jm_values = np.linspace(7.0, 45.0, 42)
    for language in ("en", "ru"):
        fig, axis = plt.subplots(figsize=(8.5, 5.5))
        line, = axis.plot([], [], linewidth=2.7)
        axis.set_xlim(stretches[0], stretches[-1])
        axis.set_ylim(0.0, 12.0)
        axis.set_xlabel(tr("stretch", language))
        axis.set_ylabel(tr("response", language))
        title = axis.set_title("")

        def update(frame: int):
            jm = float(jm_values[frame])
            response = path_response("gent", stretches, parameters={"jm": jm})
            line.set_data(stretches, response)
            title.set_text(tr("frame", language, value=jm))
            return line, title

        movie = animation.FuncAnimation(fig, update, frames=len(jm_values), interval=90, blit=False)
        movie.save(output_path("gent_limiting_chain", language, ".gif"), writer=animation.PillowWriter(fps=10))
        plt.close(fig)


if __name__ == "__main__":
    main()
