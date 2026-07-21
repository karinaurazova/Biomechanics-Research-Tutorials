# Development environments and IDEs

This project supports two environment strategies:

- a project-local **`.venv`**, recommended for VS Code, Visual Studio, and command-line use;
- a named **conda environment**, recommended for users who already work with Anaconda or Miniconda.

Do not mix interpreters within one session. The Python interpreter used by the terminal, IDE, and notebook kernel must point to the same environment.

## Requirements

- Python 3.10 or newer;
- Git if cloning the repository;
- internet access during the first dependency installation.

## Universal `.venv` setup

Run from the directory containing `pyproject.toml`.

### Windows

```bat
py -3 scripts\setup_venv.py
```

If the `py` launcher is unavailable, use an installed Python directly:

```bat
python scripts\setup_venv.py
```

### Linux

```bash
python3 scripts/setup_venv.py
```

On Debian/Ubuntu, install the system `python3-venv` package if virtual-environment creation is unavailable.

### macOS

```bash
python3 scripts/setup_venv.py
```

The script creates `.venv`, installs the repository with `pip install -e ".[dev]"`, registers a Jupyter kernel, and runs `scripts/diagnose_environment.py`.

Convenience wrappers are also provided:

```text
Windows: scripts\setup_venv_windows.bat
Linux/macOS: bash scripts/setup_venv_unix.sh
```

## Starting Jupyter

The cross-platform launcher automatically uses `.venv` when it exists:

```bash
python scripts/start_jupyter.py
```

Alternatively activate the environment and run `python -m jupyterlab`.

## Anaconda / Miniconda

```text
Windows: scripts\setup_anaconda_windows.bat
Linux/macOS: bash scripts/setup_anaconda_unix.sh
```

Start Jupyter with the platform-specific launcher or with:

```bash
conda run -n biomechanics-tutorials jupyter lab
```

## Visual Studio Code

The repository includes `.vscode/extensions.json`, `settings.json`, `tasks.json`, and `launch.json`.

1. Open the **repository root folder**, not an isolated notebook.
2. Install the recommended Microsoft Python, Pylance, and Jupyter extensions.
3. Run the VS Code task **Setup project .venv** or use `scripts/setup_venv.py` in the terminal.
4. Run **Python: Select Interpreter** and choose the interpreter from `.venv`.
5. Open a notebook and use **Select Kernel** to choose the same `.venv` kernel.
6. Run the diagnostic task before troubleshooting model imports.

The workspace configuration adds `src/` to static analysis, enables pytest discovery, and keeps notebook working directories anchored to the repository root.

## Visual Studio on Windows

Full Visual Studio Python support is Windows-only. The root `.vsconfig` requests the **Python development** workload.

1. Open `.vsconfig` with Visual Studio Installer and install missing components.
2. Run `scripts\setup_venv_windows.bat` from PowerShell or Command Prompt.
3. In Visual Studio, choose **File → Open → Folder** and select the repository root.
4. Open **Python Environments** and select or add `.venv\Scripts\python.exe`.
5. Run Python scripts, experiments, and tests from that environment.
6. To work with `.ipynb`, launch Jupyter from Visual Studio's terminal with `python scripts/start_jupyter.py`, or open the repository in VS Code/JupyterLab.

No `.sln` or `.pyproj` file is required: modern Visual Studio can open a folder containing Python code directly.

## Diagnostics

Run with the interpreter you intend to use:

```bash
python scripts/diagnose_environment.py
```

The output must show the active Python executable and the local package path ending in `src/biomechanics_tutorials/__init__.py`.

## Common errors

### `ModuleNotFoundError: biomechanics_tutorials`

The repository has not been installed in the selected environment, or the notebook uses another kernel. Run the setup script and select the matching kernel.

### Terminal works but notebook fails

The terminal interpreter and notebook kernel differ. Check `sys.executable` in the first notebook cell and select the same environment.

### VS Code shows unresolved imports but code runs

Refresh Python environments, select `.venv`, and reload the VS Code window. The workspace also includes `src/` in `python.analysis.extraPaths`.
