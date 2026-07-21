"""Start JupyterLab with the project-local environment when available."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def project_python() -> Path:
    """Prefer the repository .venv and otherwise use the current interpreter."""
    if sys.platform == "win32":
        candidate = REPOSITORY_ROOT / ".venv" / "Scripts" / "python.exe"
    else:
        candidate = REPOSITORY_ROOT / ".venv" / "bin" / "python"
    return candidate if candidate.exists() else Path(sys.executable)


def main() -> int:
    executable = project_python()
    print(f"Starting JupyterLab with: {executable}")
    command = [str(executable), "-m", "jupyterlab", *sys.argv[1:]]
    return subprocess.call(command, cwd=REPOSITORY_ROOT)


if __name__ == "__main__":
    raise SystemExit(main())
