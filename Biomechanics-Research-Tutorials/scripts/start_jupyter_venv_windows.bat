@echo off
setlocal
cd /d "%~dp0\.."
if not exist ".venv\Scripts\python.exe" (
    echo .venv was not found. Run scripts\setup_venv_windows.bat first.
    exit /b 1
)
.venv\Scripts\python.exe scripts\start_jupyter.py %*
