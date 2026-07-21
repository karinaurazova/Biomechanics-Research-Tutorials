from pathlib import Path

import nbformat


ROOT = Path(__file__).resolve().parents[1]


def test_tutorial_03_has_complete_bilingual_structure():
    required = [
        "README.md",
        "README.ru.md",
        "instructor_notes.md",
        "instructor_notes.ru.md",
        "references.bib",
        "reproduce.py",
        "figures/README.md",
        "figures/README.ru.md",
        "animations/README.md",
        "animations/README.ru.md",
    ]
    for relative in required:
        assert (ROOT / relative).exists(), relative

    english_chapters = sorted(path.name for path in (ROOT / "chapters").glob("*.md"))
    russian_chapters = sorted(path.name for path in (ROOT / "chapters/ru").glob("*.md"))
    assert english_chapters == russian_chapters
    assert len(english_chapters) == 10


def test_tutorial_03_notebooks_are_bilingual_and_share_code():
    en = nbformat.read(ROOT / "notebooks/03_hyperelastic_constitutive_models.ipynb", as_version=4)
    ru = nbformat.read(ROOT / "notebooks/03_hyperelastic_constitutive_models_ru.ipynb", as_version=4)
    en_code = [cell.source.replace('LANGUAGE = "en"', 'LANGUAGE = "LANG"') for cell in en.cells if cell.cell_type == "code"]
    ru_code = [cell.source.replace('LANGUAGE = "ru"', 'LANGUAGE = "LANG"') for cell in ru.cells if cell.cell_type == "code"]
    assert en_code == ru_code


def test_tutorial_03_visual_assets_have_language_pairs():
    for english in (ROOT / "figures").glob("*.png"):
        if english.stem.endswith("_ru"):
            continue
        assert english.with_name(f"{english.stem}_ru.png").exists()
    for english in (ROOT / "animations").glob("*.gif"):
        if english.stem.endswith("_ru"):
            continue
        assert english.with_name(f"{english.stem}_ru.gif").exists()


def test_tutorial_03_contains_sixteen_model_names_in_readme():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    for name in [
        "Neo-Hookean",
        "Mooney–Rivlin",
        "Yeoh",
        "Gent",
        "Arruda–Boyce",
        "Ogden",
        "Demiray",
        "Veronda–Westmann",
        "HGO",
        "GOH",
        "Guccione",
        "Costa",
        "Holzapfel–Ogden",
    ]:
        assert name in text
