# Anaconda setup

[Русский](ru/anaconda-setup.md)

## Why `ModuleNotFoundError` appears

`biomechanics_tutorials` is the local package stored in `src/biomechanics_tutorials`. A Jupyter notebook uses the Python environment of its selected kernel. If the repository has not been installed in that environment, or if Jupyter uses another kernel, Python cannot resolve the import.

## Recommended Windows setup

1. Extract or clone the **entire repository**. Do not copy only the notebook.
2. Open **Anaconda Prompt**.
3. Change to the repository root, the directory containing `pyproject.toml`.
4. Run:

```bat
scripts\setup_anaconda_windows.bat
```

The script creates the `biomechanics-tutorials` conda environment, installs the local repository in editable mode, registers a Jupyter kernel, and runs a diagnostic check.

Start Jupyter with:

```bat
scripts\start_jupyter_windows.bat
```

or with `conda run -n biomechanics-tutorials jupyter lab`.

In Jupyter choose:

```text
Kernel → Change Kernel → Python (Biomechanics Research Tutorials)
```

## Manual commands

First installation:

```bat
conda env create --file environment.yml
```

Later environment updates:

```bat
conda env update --name biomechanics-tutorials --file environment.yml --prune
```

Then continue with:

```bat
conda activate biomechanics-tutorials
python -m pip install -e ".[dev]"
python -m ipykernel install --user --name biomechanics-tutorials --display-name "Python (Biomechanics Research Tutorials)"
python scripts\diagnose_environment.py
jupyter lab
```

## Important checks

Inside a notebook, run:

```python
import sys
print(sys.executable)
```

The path should point to the `biomechanics-tutorials` conda environment. The notebook setup cell also prints the repository root and the exact local package file that is being used.
