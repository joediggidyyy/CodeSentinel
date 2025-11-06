@echo off
REM ============================================================================
REM   CODESENTINEL INSTALLER - DOUBLE CLICK TO INSTALL
REM ============================================================================
REM
REM   This batch file makes it easy to install CodeSentinel on Windows.
REM
REM   Just double-click this file and the setup wizard will launch.
REM
REM ============================================================================

setlocal enabledelayedexpansion

echo.
echo CodeSentinel Interactive GUI Installer
echo.
echo Starting installation wizard...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python is not installed or not in your PATH!
    echo.
    echo Please install Python 3.8 or later from: https://www.python.org/
    echo.
    pause
    exit /b 1
)

echo ✅ Python found!
echo.

REM Run the installer
python INSTALL_CODESENTINEL_GUI.py
if errorlevel 1 (
    echo.
    echo ❌ Installation failed! See error messages above.
    echo.
    pause
    exit /b 1
)

REM Success
echo.
echo ✅ Installation complete!
echo.
pause
exit /b 0
