#!/bin/bash
# CodeSentinel Installation Script for Unix/Linux/macOS
# ====================================================

echo
echo "============================================================"
echo "                    CodeSentinel Installer"
echo "============================================================"
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "ERROR: Python is not installed or not in PATH"
        echo "Please install Python 3.13+ and add it to PATH"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

echo "Using Python command: $PYTHON_CMD"

# Check Python version
PYTHON_VERSION=$($PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "Python version: $PYTHON_VERSION"

if ! $PYTHON_CMD -c "import sys; exit(0 if sys.version_info >= (3,13) else 1)" 2>/dev/null; then
    echo "ERROR: Python version $PYTHON_VERSION is too old"
    echo "CodeSentinel requires Python 3.13+"
    exit 1
fi

echo "Running CodeSentinel installer..."
echo

# Run the Python installer
$PYTHON_CMD install.py

if [ $? -ne 0 ]; then
    echo
    echo "ERROR: Installation failed"
    exit 1
fi

echo
echo "============================================================"
echo "Installation completed!"
echo
echo "To configure CodeSentinel, run:"
echo "  $PYTHON_CMD -c \"from tools.codesentinel.setup_wizard import main; main()\""
echo
echo "For GUI setup, run:"
echo "  $PYTHON_CMD -c \"from tools.codesentinel.gui_setup_wizard import main; main()\""
echo "============================================================"
echo