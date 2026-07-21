[English](START_HERE.md) | [Русский](START_HERE.ru.md)

# Start here

This repository contains three connected layers:

1. **`src/biomechanics_tutorials/`** — the shared local Python package with mathematical models and reusable plotting utilities;
2. **`tutorials/.../notebooks/`** — interactive educational walkthroughs that compute results in the active Jupyter kernel and display plots inline;
3. **`tutorials/.../experiments/`** — reproducibility scripts that generate the committed PNG and GIF files in `figures/` and `animations/`.

The name `biomechanics_tutorials` in an import statement does **not** refer to a package downloaded from the internet. It refers to source code in this repository.

## Recommended setup

For the most portable setup across Windows, Linux, macOS, VS Code, and Visual Studio, create a project-local virtual environment:

```bash
# Windows
py -3 scripts/setup_venv.py

# Linux/macOS
python3 scripts/setup_venv.py
```

Start Jupyter with `python scripts/start_jupyter.py` and select the registered kernel **Python (.venv — Biomechanics Research Tutorials)**.

Anaconda remains fully supported through the scripts in `scripts/setup_anaconda_*`.

- Complete environment and IDE guide: [docs/development-environments.md](docs/development-environments.md)
- Anaconda-specific guide: [docs/anaconda-setup.md](docs/anaconda-setup.md)
- Repository and figure workflow: [docs/how-the-repository-works.md](docs/how-the-repository-works.md)
