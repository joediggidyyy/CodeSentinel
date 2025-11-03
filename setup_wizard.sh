#!/bin/bash
# CodeSentinel Setup Wizard for Unix/Linux/macOS
# ==============================================
# 
# This script launches the CodeSentinel installation wizard.
# No additional setup required - just run: ./setup_wizard.sh

echo ""
echo "CodeSentinel Setup Wizard"
echo "============================"
echo ""
echo "Starting installation wizard..."
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "✗ Python not found! Please install Python 3.7+ first."
    echo ""
    echo "Install Python:"
    echo "  Ubuntu/Debian: sudo apt install python3"
    echo "  macOS: brew install python3"
    echo "  CentOS/RHEL: sudo yum install python3"
    echo ""
    exit 1
fi

# Use python3 if available, otherwise python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi

# Run the setup wizard
$PYTHON_CMD setup_wizard.py

# Exit with the same code as the wizard
exit $?