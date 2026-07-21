from pathlib import Path


def test_required_tutorial_sections_exist():
    root = Path(__file__).resolve().parents[1]
    required = [
        root / "README.md",
        root / "chapters" / "04_mathematical_model.md",
        root / "chapters" / "09_references.md",
        root / "references.bib",
        root / "experiments" / "baseline.py",
        root / "experiments" / "distribution_gallery.py",
        root / "experiments" / "tensor_verification.py",
        root / "experiments" / "aligned_response.py",
        root / "experiments" / "oblique_response.py",
        root / "experiments" / "anisotropy_map.py",
        root / "experiments" / "quadrature_convergence.py",
        root / "experiments" / "population_animation.py",
        root / "exercises" / "explore.md",
        root / "exercises" / "experiment.md",
        root / "exercises" / "research_challenge.md",
    ]
    assert all(path.exists() for path in required)
