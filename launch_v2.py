#!/usr/bin/env python3
"""
CodeSentinel v2.0 Setup Launcher

Created by: joediggidyyy
Architecture: SECURITY > EFFICIENCY > MINIMALISM

Launch script for the new CodeSentinel v2.0 setup wizard.
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
        print("   Option 1 (Recommended): python install_v2_deps.py")
        print("   Option 2: pip install -r src/requirements-v2.txt")
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

def try_v1_fallback():
    """Try to launch the v1.0 setup wizard as a fallback."""
    print("\n🔄 Attempting to launch v1.0 setup wizard as fallback...")
    
    try:
        # Try GUI setup wizard
        import subprocess
        result = subprocess.run([sys.executable, "-m", "tools.codesentinel.gui_setup_wizard"], 
                              cwd=Path(__file__).parent)
        return result.returncode == 0
    except Exception as e:
        print(f"   Failed to launch v1.0 GUI wizard: {e}")
    
    try:
        # Try CLI setup wizard
        result = subprocess.run([sys.executable, "-m", "tools.codesentinel.setup_wizard"], 
                              cwd=Path(__file__).parent)
        return result.returncode == 0
    except Exception as e:
        print(f"   Failed to launch v1.0 CLI wizard: {e}")
    
    try:
        # Try direct execution
        result = subprocess.run([sys.executable, "tools/codesentinel/gui_setup_wizard.py"], 
                              cwd=Path(__file__).parent)
        return result.returncode == 0
    except Exception as e:
        print(f"   Failed direct execution: {e}")
    
    return False

def main():
    """Main launcher function."""
    print("🚀 CodeSentinel v2.0 Setup Launcher")
    print("Created by: joediggidyyy")
    print("Architecture: SECURITY > EFFICIENCY > MINIMALISM")
    print("=" * 50)
    print("ℹ️  NOTE: v2.0 is under active development")
    print("   If v2.0 components are incomplete, fallback to v1.0 is available")
    print("")
    
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
    
    except ModuleNotFoundError as e:
        print(f"❌ Module not found: {e}")
        print("   The v2.0 modules are not complete yet.")
        print("   This is expected as v2.0 is under development.")
        
        # Offer fallback to v1.0
        print("\n🔄 Would you like to try the v1.0 setup wizard instead? (y/n): ", end="")
        try:
            response = input().lower().strip()
            if response in ['y', 'yes']:
                if try_v1_fallback():
                    print("✅ Successfully launched v1.0 setup wizard")
                    return 0
                else:
                    print("❌ Failed to launch v1.0 setup wizard")
        except (EOFError, KeyboardInterrupt):
            print("\n❌ User cancelled")
        
        print("\n   To use the current stable version manually:")
        print("   - Run: python -m tools.codesentinel.gui_setup_wizard")
        print("   - Or: codesentinel-setup-gui")
        return 1
    
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   This usually means:")
        print("   1. Missing dependencies (run dependency check again)")
        print("   2. Running from wrong directory (should be CodeSentinel root)")
        print("   3. Incomplete v2.0 installation")
        print("\n   Try:")
        print("   - Ensure you're in the CodeSentinel directory")
        print("   - Install dependencies: pip install -r src/requirements-v2.txt")
        print("   - Check that src/codesentinel_v2/ directory exists")
        return 1
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("   Please report this error at:")
        print("   https://github.com/joediggidyyy/CodeSentinel/issues")
        return 1

if __name__ == "__main__":
    sys.exit(main())