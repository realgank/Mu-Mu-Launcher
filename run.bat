@echo off
chcp 65001 >nul
cd /d "%~dp0PythonApplication4"
python main.py
if errorlevel 1 (
    echo.
    echo [ОШИБКА] Приложение завершилось с ошибкой.
    echo Убедитесь, что выполнили install.bat
    pause
)
