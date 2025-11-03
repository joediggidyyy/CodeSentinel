@echo off
REM CodeSentinel Setup Wizard for Windows
REM ====================================
REM 
REM This script launches the CodeSentinel installation wizard.
REM No additional setup required - just double-click to run!

echo.
echo CodeSentinel Setup Wizard
echo ============================
echo.
echo Starting installation wizard...
echo.

REM Try to find Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ Python not found! Please install Python 3.7+ first.
    echo.
    echo Download Python from: https://python.org/downloads
    echo.
    pause
    exit /b 1
)

REM Run the setup wizard
python setup_wizard.py

REM Keep window open if there was an error
if %errorlevel% neq 0 (
    echo.
    echo ✗ Setup wizard failed. Press any key to close.
    pause >nul
)