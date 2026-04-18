@echo off
echo ============================================================
echo  MuMu Launcher - Installing dependencies
echo ============================================================
echo.
python --version >/dev/null 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found.
    echo Download Python 3.10+ from https://www.python.org/downloads/
    echo During install check: Add Python to PATH
    pause
    exit /b 1
)
echo [OK] Python found:
python --version
echo.
echo Installing Python packages...
pip install -r "%~dp0requirements.txt"
if errorlevel 1 (
    echo [ERROR] Failed to install packages.
    pause
    exit /b 1
)
echo [OK] Python packages installed.
echo.
adb version >/dev/null 2>&1
if errorlevel 1 (
    echo [WARNING] ADB not found in PATH.
    echo Download: https://developer.android.com/tools/releases/platform-tools
    echo.
) else (
    echo [OK] ADB found.
)
if not exist "%ProgramFiles%\Tesseract-OCR\tesseract.exe" (
    echo [WARNING] Tesseract OCR not found.
    echo Download: https://github.com/UB-Mannheim/tesseract/wiki
    echo Install to default path and select Russian language.
    echo.
) else (
    echo [OK] Tesseract found.
)
echo.
echo ============================================================
echo  Done. Run run.bat to start the application.
echo ============================================================
pause
