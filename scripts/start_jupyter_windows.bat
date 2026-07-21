@echo off
setlocal
cd /d "%~dp0\.."
call conda run -n biomechanics-tutorials jupyter lab
if errorlevel 1 (
    echo.
    echo Jupyter could not start. Run scripts\setup_anaconda_windows.bat first.
    exit /b 1
)
