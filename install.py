#!/usr/bin/env python3
"""
CodeSentinel Installer with PATH Configuration
==============================================

This script installs CodeSentinel and automatically configures PATH
so CLI commands work immediately.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def print_header(title):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(title.center(60))
    print(f"{'='*60}\n")


def print_step(step, title):
    """Print a step header."""
    print(f"[Step {step}] {title}")


def print_success(message):
    """Print a success message."""
    print(f"✓ {message}")


def print_error(message):
    """Print an error message."""
    print(f"✗ {message}")


def print_warning(message):
    """Print a warning message."""
    print(f"⚠ {message}")


def check_python_version():
    """Check if Python version meets requirements."""
    version = sys.version_info
    if version < (3, 13):
        print_error(f"Python {version.major}.{version.minor} detected")
        print_error("CodeSentinel requires Python 3.13 or later")
        return False
    
    print_success(f"Python {version.major}.{version.minor}.{version.micro} detected")
    return True


def ensure_pip():
    """Ensure pip is available, install if missing."""
    print("🔧 Checking pip availability...")
    
    try:
        import pip
        print("✅ pip is already available")
        return True
    except ImportError:
        print("⚠️ pip not found, attempting to install...")
        
        try:
            # Try using ensurepip module (available in Python 3.4+)
            import subprocess
            import sys
            
            result = subprocess.run([
                sys.executable, "-m", "ensurepip", "--upgrade"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ pip installed successfully via ensurepip")
                return True
            else:
                print(f"❌ ensurepip failed: {result.stderr}")
                
        except Exception as e:
            print(f"❌ Could not install pip automatically: {e}")
            
        print("\n🚨 MANUAL ACTION REQUIRED:")
        print("   Please install pip manually before proceeding:")
        print("   1. Download get-pip.py from https://bootstrap.pypa.io/get-pip.py")
        print("   2. Run: python get-pip.py")
        print("   3. Re-run this installer")
        return False

def check_pip_availability():
    """Check if pip is available and install if missing."""
    print("Checking pip availability...")
    
    try:
        # Test if pip is available
        result = subprocess.run([
            sys.executable, '-m', 'pip', '--version'
        ], capture_output=True, text=True, check=True)
        
        print_success("pip is available")
        return True
        
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_warning("pip is not available - attempting to install...")
        
        try:
            # Try to install pip using ensurepip
            result = subprocess.run([
                sys.executable, '-m', 'ensurepip', '--upgrade'
            ], capture_output=True, text=True, check=True)
            
            print_success("pip installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            print_error("Failed to install pip using ensurepip")
            print(f"Error: {e.stderr}")
            
            # Provide manual installation instructions
            print("\nTo install pip manually:")
            print("1. Download get-pip.py from https://bootstrap.pypa.io/get-pip.py")
            print("2. Run: python get-pip.py")
            print("3. Or install Python from python.org which includes pip")
            
            return False


def check_core_dependencies():
    """Check if core Python modules are available."""
    print("Checking core dependencies...")
    
    missing_modules = []
    optional_missing = []
    
    # Core modules (should be in standard library)
    core_modules = [
        'pathlib', 'json', 'os', 'sys', 'platform', 'subprocess',
        'urllib.request', 'urllib.error', 'smtplib', 'email',
        'logging', 'datetime', 'argparse', 'shutil', 'getpass',
        'threading', 'queue', 'typing', 're', 'sysconfig'
    ]
    
    # Optional modules
    optional_modules = [
        ('tkinter', 'GUI functionality'),
        ('requests', 'HTTP requests and Slack alerts'),
        ('schedule', 'Automated scheduling')
    ]
    
    # Check core modules
    for module in core_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    # Check optional modules
    for module, description in optional_modules:
        try:
            __import__(module)
            print_success(f"{module} available - {description}")
        except ImportError:
            optional_missing.append((module, description))
            print_warning(f"{module} not available - {description} will be limited")
    
    if missing_modules:
        print_error(f"Missing core modules: {', '.join(missing_modules)}")
        print_error("These modules should be included with Python. Please check your Python installation.")
        return False
    
    print_success("All core dependencies available")
    
    if optional_missing:
        print("\nOptional dependencies that will be installed:")
        for module, description in optional_missing:
            print(f"  - {module}: {description}")
    
    return True


def install_package():
    """Install the CodeSentinel package."""
    print("Installing CodeSentinel package...")
    
    try:
        # Upgrade pip first
        print("Upgrading pip...")
        subprocess.run([
            sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'
        ], check=True, capture_output=True, text=True)
        
        # Install setuptools and wheel
        print("Installing build dependencies...")
        subprocess.run([
            sys.executable, '-m', 'pip', 'install', '--upgrade', 'setuptools', 'wheel'
        ], check=True, capture_output=True, text=True)
        
        # Install requirements first
        print("Installing core requirements...")
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print_warning("Some requirements may not have installed correctly")
            print(f"Requirements output: {result.stderr}")
        
        # Install CodeSentinel in editable mode
        print("Installing CodeSentinel...")
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-e', '.'
        ], check=True, capture_output=True, text=True)
        
        print_success("CodeSentinel package installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print_error("Package installation failed")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        
        # Provide troubleshooting information
        print("\nTroubleshooting:")
        print("1. Check that you have write permissions to the Python installation")
        print("2. Try running as administrator/sudo if needed")
        print("3. Check that your Python installation is complete")
        print("4. Try: python -m pip install --user -e .")
        
        return False


def configure_path():
    """Configure PATH for CLI commands."""
    print("Configuring PATH for CLI commands...")
    
    try:
        # Run the PATH configurator as a subprocess
        result = subprocess.run([
            sys.executable, 'tools/codesentinel/path_configurator.py', '--auto'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print_success("PATH configuration completed")
            return True
        else:
            print_warning("PATH configuration had issues")
            print(result.stdout)
            return False
        
    except Exception as e:
        print_warning(f"Could not run PATH configurator: {e}")
        print_warning("You can configure PATH manually later using:")
        print("  python tools/codesentinel/path_configurator.py")
        return False


def test_installation():
    """Test if the installation works."""
    print("Testing installation...")
    
    try:
        # Test Python import
        import codesentinel
        print_success("Package import successful")
        
        # Test CLI import
        from codesentinel.cli import main
        print_success("CLI import successful")
        
        # Test setup wizard import
        from tools.codesentinel.setup_wizard import main as setup_main
        print_success("Setup wizard import successful")
        
        # Test GUI setup wizard import
        try:
            from tools.codesentinel.gui_setup_wizard import main as gui_main
            print_success("GUI setup wizard import successful")
        except ImportError:
            print_warning("GUI setup wizard not available (tkinter missing)")
        
        return True
        
    except ImportError as e:
        print_error(f"Import test failed: {e}")
        return False


def show_usage_instructions():
    """Show how to use CodeSentinel after installation."""
    print_header("Installation Complete!")
    
    print("CodeSentinel has been installed successfully!")
    print("\nAvailable commands:")
    
    # Try to determine if CLI commands are available
    import shutil
    if shutil.which('codesentinel'):
        print("\nDirect CLI commands:")
        print("  codesentinel --help                    # Main CLI")
        print("  codesentinel status                    # Check status")
        print("  codesentinel scan                      # Security scan")
        print("  codesentinel maintenance daily         # Daily maintenance")
        print("  codesentinel-setup                     # Setup wizard")
        print("  codesentinel-setup-gui                 # GUI setup wizard")
    else:
        print("\nPython module commands (CLI not in PATH):")
        print("  python -c \"from codesentinel.cli import main; main()\" --help")
        print("  python -c \"from tools.codesentinel.setup_wizard import main; main()\"")
        print("  python -c \"from tools.codesentinel.gui_setup_wizard import main; main()\"")
    
    print("\nDirect script execution:")
    print("  python tools/codesentinel/scheduler.py --help")
    print("  python tools/codesentinel/alert_system.py --help")
    print("  python tools/codesentinel/path_configurator.py")
    
    print("\nNext steps:")
    print("1. Run the setup wizard to configure your environment")
    print("2. Configure alerts and maintenance schedules")
    print("3. Set up GitHub integration if desired")
    
    print(f"\n{'='*60}")


def main():
    """Main installer entry point."""
    print_header("CodeSentinel Installer")
    
    print("Installing CodeSentinel with comprehensive dependency checking...")
    
    # Step 1: Check Python version
    print_step(1, "Checking Python Version")
    if not check_python_version():
        sys.exit(1)
    
    # Step 2: Ensure pip is available
    print_step(2, "Ensuring pip Availability")
    if not ensure_pip():
        sys.exit(1)
    
    # Step 3: Check pip availability and upgrade
    print_step(3, "Checking pip Availability")
    if not check_pip_availability():
        sys.exit(1)
    
    # Step 4: Check dependencies
    print_step(4, "Checking Dependencies")
    if not check_core_dependencies():
        sys.exit(1)
    
    # Step 5: Install package
    print_step(5, "Installing Package")
    if not install_package():
        sys.exit(1)
    
    # Step 6: Configure PATH
    print_step(6, "Configuring PATH")
    configure_path()  # Don't fail if this doesn't work
    
    # Step 7: Test installation
    print_step(7, "Testing Installation")
    if not test_installation():
        print_warning("Some tests failed, but basic installation may still work")
    
    # Step 8: Show usage
    show_usage_instructions()
    
    print("\nTo configure CodeSentinel for your environment, run:")
    print("  python -c \"from tools.codesentinel.setup_wizard import main; main()\"")
    
    print("\nFor PATH configuration help, run:")
    print("  python tools/codesentinel/path_configurator.py")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInstallation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nInstallation failed with error: {e}")
        sys.exit(1)