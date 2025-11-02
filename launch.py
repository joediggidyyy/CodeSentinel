#!/usr/bin/env python3
"""
CodeSentinel Setup Launcher

Created by: joediggidyyy
Architecture: SECURITY > EFFICIENCY > MINIMALISM

Launch script for the CodeSentinel setup wizard.
"""

import sys
import os
import subprocess
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def check_dependencies():
    """Check if required dependencies are available."""
    missing_deps = []
    
    try:
        import tkinter
    except ImportError:
        missing_deps.append("tkinter (usually comes with Python)")
    
    try:
        import yaml
    except ImportError:
        missing_deps.append("PyYAML")
    
    try:
        import keyring
    except ImportError:
        missing_deps.append("keyring")
    
    try:
        import cryptography
    except ImportError:
        missing_deps.append("cryptography")
    
    if missing_deps:
        print("❌ Missing required dependencies:")
        for dep in missing_deps:
            print(f"   - {dep}")
        print("\nTo install missing dependencies:")
        print("   Option 1 (Recommended): python install_deps.py")
        print("   Option 2: pip install -r src/requirements.txt")
        print("\nAlternatively, install individually:")
        if "PyYAML" in str(missing_deps):
            print("   pip install PyYAML")
        if "keyring" in str(missing_deps):
            print("   pip install keyring")
        if "cryptography" in str(missing_deps):
            print("   pip install cryptography")
        print("\n❌ Cannot proceed without required dependencies.")
        return False
    
    return True

def main():
    """Main launcher function."""
    print("🚀 CodeSentinel Setup Launcher")
    print("Created by: joediggidyyy")
    print("Architecture: SECURITY > EFFICIENCY > MINIMALISM")
    print("=" * 50)
    print("")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ CodeSentinel requires Python 3.8 or higher")
        print(f"   Current version: {sys.version}")
        return 1
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    
    # Check dependencies
    print("🔍 Checking dependencies...")
    if not check_dependencies():
        return 1
    
    print("✅ All dependencies available")
    
    # Launch setup wizard
    print("🎯 Launching CodeSentinel Setup Wizard...")
    
    try:
        # Import after path setup
        from codesentinel.ui.setup.wizard import main as wizard_main
        wizard_main()
        return 0
    
    except ModuleNotFoundError as e:
        print(f"❌ Module not found: {e}")
        print("   The setup wizard modules are not complete yet.")
        print("   This may be due to incomplete installation.")
        
        print("\n   To complete installation:")
        print("   - Ensure all dependencies are installed")
        print("   - Check that src/codesentinel/ directory exists")
        print("   - Run: python install.py")
        return 1
    
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   This usually means:")
        print("   1. Missing dependencies (run dependency check again)")
        print("   2. Running from wrong directory (should be CodeSentinel root)")
        print("   3. Incomplete installation")
        print("\n   Try:")
        print("   - Ensure you're in the CodeSentinel directory")
        print("   - Install dependencies: pip install -r src/requirements.txt")
        print("   - Check that src/codesentinel/ directory exists")
        return 1
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("   Please report this error at:")
        print("   https://github.com/joediggidyyy/CodeSentinel/issues")
        return 1

if __name__ == "__main__":
    sys.exit(main())

# Entry point for console script
def launcher_main():
    """Entry point for codesentinel-setup console script."""
    import sys
    # Ensure we can import from the current directory
    sys.exit(main())