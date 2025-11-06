#!/bin/bash
################################################################################
#
#  CODESENTINEL INSTALLER - RUN THIS TO INSTALL
#
#  This script makes it easy to install CodeSentinel on Linux/macOS.
#
#  Simply run:
#      bash INSTALL_CODESENTINEL_GUI.sh
#
#  Or make it executable and run:
#      chmod +x INSTALL_CODESENTINEL_GUI.sh
#      ./INSTALL_CODESENTINEL_GUI.sh
#
################################################################################

set -e

# Print banner
cat << 'EOF'

CodeSentinel Interactive GUI Installer

Starting installation wizard...

EOF

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: Python 3 is not installed!"
    echo ""
    echo "Please install Python 3.8 or later:"
    echo "  • Ubuntu/Debian: sudo apt-get install python3 python3-pip python3-tk"
    echo "  • macOS: brew install python3"
    echo "  • Or download from: https://www.python.org/"
    echo ""
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo ""

# Run the installer
python3 INSTALL_CODESENTINEL_GUI.py

# Success
echo ""
echo "✅ Installation complete!"
echo ""
exit 0
