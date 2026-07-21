#!/usr/bin/env python3
"""Repository-level structural verification for Biomechanics Research Tutorials."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TUTORIALS = ROOT / "tutorials"
REQUIRED_FILES = ["README.md", "README.ru.md", "reproduce.py"]
FORBIDDEN_TOP_LEVEL_FRAGMENTS = ["Final addition:", "Финальное добавление:", "Патриарх Алексий\n", "Патриарх Алексий\r\n"]


def tutorial_dirs() -> list[Path]:
    return sorted([p for p in TUTORIALS.iterdir() if p.is_dir() and p.name[:2].isdigit()])


def check_markdown_fences() -> list[str]:
    errors: list[str] = []
    for path in ROOT.rglob("*.md"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        if text.count("```") % 2 != 0:
            errors.append(f"{path.relative_to(ROOT)}: unmatched fenced code block")
    return errors


def check_top_level_text() -> list[str]:
    errors: list[str] = []
    for name in ["README.md", "README.ru.md"]:
        text = (ROOT / name).read_text(encoding="utf-8", errors="ignore")
        for fragment in FORBIDDEN_TOP_LEVEL_FRAGMENTS:
            if fragment in text:
                errors.append(f"{name}: forbidden stale fragment {fragment!r}")
    return errors


def check_gif_pairs(path: Path) -> list[str]:
    missing: list[str] = []
    for gif in path.rglob("*.gif"):
        if gif.stem.endswith("_ru"):
            continue
        ru_pair = gif.with_name(gif.stem + "_ru.gif")
        if not ru_pair.exists():
            missing.append(gif.relative_to(ROOT).as_posix())
    return missing


def check_tutorial(path: Path) -> dict:
    missing = []
    for name in REQUIRED_FILES:
        if not (path / name).exists():
            missing.append(name)
    chapters = list((path / "chapters").glob("*.md")) if (path / "chapters").exists() else []
    chapters_ru = list((path / "chapters" / "ru").glob("*.md")) if (path / "chapters" / "ru").exists() else []
    exercises = list((path / "exercises").glob("*.md")) if (path / "exercises").exists() else []
    exercises_ru = list((path / "exercises" / "ru").glob("*.md")) if (path / "exercises" / "ru").exists() else []
    notebooks = list((path / "notebooks").glob("*.ipynb")) if (path / "notebooks").exists() else []
    png = list(path.rglob("*.png"))
    gif = list(path.rglob("*.gif"))
    gif_ru_missing = check_gif_pairs(path)
    data = list(path.rglob("*.npz")) + list(path.rglob("*.csv")) + list(path.rglob("*.json"))
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "missing": missing,
        "chapters_en": len(chapters),
        "chapters_ru": len(chapters_ru),
        "exercises_en": len(exercises),
        "exercises_ru": len(exercises_ru),
        "notebooks": len(notebooks),
        "png": len(png),
        "gif": len(gif),
        "gif_ru_missing": gif_ru_missing,
        "data": len(data),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true", help="Fail if recommended visual/bilingual minima are not met.")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of text.")
    args = parser.parse_args()

    dirs = tutorial_dirs()
    results = [check_tutorial(p) for p in dirs]
    errors: list[str] = []

    if len(dirs) != 25:
        errors.append(f"Expected 25 tutorials, found {len(dirs)}")

    for r in results:
        if r["missing"]:
            errors.append(f"{r['path']}: missing {', '.join(r['missing'])}")
        if args.strict:
            if r["chapters_en"] == 0 or r["chapters_ru"] == 0:
                errors.append(f"{r['path']}: missing bilingual chapters")
            if r["png"] < 2:
                errors.append(f"{r['path']}: fewer than 2 PNG figures")
            if r["gif"] < 1:
                errors.append(f"{r['path']}: no GIF animation")
            if r["gif_ru_missing"]:
                errors.append(f"{r['path']}: missing Russian GIF pairs for {len(r['gif_ru_missing'])} animation(s)")

    if args.strict:
        errors.extend(check_markdown_fences())
        errors.extend(check_top_level_text())

    shared_missing = check_gif_pairs(ROOT / "assets") if (ROOT / "assets").exists() else []
    if args.strict and shared_missing:
        errors.append(f"assets: missing Russian GIF pairs for {len(shared_missing)} animation(s)")

    summary = {
        "tutorial_count": len(dirs),
        "png_total": sum(r["png"] for r in results) + len(list((ROOT / "assets").rglob("*.png"))) if (ROOT / "assets").exists() else sum(r["png"] for r in results),
        "gif_total": sum(r["gif"] for r in results) + len(list((ROOT / "assets").rglob("*.gif"))) if (ROOT / "assets").exists() else sum(r["gif"] for r in results),
        "chapter_total_en": sum(r["chapters_en"] for r in results),
        "chapter_total_ru": sum(r["chapters_ru"] for r in results),
        "errors": errors,
        "tutorials": results,
    }

    if args.json:
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    else:
        print("Biomechanics Research Tutorials verification")
        print(f"Tutorials: {summary['tutorial_count']}")
        print(f"PNG figures: {summary['png_total']}")
        print(f"GIF animations: {summary['gif_total']}")
        print(f"Chapters EN/RU: {summary['chapter_total_en']} / {summary['chapter_total_ru']}")
        if errors:
            print("\nErrors:")
            for e in errors:
                print(f"- {e}")
        else:
            print("\nOK: repository structure passed verification.")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
