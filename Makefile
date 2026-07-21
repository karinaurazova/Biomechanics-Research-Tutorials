.PHONY: setup jupyter install check tutorial-01 tutorial-02 tutorial-03 tutorial-04 tutorial-05 tutorial-06 tutorial-07 tutorial-08 tutorial-09 tutorial-10 tutorial-11 tutorial-12 tutorial-13 tutorial-14 tutorial-15 tutorial-16 tutorials docs docs-en docs-ru docs-build clean
setup:
	python scripts/setup_venv.py

jupyter:
	python scripts/start_jupyter.py

install:
	python -m pip install -e .[dev]
test:
	pytest -q
check:
	python scripts/diagnose_environment.py
tutorial-01:
	python tutorials/01-fiber-reorientation/reproduce.py
tutorial-02:
	python tutorials/02-collagen-fiber-dispersion/reproduce.py
tutorial-03:
	python tutorials/03-hyperelastic-constitutive-models/reproduce.py
tutorial-04:
	python tutorials/04-active-passive-stress/reproduce.py
tutorial-05:
	python tutorials/05-structure-tensor-orientation/reproduce.py
tutorial-06:
	python tutorials/06-mechanical-homeostasis/reproduce.py
tutorial-07:
	python tutorials/07-growth-tensor-multiplicative-decomposition/reproduce.py
tutorial-08:
	python tutorials/08-stress-driven-volumetric-growth/reproduce.py
tutorial-09:
	python tutorials/09-fiber-family-remodeling/reproduce.py
tutorial-10:
	python tutorials/10-extracellular-matrix-turnover/reproduce.py
tutorial-11:
	python tutorials/11-constrained-mixture-toy-model/reproduce.py
tutorial-12:
	python tutorials/12-residual-stress-ring-opening/reproduce.py
tutorial-13:
	python tutorials/13-synthetic-fibrous-tissue-generation/reproduce.py
tutorial-14:
	python tutorials/14-synthetic-microscopy-sem-like-imaging/reproduce.py

tutorial-15:
	python tutorials/15-polarization-like-orientation-maps/reproduce.py
tutorial-16:
	python tutorials/16-synthetic-digital-image-correlation/reproduce.py
tutorials: tutorial-01 tutorial-02 tutorial-03 tutorial-04 tutorial-05 tutorial-06 tutorial-07 tutorial-08 tutorial-09 tutorial-10 tutorial-11 tutorial-12 tutorial-13 tutorial-14 tutorial-15 tutorial-16
docs: docs-en
docs-en:
	mkdocs serve -f mkdocs.en.yml
docs-ru:
	mkdocs serve -f mkdocs.ru.yml
docs-build:
	mkdocs build -f mkdocs.en.yml --strict
	mkdocs build -f mkdocs.ru.yml --strict
clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -prune -exec rm -rf {} +


release-check:
	python scripts/verify_repository.py --strict
	python scripts/diagnose_environment.py

reproduce-selected:
	python scripts/run_reproduce_selected.py 1 5 13 20 25
