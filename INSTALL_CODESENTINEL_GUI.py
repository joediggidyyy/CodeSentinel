#!/usr/bin/env python3
"""
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║              🚀 CODESENTINEL INSTALLER - START HERE 🚀                    ║
║                                                                            ║
║  This is the easiest way to install CodeSentinel with the GUI wizard.     ║
║                                                                            ║
║  Simply run:                                                               ║
║      python INSTALL_CODESENTINEL_GUI.py                                   ║
║                                                                            ║
║  Or on Windows, just double-click this file.                              ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
"""

import sys
import subprocess
from pathlib import Path


def print_header():
    """Print welcome banner."""
    print("\n" + "=" * 80)
    print("║ CodeSentinel Interactive GUI Installer".ljust(80) + "║")
    print("=" * 80)
    print()


def install_requirements():
    """Install required dependencies."""
    print("📦 Installing dependencies...")
    print("-" * 80)
    
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    if not requirements_file.exists():
        print("❌ ERROR: requirements.txt not found!")
        print(f"   Expected at: {requirements_file}")
        sys.exit(1)
    
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-q", "-r", str(requirements_file)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print("✅ Dependencies installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        print("\nTrying with verbose output for troubleshooting...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)])
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error during installation: {e}")
        sys.exit(1)
    
    print()


def launch_gui_wizard():
    """Launch the GUI setup wizard."""
    print("🎨 Launching CodeSentinel Setup Wizard...")
    print("-" * 80)
    
    try:
        # Try to import and run the GUI wizard
        from codesentinel.gui_wizard_v2 import WizardApp
        
        print("✅ GUI module loaded!")
        print()
        
        # Create and run wizard
        wizard = WizardApp()
        wizard.root.mainloop()
        
        print()
        print("=" * 80)
        print("✅ CodeSentinel installation complete!")
        print("=" * 80)
        print()
        print("📖 Next steps:")
        print("   1. Type 'codesentinel' in your terminal to verify installation")
        print("   2. Run 'codesentinel setup' to configure monitoring")
        print("   3. Check 'codesentinel status' to see system status")
        print()
        
    except ImportError as e:
        print(f"❌ Could not load GUI module: {e}")
        print()
        print("This might mean:")
        print("  • The GUI module is not installed")
        print("  • There's a Python path issue")
        print()
        print("Try running: pip install -e .")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error launching wizard: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """Main installer flow."""
    print_header()
    
    print("This script will:")
    print("  1. Install all required dependencies")
    print("  2. Launch the interactive setup wizard")
    print()
    
    # Step 1: Install requirements
    install_requirements()
    
    # Step 2: Launch GUI wizard
    launch_gui_wizard()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Installation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
