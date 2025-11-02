#!/usr/bin/env python3
"""
CodeSentinel Standalone Installer

This is a standalone installer that downloads and installs CodeSentinel
without requiring the source code to be present.

Usage: python install_codesentinel.py

Created by: joediggidyyy
Architecture: SECURITY > EFFICIENCY > MINIMALISM
"""

import sys
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import tempfile
import zipfile
import urllib.request
import os
from pathlib import Path

class CodeSentinelInstaller:
    """Standalone CodeSentinel installer."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CodeSentinel Installer")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        
        # Center the window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (700 // 2)
        y = (self.root.winfo_screenheight() // 2) - (600 // 2)
        self.root.geometry(f"700x600+{x}+{y}")
        
        self.setup_ui()
        
    def setup_ui(self):
        """Create the installer UI."""
        # Header
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill="x", padx=20, pady=20)
        
        title_label = ttk.Label(
            header_frame, 
            text="🛡️ CodeSentinel Installer",
            font=("Segoe UI", 18, "bold")
        )
        title_label.pack()
        
        subtitle_label = ttk.Label(
            header_frame,
            text="Security-First Automated Maintenance and Monitoring",
            font=("Segoe UI", 11)
        )
        subtitle_label.pack(pady=(5, 0))
        
        # Installation options
        options_frame = ttk.LabelFrame(self.root, text="Installation Options", padding=15)
        options_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        self.install_mode = tk.StringVar(value="dependencies")
        
        # Option 1: Dependencies only (current situation)
        deps_radio = ttk.Radiobutton(
            options_frame,
            text="Install Dependencies Only (PyYAML, keyring, cryptography)",
            variable=self.install_mode,
            value="dependencies"
        )
        deps_radio.pack(anchor="w", pady=2)
        
        deps_info = ttk.Label(
            options_frame,
            text="Use this if you already have CodeSentinel source code",
            font=("Segoe UI", 9),
            foreground="gray"
        )
        deps_info.pack(anchor="w", padx=20, pady=(0, 10))
        
        # Option 2: Full installation (future)
        full_radio = ttk.Radiobutton(
            options_frame,
            text="Full Installation (Download and Install CodeSentinel)",
            variable=self.install_mode,
            value="full",
            state="disabled"
        )
        full_radio.pack(anchor="w", pady=2)
        
        full_info = ttk.Label(
            options_frame,
            text="Coming soon - will download from GitHub/PyPI",
            font=("Segoe UI", 9),
            foreground="gray"
        )
        full_info.pack(anchor="w", padx=20)
        
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
            height=12,
            font=("Consolas", 9),
            wrap=tk.WORD
        )
        self.log_text.pack(fill="both", expand=True)
        
        # Buttons
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill="x", padx=20, pady=20)
        
        self.install_button = ttk.Button(
            button_frame,
            text="🚀 Start Installation",
            command=self.start_installation
        )
        self.install_button.pack(side="left")
        
        self.close_button = ttk.Button(
            button_frame,
            text="Close",
            command=self.root.destroy,
            state="disabled"
        )
        self.close_button.pack(side="right")
        
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
        self.install_button.config(state="disabled")
        self.progress_bar.start()
        
        # Start installation in a separate thread
        thread = threading.Thread(target=self.run_installation)
        thread.daemon = True
        thread.start()
        
    def run_installation(self):
        """Run the installation process."""
        try:
            mode = self.install_mode.get()
            
            self.log_message("🛡️ CodeSentinel Standalone Installer")
            self.log_message("=" * 40)
            
            # Check Python version
            self.update_status("Checking Python version...")
            self.log_message("\n🐍 Checking Python version...")
            
            python_version = sys.version_info
            if python_version >= (3, 7):
                self.log_message(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro} - Compatible")
            else:
                self.log_message(f"❌ Python {python_version.major}.{python_version.minor}.{python_version.micro} - Requires Python 3.7+")
                self.installation_failed("Python 3.7+ required")
                return
            
            if mode == "dependencies":
                self.install_dependencies_only()
            elif mode == "full":
                self.install_full_codesentinel()
                
        except Exception as e:
            self.log_message(f"\n💥 Installation error: {e}")
            self.installation_failed(str(e))
    
    def install_dependencies_only(self):
        """Install only the required dependencies."""
        self.update_status("Installing dependencies...")
        self.log_message("\n📦 Installing CodeSentinel dependencies...")
        
        required_packages = ["PyYAML", "keyring", "cryptography"]
        
        for package in required_packages:
            if not self.install_package(package):
                self.installation_failed(f"Failed to install {package}")
                return
        
        self.installation_complete_dependencies()
    
    def install_full_codesentinel(self):
        """Full CodeSentinel installation (future feature)."""
        self.log_message("\n🚧 Full installation not yet implemented")
        self.log_message("This feature will download CodeSentinel from GitHub/PyPI")
        self.installation_failed("Full installation coming soon")
    
    def install_package(self, package):
        """Install a single package."""
        self.log_message(f"🔧 Installing {package}...")
        
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", package
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            self.log_message(f"✅ {package} installed successfully")
            return True
        else:
            self.log_message(f"❌ Failed to install {package}")
            self.log_message(f"Error: {result.stderr}")
            return False
    
    def installation_complete_dependencies(self):
        """Handle successful dependency installation."""
        self.progress_bar.stop()
        self.update_status("Dependencies installed!")
        
        self.log_message("\n🎉 Dependencies installed successfully!")
        self.log_message("\nNext steps:")
        self.log_message("1. Download CodeSentinel source code if you haven't already")
        self.log_message("2. Extract to a directory")
        self.log_message("3. Navigate to that directory")
        self.log_message("4. Run: python launch.py")
        self.log_message("\nOr if CodeSentinel is installed as a package:")
        self.log_message("   codesentinel-setup")
        
        self.install_button.config(text="✅ Complete", state="disabled")
        self.close_button.config(state="normal")
        
    def installation_failed(self, error):
        """Handle installation failure."""
        self.progress_bar.stop()
        self.update_status(f"Installation failed: {error}")
        
        self.install_button.config(text="❌ Failed", state="disabled")
        self.close_button.config(state="normal")

def main():
    """Main entry point."""
    print("🛡️ CodeSentinel Standalone Installer")
    print("=" * 35)
    print("Starting installation wizard...")
    
    try:
        app = CodeSentinelInstaller()
        app.root.mainloop()
    except KeyboardInterrupt:
        print("\n❌ Installation cancelled by user")
        return 1
    except Exception as e:
        print(f"❌ Installation failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())