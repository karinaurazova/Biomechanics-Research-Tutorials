# Начало работы

[English](https://github.com/karinaurazova/Biomechanics-Research-Tutorials/blob/main/docs/getting-started.md)

## Выберите сценарий работы

- **Anaconda/Jupyter:** используйте [инструкцию по настройке Anaconda](anaconda-setup.md).
- **Чтение на GitHub:** установка не требуется; откройте README tutorial и готовые рисунки.
- **Полное воспроизведение:** установите окружение и запустите `reproduce.py` соответствующего tutorial.

## Что именно импортируется?

Строка

```python
from biomechanics_tutorials... import ...
```

загружает собственный исходный код репозитория из `src/biomechanics_tutorials`. Это не отдельно скачиваемая библиотека. Editable-установка (`python -m pip install -e .`) связывает эту папку с активным Python-окружением.

## Рекомендуемая установка

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python scripts/diagnose_environment.py
jupyter lab
```

Для Anaconda в Windows используйте готовый скрипт из [инструкции](anaconda-setup.md).

## Первый интерактивный запуск

Откройте:

```text
tutorials/01-fiber-reorientation/notebooks/01_fiber_reorientation_ru.ipynb
```

Выполняйте ячейки сверху вниз. Установочная ячейка выведет корень репозитория, используемый Python kernel и путь к локальному пакету.

## Пересоздание результатов

```bash
python tutorials/01-fiber-reorientation/reproduce.py
python tutorials/02-collagen-fiber-dispersion/reproduce.py
python tutorials/03-hyperelastic-constitutive-models/reproduce.py
python tutorials/04-active-passive-stress/reproduce.py
python tutorials/05-structure-tensor-orientation/reproduce.py
python tutorials/06-mechanical-homeostasis/reproduce.py
python tutorials/07-growth-tensor-multiplicative-decomposition/reproduce.py
```

Точное происхождение графиков и численных значений объяснено в разделе [Как устроен репозиторий](how-the-repository-works.md).

Инструкции для Windows, Linux, macOS, VS Code и Visual Studio приведены в разделе [Окружения разработки и IDE](development-environments.md).
