# Getting started

[Русский](ru/getting-started.md)

## Choose a workflow

- **Anaconda/Jupyter:** follow [Anaconda setup](anaconda-setup.md).
- **Read on GitHub:** no installation is required; open a tutorial README and its committed figures.
- **Reproduce all outputs:** install the environment and run the tutorial-level `reproduce.py` script.

## What is being imported?

The statement

```python
from biomechanics_tutorials... import ...
```

loads the repository's own source code from `src/biomechanics_tutorials`. It is not a separately downloaded library. Editable installation (`python -m pip install -e .`) connects this folder to the active Python environment.

## Recommended setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python scripts/diagnose_environment.py
jupyter lab
```

## First interactive run

Open:

```text
tutorials/01-fiber-reorientation/notebooks/01_fiber_reorientation.ipynb
```

Run the cells from top to bottom. The setup cell reports the repository root, Python kernel, and local package path.

## Rebuild generated outputs

```bash
python tutorials/01-fiber-reorientation/reproduce.py
python tutorials/02-collagen-fiber-dispersion/reproduce.py
python tutorials/03-hyperelastic-constitutive-models/reproduce.py
python tutorials/04-active-passive-stress/reproduce.py
python tutorials/05-structure-tensor-orientation/reproduce.py
python tutorials/06-mechanical-homeostasis/reproduce.py
python tutorials/07-growth-tensor-multiplicative-decomposition/reproduce.py
```

See [How the repository works](how-the-repository-works.md) for the exact origin of plots and numerical values.

For Windows, Linux, macOS, VS Code, and Visual Studio instructions, see [Development environments and IDEs](development-environments.md).
