@echo off
REM Build installer for Windows using Inno Setup

echo ========================================
echo   Building Windows Installer
echo ========================================
echo.

REM Navigate to project root (parent directory of scripts)
cd /d "%~dp0\.."
echo Working directory: %CD%
echo.

REM Check if Inno Setup is installed
set INNO_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe
if not exist "%INNO_PATH%" (
    echo ERROR: Inno Setup not found at: %INNO_PATH%
    echo.
    echo Please download and install Inno Setup from:
    echo https://jrsoftware.org/isinfo.php
    echo.
    echo OR you can distribute the portable folder:
    echo dist\Evading PSCP\
    echo.
    pause
    exit /b 1
)

echo Using Inno Setup: %INNO_PATH%
echo.

REM Create output directory
if not exist installers mkdir installers

echo Compiling installer...
"%INNO_PATH%" build_config\Evading_PSCP_installer.iss

if exist "installers\Evading_PSCP_Setup.exe" (
    echo.
    echo ^✓ Installer created successfully!
    echo Installer: installers\Evading_PSCP_Setup.exe
    echo.
) else (
    echo.
    echo ^✗ Installer creation failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Installer Complete!
echo ========================================
echo.
echo Distribute: installers\Evading_PSCP_Setup.exe
pause
