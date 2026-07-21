[English](START_HERE.md) | [Русский](START_HERE.ru.md)

# Начните отсюда

Репозиторий содержит три связанных уровня:

1. **`src/biomechanics_tutorials/`** — общий локальный Python-пакет с математическими моделями и переиспользуемыми средствами визуализации;
2. **`tutorials/.../notebooks/`** — интерактивные учебные разборы, выполняющие вычисления в выбранном Jupyter kernel;
3. **`tutorials/.../experiments/`** — скрипты воспроизводимости, создающие PNG- и GIF-файлы в `figures/` и `animations/`.

Название `biomechanics_tutorials` в строке импорта **не означает внешнюю библиотеку из интернета**. Это исходный код внутри данного репозитория.

## Рекомендуемая установка

Наиболее универсальный вариант для Windows, Linux, macOS, VS Code и Visual Studio — локальное виртуальное окружение проекта:

```bash
# Windows
py -3 scripts/setup_venv.py

# Linux/macOS
python3 scripts/setup_venv.py
```

Запустите Jupyter командой `python scripts/start_jupyter.py` и выберите kernel **Python (.venv — Biomechanics Research Tutorials)**.

Anaconda также полностью поддерживается через скрипты `scripts/setup_anaconda_*`.

- Полная инструкция по окружениям и IDE: [docs/ru/development-environments.md](docs/ru/development-environments.md)
- Отдельная инструкция Anaconda: [docs/ru/anaconda-setup.md](docs/ru/anaconda-setup.md)
- Устройство репозитория и происхождение рисунков: [docs/ru/how-the-repository-works.md](docs/ru/how-the-repository-works.md)
