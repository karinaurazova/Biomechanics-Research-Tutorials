"""Create a project-local virtual environment for all supported platforms."""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess
import sys
import venv


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
VENV_DIRECTORY = REPOSITORY_ROOT / ".venv"
KERNEL_NAME = "biomechanics-tutorials-venv"
KERNEL_DISPLAY_NAME = "Python (.venv — Biomechanics Research Tutorials)"


def _venv_python(directory: Path = VENV_DIRECTORY) -> Path:
    """Return the virtual-environment Python executable for the current OS."""
    if sys.platform == "win32":
        return directory / "Scripts" / "python.exe"
    return directory / "bin" / "python"


def _run(command: list[str]) -> None:
    """Run a command from the repository root and fail clearly on errors."""
    print("+", " ".join(command), flush=True)
    subprocess.run(command, cwd=REPOSITORY_ROOT, check=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create .venv, install the repository, register a Jupyter kernel, "
            "and diagnose the environment."
        )
    )
    parser.add_argument(
        "--recreate",
        action="store_true",
        help="Remove an existing .venv before creating it again.",
    )
    parser.add_argument(
        "--no-kernel",
        action="store_true",
        help="Do not register the Jupyter kernel.",
    )
    parser.add_argument(
        "--upgrade-pip",
        action="store_true",
        help="Upgrade pip before installing the repository.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if sys.version_info < (3, 10):
        print("Python 3.10 or newer is required.", file=sys.stderr)
        return 2

    print("Biomechanics Research Tutorials — .venv setup")
    print(f"Repository root : {REPOSITORY_ROOT}")
    print(f"Bootstrap Python: {sys.executable}")
    print(f"Target .venv    : {VENV_DIRECTORY}")

    if args.recreate and VENV_DIRECTORY.exists():
        print("Removing existing .venv ...")
        shutil.rmtree(VENV_DIRECTORY)

    if not VENV_DIRECTORY.exists():
        print("Creating .venv ...")
        venv.EnvBuilder(with_pip=True).create(VENV_DIRECTORY)
    else:
        print("Using existing .venv.")

    python_executable = _venv_python()
    if not python_executable.exists():
        print(f"Virtual-environment Python was not found: {python_executable}", file=sys.stderr)
        return 3

    if args.upgrade_pip:
        _run([str(python_executable), "-m", "pip", "install", "--upgrade", "pip"])

    _run([str(python_executable), "-m", "pip", "install", "-e", ".[dev]"])

    if not args.no_kernel:
        _run(
            [
                str(python_executable),
                "-m",
                "ipykernel",
                "install",
                "--user",
                "--name",
                KERNEL_NAME,
                "--display-name",
                KERNEL_DISPLAY_NAME,
            ]
        )

    _run([str(python_executable), "scripts/diagnose_environment.py"])

    print("\nSetup completed successfully.")
    print(f"Interpreter: {python_executable}")
    print('Start Jupyter with: python scripts/start_jupyter.py')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
