@echo off
chcp 65001 >nul
echo ============================================================
echo  Установка зависимостей MuMu Launcher
echo ============================================================
echo.

:: Проверяем Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] Python не найден.
    echo Скачайте Python 3.10+ с https://www.python.org/downloads/
    echo При установке отметьте "Add Python to PATH"
    pause
    exit /b 1
)

echo [OK] Python найден:
python --version
echo.

:: Устанавливаем pip-зависимости
echo Устанавливаем Python-зависимости...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ОШИБКА] Не удалось установить зависимости.
    pause
    exit /b 1
)
echo.
echo [OK] Python-зависимости установлены.
echo.

:: Проверяем ADB
adb version >nul 2>&1
if errorlevel 1 (
    echo [ВНИМАНИЕ] ADB не найден в PATH.
    echo Скачайте Android Platform Tools и добавьте в PATH:
    echo https://developer.android.com/tools/releases/platform-tools
    echo.
) else (
    echo [OK] ADB найден.
)

:: Проверяем Tesseract
if not exist "C:\Program Files\Tesseract-OCR\tesseract.exe" (
    echo [ВНИМАНИЕ] Tesseract OCR не найден.
    echo Скачайте установщик:
    echo https://github.com/UB-Mannheim/tesseract/wiki
    echo Устанавливайте в папку по умолчанию: C:\Program Files\Tesseract-OCR\
    echo Во время установки выберите дополнительный язык: Russian
    echo.
) else (
    echo [OK] Tesseract найден.
)

echo.
echo ============================================================
echo  Установка завершена. Запустите run.bat для старта.
echo ============================================================
pause
