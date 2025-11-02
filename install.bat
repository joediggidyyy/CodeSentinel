@echo off
REM CodeSentinel Installation Script for Windows
REM ============================================

echo.
echo ============================================================
echo                    CodeSentinel Installer
echo ============================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.13+ and add it to PATH
    pause
    exit /b 1
)

echo Running CodeSentinel installer...
echo.

REM Run the Python installer
python install.py

if errorlevel 1 (
    echo.
    echo ERROR: Installation failed
    pause
    exit /b 1
)

echo.
echo ============================================================
echo Installation completed! 
echo.
echo To configure CodeSentinel, run:
echo   python -c "from tools.codesentinel.setup_wizard import main; main()"
echo.
echo For GUI setup, run:
echo   python -c "from tools.codesentinel.gui_setup_wizard import main; main()"
echo ============================================================
echo.
pause