# Окружения разработки и IDE

Проект поддерживает два способа организации окружения:

- локальное **`.venv`** в папке проекта — рекомендуется для VS Code, Visual Studio и командной строки;
- именованное **conda-окружение** — рекомендуется пользователям Anaconda или Miniconda.

Не смешивайте интерпретаторы в одной рабочей сессии. Терминал, IDE и kernel notebook должны использовать одно окружение.

## Требования

- Python 3.10 или новее;
- Git при клонировании репозитория;
- доступ к интернету во время первой установки зависимостей.

## Универсальная установка `.venv`

Команды выполняются в папке, содержащей `pyproject.toml`.

### Windows

```bat
py -3 scripts\setup_venv.py
```

Если launcher `py` недоступен:

```bat
python scripts\setup_venv.py
```

### Linux

```bash
python3 scripts/setup_venv.py
```

В Debian/Ubuntu может потребоваться системный пакет `python3-venv`.

### macOS

```bash
python3 scripts/setup_venv.py
```

Скрипт создаёт `.venv`, устанавливает репозиторий командой `pip install -e ".[dev]"`, регистрирует Jupyter kernel и запускает `scripts/diagnose_environment.py`.

Также доступны короткие обёртки:

```text
Windows: scripts\setup_venv_windows.bat
Linux/macOS: bash scripts/setup_venv_unix.sh
```

## Запуск Jupyter

Кроссплатформенный launcher автоматически использует `.venv`, если оно существует:

```bash
python scripts/start_jupyter.py
```

Можно также активировать окружение и выполнить `python -m jupyterlab`.

## Anaconda / Miniconda

```text
Windows: scripts\setup_anaconda_windows.bat
Linux/macOS: bash scripts/setup_anaconda_unix.sh
```

Запуск Jupyter:

```bash
conda run -n biomechanics-tutorials jupyter lab
```

## Visual Studio Code

В репозитории находятся готовые `.vscode/extensions.json`, `settings.json`, `tasks.json` и `launch.json`.

1. Откройте **корневую папку репозитория**, а не отдельный notebook.
2. Установите рекомендованные расширения Microsoft Python, Pylance и Jupyter.
3. Запустите задачу VS Code **Setup project .venv** либо выполните `scripts/setup_venv.py` во встроенном терминале.
4. Выполните **Python: Select Interpreter** и выберите интерпретатор из `.venv`.
5. Откройте notebook, нажмите **Select Kernel** и выберите то же окружение.
6. Перед поиском ошибок импорта запустите задачу диагностики.

Настройки workspace добавляют `src/` в статический анализ, включают обнаружение pytest и фиксируют рабочую папку notebooks на корне репозитория.

## Visual Studio в Windows

Полная Visual Studio поддерживает Python только в Windows. Корневой файл `.vsconfig` запрашивает workload **Python development**.

1. Откройте `.vsconfig` через Visual Studio Installer и установите недостающие компоненты.
2. Выполните `scripts\setup_venv_windows.bat` в PowerShell или Command Prompt.
3. В Visual Studio выберите **File → Open → Folder** и укажите корневую папку репозитория.
4. В окне **Python Environments** выберите или добавьте `.venv\Scripts\python.exe`.
5. Запускайте скрипты, эксперименты и тесты в этом окружении.
6. Для `.ipynb` запустите Jupyter во встроенном терминале командой `python scripts/start_jupyter.py` либо используйте VS Code/JupyterLab.

Файлы `.sln` и `.pyproj` не обязательны: современные версии Visual Studio могут открывать папку с Python-кодом напрямую.

## Диагностика

Запускайте её тем интерпретатором, который планируете использовать:

```bash
python scripts/diagnose_environment.py
```

В выводе должны быть активный Python и путь локального пакета, заканчивающийся на `src/biomechanics_tutorials/__init__.py`.

## Частые ошибки

### `ModuleNotFoundError: biomechanics_tutorials`

Репозиторий не установлен в выбранное окружение либо notebook использует другой kernel. Выполните установочный скрипт и выберите соответствующий kernel.

### В терминале всё работает, а notebook выдаёт ошибку

Терминал и notebook используют разные интерпретаторы. Проверьте `sys.executable` в первой ячейке и выберите то же окружение.

### VS Code подчёркивает импорт, но код выполняется

Обновите список окружений Python, выберите `.venv` и перезагрузите окно VS Code. В workspace уже добавлена папка `src/` через `python.analysis.extraPaths`.
