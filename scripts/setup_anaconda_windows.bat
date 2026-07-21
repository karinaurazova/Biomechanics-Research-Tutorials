@echo off
setlocal
cd /d "%~dp0\.."

echo [1/4] Creating or updating the conda environment...
call conda run -n biomechanics-tutorials python --version >nul 2>&1
if errorlevel 1 (
    call conda env create --file environment.yml
) else (
    call conda env update --name biomechanics-tutorials --file environment.yml --prune
)
if errorlevel 1 goto :error

echo [2/4] Installing this repository as an editable local package...
call conda run -n biomechanics-tutorials python -m pip install -e ".[dev]"
if errorlevel 1 goto :error

echo [3/4] Registering the Jupyter kernel...
call conda run -n biomechanics-tutorials python -m ipykernel install --user --name biomechanics-tutorials --display-name "Python (Biomechanics Research Tutorials)"
if errorlevel 1 goto :error

echo [4/4] Running the environment check...
call conda run -n biomechanics-tutorials python scripts\diagnose_environment.py
if errorlevel 1 goto :error

echo.
echo Setup completed successfully.
echo Start Jupyter with: conda run -n biomechanics-tutorials jupyter lab
exit /b 0

:error
echo.
echo Setup failed. Run this file from Anaconda Prompt and review the message above.
exit /b 1
