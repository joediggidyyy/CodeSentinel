#!/usr/bin/env python3
"""
CodeSentinel Setup Wizard

This is the main installation entry point for new users.
Simply run: python setup_wizard.py

Created by: joediggidyyy
Architecture: SECURITY > EFFICIENCY > MINIMALISM
"""

import sys
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import os
from pathlib import Path
import shutil

class CodeSentinelSetupWizard:
    """Main setup wizard for CodeSentinel installation."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CodeSentinel Setup Wizard")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        
        # Center the window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (700 // 2)
        y = (self.root.winfo_screenheight() // 2) - (600 // 2)
        self.root.geometry(f"700x600+{x}+{y}")
        
        # Set icon and theme
        try:
            self.root.configure(bg='#f0f0f0')
        except:
            pass
            
        self.setup_ui()
        
    def setup_ui(self):
        """Create the setup wizard UI."""
        # Header
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill="x", padx=20, pady=20)
        
        title_label = ttk.Label(
            header_frame, 
            text="CodeSentinel Setup Wizard",
            font=("Segoe UI", 18, "bold")
        )
        title_label.pack()
        
        subtitle_label = ttk.Label(
            header_frame,
            text="Security-First Automated Maintenance and Monitoring",
            font=("Segoe UI", 11)
        )
        subtitle_label.pack(pady=(5, 0))
        
        version_label = ttk.Label(
            header_frame,
            text="Architecture: SECURITY > EFFICIENCY > MINIMALISM",
            font=("Segoe UI", 9),
            foreground="gray"
        )
        version_label.pack(pady=(5, 0))
        
        # Welcome message
        welcome_frame = ttk.LabelFrame(self.root, text="Welcome", padding=15)
        welcome_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        welcome_text = ttk.Label(
            welcome_frame,
            text="Welcome to CodeSentinel! This wizard will:\n\n"
                 "1. Check your system requirements\n"
                 "2. Install required dependencies (PyYAML, keyring, cryptography)\n"
                 "3. Install CodeSentinel package\n"
                 "4. Launch the project configuration wizard\n\n"
                 "This wizard will automatically verify and install prerequisites. No action is required.",
            font=("Segoe UI", 10)
        )
        welcome_text.pack()
        
        # Progress section
        progress_frame = ttk.LabelFrame(self.root, text="Installation Progress", padding=15)
        progress_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        self.progress_bar = ttk.Progressbar(
            progress_frame, 
            mode="indeterminate",
            length=400
        )
        self.progress_bar.pack(pady=(0, 10))
        
        self.status_label = ttk.Label(
            progress_frame,
            text="Ready to install",
            font=("Segoe UI", 10)
        )
        self.status_label.pack(pady=(0, 10))
        
        # Log area
        log_frame = ttk.Frame(progress_frame)
        log_frame.pack(fill="both", expand=True)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=15,
            font=("Consolas", 9),
            wrap=tk.WORD
        )
        self.log_text.pack(fill="both", expand=True)
        
        # Buttons (no Start button; flow is automatic)
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill="x", padx=20, pady=20)
        
        self.close_button = ttk.Button(
            button_frame,
            text="Close",
            command=self.root.destroy,
            state="disabled"
        )
        self.close_button.pack(side="right")
        
        self.next_button = ttk.Button(
            button_frame,
            text="Launch Project Setup",
            command=self.launch_project_setup,
            state="disabled"
        )
        self.next_button.pack(side="right", padx=(0, 10))

        # Auto-start after UI renders
        self.root.after(300, self.start_installation)
        
    def log_message(self, message):
        """Add a message to the log."""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def update_status(self, status):
        """Update the status label."""
        self.status_label.config(text=status)
        self.root.update_idletasks()
        
    def start_installation(self):
        """Start the installation process."""
        # Ensure progress bar runs (no manual buttons in automatic flow)
        self.progress_bar.start()
        
        # Start installation in a separate thread
        thread = threading.Thread(target=self.run_installation)
        thread.daemon = True
        thread.start()
        
    def run_installation(self):
        """Run the complete installation process."""
        try:
            self.log_message("CodeSentinel Setup Wizard Started")
            self.log_message("=" * 50)
            
            # Step 1: Check Python version
            self.update_status("Checking Python version...")
            self.log_message("\nChecking Python version...")
            
            python_version = sys.version_info
            if python_version >= (3, 7):
                self.log_message(f"✓ Python {python_version.major}.{python_version.minor}.{python_version.micro} - Compatible")
            else:
                self.log_message(f"✗ Python {python_version.major}.{python_version.minor}.{python_version.micro} - Requires Python 3.7+")
                self.installation_failed("Python 3.7+ required")
                return
            
            # Step 2: Check tkinter
            self.update_status("Checking GUI support...")
            self.log_message("\nChecking GUI support...")
            try:
                import tkinter
                self.log_message("✓ tkinter - Available")
            except ImportError:
                self.log_message("✗ tkinter - Missing (required for GUI)")
                
            # Step 3: Install dependencies (skip if already satisfied)
            self.update_status("Installing dependencies...")
            self.log_message("\nInstalling required dependencies...")
            
            required_packages = [
                ("PyYAML", "yaml"),
                ("keyring", "keyring"),
                ("cryptography", "cryptography")
            ]
            all_present = True
            import importlib.util as _ilutil
            for pkg_name, import_name in required_packages:
                if _ilutil.find_spec(import_name) is None:
                    all_present = False
                    if not self.install_package(pkg_name):
                        self.installation_failed(f"Failed to install {pkg_name}")
                        return
                else:
                    self.log_message(f"✓ {pkg_name} already installed")
            
            # Step 4: Install CodeSentinel package (skip if already installed)
            self.update_status("Installing CodeSentinel...")
            self.log_message("\nInstalling CodeSentinel package...")
            
            # Check if we're in a CodeSentinel source directory
            current_dir = Path(__file__).parent
            result = None
            try:
                import codesentinel  # type: ignore
                self.log_message("✓ CodeSentinel already installed")
            except Exception:
                if (current_dir / "setup.py").exists() and (current_dir / "codesentinel").exists():
                    # Development installation from source
                    self.log_message("Found CodeSentinel source directory - installing from source...")
                    result = subprocess.run([
                        sys.executable, "-m", "pip", "install", "-e", "."
                    ], capture_output=True, text=True, cwd=current_dir)
                else:
                    # Production installation from PyPI (when available)
                    self.log_message("Installing CodeSentinel from PyPI...")
                    result = subprocess.run([
                        sys.executable, "-m", "pip", "install", "codesentinel"
                    ], capture_output=True, text=True)
            
            if result is not None:
                if result.returncode == 0:
                    self.log_message("✓ CodeSentinel package installed successfully")
                else:
                    self.log_message(f"✗ Failed to install CodeSentinel package")
                    self.log_message(f"Error: {result.stderr}")
                    
                    # If PyPI installation failed, suggest manual installation
                    if not (current_dir / "setup.py").exists():
                        self.log_message("\nSuggestion:")
                        self.log_message("  1. Download the full CodeSentinel source code")
                        self.log_message("  2. Extract to a directory")
                        self.log_message("  3. Run setup_wizard.py from that directory")
                    
                    self.installation_failed("CodeSentinel package installation failed")
                    return
            
            # Step 5: Verify installation
            self.update_status("Verifying installation...")
            self.log_message("\nVerifying installation...")
            
            try:
                # Test entry points
                result = subprocess.run([
                    sys.executable, "-c", "import codesentinel; print('Package imported successfully')"
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    self.log_message("✓ CodeSentinel package verification successful")
                else:
                    self.log_message("✗ Package verification failed")
                    self.installation_failed("Package verification failed")
                    return
                
            except Exception as e:
                self.log_message(f"✗ Verification error: {e}")
                self.installation_failed("Verification failed")
                return
            
            # Success or already satisfied
            self.installation_complete()
            
        except Exception as e:
            self.log_message(f"\nInstallation error: {e}")
            self.installation_failed(str(e))
    
    def install_package(self, package):
        """Install a single package."""
        self.log_message(f"Installing {package}...")
        
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", package
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            self.log_message(f"✓ {package} installed successfully")
            return True
        else:
            self.log_message(f"✗ Failed to install {package}")
            self.log_message(f"Error: {result.stderr}")
            return False
    
    def installation_complete(self):
        """Handle successful installation."""
        self.progress_bar.stop()
        self.update_status("Installation complete!")
        
        self.log_message("\nInstallation completed successfully!")
        self.log_message("\nCodeSentinel is now installed and ready to use.")
        self.log_message("\nAvailable commands:")
        self.log_message("  codesentinel-setup     - Project setup wizard")
        self.log_message("  codesentinel           - Main CLI interface")
        self.log_message("\nNext steps:")
        self.log_message("  • You may close this window.")
        self.log_message("  • Launching the CodeSentinel project setup in a moment...")
        
        self.next_button.config(state="normal")
        self.close_button.config(state="normal")

        # Automatically advance to project setup shortly after success
        # Give the UI a brief moment so users can read the success line
        self.root.after(1500, self.launch_project_setup)
        
    def installation_failed(self, error):
        """Handle installation failure."""
        self.progress_bar.stop()
        self.update_status(f"Installation failed: {error}")
        
        self.close_button.config(state="normal")
        
    def launch_project_setup(self):
        """Launch the project setup wizard."""
        try:
            self.log_message("\nLaunching project setup wizard...")

            # Resolve best available setup command
            cmd, desc = self._resolve_setup_command()
            if not cmd:
                raise RuntimeError(
                    "No setup command found. Try running 'codesentinel-setup' or 'python -m codesentinel.cli setup' manually."
                )

            self.log_message(f"Using: {desc}")
            # Launch detached so the setup can continue even if this window closes
            subprocess.Popen(cmd)

            # Close this wizard after launching
            self.root.destroy()
            
        except Exception as e:
            messagebox.showerror(
                "Launch Error",
                f"Could not launch project setup: {e}\n\n"
                "You can run it manually:\n"
                "  - codesentinel-setup\n"
                "  - codesentinel-setup-gui\n"
                "  - python -m codesentinel.cli setup --gui"
            )

    def _resolve_setup_command(self):
        """Return (cmd_list, description) for the best available setup entry.

        Preference order:
        1) codesentinel-setup-gui (if on PATH)
        2) codesentinel-setup (CLI)
        3) python -m codesentinel.cli setup --gui
        4) python -m codesentinel.cli setup
        5) python launch.py (repo-local fallback)
        """
        # 1) Prefer dedicated GUI entry point if present
        if shutil.which("codesentinel-setup-gui"):
            return (["codesentinel-setup-gui"], "codesentinel-setup-gui (GUI)")

        # 2) Fallback to generic setup entry point
        if shutil.which("codesentinel-setup"):
            return (["codesentinel-setup"], "codesentinel-setup (CLI)")

        # 3) Module invocation (GUI flag)
        # Even if GUI isn't implemented, attempting this keeps behavior consistent
        returncode = None
        try:
            # Quick import probe to see if module exists
            __import__("codesentinel.cli")
            return ([sys.executable, "-m", "codesentinel.cli", "setup", "--gui"],
                    "python -m codesentinel.cli setup --gui")
        except Exception:
            returncode = 1

        # 4) Non-GUI module invocation
        try:
            __import__("codesentinel.cli")
            return ([sys.executable, "-m", "codesentinel.cli", "setup"],
                    "python -m codesentinel.cli setup")
        except Exception:
            pass

        # 5) Repo-local launcher fallback (when running from source tree)
        current_dir = Path(__file__).parent
        launch_py = current_dir / "launch.py"
        if launch_py.exists():
            return ([sys.executable, str(launch_py)], "local launch.py")

        return (None, "")

def main():
    """Main entry point."""
    print("CodeSentinel Setup Wizard")
    print("=" * 30)
    print("Starting GUI installation wizard...")
    
    try:
        app = CodeSentinelSetupWizard()
        app.root.mainloop()
    except KeyboardInterrupt:
        print("\n✗ Setup cancelled by user")
        return 1
    except Exception as e:
        print(f"✗ Setup failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())