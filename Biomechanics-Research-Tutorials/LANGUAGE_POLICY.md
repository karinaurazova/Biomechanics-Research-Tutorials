[English](LANGUAGE_POLICY.md) | [Русский](LANGUAGE_POLICY.ru.md)

# Bilingual content policy

The repository uses **English as the default GitHub language** and provides a complete Russian educational mirror.

## One scientific core

The following are shared and must not be duplicated as independent implementations:

- Python source code and public API;
- tests and numerical verification criteria;
- parameters and synthetic numerical data;
- mathematical symbols, equations, and model assumptions;
- BibTeX bibliographies and evidence boundaries.

Figures and animations are generated as localized pairs from the same scripts and the same numerical results:

- English output: `figure.png` or `animation.gif`;
- Russian output: `figure_ru.png` or `animation_ru.gif`.

Localization may change titles, labels, legends, and explanatory text, but it must not change parameters, computed values, plotted curves, sampling seeds, or scientific conclusions.

## File convention

- root English document: `NAME.md`;
- root Russian document: `NAME.ru.md`;
- English tutorial chapters: `chapters/*.md`;
- Russian tutorial chapters: `chapters/ru/*.md`;
- English exercises: `exercises/*.md`;
- Russian exercises: `exercises/ru/*.md`;
- Russian notebook: `*_ru.ipynb`;
- Russian workshop document: `*.ru.md`;
- Russian figure or animation: `*_ru.<extension>`.

## Translation parity

A scientific or methodological change is complete only when both language versions communicate the same:

1. research question;
2. assumptions and evidence boundary;
3. equations and parameter definitions;
4. verification requirements;
5. exercises and assessment criteria;
6. numerical results and visual conclusions.

Translations may use natural language rather than sentence-by-sentence literal wording, but they must not add stronger scientific claims.

## Code language

Code identifiers, command-line instructions, filenames of executable scripts, and developer-facing docstrings remain in English to preserve one executable interface. A small localization layer may supply human-readable labels and messages for figures and notebooks.
