@echo off
REM Build script for Windows

echo ========================================
echo   Building Evading PSCP for Windows
echo ========================================
echo.

REM Navigate to project root (parent directory of scripts)
cd /d "%~dp0\.."
echo Working directory: %CD%
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

echo Creating virtual environment...
if not exist venv_windows (
    python -m venv venv_windows
)

echo Activating virtual environment...
call venv_windows\Scripts\activate.bat

echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist\Evading^ PSCP rmdir /s /q "dist\Evading PSCP"

echo Building application with PyInstaller...
pyinstaller build_config\Evading_PSCP_windows.spec --clean --noconfirm

if exist "dist\Evading PSCP\Evading PSCP.exe" (
    echo.
    echo ^✓ Build successful!
    echo App created at: dist\Evading PSCP\
    echo.
) else (
    echo.
    echo ^✗ Build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Build Complete!
echo ========================================
echo.
echo Run scripts\build_windows_installer.bat to create installer
pause
