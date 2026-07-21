"""Check that the active Python environment can run the tutorials."""

from __future__ import annotations

import importlib
from pathlib import Path
import platform
import sys


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIRECTORY = REPOSITORY_ROOT / "src"


def main() -> int:
    """Print a concise diagnostic report and return a shell status code."""
    print("Biomechanics Research Tutorials — environment check")
    print(f"Repository root : {REPOSITORY_ROOT}")
    print(f"Python executable: {sys.executable}")
    print(f"Python version   : {platform.python_version()}")
    print(f"Working directory: {Path.cwd()}")

    if str(SOURCE_DIRECTORY) not in sys.path:
        sys.path.insert(0, str(SOURCE_DIRECTORY))

    required = ["numpy", "matplotlib", "scipy", "jupyterlab", "ipykernel"]
    failed: list[str] = []
    for module_name in required:
        try:
            module = importlib.import_module(module_name)
            version = getattr(module, "__version__", "installed")
            print(f"[OK] {module_name:<12} {version}")
        except Exception as exc:  # pragma: no cover - diagnostic utility
            failed.append(module_name)
            print(f"[FAIL] {module_name:<12} {exc}")

    try:
        package = importlib.import_module("biomechanics_tutorials")
        print(f"[OK] local package {Path(package.__file__).resolve()}")
    except Exception as exc:  # pragma: no cover - diagnostic utility
        failed.append("biomechanics_tutorials")
        print(f"[FAIL] local package {exc}")

    if failed:
        print("\nEnvironment is not ready. Missing or broken:", ", ".join(failed))
        return 1

    print("\nEnvironment is ready.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
