from pathlib import Path


def test_required_tutorial_sections_exist():
    r = Path(__file__).resolve().parents[1]
    required = [
        r / "README.md",
        r / "chapters" / "04_mathematical_model.md",
        r / "chapters" / "09_references.md",
        r / "references.bib",
        r / "experiments" / "baseline.py",
        r / "experiments" / "analytical_verification.py",
        r / "experiments" / "orthogonal_case.py",
        r / "exercises" / "explore.md",
        r / "exercises" / "experiment.md",
        r / "exercises" / "research_challenge.md",
    ]
    assert all(p.exists() for p in required)
