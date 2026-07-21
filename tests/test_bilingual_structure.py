from pathlib import Path
import re

import nbformat


ROOT = Path(__file__).resolve().parents[1]


def test_root_bilingual_pairs_exist():
    pairs = [
        ("README.md", "README.ru.md"),
        ("ROADMAP.md", "ROADMAP.ru.md"),
        ("CONTRIBUTING.md", "CONTRIBUTING.ru.md"),
        ("CHANGELOG.md", "CHANGELOG.ru.md"),
        ("LANGUAGE_POLICY.md", "LANGUAGE_POLICY.ru.md"),
    ]
    assert all((ROOT / en).exists() and (ROOT / ru).exists() for en, ru in pairs)


def test_documentation_has_russian_mirror():
    docs = ROOT / "docs"
    english = sorted(path.name for path in docs.glob("*.md"))
    russian = sorted(path.name for path in (docs / "ru").glob("*.md"))
    assert english == russian


def test_each_tutorial_has_bilingual_learning_materials():
    for tutorial in sorted((ROOT / "tutorials").glob("[0-9][0-9]-*")):
        assert (tutorial / "README.md").exists()
        assert (tutorial / "README.ru.md").exists()
        english_chapters = sorted(path.name for path in (tutorial / "chapters").glob("*.md"))
        russian_chapters = sorted(path.name for path in (tutorial / "chapters" / "ru").glob("*.md"))
        assert english_chapters == russian_chapters
        english_exercises = sorted(path.name for path in (tutorial / "exercises").glob("*.md"))
        russian_exercises = sorted(path.name for path in (tutorial / "exercises" / "ru").glob("*.md"))
        assert english_exercises == russian_exercises
        assert (tutorial / "instructor_notes.md").exists()
        assert (tutorial / "instructor_notes.ru.md").exists()


def test_russian_notebooks_preserve_code_cells():
    for tutorial in sorted((ROOT / "tutorials").glob("[0-9][0-9]-*")):
        notebook_dir = tutorial / "notebooks"
        english_notebooks = sorted(
            path for path in notebook_dir.glob("*.ipynb") if not path.stem.endswith("_ru")
        )
        assert english_notebooks, f"No English notebook found in {tutorial.name}"
        for english_path in english_notebooks:
            russian_path = english_path.with_name(f"{english_path.stem}_ru.ipynb")
            assert russian_path.exists(), f"Missing Russian notebook for {english_path.name}"
            english = nbformat.read(english_path, as_version=4)
            russian = nbformat.read(russian_path, as_version=4)
            english_code = [cell.source for cell in english.cells if cell.cell_type == "code"]
            russian_code = [cell.source for cell in russian.cells if cell.cell_type == "code"]
            def normalize(source: str) -> str:
                return re.sub(r'LANGUAGE = "(?:en|ru)"', 'LANGUAGE = "LANG"', source)

            assert [normalize(source) for source in english_code] == [
                normalize(source) for source in russian_code
            ]


def test_workshop_materials_have_russian_pairs():
    for directory in [
        ROOT / "workshop/instructor-materials",
        ROOT / "workshop/student-handouts",
        ROOT / "workshop/presentation-assets",
    ]:
        english = sorted(path for path in directory.glob("*.md") if not path.name.endswith(".ru.md"))
        for english_path in english:
            russian_path = english_path.with_name(f"{english_path.stem}.ru.md")
            assert russian_path.exists()


def test_committed_visual_assets_have_localized_pairs():
    for tutorial in sorted((ROOT / "tutorials").glob("[0-9][0-9]-*")):
        for directory_name, suffixes in [
            ("figures", {".png", ".svg"}),
            ("animations", {".gif"}),
        ]:
            directory = tutorial / directory_name
            english_assets = sorted(
                path
                for path in directory.iterdir()
                if path.is_file()
                and path.suffix.lower() in suffixes
                and not path.stem.endswith("_ru")
            )
            for english_path in english_assets:
                russian_path = english_path.with_name(
                    f"{english_path.stem}_ru{english_path.suffix}"
                )
                assert russian_path.exists(), f"Missing localized pair for {english_path}"


def test_environment_and_start_here_materials_exist():
    required = [
        "START_HERE.md",
        "START_HERE.ru.md",
        "environment.yml",
        ".vsconfig",
        ".vscode/extensions.json",
        ".vscode/settings.json",
        ".vscode/tasks.json",
        ".vscode/launch.json",
        "scripts/setup_anaconda_windows.bat",
        "scripts/setup_anaconda_unix.sh",
        "scripts/setup_venv.py",
        "scripts/setup_venv_windows.bat",
        "scripts/setup_venv_unix.sh",
        "scripts/start_jupyter.py",
        "scripts/start_jupyter_windows.bat",
        "scripts/start_jupyter_unix.sh",
        "scripts/start_jupyter_venv_windows.bat",
        "scripts/start_jupyter_venv_unix.sh",
        "scripts/diagnose_environment.py",
    ]
    for relative_path in required:
        assert (ROOT / relative_path).exists(), relative_path


def test_readmes_begin_with_requested_quote():
    quote = "Выше закона может быть только любовь"
    for filename in ["README.md", "README.ru.md"]:
        content = (ROOT / filename).read_text(encoding="utf-8")
        assert content.startswith("> «" + quote)


def test_visual_studio_and_vscode_configuration_is_valid():
    import json

    visual_studio = json.loads((ROOT / ".vsconfig").read_text(encoding="utf-8"))
    assert "Microsoft.VisualStudio.Workload.Python" in visual_studio["components"]

    for config_path in sorted((ROOT / ".vscode").glob("*.json")):
        json.loads(config_path.read_text(encoding="utf-8"))


def test_notebooks_have_local_repository_bootstrap():
    for notebook_path in sorted((ROOT / "tutorials").glob("*/notebooks/*.ipynb")):
        notebook = nbformat.read(notebook_path, as_version=4)
        code = "\n".join(cell.source for cell in notebook.cells if cell.cell_type == "code")
        assert "_find_repository_root" in code
        assert 'SOURCE_DIRECTORY = REPOSITORY_ROOT / "src"' in code
        assert "Path(biomechanics_tutorials.__file__).resolve()" in code


def test_each_tutorial_has_reproduction_entry_point_and_output_manifests():
    for tutorial in sorted((ROOT / "tutorials").glob("[0-9][0-9]-*")):
        assert (tutorial / "reproduce.py").exists()
        assert (tutorial / "figures/README.md").exists()
        assert (tutorial / "figures/README.ru.md").exists()
        assert (tutorial / "animations/README.md").exists()
        assert (tutorial / "animations/README.ru.md").exists()


def test_universal_tutorial_policy_and_tutorial_12_scope():
    forbidden = re.compile(r"(?:ВКР|бакалаврск|дипломн|thesis integration)", re.IGNORECASE)
    tutorial_11 = ROOT / "tutorials/11-constrained-mixture-toy-model"
    for path in list(tutorial_11.rglob("*.md")) + list(tutorial_11.rglob("*.ipynb")):
        assert not forbidden.search(path.read_text(encoding="utf-8")), path

    tutorial_12 = ROOT / "tutorials/12-residual-stress-ring-opening"
    assert len(list((tutorial_12 / "chapters").glob("*.md"))) == 20
    assert len(list((tutorial_12 / "chapters/ru").glob("*.md"))) == 20
    assert len(list((tutorial_12 / "figures").glob("*.png"))) >= 42
    assert (tutorial_12 / "animations/ring_opening.gif").exists()
    assert (tutorial_12 / "animations/ring_opening_ru.gif").exists()


def test_visual_assets_are_readable_and_language_pairs_match():
    from PIL import Image

    for tutorial in sorted((ROOT / "tutorials").glob("[0-9][0-9]-*")):
        for english in sorted(
            path
            for path in (tutorial / "figures").glob("*.png")
            if not path.stem.endswith("_ru")
        ):
            russian = english.with_name(f"{english.stem}_ru.png")
            assert russian.exists()
            with Image.open(english) as en_image, Image.open(russian) as ru_image:
                en_ratio = en_image.width / en_image.height
                ru_ratio = ru_image.width / ru_image.height
                assert abs(en_ratio - ru_ratio) / max(en_ratio, 1e-12) < 0.12
                assert ru_image.width >= 900
                assert ru_image.height >= 650
