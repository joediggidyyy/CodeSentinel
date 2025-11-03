#!/usr/bin/env python3
"""
CodeSentinel GUI Setup Wizard
==============================

SECURITY > EFFICIENCY > MINIMALISM

Graphical setup wizard for CodeSentinel configuration and environment setup.
Provides a user-friendly interface for configuring CodeSentinel with pop-up dialogs.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from tkinter import simpledialog
import os
import sys
import json
import shutil
import platform
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import getpass
import urllib.request
import urllib.error
import threading
import queue

# Import the backend wizard
from .setup_wizard import CodeSentinelSetupWizard


class GUISetupWizard:
    """GUI-based setup wizard for CodeSentinel configuration."""

    def __init__(self, install_location: Optional[Path] = None):
        # Initialize the backend wizard logic
        self.backend_wizard = CodeSentinelSetupWizard(install_location)

        # GUI setup
        self.root = tk.Tk()
        self.root.title("CodeSentinel Setup Wizard")
        self.root.geometry("800x700")
        self.root.resizable(True, True)

        # Center the window
        self.center_window(self.root, 800, 700)

        # Style configuration
        self.style = ttk.Style()
        self.style.configure('Wizard.TFrame', padding=20)
        self.style.configure('Step.TLabel', font=('Arial', 12, 'bold'))
        self.style.configure('Title.TLabel', font=('Arial', 16, 'bold'))

        # Progress tracking
        self.current_step = 0
        self.steps = [
            "Welcome",
            "Installation Location",
            "System Requirements",
            "Environment Setup",
            "Alert System",
            "Code Formatting",
            "GitHub Integration",
            "IDE Integration",
            "Optional Features",
            "Summary"
        ]

        # Configuration storage
        self.config = {
            'install_location': str(self.backend_wizard.install_location),
            'alerts': {},
            'github': {},
            'ide': {},
            'optional': {}
        }

        # Initialize ALL GUI state variables at once to prevent recreation
        self.init_all_gui_variables()

        # Create the main interface
        self.create_main_interface()

    def init_all_gui_variables(self):
        """Initialize ALL GUI variables at once to ensure they persist across navigation."""
        # Step 2: Installation location variables
        self.location_var = tk.StringVar(value=str(self.backend_wizard.install_location))
        self.mode_var = tk.StringVar(value="repository" if self.backend_wizard.is_git_repo else "standalone")
        
        # Step 5: Alert system variables
        self.console_var = tk.BooleanVar(value=True)
        self.file_var = tk.BooleanVar(value=True)
        self.email_var = tk.BooleanVar(value=False)
        self.slack_var = tk.BooleanVar(value=False)
        self.security_var = tk.BooleanVar(value=True)
        self.task_var = tk.BooleanVar(value=True)
        self.dependency_var = tk.BooleanVar(value=True)
        
        # Email configuration variables
        self.smtp_server_var = tk.StringVar(value="smtp.gmail.com")
        self.smtp_port_var = tk.StringVar(value="587")
        self.email_user_var = tk.StringVar(value="")
        self.email_pass_var = tk.StringVar(value="")
        self.from_email_var = tk.StringVar(value="")
        
        # Slack configuration variables
        self.webhook_url_var = tk.StringVar(value="")
        self.slack_channel_var = tk.StringVar(value="#maintenance-alerts")
        self.slack_username_var = tk.StringVar(value="CodeSentinel")
        
        # Step 6: Code formatting variables - Comprehensive formatting configuration
        self.format_preset_var = tk.StringVar(value="house_style")  # Default to house style
        
        # Basic formatting
        self.line_length_var = tk.StringVar(value="88")
        self.indent_size_var = tk.StringVar(value="4") 
        self.quote_style_var = tk.StringVar(value="double")
        self.trailing_commas_var = tk.BooleanVar(value=True)
        
        # Import and organization
        self.format_imports_var = tk.BooleanVar(value=True)
        self.import_sort_style_var = tk.StringVar(value="isort")  # isort, black, none
        self.group_imports_var = tk.BooleanVar(value=True)
        
        # String and literal formatting
        self.format_strings_var = tk.BooleanVar(value=False)
        self.normalize_quotes_var = tk.BooleanVar(value=True)
        self.multiline_string_style_var = tk.StringVar(value="preserve")  # preserve, format, normalize
        
        # Code structure
        self.blank_lines_class_var = tk.StringVar(value="2")
        self.blank_lines_function_var = tk.StringVar(value="1")
        self.blank_lines_method_var = tk.StringVar(value="1")
        
        # Expression formatting
        self.format_comprehensions_var = tk.BooleanVar(value=True)
        self.format_lambdas_var = tk.BooleanVar(value=False)
        self.split_complex_expressions_var = tk.BooleanVar(value=True)
        
        # Comment and docstring formatting
        self.format_comments_var = tk.BooleanVar(value=False)
        self.docstring_style_var = tk.StringVar(value="google")  # google, numpy, sphinx, pep257
        self.preserve_docstring_formatting_var = tk.BooleanVar(value=True)
        
        # Advanced formatting options
        self.aggressive_formatting_var = tk.BooleanVar(value=False)
        self.experimental_features_var = tk.BooleanVar(value=False)
        self.skip_magic_methods_var = tk.BooleanVar(value=True)
        
        # Step 7: GitHub integration variables
        self.copilot_var = tk.BooleanVar(value=True)
        self.api_var = tk.BooleanVar(value=False)
        self.repo_var = tk.BooleanVar(value=True)
        
        # Step 6: Repository setup variables (CRITICAL FIX: Initialize here to persist state)
        self.repo_scenario_var = tk.StringVar(value="local_to_existing")
        self.github_url_var = tk.StringVar(value="")
        self.merge_strategy_var = tk.StringVar(value="merge")
        self.github_token_var = tk.StringVar(value="")
        
        # Step 9: Optional features variables
        self.cron_var = tk.BooleanVar(value=False)
        self.git_hooks_var = tk.BooleanVar(value=True)  # Recommended by default
        self.ci_cd_var = tk.BooleanVar(value=False)
        
        # Validation flags for navigation locking
        self.email_validated = False
        self.slack_validated = True  # Slack doesn't require complex validation
        self.github_api_validated = False
        
        # Add trace callbacks to reset validation when checkboxes change
        self.email_var.trace('w', self.on_email_checkbox_change)
        self.api_var.trace('w', self.on_api_checkbox_change)

    def get_or_create_var(self, var_name, var_type, default_value):
        """Get existing variable or create it with default value if it doesn't exist."""
        if not hasattr(self, var_name):
            setattr(self, var_name, var_type(value=default_value))
        return getattr(self, var_name)

    def center_window(self, window, width, height):
        """Center a window on the screen."""
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        window.geometry(f'{width}x{height}+{x}+{y}')

    def create_main_interface(self):
        """Create the main wizard interface."""
        # Main container
        main_frame = ttk.Frame(self.root, style='Wizard.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(main_frame, text="CodeSentinel Setup Wizard",
                               style='Title.TLabel')
        title_label.pack(pady=(0, 20))

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var,
                                           maximum=len(self.steps))
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))

        # Step indicator
        self.step_label = ttk.Label(main_frame, text="", style='Step.TLabel')
        self.step_label.pack(pady=(0, 20))

        # Content frame with scrolling
        content_container = ttk.Frame(main_frame)
        content_container.pack(fill=tk.BOTH, expand=True)
        
        # Create canvas and scrollbar for scrolling
        self.canvas = tk.Canvas(content_container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(content_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Content frame is now the scrollable frame
        self.content_frame = self.scrollable_frame
        
        # Bind mousewheel to canvas
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Navigation buttons
        nav_frame = ttk.Frame(main_frame)
        nav_frame.pack(fill=tk.X, pady=(20, 0))

        self.back_button = ttk.Button(nav_frame, text="Back", command=self.go_back,
                                     state=tk.DISABLED)
        self.back_button.pack(side=tk.LEFT)

        self.next_button = ttk.Button(nav_frame, text="Next", command=self.go_next)
        self.next_button.pack(side=tk.RIGHT)

        self.cancel_button = ttk.Button(nav_frame, text="Cancel",
                                       command=self.cancel_wizard)
        self.cancel_button.pack(side=tk.RIGHT, padx=(0, 10))

        # TESTING: Add reset button for development/testing
        self.reset_button = ttk.Button(nav_frame, text="🔄 Reset", 
                                      command=self.reset_wizard_state)
        self.reset_button.pack(side=tk.LEFT, padx=(10, 0))

        # Initialize first step
        self.show_step(0)

    def show_step(self, step_index):
        """Show the specified step."""
        try:
            # Validate step index
            if not (0 <= step_index < len(self.steps)):
                print(f"Invalid step index: {step_index}")
                return
                
            self.current_step = step_index
            self.step_label.config(text=f"Step {step_index + 1} of {len(self.steps)}: {self.steps[step_index]}")
            self.progress_var.set(step_index + 1)

            # Enhanced widget cleanup to prevent naming conflicts
            self.cleanup_content_frame()

            # Show appropriate step content
            step_methods = [
                self.show_welcome,
                self.show_install_location,
                self.show_system_requirements,
                self.show_environment_setup,
                self.show_alert_system,
                self.show_code_formatting,
                self.show_github_integration,
                self.show_ide_integration,
                self.show_optional_features,
                self.show_summary
            ]

            # Call the step method
            step_methods[step_index]()

            # Update navigation buttons with validation checks
            self.update_navigation_buttons(step_index)
            
            # Force canvas scroll region update to ensure content is visible
            self.update_canvas_scroll_region()
                
        except Exception as e:
            print(f"Error showing step {step_index}: {e}")
            self.show_error_step(f"Failed to show step {step_index + 1}: {str(e)}")
            import traceback
            traceback.print_exc()

    def update_canvas_scroll_region(self):
        """Force update of canvas scroll region to make content visible."""
        try:
            # Force the scrollable frame to update its layout
            self.scrollable_frame.update_idletasks()
            
            # Update the canvas scroll region
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            
            # Ensure the canvas is at the top
            self.canvas.yview_moveto(0)
        except Exception as e:
            print(f"Warning: Could not update canvas scroll region: {e}")

    def update_navigation_buttons(self, step_index):
        """Update navigation buttons with validation checks."""
        # Back button is always enabled (except on first step)
        self.back_button.config(state=tk.NORMAL if step_index > 0 else tk.DISABLED)
        
        # Check if navigation should be locked
        navigation_locked, lock_reason = self.check_navigation_lock(step_index)
        
        if step_index == len(self.steps) - 1:
            # Final step - Finish button
            if navigation_locked:
                self.next_button.config(text=f"⚠️ {lock_reason}", state=tk.DISABLED)
            else:
                self.next_button.config(text="Finish", command=self.finish_wizard, state=tk.NORMAL)
        else:
            # Regular next button
            if navigation_locked:
                self.next_button.config(text=f"⚠️ {lock_reason}", state=tk.DISABLED)
            else:
                self.next_button.config(text="Next", command=self.go_next, state=tk.NORMAL)

    def check_navigation_lock(self, step_index):
        """Check if navigation should be locked due to required validations."""
        # Step 5 (index 4) - Alert System: Check email and other integrations
        if step_index == 4:
            return self.check_alert_system_validation()
        
        # Step 7 (index 6) - GitHub Integration: Check GitHub API validation  
        elif step_index == 6:
            return self.check_github_integration_validation()
        
        # No locks for other steps
        return False, ""

    def check_alert_system_validation(self):
        """Check if alert system requires validation before proceeding."""
        # Check if email is selected but not validated
        if hasattr(self, 'email_var') and self.email_var.get():
            if not hasattr(self, 'email_validated') or not self.email_validated:
                return True, "Validate email settings"
        
        # Check if Slack is selected but not configured
        if hasattr(self, 'slack_var') and self.slack_var.get():
            if not hasattr(self, 'slack_validated') or not self.slack_validated:
                return True, "Configure Slack settings"
        
        return False, ""

    def check_github_integration_validation(self):
        """Check if GitHub integration requires validation before proceeding."""
        # Check if GitHub API is selected but not validated
        if hasattr(self, 'api_var') and self.api_var.get():
            if not hasattr(self, 'github_api_validated') or not self.github_api_validated:
                return True, "Validate GitHub API"
        
        return False, ""

    def on_email_checkbox_change(self, *args):
        """Reset email validation when checkbox state changes."""
        if not self.email_var.get():
            # If unchecked, mark as validated (no validation needed)
            self.email_validated = True
        else:
            # If checked, require validation
            self.email_validated = False
        
        # Update navigation buttons using root.after to prevent timing conflicts
        self.root.after(10, lambda: self.update_navigation_buttons(self.current_step))

    def on_api_checkbox_change(self, *args):
        """Handle API checkbox state changes."""
        if not self.api_var.get():
            # If unchecked, mark as validated (no validation needed)
            self.github_api_validated = True
        else:
            # If checked and we don't have validation yet, require it
            # But preserve existing validation state if already validated
            if not getattr(self, 'github_api_validated', False):
                self.github_api_validated = False
        
        # Update navigation buttons using root.after to prevent timing conflicts
        self.root.after(10, lambda: self.update_navigation_buttons(self.current_step))

    def show_welcome(self):
        """Show welcome screen."""
        frame = ttk.Frame(self.content_frame)
        frame.pack(fill=tk.BOTH, expand=True)

        welcome_text = """
Welcome to CodeSentinel Setup Wizard!

This wizard will guide you through configuring CodeSentinel for your environment.

CodeSentinel provides:
• Automated maintenance and security monitoring
• Alert system for critical issues
• GitHub integration with Copilot support
• IDE integration for seamless development

Click Next to begin the setup process.
        """

        text_widget = scrolledtext.ScrolledText(frame, wrap=tk.WORD, height=15)
        text_widget.insert(tk.END, welcome_text.strip())
        text_widget.config(state=tk.DISABLED)
        text_widget.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        # Repository info
        info_frame = ttk.LabelFrame(frame, text="Environment Information")
        info_frame.pack(fill=tk.X, pady=(0, 20))

        ttk.Label(info_frame, text=f"Current Directory: {Path.cwd()}").pack(anchor=tk.W, pady=2)
        ttk.Label(info_frame, text=f"Install Location: {self.backend_wizard.install_location}").pack(anchor=tk.W, pady=2)

        if self.backend_wizard.is_git_repo:
            ttk.Label(info_frame, text=f"Git Repository: {self.backend_wizard.git_root}").pack(anchor=tk.W, pady=2)
            ttk.Label(info_frame, text="Mode: Repository Integration").pack(anchor=tk.W, pady=2)
        else:
            ttk.Label(info_frame, text="Mode: Standalone Installation").pack(anchor=tk.W, pady=2)

    def show_install_location(self):
        """Show installation location configuration."""
        frame = ttk.Frame(self.content_frame)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Installation Location",
                 font=('Arial', 12, 'bold')).pack(pady=(0, 10))

        # Current location info
        info_text = f"Current location: {self.backend_wizard.install_location}\n"
        
        if self.backend_wizard.is_git_repo:
            info_text += f"✓ Git repository detected: {self.backend_wizard.git_root}\n"
            info_text += "Repository mode integrates CodeSentinel into your project."
        else:
            info_text += "Standalone mode installs CodeSentinel independently."

        ttk.Label(frame, text=info_text.strip()).pack(pady=(0, 15))

        # Quick repository selection (if repositories found)
        nearby_repos = self.find_nearby_repositories()
        if nearby_repos:
            self.show_repository_suggestions(frame, nearby_repos)

        # Manual location selection
        location_frame = ttk.LabelFrame(frame, text="Custom Installation Directory")
        location_frame.pack(fill=tk.X, pady=(10, 0))

        entry_frame = ttk.Frame(location_frame)
        entry_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(entry_frame, text="Directory:").grid(row=0, column=0, sticky=tk.W)
        # Variables already initialized in init_all_gui_variables()
        location_entry = ttk.Entry(entry_frame, textvariable=self.location_var, width=45)
        location_entry.grid(row=0, column=1, padx=(10, 5), sticky=tk.EW)

        ttk.Button(entry_frame, text="Browse...",
                  command=self.browse_location).grid(row=0, column=2, padx=(5, 0))

        entry_frame.columnconfigure(1, weight=1)

        # Mode selection
        mode_frame = ttk.LabelFrame(frame, text="Installation Mode")
        mode_frame.pack(fill=tk.X, pady=(15, 0))

        # Variables already initialized in init_all_gui_variables()
        ttk.Radiobutton(mode_frame, text="Repository Integration (recommended for git projects)",
                       variable=self.mode_var, value="repository").pack(anchor=tk.W, pady=5, padx=10)
        ttk.Radiobutton(mode_frame, text="Standalone Installation",
                       variable=self.mode_var, value="standalone").pack(anchor=tk.W, pady=5, padx=10)

    def find_nearby_repositories(self):
        """Find Git repositories in common locations."""
        import os
        from pathlib import Path
        
        repos = []
        search_paths = []
        
        # Add common development directories
        home = Path.home()
        current_parent = Path.cwd().parent
        
        common_dirs = [
            home / "Documents",
            home / "Projects", 
            home / "Development",
            home / "Code",
            home / "workspace",
            home / "src",
            home / "Desktop",
            current_parent,  # Parent of current directory
        ]
        
        # Add more search paths if they exist
        if current_parent != home:
            common_dirs.extend([
                current_parent.parent,  # Grandparent directory
                current_parent / "Projects",
                current_parent / "Code",
            ])
        
        # Only search existing directories
        search_paths = [path for path in common_dirs if path.exists() and path.is_dir()]
        
        # Limit search to avoid performance issues
        max_repos = 10
        max_depth = 3
        
        for search_path in search_paths:
            if len(repos) >= max_repos:
                break
                
            try:
                # Search for .git directories
                for root, dirs, files in os.walk(search_path):
                    # Limit search depth
                    level = root.replace(str(search_path), '').count(os.sep)
                    if level >= max_depth:
                        dirs[:] = []  # Don't recurse deeper
                        continue
                    
                    if '.git' in dirs:
                        repo_path = Path(root)
                        # Skip if it's the current directory or already added
                        if (repo_path.resolve() != Path.cwd().resolve() and 
                            not any(r['path'].resolve() == repo_path.resolve() for r in repos)):
                            repos.append({
                                'path': repo_path,
                                'name': repo_path.name,
                                'relative': self.get_relative_path_display(repo_path)
                            })
                            if len(repos) >= max_repos:
                                break
                    
                    # Skip hidden directories and common non-project dirs  
                    dirs[:] = [d for d in dirs if not d.startswith('.') and 
                              d.lower() not in ['node_modules', '__pycache__', 'venv', '.venv', 'env', 
                                               'target', 'build', 'dist', 'out', 'bin', 'obj']]
                              
            except (PermissionError, OSError):
                continue  # Skip directories we can't access
        
        # Sort by name for consistent display
        repos.sort(key=lambda x: x['name'].lower())
        return repos[:max_repos]

    def get_relative_path_display(self, path):
        """Get a user-friendly relative path display."""
        try:
            # Try to get relative path from current directory
            rel_from_cwd = path.relative_to(Path.cwd())
            if len(str(rel_from_cwd)) < len(str(path)):
                return f"./{rel_from_cwd}"
        except ValueError:
            pass
        
        try:
            # Try to get relative path from home directory
            rel_from_home = path.relative_to(Path.home())
            return f"~/{rel_from_home}"
        except ValueError:
            pass
        
        # Fallback to absolute path, but truncate if too long
        abs_path = str(path)
        if len(abs_path) > 50:
            return f"...{abs_path[-47:]}"
        return abs_path

    def show_repository_suggestions(self, parent_frame, repos):
        """Show repository suggestions for quick selection."""
        suggestions_frame = ttk.LabelFrame(parent_frame, text="� Detected Git Repositories")
        suggestions_frame.pack(fill=tk.X, pady=(0, 10))

        if not repos:
            ttk.Label(suggestions_frame, 
                     text="No Git repositories detected in common locations.\n"
                          "Use the custom directory option below to specify your project location.",
                     font=('Arial', 9), foreground='gray').pack(padx=10, pady=10)
            return

        ttk.Label(suggestions_frame, text="Quick select a repository to install CodeSentinel:",
                 font=('Arial', 9)).pack(anchor=tk.W, padx=10, pady=(10, 5))

        # Create a scrollable frame for repository buttons if many repos
        if len(repos) > 6:
            # Create canvas for scrolling
            canvas = tk.Canvas(suggestions_frame, height=120)
            scrollbar = ttk.Scrollbar(suggestions_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side="left", fill="both", expand=True, padx=10)
            scrollbar.pack(side="right", fill="y")
            
            repos_frame = scrollable_frame
        else:
            repos_frame = ttk.Frame(suggestions_frame)
            repos_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        # Display repositories in a grid (2 columns for better space usage)
        for i, repo in enumerate(repos):
            row = i // 2
            col = i % 2
            
            # Create button with repository info
            button_text = f"📂 {repo['name']}\n{repo['relative']}"
            repo_button = ttk.Button(
                repos_frame,
                text=button_text,
                command=lambda r=repo: self.select_repository(r['path']),
                width=30
            )
            repo_button.grid(row=row, column=col, padx=3, pady=2, sticky=tk.EW)
        
        # Configure grid weights for responsive layout
        repos_frame.columnconfigure(0, weight=1)
        repos_frame.columnconfigure(1, weight=1)

    def select_repository(self, repo_path):
        """Select a repository as the installation location."""
        self.location_var.set(str(repo_path))
        
        # Update mode to repository if selecting a git repo
        self.mode_var.set("repository")
        
        # Provide visual feedback
        # This could trigger a brief highlight or status message
        self.root.after(100, lambda: None)  # Small delay for visual feedback

    def browse_location(self):
        """Browse for installation location."""
        directory = filedialog.askdirectory(title="Select Installation Directory")
        if directory:
            self.location_var.set(directory)

    def show_system_requirements(self):
        """Show system requirements check."""
        frame = ttk.Frame(self.content_frame)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="System Requirements Check",
                 font=('Arial', 12, 'bold')).pack(pady=(0, 20))

        # Run requirements check in background
        self.requirements_result = None
        self.check_requirements()

        if self.requirements_result is None:
            checking_frame = ttk.Frame(frame)
            checking_frame.pack(pady=20)
            
            ttk.Label(checking_frame, text="🔍 Checking system requirements...", 
                     font=('Arial', 10)).pack()
            ttk.Label(checking_frame, text="This may take a moment while we verify your system setup.", 
                     font=('Arial', 9), foreground='gray').pack(pady=(5, 0))
            
            # Schedule check
            self.root.after(100, self.show_requirements_result)
        else:
            self.show_requirements_result()

    def check_requirements(self):
        """Check system requirements."""
        try:
            self.requirements_result = self.backend_wizard.check_system_requirements()
        except Exception as e:
            self.requirements_result = False
            self.requirements_error = str(e)

    def show_requirements_result(self):
        """Show requirements check result."""
        # Clear frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        frame = ttk.Frame(self.content_frame)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="System Requirements Check",
                 font=('Arial', 12, 'bold')).pack(pady=(0, 20))

        if self.requirements_result:
            # Success header
            ttk.Label(frame, text="✓ All system requirements met!",
                     foreground="green", font=('Arial', 10, 'bold')).pack(pady=(0, 15))

            # System information display
            self.show_system_info(frame)
            
            # CodeSentinel capabilities preview
            self.show_capabilities_preview(frame)
            
        else:
            ttk.Label(frame, text="✗ System requirements not met. Please fix the issues below:",
                     foreground="red").pack(pady=10)

            # Show detailed requirements
            details_frame = ttk.LabelFrame(frame, text="Details")
            details_frame.pack(fill=tk.BOTH, expand=True, pady=20)

            # This would show detailed requirement checks
            ttk.Label(details_frame, text="Python 3.13+ required").pack(anchor=tk.W, pady=2)
            ttk.Label(details_frame, text="Git required for repository features").pack(anchor=tk.W, pady=2)
            ttk.Label(details_frame, text="Write permissions required").pack(anchor=tk.W, pady=2)

    def show_system_info(self, parent_frame):
        """Display system information in a clean, professional format."""
        import sys
        import platform
        import subprocess
        
        # System specifications frame
        specs_frame = ttk.LabelFrame(parent_frame, text="System Specifications")
        specs_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Create a grid layout for clean presentation
        specs_inner = ttk.Frame(specs_frame)
        specs_inner.pack(fill=tk.X, padx=15, pady=10)
        
        # Python version
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        self.create_spec_row(specs_inner, 0, "Python", f"v{python_version}", "✓")
        
        # Operating system
        os_info = f"{platform.system()} {platform.release()}"
        self.create_spec_row(specs_inner, 1, "Operating System", os_info, "✓")
        
        # Git availability
        try:
            git_result = subprocess.run(['git', '--version'], capture_output=True, text=True, timeout=5)
            if git_result.returncode == 0:
                git_version = git_result.stdout.strip().split()[-1] if git_result.stdout else "Available"
                self.create_spec_row(specs_inner, 2, "Git", f"v{git_version}", "✓")
            else:
                self.create_spec_row(specs_inner, 2, "Git", "Not found", "!")
        except:
            self.create_spec_row(specs_inner, 2, "Git", "Not available", "!")
        
        # Architecture
        arch = platform.machine() or platform.processor()
        self.create_spec_row(specs_inner, 3, "Architecture", arch, "✓")

    def create_spec_row(self, parent, row, label, value, status):
        """Create a clean specification row."""
        # Status indicator
        status_colors = {"✓": "green", "!": "orange", "✗": "red"}
        ttk.Label(parent, text=status, foreground=status_colors.get(status, "black"), 
                 font=('Arial', 9, 'bold')).grid(row=row, column=0, sticky=tk.W, padx=(0, 10))
        
        # Label
        ttk.Label(parent, text=f"{label}:", font=('Arial', 9, 'bold')).grid(row=row, column=1, sticky=tk.W, padx=(0, 15))
        
        # Value
        ttk.Label(parent, text=value, font=('Arial', 9)).grid(row=row, column=2, sticky=tk.W)
        
        parent.columnconfigure(2, weight=1)

    def show_capabilities_preview(self, parent_frame):
        """Show CodeSentinel capabilities in an engaging but minimal way."""
        capabilities_frame = ttk.LabelFrame(parent_frame, text="CodeSentinel Capabilities")
        capabilities_frame.pack(fill=tk.X, pady=(0, 10))
        
        cap_inner = ttk.Frame(capabilities_frame)
        cap_inner.pack(fill=tk.X, padx=15, pady=10)
        
        capabilities = [
            ("🔒", "Security Monitoring", "Automated vulnerability scanning and dependency analysis"),
            ("⚡", "Performance Optimization", "Code quality analysis and automated maintenance"),
            ("🤖", "CI/CD Integration", "GitHub Actions, GitLab CI, and Azure DevOps workflows"),
            ("📊", "Smart Reporting", "Comprehensive maintenance reports and alerting system")
        ]
        
        for i, (icon, title, description) in enumerate(capabilities):
            cap_row = ttk.Frame(cap_inner)
            cap_row.pack(fill=tk.X, pady=2)
            
            ttk.Label(cap_row, text=icon, font=('Arial', 11)).pack(side=tk.LEFT, padx=(0, 8))
            ttk.Label(cap_row, text=title, font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=(0, 10))
            ttk.Label(cap_row, text=description, font=('Arial', 8), 
                     foreground="gray40").pack(side=tk.LEFT)
        
        # Installation readiness indicator
        ready_frame = ttk.Frame(parent_frame)
        ready_frame.pack(fill=tk.X, pady=(15, 0))
        
        ttk.Label(ready_frame, text="🚀", font=('Arial', 14)).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(ready_frame, text="System ready for CodeSentinel installation", 
                 font=('Arial', 10, 'bold'), foreground="green").pack(side=tk.LEFT)
        ttk.Label(ready_frame, text="• Continue to configure your environment", 
                 font=('Arial', 9), foreground="gray40").pack(side=tk.LEFT, padx=(15, 0))

    def show_environment_setup(self):
        """Show environment variables setup."""
        frame = ttk.Frame(self.content_frame)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Environment Variables Setup",
                 font=('Arial', 12, 'bold')).pack(pady=(0, 20))

        ttk.Label(frame, text="CodeSentinel uses environment variables for configuration.").pack(pady=(0, 10))

        # Environment variables list
        vars_frame = ttk.LabelFrame(frame, text="Environment Variables")
        vars_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))

        # This would show the environment variables that will be set
        env_vars = [
            ("CODESENTINEL_CONFIG_DIR", "Configuration directory"),
            ("CODESENTINEL_LOG_DIR", "Log files directory"),
            ("CODESENTINEL_ENABLED", "Enable/disable CodeSentinel"),
            ("CODESENTINEL_SCHEDULE_DAILY", "Daily maintenance schedule"),
            ("CODESENTINEL_SCHEDULE_WEEKLY", "Weekly maintenance schedule"),
            ("CODESENTINEL_SCHEDULE_MONTHLY", "Monthly maintenance schedule")
        ]

        for var_name, description in env_vars:
            var_frame = ttk.Frame(vars_frame)
            var_frame.pack(fill=tk.X, pady=2)
            ttk.Label(var_frame, text=f"{var_name}:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT)
            ttk.Label(var_frame, text=description).pack(side=tk.LEFT, padx=(10, 0))

        ttk.Label(frame, text="These variables will be added to your shell profile.").pack(pady=(20, 0))

    def show_alert_system(self):
        """Show alert system configuration."""
        print("Loading Alert System configuration step...")
        
        frame = ttk.Frame(self.content_frame)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Alert System Configuration",
                 font=('Arial', 12, 'bold')).pack(pady=(0, 20))

        ttk.Label(frame, text="Configure how CodeSentinel notifies you of critical issues.").pack(pady=(0, 20))

        # Alert channels
        channels_frame = ttk.LabelFrame(frame, text="Alert Channels")
        channels_frame.pack(fill=tk.X, pady=(0, 20))

        # Variables already initialized in init_all_gui_variables()
        ttk.Checkbutton(channels_frame, text="Console alerts (terminal output)",
                       variable=self.console_var).pack(anchor=tk.W, pady=2)
        ttk.Checkbutton(channels_frame, text="File logging",
                       variable=self.file_var).pack(anchor=tk.W, pady=2)
        ttk.Checkbutton(channels_frame, text="Email notifications",
                       variable=self.email_var, command=self.toggle_email_config).pack(anchor=tk.W, pady=2)
        ttk.Checkbutton(channels_frame, text="Slack notifications",
                       variable=self.slack_var, command=self.toggle_slack_config).pack(anchor=tk.W, pady=2)

        # Email configuration (initially hidden)
        self.email_frame = ttk.LabelFrame(frame, text="Email Configuration")
        # Will be shown when email checkbox is selected

        # Slack configuration (initially hidden)
        self.slack_frame = ttk.LabelFrame(frame, text="Slack Configuration")
        # Will be shown when slack checkbox is selected

        # Alert rules
        rules_frame = ttk.LabelFrame(frame, text="Alert Rules")
        rules_frame.pack(fill=tk.X, pady=(20, 0))

        # Variables already initialized in init_all_gui_variables()
        ttk.Checkbutton(rules_frame, text="Critical security issues",
                       variable=self.security_var).pack(anchor=tk.W, pady=2)
        ttk.Checkbutton(rules_frame, text="Maintenance task failures",
                       variable=self.task_var).pack(anchor=tk.W, pady=2)
        ttk.Checkbutton(rules_frame, text="Dependency vulnerabilities",
                       variable=self.dependency_var).pack(anchor=tk.W, pady=2)

    def toggle_email_config(self):
        """Toggle email configuration visibility."""
        if self.email_var.get():
            self.show_email_config()
        else:
            self.hide_email_config()

    def show_email_config(self):
        """Show email configuration options."""
        # Clear existing email frame
        for widget in self.email_frame.winfo_children():
            widget.destroy()

        self.email_frame.pack(fill=tk.X, pady=(10, 0))

        # SMTP settings
        ttk.Label(self.email_frame, text="SMTP Server:").grid(row=0, column=0, sticky=tk.W, pady=5)
        # Variables already initialized in init_all_gui_variables()
        ttk.Entry(self.email_frame, textvariable=self.smtp_server_var).grid(row=0, column=1, padx=(10, 0), pady=5)

        ttk.Label(self.email_frame, text="SMTP Port:").grid(row=1, column=0, sticky=tk.W, pady=5)
        # Variables already initialized in init_all_gui_variables()
        ttk.Entry(self.email_frame, textvariable=self.smtp_port_var).grid(row=1, column=1, padx=(10, 0), pady=5)

        ttk.Label(self.email_frame, text="Username:").grid(row=2, column=0, sticky=tk.W, pady=5)
        # Variables already initialized in init_all_gui_variables()
        ttk.Entry(self.email_frame, textvariable=self.email_user_var).grid(row=2, column=1, padx=(10, 0), pady=5)

        ttk.Label(self.email_frame, text="Password:").grid(row=3, column=0, sticky=tk.W, pady=5)
        # Variables already initialized in init_all_gui_variables()
        ttk.Entry(self.email_frame, textvariable=self.email_pass_var, show="*").grid(row=3, column=1, padx=(10, 0), pady=5)

        ttk.Label(self.email_frame, text="From Email:").grid(row=4, column=0, sticky=tk.W, pady=5)
        # Variables already initialized in init_all_gui_variables()
        ttk.Entry(self.email_frame, textvariable=self.from_email_var).grid(row=4, column=1, padx=(10, 0), pady=5)

        # Recipients
        ttk.Label(self.email_frame, text="Recipients:").grid(row=5, column=0, sticky=tk.W, pady=5)
        recipients_frame = ttk.Frame(self.email_frame)
        recipients_frame.grid(row=5, column=1, padx=(10, 0), pady=5, sticky=tk.W)

        self.recipients_listbox = tk.Listbox(recipients_frame, height=2, width=25)
        self.recipients_listbox.pack(side=tk.LEFT)

        recipients_buttons = ttk.Frame(recipients_frame)
        recipients_buttons.pack(side=tk.LEFT, padx=(10, 0))

        ttk.Button(recipients_buttons, text="Add",
                  command=self.add_email_recipient).pack(fill=tk.X, pady=2)
        ttk.Button(recipients_buttons, text="Remove",
                  command=self.remove_email_recipient).pack(fill=tk.X, pady=2)

        # CRITICAL ADDITION: Email validation button
        validation_frame = ttk.Frame(self.email_frame)
        validation_frame.grid(row=6, column=0, columnspan=2, pady=(10, 5), sticky=tk.W)
        
        ttk.Button(validation_frame, text="Test Email Connection",
                  command=self.test_email_connection).pack(side=tk.LEFT)
        
        self.email_status_label = ttk.Label(validation_frame, text="", foreground="blue")
        self.email_status_label.pack(side=tk.LEFT, padx=(10, 0))

    def hide_email_config(self):
        """Hide email configuration options."""
        self.email_frame.pack_forget()

    def add_email_recipient(self):
        """Add an email recipient."""
        email = simpledialog.askstring("Add Recipient", "Enter email address:")
        if email and email not in self.recipients_listbox.get(0, tk.END):
            self.recipients_listbox.insert(tk.END, email)

    def remove_email_recipient(self):
        """Remove selected email recipient."""
        selection = self.recipients_listbox.curselection()
        if selection:
            self.recipients_listbox.delete(selection[0])

    def test_email_connection(self):
        """Test email SMTP connection and send test email."""
        import smtplib
        import email.mime.text
        import threading
        
        # Capture current step for navigation update
        validation_step = self.current_step
        
        def test_connection():
            try:
                self.email_status_label.config(text="🔗 Connecting to SMTP server...", foreground="blue")
                self.root.update()
                
                # Get email configuration
                smtp_server = self.smtp_server_var.get()
                smtp_port = int(self.smtp_port_var.get()) if self.smtp_port_var.get() else 587
                username = self.email_user_var.get()
                password = self.email_pass_var.get()
                from_email = self.from_email_var.get()
                
                # Validate required fields
                if not all([smtp_server, username, password, from_email]):
                    self.email_status_label.config(text="❌ Please fill all required fields", foreground="red")
                    return
                
                self.email_status_label.config(text="🔐 Authenticating with server...", foreground="blue")
                self.root.update()
                
                # Test SMTP connection
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
                server.login(username, password)
                
                self.email_status_label.config(text="📧 Sending test email...", foreground="blue")
                self.root.update()
                
                # Send test email
                msg = email.mime.text.MIMEText("CodeSentinel email test successful!")
                msg['Subject'] = "CodeSentinel Setup - Email Test"
                msg['From'] = from_email
                msg['To'] = from_email
                
                server.send_message(msg)
                server.quit()
                
                # Mark email as validated
                self.email_validated = True
                
                self.email_status_label.config(text="✅ Email test successful! Check your inbox.", foreground="green")
                
                # Update navigation buttons after successful validation
                self.root.after(100, lambda: self.update_navigation_buttons(validation_step))
                
            except Exception as e:
                # Mark email as not validated on error
                self.email_validated = False
                self.email_status_label.config(text=f"❌ Error: {str(e)[:50]}...", foreground="red")
                
                # Update navigation buttons after failed validation
                self.root.after(100, lambda: self.update_navigation_buttons(validation_step))
        
        # Run test in background thread to avoid UI freezing
        threading.Thread(target=test_connection, daemon=True).start()

    def validate_git_repository(self):
        """Validate GitHub repository URL and accessibility."""
        import subprocess
        import urllib.parse
        import threading
        
        # Capture current step for navigation update
        validation_step = self.current_step
        
        def validate_repo():
            try:
                self.git_status_label.config(text="🔍 Checking URL format...", foreground="blue")
                self.root.update()
                
                github_url = self.github_url_var.get().strip()
                
                # Validate URL format
                if not github_url:
                    self.git_status_label.config(text="❌ Please enter a repository URL", foreground="red")
                    return
                
                if not github_url.startswith(('https://github.com/', 'git@github.com:')):
                    self.git_status_label.config(text="❌ Please enter a valid GitHub URL", foreground="red")
                    return
                
                self.git_status_label.config(text="🌐 Connecting to GitHub...", foreground="blue")
                self.root.update()
                
                # Test if repository exists and is accessible
                result = subprocess.run(['git', 'ls-remote', '--heads', github_url], 
                                      capture_output=True, text=True, timeout=15)
                
                if result.returncode == 0:
                    self.git_status_label.config(text="📋 Analyzing repository...", foreground="blue")
                    self.root.update()
                    
                    # Parse repository info
                    lines = result.stdout.strip().split('\n')
                    branches = []
                    for line in lines:
                        if line:
                            parts = line.split('\t')
                            if len(parts) == 2:
                                branch = parts[1].replace('refs/heads/', '')
                                branches.append(branch)
                    
                    branch_info = f" (branches: {', '.join(branches[:3])}" + ("..." if len(branches) > 3 else "") + ")"
                    
                    # Mark GitHub API as validated
                    self.github_api_validated = True
                    
                    self.git_status_label.config(text=f"✅ Repository accessible{branch_info}", foreground="green")
                    
                    # Update navigation buttons after successful validation
                    self.root.after(100, lambda: self.update_navigation_buttons(validation_step))
                else:
                    # Mark GitHub API as not validated
                    self.github_api_validated = False
                    error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                    self.git_status_label.config(text=f"❌ Repository not accessible: {error_msg[:30]}...", foreground="red")
                    
                    # Update navigation buttons after failed validation
                    self.root.after(100, lambda: self.update_navigation_buttons(validation_step))
                    
            except subprocess.TimeoutExpired:
                # Mark GitHub API as not validated
                self.github_api_validated = False
                self.git_status_label.config(text="❌ Timeout: Repository unreachable", foreground="red")
                self.root.after(100, lambda: self.update_navigation_buttons(validation_step))
            except Exception as e:
                # Mark GitHub API as not validated
                self.github_api_validated = False
                self.git_status_label.config(text=f"❌ Error: {str(e)[:30]}...", foreground="red")
                self.root.after(100, lambda: self.update_navigation_buttons(validation_step))
        
        # Run validation in background thread
        threading.Thread(target=validate_repo, daemon=True).start()

    def toggle_slack_config(self):
        """Toggle Slack configuration visibility."""
        if self.slack_var.get():
            self.show_slack_config()
        else:
            self.hide_slack_config()

    def show_slack_config(self):
        """Show Slack configuration options."""
        # Clear existing slack frame
        for widget in self.slack_frame.winfo_children():
            widget.destroy()

        self.slack_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Label(self.slack_frame, text="Webhook URL:").grid(row=0, column=0, sticky=tk.W, pady=5)
        # Variables already initialized in init_all_gui_variables()
        ttk.Entry(self.slack_frame, textvariable=self.webhook_url_var).grid(row=0, column=1, padx=(10, 0), pady=5)

        ttk.Label(self.slack_frame, text="Channel:").grid(row=1, column=0, sticky=tk.W, pady=5)
        # Variables already initialized in init_all_gui_variables()
        ttk.Entry(self.slack_frame, textvariable=self.slack_channel_var).grid(row=1, column=1, padx=(10, 0), pady=5)

        ttk.Label(self.slack_frame, text="Bot Name:").grid(row=2, column=0, sticky=tk.W, pady=5)
        # Variables already initialized in init_all_gui_variables()
        ttk.Entry(self.slack_frame, textvariable=self.slack_username_var).grid(row=2, column=1, padx=(10, 0), pady=5)

    def hide_slack_config(self):
        """Hide Slack configuration options."""
        self.slack_frame.pack_forget()

    def show_code_formatting(self):
        """Show code formatting preferences configuration."""
        frame = ttk.Frame(self.content_frame)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Code Formatting Preferences",
                 font=('Arial', 12, 'bold')).pack(pady=(0, 20))

        ttk.Label(frame, text="Configure how CodeSentinel formats your code. "
                             "Choose a preset or customize detailed settings.",
                 font=('Arial', 10)).pack(pady=(0, 20))

        # Preset configurations
        presets_frame = ttk.LabelFrame(frame, text="Quick Setup - Choose a Preset")
        presets_frame.pack(fill=tk.X, pady=(0, 20))

        # Variables already initialized in init_all_gui_variables()
        preset_descriptions = {
            "house_style": "🏠 CodeSentinel House Style (Recommended)\n" +
                          "• Line length: 88 characters (optimal for modern displays)\n" +
                          "• 4-space indentation (Python standard)\n" +
                          "• Double quotes for strings (consistency)\n" +
                          "• Trailing commas enabled (better Git diffs)\n" +
                          "• Import sorting with isort (organized imports)\n" +
                          "• Google-style docstrings (readable documentation)\n" +
                          "• Optimized for team collaboration and maintainability",
            
            "pep8_strict": "📏 PEP 8 Strict Standard\n" +
                          "• Line length: 79 characters (original PEP 8)\n" +
                          "• 4-space indentation\n" +
                          "• Single quotes for strings\n" +
                          "• Conservative formatting\n" +
                          "• Minimal automated changes\n" +
                          "• Traditional Python conventions",
            
            "google_style": "🌐 Google Style Guide\n" +
                          "• Line length: 80 characters\n" +
                          "• 4-space indentation\n" +
                          "• Double quotes for strings\n" +
                          "• Google's internal Python style\n" +
                          "• Comprehensive formatting rules\n" +
                          "• Industry standard for large projects",
            
            "black_default": "⚫ Black Formatter Default\n" +
                           "• Line length: 88 characters\n" +
                           "• 4-space indentation\n" +
                           "• Double quotes for strings\n" +
                           "• Uncompromising code formatter\n" +
                           "• Zero configuration required\n" +
                           "• Maximum automation and consistency"
        }

        for preset_key, description in preset_descriptions.items():
            preset_frame = ttk.Frame(presets_frame)
            preset_frame.pack(fill=tk.X, pady=5, padx=10)
            
            ttk.Radiobutton(preset_frame, text="", variable=self.format_preset_var, 
                           value=preset_key).pack(side=tk.LEFT)
            
            ttk.Label(preset_frame, text=description, font=('Arial', 9), 
                     justify=tk.LEFT).pack(side=tk.LEFT, padx=(10, 0))

        # Custom configuration button
        custom_frame = ttk.LabelFrame(frame, text="Advanced Configuration")
        custom_frame.pack(fill=tk.X, pady=(20, 0))

        ttk.Label(custom_frame, text="Need more control? Configure detailed formatting options.",
                 font=('Arial', 9)).pack(pady=10)

        ttk.Button(custom_frame, text="🔧 Advanced Formatting Options...",
                  command=self.show_advanced_formatting_dialog).pack(pady=5)

        # Preview current settings
        preview_frame = ttk.LabelFrame(frame, text="Current Configuration Preview")
        preview_frame.pack(fill=tk.X, pady=(20, 0))

        self.format_preview_label = ttk.Label(preview_frame, text="", font=('Arial', 8, 'italic'),
                                            foreground='gray')
        self.format_preview_label.pack(pady=10)

        # Update preview when preset changes
        self.format_preset_var.trace('w', self.update_format_preview)
        self.update_format_preview()

    def update_format_preview(self, *args):
        """Update the formatting configuration preview."""
        preset = self.format_preset_var.get()
        
        preview_configs = {
            "house_style": f"Line Length: {self.line_length_var.get()} • " +
                          f"Indent: {self.indent_size_var.get()} spaces • " +
                          f"Quotes: {self.quote_style_var.get()} • " +
                          f"Trailing Commas: {'Yes' if self.trailing_commas_var.get() else 'No'}",
            "pep8_strict": "Line Length: 79 • Indent: 4 spaces • Quotes: single • Standard PEP 8",
            "google_style": "Line Length: 80 • Indent: 4 spaces • Quotes: double • Google Style",
            "black_default": "Line Length: 88 • Indent: 4 spaces • Quotes: double • Black defaults"
        }
        
        preview_text = preview_configs.get(preset, "Custom configuration")
        self.format_preview_label.config(text=preview_text)

    def show_advanced_formatting_dialog(self):
        """Show the comprehensive advanced formatting configuration dialog."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Advanced Code Formatting Configuration")
        dialog.geometry("700x600")
        dialog.resizable(False, False)
        
        # Make dialog modal
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        self.center_window(dialog, 700, 600)

        # Main content frame with scrolling
        main_frame = ttk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        ttk.Label(main_frame, text="Advanced Formatting Configuration",
                 font=('Arial', 14, 'bold')).pack(pady=(0, 20))

        # Create tabbed interface for organization
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: Basic Settings
        basic_tab = ttk.Frame(notebook)
        notebook.add(basic_tab, text="Basic Settings")
        
        # Basic formatting options
        basic_frame = ttk.LabelFrame(basic_tab, text="Core Formatting")
        basic_frame.pack(fill=tk.X, pady=(10, 15), padx=10)

        # Line length
        ttk.Label(basic_frame, text="Maximum Line Length:").grid(row=0, column=0, sticky=tk.W, pady=8, padx=10)
        line_entry = ttk.Entry(basic_frame, textvariable=self.line_length_var, width=10)
        line_entry.grid(row=0, column=1, padx=(10, 5), pady=8)
        ttk.Label(basic_frame, text="characters (79, 88, 100, 120)").grid(row=0, column=2, padx=(5, 10), pady=8)

        # Indentation
        ttk.Label(basic_frame, text="Indentation Size:").grid(row=1, column=0, sticky=tk.W, pady=8, padx=10)
        indent_entry = ttk.Entry(basic_frame, textvariable=self.indent_size_var, width=10)
        indent_entry.grid(row=1, column=1, padx=(10, 5), pady=8)
        ttk.Label(basic_frame, text="spaces (2 or 4 recommended)").grid(row=1, column=2, padx=(5, 10), pady=8)

        # Quote style
        ttk.Label(basic_frame, text="String Quote Style:").grid(row=2, column=0, sticky=tk.W, pady=8, padx=10)
        quote_frame = ttk.Frame(basic_frame)
        quote_frame.grid(row=2, column=1, columnspan=2, sticky=tk.W, padx=(10, 0), pady=8)
        
        ttk.Radiobutton(quote_frame, text='Double quotes (")', variable=self.quote_style_var, 
                       value="double").pack(side=tk.LEFT)
        ttk.Radiobutton(quote_frame, text="Single quotes (')", variable=self.quote_style_var, 
                       value="single").pack(side=tk.LEFT, padx=(20, 0))

        # Code structure
        structure_frame = ttk.LabelFrame(basic_tab, text="Code Structure")
        structure_frame.pack(fill=tk.X, pady=(15, 10), padx=10)

        ttk.Label(structure_frame, text="Blank lines before classes:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=10)
        ttk.Entry(structure_frame, textvariable=self.blank_lines_class_var, width=5).grid(row=0, column=1, padx=(10, 0), pady=5)

        ttk.Label(structure_frame, text="Blank lines before functions:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=10)
        ttk.Entry(structure_frame, textvariable=self.blank_lines_function_var, width=5).grid(row=1, column=1, padx=(10, 0), pady=5)

        # Tab 2: Import & Organization
        imports_tab = ttk.Frame(notebook)
        notebook.add(imports_tab, text="Imports & Organization")

        imports_frame = ttk.LabelFrame(imports_tab, text="Import Formatting")
        imports_frame.pack(fill=tk.X, pady=(10, 15), padx=10)

        ttk.Checkbutton(imports_frame, text="Sort and organize imports automatically",
                       variable=self.format_imports_var).pack(anchor=tk.W, pady=8, padx=10)
        ttk.Checkbutton(imports_frame, text="Group imports by type (standard, third-party, local)",
                       variable=self.group_imports_var).pack(anchor=tk.W, pady=8, padx=10)

        ttk.Label(imports_frame, text="Import sorting style:").pack(anchor=tk.W, pady=(15, 5), padx=10)
        import_style_frame = ttk.Frame(imports_frame)
        import_style_frame.pack(anchor=tk.W, padx=20)
        
        ttk.Radiobutton(import_style_frame, text="isort (recommended)", variable=self.import_sort_style_var, 
                       value="isort").pack(anchor=tk.W)
        ttk.Radiobutton(import_style_frame, text="black style", variable=self.import_sort_style_var, 
                       value="black").pack(anchor=tk.W)
        ttk.Radiobutton(import_style_frame, text="no sorting", variable=self.import_sort_style_var, 
                       value="none").pack(anchor=tk.W)

        # Tab 3: Advanced Options
        advanced_tab = ttk.Frame(notebook)
        notebook.add(advanced_tab, text="Advanced Options")

        # String formatting
        strings_frame = ttk.LabelFrame(advanced_tab, text="String & Literal Formatting")
        strings_frame.pack(fill=tk.X, pady=(10, 15), padx=10)

        ttk.Checkbutton(strings_frame, text="Format string literals (f-strings, etc.)",
                       variable=self.format_strings_var).pack(anchor=tk.W, pady=5, padx=10)
        ttk.Checkbutton(strings_frame, text="Normalize string quotes consistently",
                       variable=self.normalize_quotes_var).pack(anchor=tk.W, pady=5, padx=10)
        ttk.Checkbutton(strings_frame, text="Use trailing commas in multi-line structures",
                       variable=self.trailing_commas_var).pack(anchor=tk.W, pady=5, padx=10)

        # Expression formatting
        expressions_frame = ttk.LabelFrame(advanced_tab, text="Expression Formatting")
        expressions_frame.pack(fill=tk.X, pady=(15, 15), padx=10)

        ttk.Checkbutton(expressions_frame, text="Format list/dict comprehensions",
                       variable=self.format_comprehensions_var).pack(anchor=tk.W, pady=5, padx=10)
        ttk.Checkbutton(expressions_frame, text="Split complex expressions across lines",
                       variable=self.split_complex_expressions_var).pack(anchor=tk.W, pady=5, padx=10)
        ttk.Checkbutton(expressions_frame, text="Format lambda expressions",
                       variable=self.format_lambdas_var).pack(anchor=tk.W, pady=5, padx=10)

        # Tab 4: Documentation & Comments
        docs_tab = ttk.Frame(notebook)
        notebook.add(docs_tab, text="Documentation")

        # Docstring formatting
        docstring_frame = ttk.LabelFrame(docs_tab, text="Docstring Formatting")
        docstring_frame.pack(fill=tk.X, pady=(10, 15), padx=10)

        ttk.Label(docstring_frame, text="Docstring style:").pack(anchor=tk.W, pady=(10, 5), padx=10)
        docstring_style_frame = ttk.Frame(docstring_frame)
        docstring_style_frame.pack(anchor=tk.W, padx=20)
        
        ttk.Radiobutton(docstring_style_frame, text="Google style (recommended)", 
                       variable=self.docstring_style_var, value="google").pack(anchor=tk.W)
        ttk.Radiobutton(docstring_style_frame, text="NumPy style", 
                       variable=self.docstring_style_var, value="numpy").pack(anchor=tk.W)
        ttk.Radiobutton(docstring_style_frame, text="Sphinx style", 
                       variable=self.docstring_style_var, value="sphinx").pack(anchor=tk.W)
        ttk.Radiobutton(docstring_style_frame, text="PEP 257 minimal", 
                       variable=self.docstring_style_var, value="pep257").pack(anchor=tk.W)

        ttk.Checkbutton(docstring_frame, text="Preserve existing docstring formatting",
                       variable=self.preserve_docstring_formatting_var).pack(anchor=tk.W, pady=(15, 5), padx=10)
        ttk.Checkbutton(docstring_frame, text="Format inline comments",
                       variable=self.format_comments_var).pack(anchor=tk.W, pady=5, padx=10)

        # Experimental options
        experimental_frame = ttk.LabelFrame(docs_tab, text="Experimental Features")
        experimental_frame.pack(fill=tk.X, pady=(15, 10), padx=10)

        ttk.Checkbutton(experimental_frame, text="Aggressive formatting (may change code behavior)",
                       variable=self.aggressive_formatting_var).pack(anchor=tk.W, pady=5, padx=10)
        ttk.Checkbutton(experimental_frame, text="Enable experimental features",
                       variable=self.experimental_features_var).pack(anchor=tk.W, pady=5, padx=10)
        ttk.Checkbutton(experimental_frame, text="Skip formatting magic methods (dunder methods)",
                       variable=self.skip_magic_methods_var).pack(anchor=tk.W, pady=5, padx=10)

        # Dialog buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, pady=(20, 0))

        def apply_and_close():
            self.format_preset_var.set("custom")
            self.update_format_preview()
            dialog.destroy()

        def reset_to_preset():
            preset = self.format_preset_var.get()
            if preset == "house_style":
                # Apply comprehensive house style settings
                self.line_length_var.set("88")
                self.indent_size_var.set("4")
                self.quote_style_var.set("double")
                self.trailing_commas_var.set(True)
                self.format_imports_var.set(True)
                self.import_sort_style_var.set("isort")
                self.group_imports_var.set(True)
                self.format_strings_var.set(False)
                self.normalize_quotes_var.set(True)
                self.blank_lines_class_var.set("2")
                self.blank_lines_function_var.set("1")
                self.format_comprehensions_var.set(True)
                self.split_complex_expressions_var.set(True)
                self.docstring_style_var.set("google")
                self.preserve_docstring_formatting_var.set(True)
                self.format_comments_var.set(False)
                self.aggressive_formatting_var.set(False)
                self.experimental_features_var.set(False)
                self.skip_magic_methods_var.set(True)
            elif preset == "pep8_strict":
                # Apply strict PEP 8 settings
                self.line_length_var.set("79")
                self.indent_size_var.set("4")
                self.quote_style_var.set("single")
                self.trailing_commas_var.set(False)
                self.format_imports_var.set(True)
                self.import_sort_style_var.set("none")
                self.group_imports_var.set(False)
                self.format_strings_var.set(False)
                self.normalize_quotes_var.set(False)
                self.blank_lines_class_var.set("2")
                self.blank_lines_function_var.set("2")
                self.format_comprehensions_var.set(False)
                self.split_complex_expressions_var.set(False)
                self.docstring_style_var.set("pep257")
                self.preserve_docstring_formatting_var.set(True)
                self.format_comments_var.set(False)
                self.aggressive_formatting_var.set(False)
                self.experimental_features_var.set(False)
                self.skip_magic_methods_var.set(True)

        ttk.Button(button_frame, text="🔄 Reset to Current Preset", 
                  command=reset_to_preset).pack(side=tk.LEFT, padx=(20, 0))
        ttk.Button(button_frame, text="✅ Apply & Close", 
                  command=apply_and_close).pack(side=tk.RIGHT, padx=(0, 20))
        ttk.Button(button_frame, text="❌ Cancel", 
                  command=dialog.destroy).pack(side=tk.RIGHT, padx=(0, 10))

    def show_github_integration(self):
        """Show GitHub integration setup."""
        # Create main frame
        frame = ttk.Frame(self.content_frame)
        frame.pack(fill=tk.BOTH, expand=True)

        # Add title
        ttk.Label(frame, text="GitHub Integration",
                 font=('Arial', 12, 'bold')).pack(pady=(0, 20))

        # CRITICAL FIX: Always show repository setup first if not a git repo
        if not self.backend_wizard.is_git_repo:
            ttk.Label(frame, text="Repository Setup Required", 
                     font=('Arial', 11, 'bold'), foreground='orange').pack(pady=(0, 10))
            ttk.Label(frame, text="Before configuring GitHub integration, you need to set up your Git repository. "
                                "Complete the repository setup below, then GitHub features will be available.",
                     wraplength=600).pack(pady=(0, 20))
            self.show_repository_setup(frame)
            
            # Show a preview of GitHub features that will be available after setup
            preview_frame = ttk.LabelFrame(frame, text="GitHub Features (Available After Repository Setup)")
            preview_frame.pack(fill=tk.X, pady=(20, 0))
            
            ttk.Label(preview_frame, text="✓ GitHub Copilot Integration", 
                     font=('Arial', 9), foreground='gray').pack(anchor=tk.W, pady=2, padx=10)
            ttk.Label(preview_frame, text="✓ GitHub API Integration", 
                     font=('Arial', 9), foreground='gray').pack(anchor=tk.W, pady=2, padx=10)
            ttk.Label(preview_frame, text="✓ Repository Features (templates, workflows)", 
                     font=('Arial', 9), foreground='gray').pack(anchor=tk.W, pady=2, padx=10)
            return

        # If we have a git repo, show GitHub features
        ttk.Label(frame, text="Configure GitHub integration features for your repository.",
                 foreground='green').pack(pady=(0, 20))

        # GitHub features
        features_frame = ttk.LabelFrame(frame, text="GitHub Features")
        features_frame.pack(fill=tk.X, pady=(0, 20))

        # GitHub Copilot Integration
        ttk.Checkbutton(features_frame, text="GitHub Copilot Integration (recommended)",
                       variable=self.copilot_var).pack(anchor=tk.W, pady=2)
        
        # GitHub API Integration - simplified without delayed command binding for now
        ttk.Checkbutton(features_frame, text="GitHub API Integration (advanced features)",
                       variable=self.api_var, command=self.toggle_api_config).pack(anchor=tk.W, pady=2)
        
        # Repository Features
        ttk.Checkbutton(features_frame, text="Repository Features (issue templates, workflows)",
                       variable=self.repo_var).pack(anchor=tk.W, pady=2)

        # API configuration (initially hidden)
        self.api_frame = ttk.LabelFrame(frame, text="GitHub API Configuration")
        
        # Initialize API config visibility immediately
        if hasattr(self, 'api_var') and self.api_var.get():
            self.show_api_config()

        # Show repository information safely
        try:
            repo_path = getattr(self.backend_wizard, 'git_root', 'Unknown')
            ttk.Label(frame, text=f"Repository: {repo_path}").pack(pady=(20, 0))
        except Exception as e:
            print(f"Warning: Could not display repository path: {e}")
            ttk.Label(frame, text="Repository: (path not available)").pack(pady=(20, 0))
        
        # Force canvas update to ensure content is visible
        self.root.after(10, self.update_canvas_scroll_region)

    def initialize_api_config_visibility(self):
        """Initialize API configuration visibility after page rendering is complete."""
        # Safety check to ensure api_frame exists
        if not hasattr(self, 'api_frame'):
            return
            
        if hasattr(self, 'api_var') and self.api_var.get():
            self.show_api_config()
        else:
            self.hide_api_config()

    def show_repository_setup(self, parent_frame):
        """Show comprehensive repository setup wizard for all scenarios."""
        ttk.Label(parent_frame, text="Repository Setup & GitHub Connection",
                 font=('Arial', 11, 'bold'), foreground='blue').pack(pady=(0, 10))
        
        ttk.Label(parent_frame, text="Connect your project to GitHub for full CodeSentinel integration. "
                                   "We'll handle the complexity of different scenarios.").pack(pady=(0, 20))

        # Scenario detection and selection
        scenario_frame = ttk.LabelFrame(parent_frame, text="Choose Your Scenario")
        scenario_frame.pack(fill=tk.X, pady=(0, 20))

        # CRITICAL FIX: Don't recreate the variable - use existing one from init_all_gui_variables()
        # self.repo_scenario_var is already initialized in __init__
        
        # Comprehensive scenario options
        scenarios = [
            ("local_to_existing", "🔗 Connect Local Project to Existing GitHub Repository",
             "I have a local project and an existing GitHub repository (your situation)"),
            ("fresh_start", "🆕 Start Fresh - Create Everything New", 
             "Create new local Git repository and new GitHub repository"),
            ("clone_existing", "📥 Clone Existing GitHub Repository",
             "Download an existing GitHub repository to work on"),
            ("local_to_new", "🚀 Local Project → New GitHub Repository",
             "I have a local project, create a new GitHub repository for it"),
            ("existing_local_git", "🔄 Connect Existing Local Git to GitHub",
             "I have a local Git repository, connect it to GitHub")
        ]

        for value, title, description in scenarios:
            scenario_container = ttk.Frame(scenario_frame)
            scenario_container.pack(fill=tk.X, pady=3, padx=5)
            
            ttk.Radiobutton(scenario_container, text="", variable=self.repo_scenario_var, 
                           value=value).pack(side=tk.LEFT)
            
            title_label = ttk.Label(scenario_container, text=title, font=('Arial', 9, 'bold'))
            title_label.pack(side=tk.LEFT, padx=(5, 0))
            
            desc_label = ttk.Label(scenario_container, text=f"  {description}", 
                                 font=('Arial', 8), foreground='gray')
            desc_label.pack(side=tk.LEFT, padx=(10, 0))

        # Configuration frame (dynamic based on selection)
        self.repo_config_frame = ttk.Frame(parent_frame)
        self.repo_config_frame.pack(fill=tk.X, pady=(15, 0))

        # Action button and status area
        action_button_frame = ttk.Frame(parent_frame)
        action_button_frame.pack(fill=tk.X, pady=(20, 0))
        
        self.setup_button = ttk.Button(action_button_frame, text="🔧 Setup Repository Connection",
                                      command=self.execute_repository_setup_immediately)
        self.setup_button.pack()
        
        # ENHANCEMENT: Add immediate status feedback area
        self.repo_status_frame = ttk.LabelFrame(parent_frame, text="Repository Setup Status")
        self.repo_status_frame.pack(fill=tk.X, pady=(15, 0))
        self.repo_status_frame.pack_forget()  # Initially hidden
        
        self.repo_status_text = tk.Text(self.repo_status_frame, height=8, width=80, 
                                       wrap=tk.WORD, font=('Consolas', 9))
        self.repo_status_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add a flag to track if repository setup was completed successfully
        self.repo_setup_completed = False
        
        # Initial configuration display
        self.update_repo_scenario_display()
        
        # Bind radio button changes
        self.repo_scenario_var.trace('w', lambda *args: self.update_repo_scenario_display())

    def update_repo_scenario_display(self):
        """Update the repository configuration display based on selected scenario."""
        # Clear existing widgets
        for widget in self.repo_config_frame.winfo_children():
            widget.destroy()

        scenario = self.repo_scenario_var.get()

        if scenario == "local_to_existing":
            self.show_local_to_existing_config()
        elif scenario == "fresh_start":
            self.show_fresh_start_config()
        elif scenario == "clone_existing":
            self.show_clone_existing_config()
        elif scenario == "local_to_new":
            self.show_local_to_new_config()
        elif scenario == "existing_local_git":
            self.show_existing_local_git_config()

    def show_local_to_existing_config(self):
        """Show configuration for connecting local project to existing GitHub repository."""
        config_frame = ttk.LabelFrame(self.repo_config_frame, text="Connect to Existing GitHub Repository")
        config_frame.pack(fill=tk.X, pady=5)

        ttk.Label(config_frame, text="GitHub Repository URL:").grid(row=0, column=0, sticky=tk.W, pady=8, padx=10)
        self.github_url_var = self.get_or_create_var('github_url_var', tk.StringVar, "https://github.com/joediggidyyy/CodeSentinel.git")
        url_entry = ttk.Entry(config_frame, textvariable=self.github_url_var, width=50)
        url_entry.grid(row=0, column=1, padx=(10, 10), pady=8, sticky=tk.EW)

        # CRITICAL ADDITION: Git validation button
        git_validation_frame = ttk.Frame(config_frame)
        git_validation_frame.grid(row=1, column=1, sticky=tk.W, padx=10, pady=5)
        
        ttk.Button(git_validation_frame, text="Validate Repository",
                  command=self.validate_git_repository).pack(side=tk.LEFT)
        
        self.git_status_label = ttk.Label(git_validation_frame, text="", foreground="blue")
        self.git_status_label.pack(side=tk.LEFT, padx=(10, 0))

        # Auto-detect and suggest
        ttk.Label(config_frame, text="💡 Detected: CodeSentinel repository", 
                 font=('Arial', 8), foreground='green').grid(row=2, column=1, sticky=tk.W, padx=10)

        ttk.Label(config_frame, text="This will:").grid(row=3, column=0, sticky=tk.NW, pady=(15, 5), padx=10)
        actions_frame = ttk.Frame(config_frame)
        actions_frame.grid(row=3, column=1, sticky=tk.W, padx=10, pady=(15, 10))
        
        actions = [
            "• Initialize Git repository in current directory (if not already Git)",
            "• Add existing GitHub repository as 'origin' remote",
            "• Fetch existing content from GitHub repository", 
            "• Merge or rebase local changes with remote content",
            "• Push local changes to GitHub repository",
            "• Set up tracking branch for seamless sync"
        ]
        
        for action in actions:
            ttk.Label(actions_frame, text=action, font=('Arial', 8)).pack(anchor=tk.W, pady=1)

        config_frame.columnconfigure(1, weight=1)

        # Conflict resolution options
        conflict_frame = ttk.LabelFrame(self.repo_config_frame, text="Conflict Resolution Strategy")
        conflict_frame.pack(fill=tk.X, pady=(10, 0))

        self.merge_strategy_var = self.get_or_create_var('merge_strategy_var', tk.StringVar, "merge")
        
        ttk.Radiobutton(conflict_frame, text="🔄 Merge (combine changes, preserve history)", 
                       variable=self.merge_strategy_var, value="merge").pack(anchor=tk.W, pady=3, padx=10)
        ttk.Radiobutton(conflict_frame, text="📝 Rebase (linear history, cleaner log)", 
                       variable=self.merge_strategy_var, value="rebase").pack(anchor=tk.W, pady=3, padx=10)
        ttk.Radiobutton(conflict_frame, text="⚠️  Force push (replace remote with local - DESTRUCTIVE)", 
                       variable=self.merge_strategy_var, value="force").pack(anchor=tk.W, pady=3, padx=10)

    def show_fresh_start_config(self):
        """Show configuration for starting fresh with new repository."""
        config_frame = ttk.LabelFrame(self.repo_config_frame, text="Create New Repository")
        config_frame.pack(fill=tk.X, pady=5)

        ttk.Label(config_frame, text="Repository Name:").grid(row=0, column=0, sticky=tk.W, pady=8, padx=10)
        self.new_repo_name_var = self.get_or_create_var('new_repo_name_var', tk.StringVar, "CodeSentinel")
        name_entry = ttk.Entry(config_frame, textvariable=self.new_repo_name_var, width=30)
        name_entry.grid(row=0, column=1, padx=(10, 10), pady=8)

        ttk.Label(config_frame, text="Description:").grid(row=1, column=0, sticky=tk.W, pady=8, padx=10)
        self.new_repo_desc_var = self.get_or_create_var('new_repo_desc_var', tk.StringVar, "CodeSentinel security and maintenance automation")
        desc_entry = ttk.Entry(config_frame, textvariable=self.new_repo_desc_var, width=50)
        desc_entry.grid(row=1, column=1, padx=(10, 10), pady=8, sticky=tk.EW)

        self.new_repo_private_var = self.get_or_create_var('new_repo_private_var', tk.BooleanVar, False)
        ttk.Checkbutton(config_frame, text="Make repository private", 
                       variable=self.new_repo_private_var).grid(row=2, column=1, sticky=tk.W, padx=10, pady=5)

        config_frame.columnconfigure(1, weight=1)

    def show_clone_existing_config(self):
        """Show configuration for cloning existing repository."""
        config_frame = ttk.LabelFrame(self.repo_config_frame, text="Clone Existing Repository")
        config_frame.pack(fill=tk.X, pady=5)

        ttk.Label(config_frame, text="GitHub Repository URL:").grid(row=0, column=0, sticky=tk.W, pady=8, padx=10)
        self.clone_url_var = self.get_or_create_var('clone_url_var', tk.StringVar, "")
        url_entry = ttk.Entry(config_frame, textvariable=self.clone_url_var, width=50)
        url_entry.grid(row=0, column=1, padx=(10, 10), pady=8, sticky=tk.EW)

        ttk.Label(config_frame, text="Local Directory Name:").grid(row=1, column=0, sticky=tk.W, pady=8, padx=10)
        self.clone_dir_var = self.get_or_create_var('clone_dir_var', tk.StringVar, "")
        dir_entry = ttk.Entry(config_frame, textvariable=self.clone_dir_var, width=30)
        dir_entry.grid(row=1, column=1, padx=(10, 10), pady=8)

        config_frame.columnconfigure(1, weight=1)

    def show_local_to_new_config(self):
        """Show configuration for connecting local project to new GitHub repository."""
        config_frame = ttk.LabelFrame(self.repo_config_frame, text="Create New GitHub Repository for Local Project")
        config_frame.pack(fill=tk.X, pady=5)

        ttk.Label(config_frame, text="Repository Name:").grid(row=0, column=0, sticky=tk.W, pady=8, padx=10)
        self.local_to_new_name_var = self.get_or_create_var('local_to_new_name_var', tk.StringVar, "CodeSentinel")
        name_entry = ttk.Entry(config_frame, textvariable=self.local_to_new_name_var, width=30)
        name_entry.grid(row=0, column=1, padx=(10, 10), pady=8)

        ttk.Label(config_frame, text="Description:").grid(row=1, column=0, sticky=tk.W, pady=8, padx=10)
        self.local_to_new_desc_var = self.get_or_create_var('local_to_new_desc_var', tk.StringVar, "Local project uploaded to GitHub")
        desc_entry = ttk.Entry(config_frame, textvariable=self.local_to_new_desc_var, width=50)
        desc_entry.grid(row=1, column=1, padx=(10, 10), pady=8, sticky=tk.EW)

        self.local_to_new_private_var = self.get_or_create_var('local_to_new_private_var', tk.BooleanVar, False)
        ttk.Checkbutton(config_frame, text="Make repository private", 
                       variable=self.local_to_new_private_var).grid(row=2, column=1, sticky=tk.W, padx=10, pady=5)

        config_frame.columnconfigure(1, weight=1)

    def show_existing_local_git_config(self):
        """Show configuration for connecting existing local Git to GitHub."""
        config_frame = ttk.LabelFrame(self.repo_config_frame, text="Connect Existing Local Git Repository")
        config_frame.pack(fill=tk.X, pady=5)

        ttk.Label(config_frame, text="Current Git Status:", font=('Arial', 9, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=5, padx=10)
        
        # Check git status
        try:
            import subprocess
            result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True, cwd=self.backend_wizard.install_location)
            if result.returncode == 0:
                status_text = "✓ Git repository detected" if result.stdout.strip() == "" else "⚠️ Uncommitted changes detected"
            else:
                status_text = "❌ Not a Git repository"
        except:
            status_text = "❌ Git not available"
            
        ttk.Label(config_frame, text=status_text).grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)

        ttk.Label(config_frame, text="GitHub Repository URL:").grid(row=1, column=0, sticky=tk.W, pady=8, padx=10)
        self.existing_git_url_var = self.get_or_create_var('existing_git_url_var', tk.StringVar, "")
        url_entry = ttk.Entry(config_frame, textvariable=self.existing_git_url_var, width=50)
        url_entry.grid(row=1, column=1, padx=(10, 10), pady=8, sticky=tk.EW)

        config_frame.columnconfigure(1, weight=1)

    def update_repo_config_display(self):
        """Update the repository configuration display based on selected option."""
        # Clear existing widgets
        for widget in self.repo_config_frame.winfo_children():
            widget.destroy()

        option = self.repo_scenario_var.get()

        if option == "initialize":
            self.show_initialize_config()
        elif option == "clone":
            self.show_clone_config()
        elif option == "connect":
            self.show_connect_config()

    def show_initialize_config(self):
        """Show configuration for initializing a new repository."""
        config_frame = ttk.LabelFrame(self.repo_config_frame, text="Initialize New Repository")
        config_frame.pack(fill=tk.X, pady=5)

        ttk.Label(config_frame, text="This will:").pack(anchor=tk.W, pady=2)
        ttk.Label(config_frame, text="• Initialize Git in current directory").pack(anchor=tk.W, padx=20)
        ttk.Label(config_frame, text="• Create initial commit with current files").pack(anchor=tk.W, padx=20)
        ttk.Label(config_frame, text="• Optionally create GitHub repository").pack(anchor=tk.W, padx=20)

        # GitHub repository creation
        github_frame = ttk.Frame(config_frame)
        github_frame.pack(fill=tk.X, pady=10)

        self.create_github_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(github_frame, text="Create repository on GitHub.com",
                       variable=self.create_github_var, command=self.toggle_github_creation).pack(anchor=tk.W)

        self.github_creation_frame = ttk.Frame(github_frame)
        self.github_creation_frame.pack(fill=tk.X, pady=5)

        self.toggle_github_creation()

    def show_clone_config(self):
        """Show configuration for cloning an existing repository."""
        config_frame = ttk.LabelFrame(self.repo_config_frame, text="Clone Existing Repository")
        config_frame.pack(fill=tk.X, pady=5)

        ttk.Label(config_frame, text="Repository URL:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.clone_url_var = tk.StringVar()
        ttk.Entry(config_frame, textvariable=self.clone_url_var, width=50).grid(row=0, column=1, padx=(10, 0), pady=5, sticky=tk.W)

        ttk.Label(config_frame, text="Local directory name:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.clone_dir_var = tk.StringVar(value="my-project")
        ttk.Entry(config_frame, textvariable=self.clone_dir_var, width=30).grid(row=1, column=1, padx=(10, 0), pady=5, sticky=tk.W)

        ttk.Label(config_frame, text="Example: https://github.com/username/repository.git",
                 font=('Arial', 8)).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))

    def show_connect_config(self):
        """Show configuration for connecting to existing GitHub repository."""
        config_frame = ttk.LabelFrame(self.repo_config_frame, text="Connect to GitHub Repository")
        config_frame.pack(fill=tk.X, pady=5)

        ttk.Label(config_frame, text="GitHub repository URL:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.connect_url_var = tk.StringVar()
        ttk.Entry(config_frame, textvariable=self.connect_url_var, width=50).grid(row=0, column=1, padx=(10, 0), pady=5, sticky=tk.W)

        ttk.Label(config_frame, text="This will:").grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(10, 2))
        ttk.Label(config_frame, text="• Add GitHub as remote origin").grid(row=2, column=0, columnspan=2, sticky=tk.W, padx=20)
        ttk.Label(config_frame, text="• Push existing commits to GitHub").grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=20)

    def toggle_github_creation(self):
        """Toggle GitHub repository creation options."""
        if self.create_github_var.get():
            self.show_github_creation_options()
        else:
            self.hide_github_creation_options()

    def show_github_creation_options(self):
        """Show GitHub repository creation options."""
        for widget in self.github_creation_frame.winfo_children():
            widget.destroy()

        ttk.Label(self.github_creation_frame, text="Repository name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.repo_name_var = tk.StringVar(value=os.path.basename(os.getcwd()))
        ttk.Entry(self.github_creation_frame, textvariable=self.repo_name_var, width=30).grid(row=0, column=1, padx=(10, 0), pady=5)

        ttk.Label(self.github_creation_frame, text="Description:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.repo_desc_var = tk.StringVar(value="CodeSentinel monitored project")
        ttk.Entry(self.github_creation_frame, textvariable=self.repo_desc_var, width=50).grid(row=1, column=1, padx=(10, 0), pady=5)

        self.private_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(self.github_creation_frame, text="Private repository",
                       variable=self.private_var).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)

    def hide_github_creation_options(self):
        """Hide GitHub repository creation options."""
        for widget in self.github_creation_frame.winfo_children():
            widget.destroy()

    def execute_repository_setup_immediately(self):
        """Execute repository setup immediately with real-time feedback."""
        scenario = self.repo_scenario_var.get()
        
        if not scenario:
            messagebox.showwarning("No Scenario Selected", "Please select a repository setup scenario first.")
            return
        
        # Show status area and update button
        self.repo_status_frame.pack(fill=tk.X, pady=(15, 0))
        self.setup_button.config(text="⏳ Setting up repository...", state="disabled")
        
        # Clear previous status
        self.repo_status_text.delete(1.0, tk.END)
        self.log_repo_status("🚀 Starting repository setup...")
        self.log_repo_status(f"📋 Scenario: {scenario}")
        
        # Execute in background thread for responsive UI
        import threading
        threading.Thread(target=self._execute_repo_setup_with_feedback, args=(scenario,), daemon=True).start()
    
    def _execute_repo_setup_with_feedback(self, scenario):
        """Execute repository setup with detailed feedback logging."""
        try:
            if scenario == "local_to_existing":
                self._setup_local_to_existing_with_feedback()
            elif scenario == "fresh_start":
                self._setup_fresh_start_with_feedback()
            elif scenario == "clone_existing":
                self._setup_clone_existing_with_feedback()
            elif scenario == "local_to_new":
                self._setup_local_to_new_with_feedback()
            elif scenario == "existing_local_git":
                self._setup_existing_git_with_feedback()
            else:
                self.log_repo_status(f"❌ Unknown scenario: {scenario}")
                return
                
            # Mark as completed and update UI
            self.repo_setup_completed = True
            self.root.after(0, lambda: self.setup_button.config(
                text="✅ Repository Setup Complete!", 
                state="normal"
            ))
            self.log_repo_status("\n🎉 Repository setup completed successfully!")
            self.log_repo_status("You can now proceed to the next step.")
            
            # Refresh backend wizard state
            self.root.after(0, lambda: setattr(self, 'backend_wizard', 
                CodeSentinelSetupWizard(self.backend_wizard.install_location)))
            
            # CRITICAL: Refresh the current step to show updated content
            self.root.after(100, lambda: self.refresh_current_step())
                
        except Exception as e:
            self.log_repo_status(f"\n❌ Setup failed: {str(e)}")
            self.root.after(0, lambda: self.setup_button.config(
                text="❌ Setup Failed - Retry", 
                state="normal"
            ))
    
    def log_repo_status(self, message):
        """Log a status message to the repository setup status area."""
        def update_ui():
            self.repo_status_text.insert(tk.END, f"{message}\n")
            self.repo_status_text.see(tk.END)
            self.root.update()
        
        self.root.after(0, update_ui)
    
    def _setup_local_to_existing_with_feedback(self):
        """Setup local project to existing GitHub repository with detailed feedback."""
        import subprocess
        
        github_url = self.github_url_var.get()
        merge_strategy = self.merge_strategy_var.get()
        cwd = str(self.backend_wizard.install_location)
        
        self.log_repo_status(f"🔗 Connecting to: {github_url}")
        self.log_repo_status(f"📁 Working directory: {cwd}")
        self.log_repo_status(f"🔄 Merge strategy: {merge_strategy}")
        
        # Step 1: Check/Initialize Git
        self.log_repo_status("\n📋 Step 1: Checking Git repository status...")
        result = subprocess.run(['git', 'status'], capture_output=True, text=True, cwd=cwd)
        
        if result.returncode != 0:
            self.log_repo_status("   Initializing new Git repository...")
            subprocess.run(['git', 'init'], capture_output=True, text=True, cwd=cwd, check=True)
            self.log_repo_status("   ✅ Git repository initialized")
            
            self.log_repo_status("   Adding all files to Git...")
            subprocess.run(['git', 'add', '.'], capture_output=True, text=True, cwd=cwd, check=True)
            subprocess.run(['git', 'commit', '-m', 'Initial commit - CodeSentinel setup'], 
                         capture_output=True, text=True, cwd=cwd, check=True)
            self.log_repo_status("   ✅ Initial commit created")
        else:
            self.log_repo_status("   ✅ Git repository already exists")
        
        # Step 2: Configure remote
        self.log_repo_status("\n📋 Step 2: Configuring GitHub remote...")
        subprocess.run(['git', 'remote', 'remove', 'origin'], capture_output=True, text=True, cwd=cwd)
        subprocess.run(['git', 'remote', 'add', 'origin', github_url], 
                     capture_output=True, text=True, cwd=cwd, check=True)
        self.log_repo_status("   ✅ Remote 'origin' configured")
        
        # Step 3: Fetch from remote
        self.log_repo_status("\n📋 Step 3: Fetching from GitHub...")
        subprocess.run(['git', 'fetch', 'origin'], capture_output=True, text=True, cwd=cwd, check=True)
        self.log_repo_status("   ✅ Successfully fetched from remote")
        
        # Step 4: Detect default branch and handle merge strategy
        self.log_repo_status("\n📋 Step 4: Detecting default branch...")
        
        # Get list of remote branches to find the default branch
        branch_result = subprocess.run(['git', 'branch', '-r'], capture_output=True, text=True, cwd=cwd)
        remote_branches = branch_result.stdout.strip().split('\n')
        
        # Find the default branch (try main, master, then first available)
        default_branch = None
        for branch in remote_branches:
            branch = branch.strip().replace('origin/', '')
            if branch in ['main', 'master']:
                default_branch = branch
                break
        
        if not default_branch and remote_branches:
            # Use first available branch
            default_branch = remote_branches[0].strip().replace('origin/', '')
        
        if not default_branch:
            self.log_repo_status("   ⚠️  No remote branches found, skipping merge")
        else:
            self.log_repo_status(f"   🎯 Default branch detected: {default_branch}")
            
            # Check if remote branch has commits
            self.log_repo_status(f"\n📋 Step 5: Synchronizing with {merge_strategy} strategy...")
            result = subprocess.run(['git', 'rev-list', '--count', f'origin/{default_branch}'], 
                                  capture_output=True, text=True, cwd=cwd)
            
            if result.returncode == 0 and int(result.stdout.strip()) > 0:
                try:
                    if merge_strategy == "merge":
                        merge_result = subprocess.run(['git', 'merge', f'origin/{default_branch}', '--allow-unrelated-histories'], 
                                     capture_output=True, text=True, cwd=cwd)
                        if merge_result.returncode != 0:
                            # Handle merge conflicts
                            self.log_repo_status(f"   ⚠️  Merge conflicts detected:")
                            self.log_repo_status(f"   {merge_result.stderr.strip()}")
                            self.log_repo_status("   🔧 Attempting automatic conflict resolution...")
                            
                            # Try to auto-resolve by favoring local changes
                            subprocess.run(['git', 'checkout', '--ours', '.'], capture_output=True, text=True, cwd=cwd)
                            subprocess.run(['git', 'add', '.'], capture_output=True, text=True, cwd=cwd)
                            subprocess.run(['git', 'commit', '--no-edit'], capture_output=True, text=True, cwd=cwd)
                            self.log_repo_status("   ✅ Conflicts resolved (favoring local changes)")
                        else:
                            self.log_repo_status("   ✅ Merged with remote history")
                            
                    elif merge_strategy == "rebase":
                        rebase_result = subprocess.run(['git', 'rebase', f'origin/{default_branch}'], 
                                     capture_output=True, text=True, cwd=cwd)
                        if rebase_result.returncode != 0:
                            # Handle rebase conflicts
                            self.log_repo_status(f"   ⚠️  Rebase conflicts detected, aborting rebase")
                            subprocess.run(['git', 'rebase', '--abort'], capture_output=True, text=True, cwd=cwd)
                            self.log_repo_status("   🔄 Falling back to merge strategy...")
                            subprocess.run(['git', 'merge', f'origin/{default_branch}', '--allow-unrelated-histories'], 
                                         capture_output=True, text=True, cwd=cwd, check=True)
                            self.log_repo_status("   ✅ Merged with remote history (fallback)")
                        else:
                            self.log_repo_status("   ✅ Rebased onto remote history")
                except subprocess.CalledProcessError as e:
                    self.log_repo_status(f"   ❌ Synchronization failed: {e.stderr}")
                    raise e
            else:
                self.log_repo_status("   ℹ️  Remote branch is empty, no merge needed")
        
        # Step 6: Push changes
        self.log_repo_status(f"\n📋 Step 6: Pushing to GitHub...")
        try:
            if merge_strategy == "force":
                push_result = subprocess.run(['git', 'push', '-u', 'origin', 'main', '--force'], 
                             capture_output=True, text=True, cwd=cwd)
            else:
                # Use the detected default branch for push
                target_branch = default_branch if default_branch else 'main'
                push_result = subprocess.run(['git', 'push', '-u', 'origin', f'HEAD:{target_branch}'], 
                             capture_output=True, text=True, cwd=cwd)
            
            if push_result.returncode != 0:
                self.log_repo_status(f"   ⚠️  Push failed: {push_result.stderr}")
                self.log_repo_status("   🔄 Trying force push...")
                subprocess.run(['git', 'push', '-u', 'origin', 'HEAD', '--force'], 
                             capture_output=True, text=True, cwd=cwd, check=True)
                self.log_repo_status("   ✅ Force pushed to GitHub")
            else:
                self.log_repo_status("   ✅ Successfully pushed to GitHub")
        except subprocess.CalledProcessError as e:
            self.log_repo_status(f"   ❌ Push failed: {e.stderr}")
            raise e
    
    def _setup_fresh_start_with_feedback(self):
        """Setup fresh repository with feedback."""
        self.log_repo_status("🚧 Fresh start setup coming soon...")
    
    def _setup_clone_existing_with_feedback(self):
        """Setup by cloning existing repository with feedback."""
        self.log_repo_status("🚧 Clone existing setup coming soon...")
    
    def _setup_local_to_new_with_feedback(self):
        """Setup local to new repository with feedback.""" 
        self.log_repo_status("🚧 Local to new repository setup coming soon...")
    
    def _setup_existing_git_with_feedback(self):
        """Setup existing Git to GitHub with feedback."""
        self.log_repo_status("🚧 Existing Git to GitHub setup coming soon...")

    def execute_repository_setup(self):
        """Execute the comprehensive repository setup based on selected scenario."""
        scenario = self.repo_scenario_var.get()
        
        try:
            if scenario == "local_to_existing":
                self.connect_local_to_existing_repo()
            elif scenario == "fresh_start":
                self.create_fresh_repository()
            elif scenario == "clone_existing":
                self.clone_existing_repository()
            elif scenario == "local_to_new":
                self.connect_local_to_new_repo()
            elif scenario == "existing_local_git":
                self.connect_existing_git_to_github()
                
            # Refresh the backend wizard state
            self.backend_wizard = CodeSentinelSetupWizard(self.backend_wizard.install_location)
            
            # Refresh the current step display
            self.show_step(self.current_step)
            
        except Exception as e:
            messagebox.showerror("Repository Setup Error", f"Failed to setup repository: {str(e)}")

    def connect_local_to_existing_repo(self):
        """Connect local project to existing GitHub repository (your scenario)."""
        import subprocess
        import os
        
        github_url = self.github_url_var.get()
        merge_strategy = self.merge_strategy_var.get()
        cwd = str(self.backend_wizard.install_location)
        
        progress_dialog = self.create_progress_dialog("Connecting to GitHub Repository")
        
        try:
            # Step 1: Initialize Git if not already a git repository
            progress_dialog.update_progress("Checking Git repository status...", 10)
            result = subprocess.run(['git', 'status'], capture_output=True, text=True, cwd=cwd)
            
            if result.returncode != 0:
                progress_dialog.update_progress("Initializing Git repository...", 20)
                subprocess.run(['git', 'init'], capture_output=True, text=True, cwd=cwd, check=True)
                
                # Add all files and create initial commit
                subprocess.run(['git', 'add', '.'], capture_output=True, text=True, cwd=cwd, check=True)
                subprocess.run(['git', 'commit', '-m', 'Initial commit - CodeSentinel setup'], 
                             capture_output=True, text=True, cwd=cwd, check=True)
            
            # Step 2: Add remote origin
            progress_dialog.update_progress("Adding GitHub remote...", 40)
            
            # Remove existing origin if it exists
            subprocess.run(['git', 'remote', 'remove', 'origin'], capture_output=True, text=True, cwd=cwd)
            
            # Add new origin
            subprocess.run(['git', 'remote', 'add', 'origin', github_url], 
                         capture_output=True, text=True, cwd=cwd, check=True)
            
            # Step 3: Fetch from remote
            progress_dialog.update_progress("Fetching from GitHub repository...", 60)
            subprocess.run(['git', 'fetch', 'origin'], capture_output=True, text=True, cwd=cwd, check=True)
            
            # Step 4: Handle merge/rebase strategy
            progress_dialog.update_progress("Synchronizing with remote repository...", 80)
            
            # Check if remote has commits
            result = subprocess.run(['git', 'rev-list', '--count', 'origin/main'], 
                                  capture_output=True, text=True, cwd=cwd)
            
            if result.returncode == 0 and int(result.stdout.strip()) > 0:
                # Remote has commits, need to merge
                if merge_strategy == "merge":
                    subprocess.run(['git', 'merge', 'origin/main', '--allow-unrelated-histories'], 
                                 capture_output=True, text=True, cwd=cwd, check=True)
                elif merge_strategy == "rebase":
                    subprocess.run(['git', 'rebase', 'origin/main'], 
                                 capture_output=True, text=True, cwd=cwd, check=True)
                elif merge_strategy == "force":
                    # Force push local changes (destructive)
                    pass  # Will be handled in push step
            
            # Step 5: Set up tracking and push
            progress_dialog.update_progress("Setting up branch tracking and pushing...", 90)
            
            if merge_strategy == "force":
                subprocess.run(['git', 'push', '-u', 'origin', 'main', '--force'], 
                             capture_output=True, text=True, cwd=cwd, check=True)
            else:
                subprocess.run(['git', 'branch', '--set-upstream-to=origin/main', 'main'], 
                             capture_output=True, text=True, cwd=cwd)
                subprocess.run(['git', 'push', '-u', 'origin', 'main'], 
                             capture_output=True, text=True, cwd=cwd, check=True)
            
            progress_dialog.update_progress("Repository connection complete!", 100)
            progress_dialog.close()
            
            messagebox.showinfo("Success", 
                              f"✅ Successfully connected local project to GitHub repository!\n\n"
                              f"Repository: {github_url}\n"
                              f"Strategy: {merge_strategy}\n"
                              f"Local and remote repositories are now synchronized.")
            
        except subprocess.CalledProcessError as e:
            progress_dialog.close()
            raise Exception(f"Git command failed: {e.stderr if e.stderr else e.stdout}")
        except Exception as e:
            progress_dialog.close()
            raise e

    def create_progress_dialog(self, title):
        """Create a progress dialog for long-running operations."""
        class ProgressDialog:
            def __init__(self, parent, title):
                self.dialog = tk.Toplevel(parent)
                self.dialog.title(title)
                self.dialog.geometry("400x150")
                self.dialog.resizable(False, False)
                self.dialog.transient(parent)
                self.dialog.grab_set()
                
                # Center the dialog
                parent_x = parent.winfo_rootx()
                parent_y = parent.winfo_rooty()
                parent_width = parent.winfo_width()
                parent_height = parent.winfo_height()
                
                x = parent_x + (parent_width // 2) - 200
                y = parent_y + (parent_height // 2) - 75
                self.dialog.geometry(f"400x150+{x}+{y}")
                
                # Progress UI
                ttk.Label(self.dialog, text=title, font=('Arial', 12, 'bold')).pack(pady=(20, 10))
                
                self.status_label = ttk.Label(self.dialog, text="Initializing...")
                self.status_label.pack(pady=(0, 10))
                
                self.progress_var = tk.DoubleVar()
                self.progress_bar = ttk.Progressbar(self.dialog, variable=self.progress_var, maximum=100)
                self.progress_bar.pack(fill=tk.X, padx=20, pady=(0, 20))
                
            def update_progress(self, message, percentage):
                self.status_label.config(text=message)
                self.progress_var.set(percentage)
                self.dialog.update()
                
            def close(self):
                self.dialog.destroy()
        
        return ProgressDialog(self.root, title)

    def create_fresh_repository(self):
        """Create a completely new repository and GitHub repository."""
        messagebox.showinfo("Coming Soon", "Fresh repository creation will be implemented next.")

    def clone_existing_repository(self):
        """Clone an existing GitHub repository."""
        messagebox.showinfo("Coming Soon", "Repository cloning will be implemented next.")

    def connect_local_to_new_repo(self):
        """Connect local project to a new GitHub repository."""
        messagebox.showinfo("Coming Soon", "Local to new repo connection will be implemented next.")

    def connect_existing_git_to_github(self):
        """Connect existing local Git repository to GitHub."""
        messagebox.showinfo("Coming Soon", "Existing Git to GitHub connection will be implemented next.")

    def initialize_repository(self):
        """Initialize a new Git repository."""
        import subprocess
        import os
        
        # Initialize git repository
        result = subprocess.run(['git', 'init'], capture_output=True, text=True, cwd=os.getcwd())
        if result.returncode != 0:
            raise Exception(f"Failed to initialize Git repository: {result.stderr}")
        
        # Add all files
        subprocess.run(['git', 'add', '.'], capture_output=True, text=True, cwd=os.getcwd())
        
        # Initial commit
        result = subprocess.run(['git', 'commit', '-m', 'Initial commit - CodeSentinel setup'], 
                              capture_output=True, text=True, cwd=os.getcwd())
        if result.returncode != 0:
            raise Exception(f"Failed to create initial commit: {result.stderr}")
        
        # Create GitHub repository if requested
        if self.create_github_var.get():
            self.create_github_repository()
        
        messagebox.showinfo("Success", "Git repository initialized successfully!")

    def clone_repository(self):
        """Clone an existing repository."""
        import subprocess
        import os
        
        url = self.clone_url_var.get().strip()
        dir_name = self.clone_dir_var.get().strip()
        
        if not url:
            raise Exception("Repository URL is required")
        if not dir_name:
            raise Exception("Directory name is required")
        
        # Clone the repository
        result = subprocess.run(['git', 'clone', url, dir_name], 
                              capture_output=True, text=True, cwd=os.getcwd())
        if result.returncode != 0:
            raise Exception(f"Failed to clone repository: {result.stderr}")
        
        messagebox.showinfo("Success", f"Repository cloned successfully to {dir_name}/\n"
                                      f"Please restart the setup wizard from the new directory.")

    def connect_repository(self):
        """Connect existing repository to GitHub."""
        import subprocess
        import os
        
        url = self.connect_url_var.get().strip()
        if not url:
            raise Exception("GitHub repository URL is required")
        
        # Add remote origin
        result = subprocess.run(['git', 'remote', 'add', 'origin', url], 
                              capture_output=True, text=True, cwd=os.getcwd())
        if result.returncode != 0:
            # If remote already exists, try to set the URL
            result = subprocess.run(['git', 'remote', 'set-url', 'origin', url], 
                                  capture_output=True, text=True, cwd=os.getcwd())
            if result.returncode != 0:
                raise Exception(f"Failed to set remote origin: {result.stderr}")
        
        # Push to GitHub
        result = subprocess.run(['git', 'push', '-u', 'origin', 'main'], 
                              capture_output=True, text=True, cwd=os.getcwd())
        if result.returncode != 0:
            # Try with master branch
            result = subprocess.run(['git', 'push', '-u', 'origin', 'master'], 
                                  capture_output=True, text=True, cwd=os.getcwd())
            if result.returncode != 0:
                raise Exception(f"Failed to push to GitHub: {result.stderr}")
        
        messagebox.showinfo("Success", "Repository connected to GitHub successfully!")

    def create_github_repository(self):
        """Create a new repository on GitHub using GitHub CLI or web interface guidance."""
        repo_name = self.repo_name_var.get().strip()
        repo_desc = self.repo_desc_var.get().strip()
        is_private = self.private_var.get()
        
        try:
            # Try using GitHub CLI if available
            import subprocess
            import os
            
            # Check if GitHub CLI is available
            result = subprocess.run(['gh', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                # Use GitHub CLI to create repository
                cmd = ['gh', 'repo', 'create', repo_name]
                if repo_desc:
                    cmd.extend(['--description', repo_desc])
                if is_private:
                    cmd.append('--private')
                else:
                    cmd.append('--public')
                cmd.extend(['--source', '.', '--push'])
                
                result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
                if result.returncode == 0:
                    messagebox.showinfo("Success", f"GitHub repository '{repo_name}' created successfully!")
                    return
                else:
                    raise Exception(f"GitHub CLI error: {result.stderr}")
            else:
                raise Exception("GitHub CLI not available")
                
        except Exception as e:
            # Fallback to manual instructions
            self.show_manual_github_instructions(repo_name, repo_desc, is_private)

    def show_manual_github_instructions(self, repo_name, repo_desc, is_private):
        """Show manual instructions for creating GitHub repository."""
        visibility = "private" if is_private else "public"
        instructions = f"""
GitHub CLI not available. Please create the repository manually:

1. Go to https://github.com/new
2. Repository name: {repo_name}
3. Description: {repo_desc}
4. Visibility: {visibility}
5. Click "Create repository"
6. Copy the repository URL
7. Run these commands in your terminal:

   git remote add origin <repository-url>
   git branch -M main
   git push -u origin main

Click OK when you've completed these steps.
        """
        
        messagebox.showinfo("Manual GitHub Setup Required", instructions.strip())

    def toggle_api_config(self):
        """Toggle GitHub API configuration visibility."""
        if self.api_var.get():
            self.show_api_config()
        else:
            self.hide_api_config()
        
        # Update navigation buttons
        self.update_navigation_buttons(self.current_step)

    def show_api_config(self):
        """Show GitHub API configuration options."""
        # Clear existing API frame
        for widget in self.api_frame.winfo_children():
            widget.destroy()

        self.api_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Label(self.api_frame, text="GitHub Personal Access Token:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.github_token_var = tk.StringVar()
        ttk.Entry(self.api_frame, textvariable=self.github_token_var, show="*").grid(row=0, column=1, padx=(10, 0), pady=5)

        ttk.Button(self.api_frame, text="Test Connection",
                  command=self.test_github_token).grid(row=1, column=0, columnspan=2, pady=(10, 0))

    def hide_api_config(self):
        """Hide GitHub API configuration options."""
        self.api_frame.pack_forget()

    def test_github_token(self):
        """Test GitHub token connection."""
        token = self.github_token_var.get()
        if not token:
            messagebox.showerror("Error", "Please enter a GitHub token first.")
            return

        # Test token in background thread
        def test_token():
            try:
                # Call the backend test method
                success = self.backend_wizard.test_github_token(token)
                if success:
                    messagebox.showinfo("Success", "GitHub token is valid!")
                else:
                    messagebox.showerror("Error", "GitHub token is invalid.")
            except Exception as e:
                messagebox.showerror("Error", f"Connection test failed: {e}")

        threading.Thread(target=test_token, daemon=True).start()

    def show_ide_integration(self):
        """Show IDE integration setup."""
        frame = ttk.Frame(self.content_frame)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="IDE Integration",
                 font=('Arial', 12, 'bold')).pack(pady=(0, 15))

        ttk.Label(frame, text="Configure integration with your development environment.").pack(pady=(0, 20))

        # CRITICAL FIX: Create UI immediately, detect IDEs asynchronously
        # IDE Support Section
        ide_frame = ttk.LabelFrame(frame, text="IDE Support")
        ide_frame.pack(fill=tk.X, pady=(0, 15))

        # Create IDE variables immediately (will be populated asynchronously)
        # Always reset detection state when showing this step to allow re-detection
        self.ide_detection_running = False
        self.ide_vars = {}
        
        # Define IDE configurations
        ide_configs = [
            {
                'name': 'Visual Studio Code',
                'key': 'vscode',
                'description': 'Lightweight, extensible code editor',
                'extensions': ['CodeSentinel', 'Python', 'GitLens'],
                'install_url': 'https://code.visualstudio.com/'
            },
            {
                'name': 'Visual Studio',
                'key': 'visualstudio',
                'description': 'Full-featured IDE for .NET and C++',
                'extensions': ['CodeSentinel Extension'],
                'install_url': 'https://visualstudio.microsoft.com/'
            },
            {
                'name': 'PyCharm',
                'key': 'pycharm',
                'description': 'Python-focused IDE by JetBrains',
                'extensions': ['CodeSentinel Plugin'],
                'install_url': 'https://www.jetbrains.com/pycharm/'
            },
            {
                'name': 'IntelliJ IDEA',
                'key': 'intellij',
                'description': 'Java IDE with multi-language support',
                'extensions': ['CodeSentinel Plugin'],
                'install_url': 'https://www.jetbrains.com/idea/'
            },
            {
                'name': 'Sublime Text',
                'key': 'sublime',
                'description': 'Fast, lightweight text editor',
                'extensions': ['CodeSentinel Package'],
                'install_url': 'https://www.sublimetext.com/'
            },
            {
                'name': 'Atom',
                'key': 'atom',
                'description': 'Hackable text editor (deprecated)',
                'extensions': ['codesentinel-atom'],
                'install_url': 'https://atom.io/'
            },
            {
                'name': 'Notepad++',
                'key': 'notepadpp',
                'description': 'Enhanced notepad with syntax highlighting',
                'extensions': ['CodeSentinel Plugin'],
                'install_url': 'https://notepad-plus-plus.org/'
            },
            {
                'name': 'Eclipse',
                'key': 'eclipse',
                'description': 'Java development environment',
                'extensions': ['CodeSentinel Plugin'],
                'install_url': 'https://www.eclipse.org/'
            }
        ]

        # Store IDE configurations and frame for async update
        self.ide_configs = ide_configs
        self.ide_frame = ide_frame
        
        # Add a visual status indicator for IDE detection
        self.ide_status_frame = ttk.Frame(ide_frame)
        self.ide_status_frame.pack(fill=tk.X, pady=(10, 5), padx=10)
        
        self.ide_status_label = ttk.Label(self.ide_status_frame, text="🔍 Scanning system for installed IDEs...", 
                                         font=('Arial', 9), foreground='blue')
        self.ide_status_label.pack(side=tk.LEFT)
        
        # Add a simple progress indicator
        self.ide_progress_label = ttk.Label(self.ide_status_frame, text="●", 
                                           font=('Arial', 12), foreground='blue')
        self.ide_progress_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Start progress animation
        self.start_progress_animation()
        
        # Display IDE options immediately with "Detecting..." status
        self.ide_widgets = {}
        for ide_config in ide_configs:
            self.ide_vars[ide_config['key']] = tk.BooleanVar(value=False)
            
            ide_row_frame = ttk.Frame(ide_frame)
            ide_row_frame.pack(fill=tk.X, pady=3, padx=10)
            
            # Initial status while detecting - more user-friendly
            checkbox_text = f"{ide_config['name']} (Scanning...)"
            checkbox = ttk.Checkbutton(ide_row_frame, text=checkbox_text,
                                     variable=self.ide_vars[ide_config['key']])
            checkbox.pack(side=tk.LEFT, anchor=tk.W)
            
            # Placeholder for install button with helpful text
            install_btn = ttk.Button(ide_row_frame, text="Please wait...", state="disabled")
            install_btn.pack(side=tk.RIGHT, padx=(10, 0))
            
            # Store widgets for async update
            self.ide_widgets[ide_config['key']] = {
                'checkbox': checkbox,
                'install_btn': install_btn,
                'config': ide_config
            }
        
        # Start async IDE detection with fallback
        import threading
        
        # Always start detection since we reset the state
        self.ide_detection_running = True
        
        # Start the detection thread
        detection_thread = threading.Thread(target=self.detect_ides_async, daemon=True)
        detection_thread.start()
        
        # Add a fallback timer in case detection fails or takes too long
        def fallback_ide_update():
            """Fallback to show installation guides if detection is taking too long."""
            try:
                if hasattr(self, 'ide_widgets') and self.ide_widgets:
                    widgets_updated = 0
                    for ide_key, widgets in self.ide_widgets.items():
                        try:
                            # Check if widgets still exist and are valid
                            checkbox = widgets['checkbox']
                            install_btn = widgets['install_btn']
                            config = widgets['config']
                            
                            # Validate widget existence before accessing
                            if not checkbox.winfo_exists() or not install_btn.winfo_exists():
                                continue
                            
                            # Check if still showing "Scanning..." or similar 
                            if any(word in checkbox.cget('text') for word in ["Scanning...", "Detecting...", "Please wait"]):
                                # Update to show manual installation option
                                checkbox.config(text=f"{config['name']} (Click to enable)")
                                install_btn.config(
                                    text="Install Guide", 
                                    state="normal",
                                    command=lambda c=config: self.show_install_guide(c)
                                )
                                widgets_updated += 1
                        except (tk.TclError, AttributeError) as e:
                            # Widget no longer exists or is invalid - skip silently
                            continue
                        except Exception as e:
                            print(f"Warning: Fallback update failed for {ide_key}: {e}")
                    
                    # Only update status if we actually made changes
                    if widgets_updated > 0:
                        self.stop_progress_animation("⏱️ Scan timeout - manual configuration available")
                        
            except Exception as e:
                print(f"Warning: Fallback IDE update failed: {e}")
            finally:
                # Reset detection state
                self.ide_detection_running = False
        
        # Schedule fallback after 5 seconds (increased for better user experience)
        try:
            self.root.after(5000, fallback_ide_update)
        except Exception as e:
            print(f"Warning: Could not schedule IDE detection fallback: {e}")
            self.ide_detection_running = False
        
        # Integration details
        details_frame = ttk.LabelFrame(frame, text="Integration Details")
        details_frame.pack(fill=tk.X, pady=(15, 0))
        
        details_text = """
Selected IDEs will receive:
• CodeSentinel configuration files and tasks
• Syntax highlighting for CodeSentinel configs
• Integrated maintenance commands
• Security scanning workflows
• Git hooks and automation scripts
        """
        
        ttk.Label(details_frame, text=details_text.strip(), justify=tk.LEFT).pack(padx=10, pady=10, anchor=tk.W)

    def detect_installed_ides(self):
        """Detect which IDEs are installed on the system."""
        import os
        import glob
        from pathlib import Path
        
        detected = set()
        username = os.getenv('USERNAME', 'User')
        
        # IDE detection patterns
        ide_patterns = {
            'vscode': [
                'C:\\Users\\{}\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe',
                'C:\\Program Files\\Microsoft VS Code\\Code.exe',
                'C:\\Program Files (x86)\\Microsoft VS Code\\Code.exe'
            ],
            'visualstudio': [
                'C:\\Program Files\\Microsoft Visual Studio\\2022\\*\\Common7\\IDE\\devenv.exe',
                'C:\\Program Files (x86)\\Microsoft Visual Studio\\2019\\*\\Common7\\IDE\\devenv.exe',
                'C:\\Program Files (x86)\\Microsoft Visual Studio\\2017\\*\\Common7\\IDE\\devenv.exe'
            ],
            'pycharm': [
                'C:\\Users\\{}\\AppData\\Local\\JetBrains\\Toolbox\\apps\\PyCharm-P\\*\\bin\\pycharm64.exe',
                'C:\\Program Files\\JetBrains\\PyCharm*\\bin\\pycharm64.exe',
                'C:\\Users\\{}\\AppData\\Local\\JetBrains\\PyCharm*\\bin\\pycharm64.exe'
            ],
            'intellij': [
                'C:\\Users\\{}\\AppData\\Local\\JetBrains\\Toolbox\\apps\\IDEA-U\\*\\bin\\idea64.exe',
                'C:\\Program Files\\JetBrains\\IntelliJ IDEA*\\bin\\idea64.exe'
            ],
            'sublime': [
                'C:\\Program Files\\Sublime Text*\\sublime_text.exe',
                'C:\\Users\\{}\\AppData\\Local\\Sublime Text*\\sublime_text.exe'
            ],
            'atom': [
                'C:\\Users\\{}\\AppData\\Local\\atom\\atom.exe'
            ],
            'notepadpp': [
                'C:\\Program Files\\Notepad++\\notepad++.exe',
                'C:\\Program Files (x86)\\Notepad++\\notepad++.exe'
            ],
            'eclipse': [
                'C:\\eclipse\\eclipse.exe',
                'C:\\Program Files\\Eclipse\\*\\eclipse.exe'
            ]
        }
        
        for ide_key, patterns in ide_patterns.items():
            for pattern in patterns:
                # Replace username placeholder
                if '{}' in pattern:
                    pattern = pattern.format(username)
                
                try:
                    # Use glob to handle wildcard patterns
                    matches = glob.glob(pattern)
                    if matches:
                        detected.add(ide_key)
                        break
                except Exception:
                    continue
        
        return detected

    def detect_ides_async(self):
        """Detect IDEs asynchronously and update UI."""
        try:
            detected_ides = self.detect_installed_ides()
            
            # Update UI on main thread with safety checks
            try:
                if hasattr(self, 'root') and self.root and self.root.winfo_exists():
                    self.root.after(0, lambda: self.update_ide_detection_results(detected_ides))
                else:
                    print("Warning: IDE detection completed but UI is no longer available")
            except Exception as ui_error:
                print(f"Warning: Could not update IDE detection UI: {ui_error}")
                
        except Exception as e:
            print(f"Warning: IDE detection failed: {e}")
            # Update UI to show detection failed, with safety checks
            try:
                if hasattr(self, 'root') and self.root and self.root.winfo_exists():
                    self.root.after(0, lambda: self.update_ide_detection_results(set()))
                else:
                    print("Warning: IDE detection failed and UI is no longer available")
            except Exception as ui_error:
                print(f"Warning: Could not update IDE detection UI after failure: {ui_error}")
        finally:
            # Always reset detection state when complete
            self.ide_detection_running = False
    
    def update_ide_detection_results(self, detected_ides):
        """Update IDE UI with detection results."""
        try:
            # Safety checks before UI updates
            if not hasattr(self, 'ide_widgets') or not self.ide_widgets:
                print("Warning: IDE widgets not available for update")
                return  # UI not ready yet
                
            if not hasattr(self, 'root') or not self.root:
                print("Warning: Root window not available for IDE update")
                return
                
            try:
                # Check if root window still exists
                self.root.winfo_exists()
            except:
                print("Warning: Root window no longer exists, skipping IDE update")
                return
                
            for ide_key, widgets in self.ide_widgets.items():
                try:
                    # Validate widgets still exist before updating
                    checkbox = widgets['checkbox']
                    install_btn = widgets['install_btn']
                    
                    if not checkbox.winfo_exists() or not install_btn.winfo_exists():
                        continue  # Skip if widgets no longer exist
                    
                    is_detected = ide_key in detected_ides
                    config = widgets['config']
                    
                    # Update checkbox text and state
                    status_text = "✓ Detected" if is_detected else "Not detected"
                    checkbox_text = f"{config['name']} ({status_text})"
                    checkbox.config(text=checkbox_text)
                    
                    # Update variable value for detected IDEs
                    if is_detected and hasattr(self, 'ide_vars') and ide_key in self.ide_vars:
                        self.ide_vars[ide_key].set(True)
                    
                    # Update install button
                    if is_detected:
                        install_btn.config(text="Detected", state="disabled")
                    else:
                        install_btn.config(
                            text="Install Guide", 
                            state="normal",
                            command=lambda c=config: self.show_install_guide(c)
                        )
                except Exception as widget_error:
                    print(f"Warning: Failed to update IDE widget {ide_key}: {widget_error}")
                    continue
            
            # Stop progress animation and show completion status
            detected_count = len(detected_ides)
            total_count = len(self.ide_widgets)
            if detected_count > 0:
                self.stop_progress_animation(f"✅ Found {detected_count} of {total_count} IDEs installed")
            else:
                self.stop_progress_animation(f"✅ Scan complete - {total_count} IDEs checked")
                    
        except Exception as e:
            print(f"Warning: Failed to update IDE detection results: {e}")
            self.stop_progress_animation("⚠️ Detection completed with warnings")

    def start_progress_animation(self):
        """Start a simple progress animation for IDE detection."""
        self.progress_animation_running = True
        self.progress_dots = 0
        self.animate_progress()
    
    def animate_progress(self):
        """Animate the progress indicator."""
        if not getattr(self, 'progress_animation_running', False):
            return
            
        try:
            if hasattr(self, 'ide_progress_label') and self.ide_progress_label.winfo_exists():
                dots = "●" * (self.progress_dots % 4)
                spaces = "  " * (3 - (self.progress_dots % 4))
                self.ide_progress_label.config(text=f"{dots}{spaces}")
                self.progress_dots += 1
                
                # Schedule next animation frame
                self.root.after(500, self.animate_progress)
        except Exception as e:
            print(f"Warning: Progress animation error: {e}")
    
    def stop_progress_animation(self, final_message="✅ Scan complete"):
        """Stop the progress animation and show final status."""
        self.progress_animation_running = False
        try:
            if hasattr(self, 'ide_status_label') and self.ide_status_label.winfo_exists():
                self.ide_status_label.config(text=final_message, foreground='green')
            if hasattr(self, 'ide_progress_label') and self.ide_progress_label.winfo_exists():
                self.ide_progress_label.config(text="✓", foreground='green')
        except Exception as e:
            print(f"Warning: Could not update progress status: {e}")

    def show_install_guide(self, ide_config):
        """Show installation guide for an IDE."""
        guide_window = tk.Toplevel(self.root)
        guide_window.title(f"Install {ide_config['name']}")
        guide_window.geometry("500x400")
        guide_window.resizable(True, True)
        
        # Center the window
        self.center_window(guide_window, 500, 400)
        
        main_frame = ttk.Frame(guide_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        ttk.Label(main_frame, text=f"Install {ide_config['name']}",
                 font=('Arial', 14, 'bold')).pack(pady=(0, 10))
        
        # Description
        ttk.Label(main_frame, text=ide_config['description'],
                 font=('Arial', 10)).pack(pady=(0, 15))
        
        # Installation steps
        steps_frame = ttk.LabelFrame(main_frame, text="Installation Steps")
        steps_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        steps_text = f"""
1. Visit the official website:
   {ide_config['install_url']}

2. Download the appropriate version for your system

3. Run the installer and follow the setup wizard

4. After installation, restart this CodeSentinel setup

5. CodeSentinel will automatically detect the installed IDE

Extensions to install after setup:
{chr(10).join('• ' + ext for ext in ide_config['extensions'])}
        """
        
        text_widget = scrolledtext.ScrolledText(steps_frame, wrap=tk.WORD, height=12)
        text_widget.insert(tk.END, steps_text.strip())
        text_widget.config(state=tk.DISABLED)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Open Website",
                  command=lambda: self.open_url(ide_config['install_url'])).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="Close",
                  command=guide_window.destroy).pack(side=tk.RIGHT)

    def open_url(self, url):
        """Open URL in default browser."""
        import webbrowser
        try:
            webbrowser.open(url)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open URL: {e}")

    def show_optional_features(self):
        """Show optional features setup."""
        frame = ttk.Frame(self.content_frame)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Optional Features",
                 font=('Arial', 12, 'bold')).pack(pady=(0, 15))

        ttk.Label(frame, text="Configure additional CodeSentinel automation features. "
                             "These features enhance security and development workflow.",
                 font=('Arial', 10)).pack(pady=(0, 20))

        # Optional features with detailed explanations
        features_frame = ttk.LabelFrame(frame, text="Automation & Integration Features")
        features_frame.pack(fill=tk.X, pady=(0, 15))

        # Note: All variables already initialized in init_all_gui_variables() to persist across navigation

        # Feature configurations with detailed descriptions
        feature_configs = [
            {
                'var': self.cron_var,
                'title': 'Automated Maintenance Scheduling',
                'subtitle': 'Cron jobs for scheduled maintenance',
                'description': 'Automatically runs CodeSentinel maintenance tasks on a schedule:\n'
                              '• Daily: Security scans, dependency checks, code formatting\n'
                              '• Weekly: Performance analysis, comprehensive audits\n'
                              '• Monthly: Deep security analysis, cleanup tasks\n\n'
                              'Requires: System permissions for task scheduling\n'
                              'Best for: Production systems, team projects',
                'recommended': False,
                'complexity': 'Advanced',
                'impact': 'Hands-off automation'
            },
            {
                'var': self.git_hooks_var,
                'title': 'Git Hooks Integration',
                'subtitle': 'Pre-commit and pre-push validation',
                'description': 'Installs Git hooks to automatically run checks before commits:\n'
                              '• Pre-commit: Code formatting, lint checks, security scans\n'
                              '• Pre-push: Full test suite, dependency validation\n'
                              '• Commit-msg: Enforce conventional commit messages\n\n'
                              'Requires: Git repository (auto-detected)\n'
                              'Best for: All developers, prevents bad commits',
                'recommended': True,
                'complexity': 'Beginner',
                'impact': 'Catch issues early'
            },
            {
                'var': self.ci_cd_var,
                'title': 'CI/CD Workflow Templates',
                'subtitle': 'GitHub Actions and pipeline configurations',
                'description': 'Creates workflow templates for continuous integration:\n'
                              '• GitHub Actions: Automated testing, security scanning\n'
                              '• GitLab CI: Pipeline templates for different environments\n'
                              '• Azure DevOps: Build and deployment pipelines\n\n'
                              'Requires: Git repository with remote (GitHub/GitLab/Azure)\n'
                              'Best for: Team projects, open source, production deployments',
                'recommended': False,
                'complexity': 'Intermediate',
                'impact': 'Professional workflows'
            }
        ]

        for i, config in enumerate(feature_configs):
            self.create_feature_section(features_frame, config, i)

        # Recommendations section
        recommendations_frame = ttk.LabelFrame(frame, text="💡 Smart Recommendations")
        recommendations_frame.pack(fill=tk.X, pady=(15, 0))

        # Generate context-aware recommendations
        recommendations = self.generate_feature_recommendations()
        
        rec_text = "Based on your configuration:\n\n" + "\n".join(f"• {rec}" for rec in recommendations)
        
        ttk.Label(recommendations_frame, text=rec_text,
                 font=('Arial', 9), justify=tk.LEFT).pack(padx=15, pady=10, anchor=tk.W)

    def create_feature_section(self, parent, config, index):
        """Create a detailed feature section with expandable information."""
        # Main feature frame
        feature_frame = ttk.Frame(parent)
        feature_frame.pack(fill=tk.X, padx=10, pady=8)

        # Header frame with checkbox and info
        header_frame = ttk.Frame(feature_frame)
        header_frame.pack(fill=tk.X)

        # Checkbox with enhanced title
        checkbox_text = config['title']
        if config['recommended']:
            checkbox_text += " (Recommended)"
        
        checkbox = ttk.Checkbutton(header_frame, text=checkbox_text,
                                 variable=config['var'])
        checkbox.pack(side=tk.LEFT, anchor=tk.W)

        # Complexity and impact badges
        badge_frame = ttk.Frame(header_frame)
        badge_frame.pack(side=tk.RIGHT)

        complexity_color = {'Beginner': 'green', 'Intermediate': 'orange', 'Advanced': 'red'}
        
        ttk.Label(badge_frame, text=f"📊 {config['complexity']}",
                 font=('Arial', 8), foreground=complexity_color.get(config['complexity'], 'black')).pack(side=tk.RIGHT, padx=(10, 0))
        
        ttk.Label(badge_frame, text=f"🎯 {config['impact']}",
                 font=('Arial', 8)).pack(side=tk.RIGHT, padx=(10, 0))

        # Subtitle
        ttk.Label(feature_frame, text=config['subtitle'],
                 font=('Arial', 9, 'italic'), foreground='gray').pack(anchor=tk.W, pady=(2, 5))

        # Description (initially collapsed for clean UI)
        desc_frame = ttk.Frame(feature_frame)
        desc_frame.pack(fill=tk.X, padx=20)

        # Create expandable description
        desc_var = tk.BooleanVar(value=False)
        
        def toggle_description():
            # Toggle the state first
            desc_var.set(not desc_var.get())
            
            # Then update UI based on the new state
            if desc_var.get():
                desc_label.pack(fill=tk.X, pady=(5, 0))
                toggle_btn.config(text="ℹ️ Hide Details")
            else:
                desc_label.pack_forget()
                toggle_btn.config(text="ℹ️ Show Details")

        toggle_btn = ttk.Button(desc_frame, text="ℹ️ Show Details",
                              command=toggle_description)
        toggle_btn.pack(anchor=tk.W)

        desc_label = ttk.Label(desc_frame, text=config['description'],
                              font=('Arial', 8), justify=tk.LEFT, foreground='#333333')

        # Add separator
        if index < 2:  # Don't add separator after last item
            ttk.Separator(feature_frame, orient='horizontal').pack(fill=tk.X, pady=(10, 0))

    def generate_feature_recommendations(self):
        """Generate intelligent feature recommendations based on user's setup."""
        recommendations = []
        
        # Check if user is in a Git repository
        if self.backend_wizard.is_git_repo:
            recommendations.append("Git Hooks are highly recommended for your Git repository to catch issues early")
            
            # Check if GitHub integration was configured
            if hasattr(self, 'copilot_var') and self.copilot_var.get():
                recommendations.append("CI/CD workflows complement your GitHub integration for professional development")
        else:
            recommendations.append("Consider initializing a Git repository to enable Git Hooks and CI/CD features")

        # Check selected IDEs for additional context
        if hasattr(self, 'ide_vars'):
            professional_ides = ['vscode', 'visualstudio', 'pycharm', 'intellij']
            selected_professional = any(self.ide_vars.get(ide, tk.BooleanVar()).get() for ide in professional_ides)
            
            if selected_professional:
                recommendations.append("Your professional IDE setup pairs well with automated maintenance scheduling")

        # Check installation mode
        if hasattr(self, 'mode_var') and self.mode_var.get() == 'repository':
            recommendations.append("Repository mode benefits from all automation features for comprehensive integration")

        # Default recommendation if no specific context
        if not recommendations:
            recommendations.append("Start with Git Hooks (beginner-friendly) and add other features as your project grows")
            recommendations.append("Cron jobs are powerful but require system administrator privileges")

        return recommendations

    def show_summary(self):
        """Show setup summary."""
        frame = ttk.Frame(self.content_frame)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Setup Summary",
                 font=('Arial', 12, 'bold')).pack(pady=(0, 20))

        # Summary text
        summary_text = f"""
CodeSentinel will be configured with the following settings:

Installation Location: {self.location_var.get() if hasattr(self, 'location_var') else self.backend_wizard.install_location}

Alert Channels:
• Console: {'Enabled' if getattr(self, 'console_var', tk.BooleanVar(value=True)).get() else 'Disabled'}
• File Logging: {'Enabled' if getattr(self, 'file_var', tk.BooleanVar(value=True)).get() else 'Disabled'}
• Email: {'Enabled' if getattr(self, 'email_var', tk.BooleanVar()).get() else 'Disabled'}
• Slack: {'Enabled' if getattr(self, 'slack_var', tk.BooleanVar()).get() else 'Disabled'}

GitHub Integration: {'Enabled' if self.backend_wizard.is_git_repo else 'Not available (not in git repository)'}
IDE Integration: {'Enabled' if getattr(self, 'vscode_var', tk.BooleanVar(value=True)).get() else 'Disabled'}

Click Finish to apply these settings.
        """

        text_widget = scrolledtext.ScrolledText(frame, wrap=tk.WORD, height=20)
        text_widget.insert(tk.END, summary_text.strip())
        text_widget.config(state=tk.DISABLED)
        text_widget.pack(fill=tk.BOTH, expand=True)

    def cleanup_content_frame(self):
        """Enhanced widget cleanup to prevent naming conflicts."""
        try:
            # Clear IDE widget references to prevent stale widget access
            if hasattr(self, 'ide_widgets'):
                self.ide_widgets = {}
            
            # Stop any running IDE detection to prevent callbacks on destroyed widgets
            if hasattr(self, 'ide_detection_running'):
                self.ide_detection_running = False
            
            # First, try to unbind any events from child widgets
            for widget in self.content_frame.winfo_children():
                try:
                    # Unbind common events to prevent callbacks on destroyed widgets
                    for event in ['<Button-1>', '<Button-2>', '<Button-3>', '<Key>', '<FocusIn>', '<FocusOut>']:
                        try:
                            widget.unbind(event)
                        except:
                            pass
                except:
                    pass
                    
                try:
                    # For complex widgets, recursively clean up children
                    if hasattr(widget, 'winfo_children'):
                        for child in widget.winfo_children():
                            try:
                                child.destroy()
                            except:
                                pass
                except:
                    pass
                    
                try:
                    # Finally destroy the widget
                    widget.destroy()
                except:
                    pass
                    
            # Force update to ensure widgets are fully destroyed
            self.content_frame.update_idletasks()
            
        except Exception as e:
            print(f"Warning: Error during widget cleanup: {e}")
            # Fallback: try simple destroy
            try:
                for widget in self.content_frame.winfo_children():
                    widget.destroy()
            except:
                pass

    def show_error_step(self, error_message):
        """Show an error step when something goes wrong."""
        try:
            # Clear content safely
            try:
                for widget in self.content_frame.winfo_children():
                    widget.destroy()
            except:
                pass
                
            # Create error display
            error_frame = ttk.Frame(self.content_frame)
            error_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # Error icon and title
            title_frame = ttk.Frame(error_frame)
            title_frame.pack(fill=tk.X, pady=(0, 20))
            
            ttk.Label(title_frame, text="⚠️", font=('Arial', 24)).pack(side=tk.LEFT, padx=(0, 10))
            ttk.Label(title_frame, text="Setup Error", font=('Arial', 16, 'bold')).pack(side=tk.LEFT)
            
            # Error message
            ttk.Label(error_frame, text=error_message, 
                     font=('Arial', 10), wraplength=500).pack(pady=(0, 20))
            
            # Instructions
            ttk.Label(error_frame, 
                     text="You can try to continue with the next step, go back to fix the issue, "
                          "or restart the wizard by clicking 'Reset All Settings' below.",
                     font=('Arial', 9), wraplength=500, foreground='gray').pack(pady=(0, 20))
            
            # Action buttons
            button_frame = ttk.Frame(error_frame)
            button_frame.pack(pady=10)
            
            ttk.Button(button_frame, text="Reset All Settings", 
                      command=self.reset_wizard_state).pack(side=tk.LEFT, padx=(0, 10))
            ttk.Button(button_frame, text="Try Current Step Again", 
                      command=lambda: self.show_step(self.current_step)).pack(side=tk.LEFT)
                      
        except Exception as e:
            print(f"Critical error in error display: {e}")
            # Last resort: show basic message
            try:
                ttk.Label(self.content_frame, text=f"Error: {error_message}").pack()
            except:
                pass

    def go_next(self):
        """Go to next step."""
        try:
            if self.current_step < len(self.steps) - 1:
                self.show_step(self.current_step + 1)
            else:
                print("Already at the last step")
        except Exception as e:
            print(f"Error navigating to next step: {e}")
            # Try to refresh current step
            self.show_step(self.current_step)

    def go_back(self):
        """Go to previous step."""
        if self.current_step > 0:
            self.show_step(self.current_step - 1)

    def cancel_wizard(self):
        """Cancel the setup wizard."""
        if messagebox.askyesno("Cancel Setup", "Are you sure you want to cancel the setup?"):
            self.root.quit()

    def reset_wizard_state(self):
        """Reset all wizard variables to initial state for testing."""
        if messagebox.askyesno("Reset Wizard", "Reset all wizard settings to start fresh?\n\nThis will clear all your current selections."):
            try:
                # CRITICAL: Reinitialize backend wizard FIRST to get fresh state
                self.backend_wizard = CodeSentinelSetupWizard(self.backend_wizard.install_location)
                
                # Reset step tracking
                self.current_step = 0
                
                # CRITICAL: Reinitialize ALL GUI variables completely
                self.init_all_gui_variables()
                
                # Clear any UI elements that might have state
                self.clear_all_ui_state()
                
                # Reset configuration storage
                self.config = {
                    'install_location': str(self.backend_wizard.install_location),
                    'alerts': {},
                    'github': {},
                    'ide': {},
                    'optional': {}
                }
                
                # Reset repository setup completion flag
                self.repo_setup_completed = False
                
                # Force refresh the current step display
                self.show_step(0)
                
                messagebox.showinfo("Reset Complete", "Wizard has been reset to initial state.\n\nAll variables cleared and ready for fresh testing!")
                
            except Exception as e:
                messagebox.showerror("Reset Error", f"Error during reset: {str(e)}")
    
    def clear_all_ui_state(self):
        """Clear all UI state elements that might persist."""
        try:
            # Clear status displays
            if hasattr(self, 'email_status_label'):
                self.email_status_label.config(text="")
            if hasattr(self, 'git_status_label'):
                self.git_status_label.config(text="")
            if hasattr(self, 'repo_status_text'):
                self.repo_status_text.delete(1.0, tk.END)
            if hasattr(self, 'repo_status_frame'):
                self.repo_status_frame.pack_forget()
            if hasattr(self, 'setup_button'):
                self.setup_button.config(text="🔧 Setup Repository Connection", state="normal")
            
            # Clear recipients listbox
            if hasattr(self, 'recipients_listbox'):
                self.recipients_listbox.delete(0, tk.END)
            
            # Hide email and slack config frames
            if hasattr(self, 'email_frame'):
                self.email_frame.pack_forget()
            if hasattr(self, 'slack_frame'):
                self.slack_frame.pack_forget()
            if hasattr(self, 'api_frame'):
                self.api_frame.pack_forget()
            
            # Clear any content frame children to force refresh
            if hasattr(self, 'content_frame'):
                for widget in self.content_frame.winfo_children():
                    widget.destroy()
                    
        except Exception as e:
            print(f"Warning: Error clearing UI state: {e}")
    
    def refresh_current_step(self):
        """Refresh the current step display to reflect updated state."""
        try:
            self.show_step(self.current_step)
        except Exception as e:
            print(f"Warning: Error refreshing step: {e}")

    def finish_wizard(self):
        """Finish the setup wizard."""
        try:
            # Disable finish button and show processing feedback
            self.next_button.config(text="⏳ Finalizing setup...", state="disabled")
            self.back_button.config(state="disabled")
            
            # Update UI to show processing
            self.root.update()
            
            # Apply configuration
            self.apply_configuration()

            # Show success message
            messagebox.showinfo("Setup Complete",
                              "🎉 CodeSentinel has been successfully configured!\n\n"
                              "Your development environment is now enhanced with automated "
                              "security monitoring and maintenance capabilities.\n\n"
                              "You can now use CodeSentinel in your development workflow.")

            self.root.quit()

        except Exception as e:
            # Re-enable buttons on error
            self.next_button.config(text="Finish", state="normal")
            self.back_button.config(state="normal")
            messagebox.showerror("Setup Failed", f"Setup failed with error: {e}")

    def apply_configuration(self):
        """Apply the wizard configuration."""
        # Update backend wizard with GUI selections
        self.backend_wizard.install_location = Path(self.location_var.get())

        # CRITICAL FIX: Execute repository setup if configured
        self.apply_repository_setup()

        # Apply alert system configuration
        self.apply_alert_config()

        # Apply GitHub configuration
        self.apply_github_config()

        # Apply IDE configuration
        self.apply_ide_config()

        # Run the backend setup
        success = self.backend_wizard.run_non_interactive_setup()
        if not success:
            raise Exception("Backend setup failed")

    def apply_alert_config(self):
        """Apply alert system configuration."""
        config = {
            "enabled": True,
            "channels": {
                "console": {"enabled": self.console_var.get()},
                "file": {"enabled": self.file_var.get(), "log_file": "tools/codesentinel/alerts.log"},
                "email": {"enabled": self.email_var.get()},
                "slack": {"enabled": self.slack_var.get()}
            },
            "alert_rules": {
                "critical_security_issues": self.security_var.get(),
                "task_failures": self.task_var.get(),
                "dependency_vulnerabilities": self.dependency_var.get()
            }
        }

        # Apply email config if enabled
        if self.email_var.get():
            config["channels"]["email"].update({
                "smtp_server": self.smtp_server_var.get(),
                "smtp_port": int(self.smtp_port_var.get()),
                "username": self.email_user_var.get(),
                "password": self.email_pass_var.get(),
                "from_email": self.from_email_var.get(),
                "to_emails": list(self.recipients_listbox.get(0, tk.END))
            })

        # Apply Slack config if enabled
        if self.slack_var.get():
            config["channels"]["slack"].update({
                "webhook_url": self.webhook_url_var.get(),
                "channel": self.slack_channel_var.get(),
                "username": self.slack_username_var.get()
            })

        # Save alert configuration
        alerts_config = self.backend_wizard.config_dir / "alerts.json"
        alerts_config.parent.mkdir(parents=True, exist_ok=True)
        with open(alerts_config, 'w') as f:
            json.dump(config, f, indent=2)

    def apply_github_config(self):
        """Apply GitHub configuration."""
        if not self.backend_wizard.is_git_repo:
            return

        # Build configuration with proper typing
        config = {
            "copilot": {"enabled": self.copilot_var.get()},
            "repository": {"enabled": self.repo_var.get()}
        }
        
        # Handle API configuration with token - use Any type to avoid type conflicts
        api_config: Dict[str, Any] = {"enabled": self.api_var.get()}
        if self.api_var.get() and hasattr(self, 'github_token_var'):
            api_config["token"] = self.github_token_var.get()
        config["api"] = api_config

        # Update backend config
        self.backend_wizard.config.update({"github": config})

    def apply_ide_config(self):
        """Apply IDE configuration."""
        config = {}
        
        # Build config from all IDE variables
        if hasattr(self, 'ide_vars'):
            for ide_key, var in self.ide_vars.items():
                config[ide_key] = {"enabled": var.get()}
        else:
            # Fallback for backwards compatibility
            config = {"vscode": {"enabled": True}}

        # Update backend config
        self.backend_wizard.config.update({"ide": config})

    def apply_repository_setup(self):
        """Apply repository setup if configured and not already completed."""
        # Check if repository setup was already completed immediately
        if hasattr(self, 'repo_setup_completed') and self.repo_setup_completed:
            print("Repository setup already completed - skipping")
            return
            
        # Only execute repository setup if we're not in a git repo and user selected an option
        if not self.backend_wizard.is_git_repo and hasattr(self, 'repo_scenario_var'):
            scenario = self.repo_scenario_var.get()
            
            # Only execute if a scenario was actually selected (not empty/default)
            if scenario and scenario != "":
                try:
                    # Use the old method as fallback if immediate setup wasn't completed
                    self.execute_repository_setup()
                    # Refresh backend wizard state after repository setup
                    self.backend_wizard = CodeSentinelSetupWizard(self.backend_wizard.install_location)
                except Exception as e:
                    # Log the error but don't fail the entire setup
                    print(f"Warning: Repository setup failed: {e}")

    def run(self):
        """Run the GUI wizard."""
        self.root.mainloop()


def main():
    """Main entry point for GUI wizard."""
    import argparse

    parser = argparse.ArgumentParser(
        description="CodeSentinel GUI Setup Wizard",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  codesentinel-setup-gui              # Run GUI setup wizard
  codesentinel-setup-gui --help       # Show this help message
        """
    )

    parser.add_argument(
        '--install-location',
        type=str,
        help='Specify installation location (default: auto-detect)'
    )

    args = parser.parse_args()

    try:
        install_location = Path(args.install_location) if args.install_location else None
        wizard = GUISetupWizard(install_location)
        wizard.run()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nSetup failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()