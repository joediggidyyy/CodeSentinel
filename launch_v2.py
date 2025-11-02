#!/usr/bin/env python3
"""
CodeSentinel v2.0 Setup Launcher

Created by: joediggidyyy
Architecture: SECURITY > EFFICIENCY > MINIMALISM

Launch script for the new CodeSentinel v2.0 setup wizard.
"""

import sys
import os
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
        print("   pip install -r src/requirements-v2.txt")
        return False
    
    return True

def main():
    """Main launcher function."""
    print("🚀 CodeSentinel v2.0 Setup Launcher")
    print("Created by: joediggidyyy")
    print("Architecture: SECURITY > EFFICIENCY > MINIMALISM")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ CodeSentinel v2.0 requires Python 3.8 or higher")
        print(f"   Current version: {sys.version}")
        return 1
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    
    # Check dependencies
    print("🔍 Checking dependencies...")
    if not check_dependencies():
        return 1
    
    print("✅ All dependencies available")
    
    # Launch setup wizard
    print("🎯 Launching CodeSentinel v2.0 Setup Wizard...")
    
    try:
        # Import after path setup
        from codesentinel_v2.ui.setup.wizard import main as wizard_main
        wizard_main()
        return 0
    
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure you're running from the CodeSentinel root directory")
        return 1
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())