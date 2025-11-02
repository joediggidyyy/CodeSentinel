#!/usr/bin/env python3
"""
CodeSentinel PATH Configuration Helper
=====================================

Automatically detects and configures PATH to include Python scripts directory
so CodeSentinel CLI commands work directly.
"""

import os
import sys
import platform
import shutil
import subprocess
from pathlib import Path
from typing import Optional


class PathConfigurator:
    """Handles PATH configuration for CodeSentinel CLI commands."""

    def __init__(self):
        self.system = platform.system().lower()
        self.scripts_dir = self.detect_scripts_directory()

    def detect_scripts_directory(self) -> Optional[Path]:
        """Detect where Python installs console scripts."""
        try:
            # Method 1: Check if codesentinel is already available
            codesentinel_path = shutil.which('codesentinel')
            if codesentinel_path:
                return Path(codesentinel_path).parent

            # Method 2: Use sysconfig to get scripts directory
            import sysconfig
            
            # Try user scripts first (more common for --user installs)
            user_scripts = sysconfig.get_path('scripts', scheme='posix_user')
            if self.system == 'windows':
                user_scripts = sysconfig.get_path('scripts', scheme='nt_user')
            
            if user_scripts and Path(user_scripts).exists():
                # Check if any CodeSentinel scripts exist there
                cs_scripts = list(Path(user_scripts).glob('codesentinel*'))
                if cs_scripts:
                    return Path(user_scripts)

            # Try system scripts directory
            scripts_dir = sysconfig.get_path('scripts')
            if scripts_dir and Path(scripts_dir).exists():
                cs_scripts = list(Path(scripts_dir).glob('codesentinel*'))
                if cs_scripts:
                    return Path(scripts_dir)

            # Method 3: Common locations based on Python installation
            python_exe = Path(sys.executable)
            common_script_dirs = []
            
            if self.system == 'windows':
                # Windows common locations
                common_script_dirs = [
                    python_exe.parent / "Scripts",
                    Path.home() / "AppData" / "Local" / "Programs" / "Python" / f"Python{sys.version_info.major}{sys.version_info.minor}" / "Scripts",
                    Path.home() / "AppData" / "Local" / "Packages" / "PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0" / "LocalCache" / "local-packages" / "Python313" / "Scripts",
                ]
            else:
                # Unix-like systems
                common_script_dirs = [
                    python_exe.parent,
                    Path.home() / ".local" / "bin",
                    Path("/usr/local/bin"),
                    Path("/opt/homebrew/bin"),  # macOS Homebrew
                ]
            
            for script_dir in common_script_dirs:
                if script_dir.exists():
                    cs_scripts = list(script_dir.glob('codesentinel*'))
                    if cs_scripts:
                        return script_dir

        except Exception as e:
            print(f"Error detecting scripts directory: {e}")
        
        return None

    def is_in_path(self, directory: Path) -> bool:
        """Check if directory is in PATH."""
        current_path = os.environ.get('PATH', '')
        path_separator = ';' if self.system == 'windows' else ':'
        path_dirs = current_path.split(path_separator)
        return str(directory) in path_dirs

    def add_to_current_session(self, directory: Path) -> bool:
        """Add directory to PATH for current session."""
        try:
            current_path = os.environ.get('PATH', '')
            path_separator = ';' if self.system == 'windows' else ':'
            
            if not self.is_in_path(directory):
                new_path = f"{directory}{path_separator}{current_path}"
                os.environ['PATH'] = new_path
                print(f"✓ Added to current session PATH: {directory}")
                return True
            else:
                print(f"✓ Already in PATH: {directory}")
                return True
        except Exception as e:
            print(f"✗ Failed to add to current session: {e}")
            return False

    def configure_path(self, auto_add: bool = False) -> bool:
        """Configure PATH for CodeSentinel commands."""
        if not self.scripts_dir:
            print("✗ Could not detect Python scripts directory")
            print("  CodeSentinel CLI commands may not work directly")
            print("  Use: python -c \"from codesentinel.cli import main; main()\" instead")
            return False

        print(f"Found Python scripts directory: {self.scripts_dir}")

        if self.is_in_path(self.scripts_dir):
            print("✓ Scripts directory already in PATH")
            return True

        # Add to current session
        if auto_add or self.prompt_add_to_session():
            if self.add_to_current_session(self.scripts_dir):
                print("\nTesting CLI commands...")
                if self.test_cli_commands():
                    print("✓ CLI commands working!")
                else:
                    print("⚠ CLI commands not working yet")

        # Provide permanent setup instructions
        self.provide_permanent_setup_instructions()
        return True

    def prompt_add_to_session(self) -> bool:
        """Prompt user to add directory to current session PATH."""
        try:
            response = input(f"Add {self.scripts_dir} to current session PATH? (Y/n): ").strip().lower()
            return response in ['', 'y', 'yes']
        except (KeyboardInterrupt, EOFError):
            return False

    def test_cli_commands(self) -> bool:
        """Test if CodeSentinel CLI commands work."""
        try:
            # Test if codesentinel command is available
            result = subprocess.run(['codesentinel', '--help'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except Exception:
            return False

    def provide_permanent_setup_instructions(self):
        """Provide platform-specific instructions for permanent PATH setup."""
        print(f"\n{'='*60}")
        print("PERMANENT PATH SETUP INSTRUCTIONS")
        print(f"{'='*60}")
        
        if self.system == "windows":
            print("\nWindows - Choose one method:")
            print("\n1. PowerShell Profile (Recommended):")
            print("   notepad $PROFILE")
            print(f"   Add: $env:PATH += \";{self.scripts_dir}\"")
            
            print("\n2. System Environment Variables:")
            print("   - Press Win+R, type 'sysdm.cpl', press Enter")
            print("   - Click 'Environment Variables'")
            print("   - Edit 'Path' in User variables")
            print(f"   - Add: {self.scripts_dir}")
            
            print("\n3. Command Prompt startup:")
            print("   Create a batch file with:")
            print(f"   set PATH=%PATH%;{self.scripts_dir}")
            
        elif self.system == "darwin":  # macOS
            print("\nmacOS:")
            print("Add to ~/.zshrc (or ~/.bash_profile if using bash):")
            print(f"echo 'export PATH=\"{self.scripts_dir}:$PATH\"' >> ~/.zshrc")
            print("source ~/.zshrc")
            
        else:  # Linux and other Unix-like
            print("\nLinux/Unix:")
            print("Add to ~/.bashrc or ~/.profile:")
            print(f"echo 'export PATH=\"{self.scripts_dir}:$PATH\"' >> ~/.bashrc")
            print("source ~/.bashrc")
        
        print(f"\n{'='*60}")
        print("After setting up PATH permanently:")
        print("1. Restart your terminal")
        print("2. Test: codesentinel --help")
        print("3. Test: codesentinel-setup --help")
        print(f"{'='*60}")

    def show_alternative_commands(self):
        """Show alternative ways to run CodeSentinel if PATH isn't configured."""
        print("\nAlternative ways to run CodeSentinel commands:")
        print("\n1. Direct Python execution:")
        print("   python -c \"from codesentinel.cli import main; main()\" --help")
        print("   python -c \"from tools.codesentinel.setup_wizard import main; main()\"")
        print("   python -c \"from tools.codesentinel.gui_setup_wizard import main; main()\"")
        
        print("\n2. Script execution:")
        print("   python tools/codesentinel/scheduler.py --help")
        print("   python tools/codesentinel/alert_system.py --help")
        
        if self.scripts_dir and self.scripts_dir.exists():
            print(f"\n3. Full path execution:")
            print(f"   {self.scripts_dir / 'codesentinel'} --help")
            print(f"   {self.scripts_dir / 'codesentinel-setup'} --help")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Configure PATH for CodeSentinel CLI commands"
    )
    parser.add_argument(
        '--auto', '-a',
        action='store_true',
        help='Automatically add to current session without prompting'
    )
    parser.add_argument(
        '--test-only', '-t',
        action='store_true',
        help='Only test if commands work, don\'t configure'
    )
    parser.add_argument(
        '--show-alternatives',
        action='store_true',
        help='Show alternative ways to run commands'
    )
    
    args = parser.parse_args()
    
    configurator = PathConfigurator()
    
    if args.show_alternatives:
        configurator.show_alternative_commands()
        return
    
    if args.test_only:
        if configurator.test_cli_commands():
            print("✓ CodeSentinel CLI commands are working!")
        else:
            print("✗ CodeSentinel CLI commands not available")
            configurator.show_alternative_commands()
        return
    
    print("CodeSentinel PATH Configuration")
    print("=" * 40)
    
    success = configurator.configure_path(auto_add=args.auto)
    
    if not success:
        configurator.show_alternative_commands()


if __name__ == "__main__":
    main()