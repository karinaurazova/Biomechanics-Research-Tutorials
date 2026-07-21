# Настройка Anaconda

[English](https://github.com/karinaurazova/Biomechanics-Research-Tutorials/blob/main/docs/anaconda-setup.md)

## Почему возникает `ModuleNotFoundError`

`biomechanics_tutorials` — локальный пакет, расположенный в `src/biomechanics_tutorials`. Jupyter Notebook выполняет код в Python-окружении выбранного kernel. Если репозиторий не установлен в этом окружении или Jupyter использует другой kernel, Python не может найти пакет.

## Рекомендуемая настройка в Windows

1. Распакуйте или клонируйте **весь репозиторий**. Нельзя переносить только файл notebook.
2. Откройте **Anaconda Prompt**.
3. Перейдите в корень репозитория — папку, в которой находится `pyproject.toml`.
4. Выполните:

```bat
scripts\setup_anaconda_windows.bat
```

Скрипт создаст окружение `biomechanics-tutorials`, установит локальный репозиторий в editable-режиме, зарегистрирует Jupyter kernel и запустит диагностику.

Запустите Jupyter:

```bat
scripts\start_jupyter_windows.bat
```

или командой `conda run -n biomechanics-tutorials jupyter lab`.

В Jupyter выберите:

```text
Kernel → Change Kernel → Python (Biomechanics Research Tutorials)
```

## Ручная установка

Первое создание окружения:

```bat
conda env create --file environment.yml
```

Последующие обновления:

```bat
conda env update --name biomechanics-tutorials --file environment.yml --prune
```

Затем выполните:

```bat
conda activate biomechanics-tutorials
python -m pip install -e ".[dev]"
python -m ipykernel install --user --name biomechanics-tutorials --display-name "Python (Biomechanics Research Tutorials)"
python scripts\diagnose_environment.py
jupyter lab
```

## Что проверить

Внутри notebook выполните:

```python
import sys
print(sys.executable)
```

Путь должен вести в conda-окружение `biomechanics-tutorials`. Новая установочная ячейка notebook также выводит корень репозитория и точный файл локального пакета, который используется при вычислениях.
