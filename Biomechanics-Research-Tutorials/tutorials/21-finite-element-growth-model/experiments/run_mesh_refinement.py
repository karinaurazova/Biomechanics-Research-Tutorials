from pathlib import Path
import sys


def _find_repository_root(start: Path) -> Path:
    current = start.resolve()
    for candidate in [current, *current.parents]:
        if (candidate / "src" / "biomechanics_tutorials").exists():
            return candidate
    raise RuntimeError("Repository root not found.")

ROOT = _find_repository_root(Path(__file__))
sys.path.insert(0, str(ROOT / "src"))

from biomechanics_tutorials.finite_element_growth import create_rectangular_tri_mesh, simulate_growth

for nx, ny in [(10, 7), (14, 9), (18, 12), (24, 16)]:
    mesh = create_rectangular_tri_mesh(nx=nx, ny=ny)
    history = simulate_growth(mesh=mesh, n_steps=8)
    final = history.metrics[-1]
    print(nx, ny, final["mean_energy_density"], final["residual_norm"])
