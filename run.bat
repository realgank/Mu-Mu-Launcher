@echo off
cd /d "%~dp0PythonApplication4"
python main.py
if errorlevel 1 (
    echo.
    echo [ERROR] App crashed. Run install.bat first.
    pause
)
