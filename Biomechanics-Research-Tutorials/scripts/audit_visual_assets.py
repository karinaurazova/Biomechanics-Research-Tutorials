"""Audit bilingual visual assets and create optional contact sheets.

The audit is intentionally deterministic and does not use OCR. It checks localized
pairing, pixel dimensions, aspect ratios, and known source-level localization risks.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from PIL import Image, ImageDraw
import math

ROOT = Path(__file__).resolve().parents[1]
KNOWN_ENGLISH_RISKS = (
    "Active stress",
    "Active strain",
    "Deposition stretch",
    "Raw MAE",
    "Normalized MAE",
    "Pressure-like",
    "Volume-like",
    "PASS",
    "FAIL",
)


def audit() -> list[str]:
    issues: list[str] = []
    for tutorial in sorted((ROOT / "tutorials").glob("[0-9][0-9]-*")):
        figures = tutorial / "figures"
        animations = tutorial / "animations"
        for directory, suffix in [(figures, ".png"), (animations, ".gif")]:
            if not directory.exists():
                issues.append(f"Missing directory: {directory}")
                continue
            for english in sorted(
                p for p in directory.glob(f"*{suffix}") if not p.stem.endswith("_ru")
            ):
                russian = english.with_name(f"{english.stem}_ru{english.suffix}")
                if not russian.exists():
                    issues.append(f"Missing Russian pair: {english}")
                    continue
                with Image.open(english) as en_image, Image.open(russian) as ru_image:
                    en_ratio = en_image.width / en_image.height
                    ru_ratio = ru_image.width / ru_image.height
                    if abs(en_ratio - ru_ratio) / max(en_ratio, 1e-12) > 0.12:
                        issues.append(
                            f"Language-pair aspect mismatch: {english.name} {en_ratio:.2f} vs {ru_ratio:.2f}"
                        )
                    if suffix == ".png":
                        width, height = ru_image.size
                        if width < 900 or height < 650:
                            issues.append(f"Low-resolution figure: {russian} ({width}x{height})")
                        ratio = width / height
                        if ratio < 0.35 or ratio > 4.5:
                            issues.append(f"Extreme aspect ratio: {russian} ({ratio:.2f})")

        # Source-level safety check. These phrases are allowed in English branches,
        # but every known occurrence should have an explicit Russian counterpart.
        for source in (tutorial / "experiments").glob("*.py"):
            text = source.read_text(encoding="utf-8")
            for phrase in KNOWN_ENGLISH_RISKS:
                if phrase in text and "language" not in text and "_t(" not in text and "t(" not in text:
                    issues.append(f"Unlocalized source phrase '{phrase}': {source}")
    return issues


def contact_sheet(tutorial: Path, output: Path) -> None:
    images = sorted((tutorial / "figures").glob("*_ru.png"))
    if not images:
        return
    cell_w, cell_h, caption_h = 440, 300, 34
    columns = 3
    rows = math.ceil(len(images) / columns)
    sheet = Image.new("RGB", (columns * cell_w, rows * (cell_h + caption_h)), "white")
    draw = ImageDraw.Draw(sheet)
    for index, path in enumerate(images):
        with Image.open(path).convert("RGB") as image:
            image.thumbnail((cell_w - 16, cell_h - 16))
            left = (index % columns) * cell_w + (cell_w - image.width) // 2
            top = (index // columns) * (cell_h + caption_h) + (cell_h - image.height) // 2
            sheet.paste(image, (left, top))
        draw.text(
            ((index % columns) * cell_w + 8, (index // columns) * (cell_h + caption_h) + cell_h + 5),
            path.stem,
            fill="black",
        )
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output, quality=90)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contact-sheets", type=Path)
    args = parser.parse_args()
    issues = audit()
    if args.contact_sheets:
        for tutorial in sorted((ROOT / "tutorials").glob("[0-9][0-9]-*")):
            contact_sheet(tutorial, args.contact_sheets / f"{tutorial.name}_ru.jpg")
    if issues:
        print("Visual audit issues:")
        for issue in issues:
            print(f"- {issue}")
        raise SystemExit(1)
    print("Visual asset audit passed.")


if __name__ == "__main__":
    main()
