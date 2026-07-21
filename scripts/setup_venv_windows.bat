@echo off
setlocal
cd /d "%~dp0\.."
where py >nul 2>&1
if errorlevel 1 (
    python scripts\setup_venv.py %*
) else (
    py -3 scripts\setup_venv.py %*
)
if errorlevel 1 (
    echo.
    echo Setup failed. Confirm that Python 3.10 or newer is installed.
    exit /b 1
)
