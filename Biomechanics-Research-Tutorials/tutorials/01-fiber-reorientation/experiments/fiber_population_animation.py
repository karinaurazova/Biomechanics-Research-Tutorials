"""Create localized animations of a synthetic fiber population."""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import numpy as np

from biomechanics_tutorials.fiber_reorientation import (
    ReorientationParameters,
    angular_difference,
    simulate_reorientation,
)
from biomechanics_tutorials.localization import (
    SUPPORTED_LANGUAGES,
    localized_path,
    tr,
)
from biomechanics_tutorials.plotting import PALETTE, apply_tutorial_style


def save_animation(
    time: np.ndarray,
    mean_orientation: np.ndarray,
    target: np.ndarray,
    offsets: np.ndarray,
    x_coordinates: np.ndarray,
    y_coordinates: np.ndarray,
    parameters: ReorientationParameters,
    output: Path,
    language: str,
) -> None:
    """Save one localized animation."""
    length = 0.18
    fig, axis = plt.subplots(figsize=(6, 6))
    axis.set(
        xlim=(-1.2, 1.2),
        ylim=(-1.2, 1.2),
        xlabel=tr("synthetic_tissue_coordinate", language),
        ylabel=tr("synthetic_tissue_coordinate", language),
    )
    axis.set_aspect("equal")
    lines = [
        axis.plot([], [], linewidth=1.5, color=PALETTE["blue"])[0] for _ in offsets
    ]
    title = axis.set_title("")

    def update(frame: int):
        base = mean_orientation[frame]
        angles = base + offsets * np.exp(-parameters.rate * time[frame])
        for line, x_value, y_value, angle in zip(
            lines, x_coordinates, y_coordinates, angles, strict=True
        ):
            dx = 0.5 * length * np.cos(angle)
            dy = 0.5 * length * np.sin(angle)
            line.set_data([x_value - dx, x_value + dx], [y_value - dy, y_value + dy])
        error = np.rad2deg(abs(float(angular_difference(target[frame], base))))
        title.set_text(tr("mean_error_frame", language, time=time[frame], error=error))
        return [*lines, title]

    animation = FuncAnimation(
        fig,
        update,
        frames=np.arange(0, len(time), 5),
        interval=60,
        blit=False,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    animation.save(output, writer=PillowWriter(fps=15))
    plt.close(fig)


def main() -> None:
    """Generate English and Russian GIF animations."""
    apply_tutorial_style()
    generator = np.random.default_rng(7)
    offsets = generator.normal(0, np.deg2rad(8), 40)
    parameters = ReorientationParameters(rate=0.35, duration=14, time_step=0.04)
    time, mean_orientation, target = simulate_reorientation(
        np.deg2rad(-50), np.deg2rad(30), parameters
    )
    x_coordinates = generator.uniform(-1, 1, len(offsets))
    y_coordinates = generator.uniform(-1, 1, len(offsets))
    base_output = (
        Path(__file__).resolve().parents[1]
        / "animations"
        / "fiber_reorientation.gif"
    )
    for language in SUPPORTED_LANGUAGES:
        output = localized_path(base_output, language)
        save_animation(
            time,
            mean_orientation,
            target,
            offsets,
            x_coordinates,
            y_coordinates,
            parameters,
            output,
            language,
        )
        print(f"Saved {output}")


if __name__ == "__main__":
    main()
