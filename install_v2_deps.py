#!/usr/bin/env python3
"""
CodeSentinel v2.0 - Dependency Installer

Created by: joediggidyyy
Quick installer for v2.0 dependencies with graceful error handling.
"""

import sys
import subprocess
from pathlib import Path

def install_dependencies():
    """Install v2.0 dependencies with error handling."""
    print("🔧 CodeSentinel v2.0 Dependency Installer")
    print("Created by: joediggidyyy")
    print("=" * 45)
    
    requirements_file = Path(__file__).parent / "src" / "requirements-v2.txt"
    
    if not requirements_file.exists():
        print("❌ Requirements file not found:")
        print(f"   Expected: {requirements_file}")
        print("   Make sure you're running from the CodeSentinel root directory")
        return 1
    
    print(f"📋 Installing dependencies from: {requirements_file}")
    print("")
    
    try:
        # Try to install using pip
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ], check=True, capture_output=True, text=True)
        
        print("✅ Dependencies installed successfully!")
        print("")
        print("📦 Installed packages:")
        for line in result.stdout.splitlines():
            if "Successfully installed" in line:
                packages = line.replace("Successfully installed", "").strip()
                for package in packages.split():
                    print(f"   ✓ {package}")
        
        print("")
        print("🚀 You can now run: python launch_v2.py")
        return 0
        
    except subprocess.CalledProcessError as e:
        print("❌ Installation failed!")
        print(f"   Error: {e}")
        if e.stderr:
            print(f"   Details: {e.stderr}")
        
        print("\n💡 Try manual installation:")
        print("   pip install PyYAML keyring cryptography")
        return 1
    
    except FileNotFoundError:
        print("❌ pip not found!")
        print("   Make sure Python and pip are properly installed")
        print("   Try: python -m ensurepip --upgrade")
        return 1

def main():
    """Main installer function."""
    try:
        return install_dependencies()
    except KeyboardInterrupt:
        print("\n❌ Installation cancelled by user")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())