"""
CodeSentinel - Installation Location Page

Created by: joediggidyyy
Architecture: SECURITY > EFFICIENCY > MINIMALISM

Intelligent installation location selection with repository detection.
"""

import tkinter as tk
from tkinter import ttk, filedialog
from pathlib import Path
from typing import Dict, Any, List, Optional
import subprocess
import os

from ..components.base_page import BasePage

class LocationPage(BasePage):
    """
    Installation location selection page with intelligent repository detection.
    """
    
    def __init__(self, parent: tk.Widget, on_next, on_previous, config_data: Dict[str, Any]):
        super().__init__(parent, on_next, on_previous, config_data)
        self.title = "Installation Location"
        
        # Variables
        self.location_var = tk.StringVar()
        self.mode_var = tk.StringVar(value="repository")
        self.detected_repos: List[Dict[str, str]] = []
        
    def create_page(self) -> tk.Frame:
        """Create the installation location page."""
        self.frame = ttk.Frame(self.parent)
        
        # Main content area
        content_frame = ttk.Frame(self.frame)
        content_frame.pack(fill="both", expand=True, padx=40, pady=30)
        
        # Header
        self._create_header(content_frame)
        
        # Installation mode selection
        self._create_mode_selection(content_frame)
        
        # Repository detection section
        self._create_repository_section(content_frame)
        
        # Manual location selection
        self._create_manual_selection(content_frame)
        
        # Current selection display
        self._create_selection_display(content_frame)
        
        # Navigation
        self._create_navigation(content_frame)
        
        # Initial setup
        self._detect_repositories()
        self._update_selection_display()
        
        return self.frame
    
    def _create_header(self, parent: tk.Widget) -> None:
        """Create page header."""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill="x", pady=(0, 20))
        
        title_label = ttk.Label(
            header_frame,
            text="Choose Installation Location",
            style="Header.TLabel"
        )
        title_label.pack(anchor="w")
        
        subtitle_label = ttk.Label(
            header_frame,
            text="Select where CodeSentinel should be installed and configured.",
            style="Body.TLabel"
        )
        subtitle_label.pack(anchor="w", pady=(5, 0))
    
    def _create_mode_selection(self, parent: tk.Widget) -> None:
        """Create installation mode selection."""
        mode_section = self.create_section(
            parent,
            "Installation Mode",
            "Choose how CodeSentinel should be installed."
        )
        
        # Repository mode
        repo_frame = ttk.Frame(mode_section)
        repo_frame.pack(fill="x", pady=5)
        
        ttk.Radiobutton(
            repo_frame,
            text="Repository Integration",
            variable=self.mode_var,
            value="repository",
            command=self._on_mode_change
        ).pack(side="left")
        
        ttk.Label(
            repo_frame,
            text="Install within an existing Git repository",
            style="Body.TLabel"
        ).pack(side="left", padx=(10, 0))
        
        # Standalone mode
        standalone_frame = ttk.Frame(mode_section)
        standalone_frame.pack(fill="x", pady=5)
        
        ttk.Radiobutton(
            standalone_frame,
            text="Standalone Installation",
            variable=self.mode_var,
            value="standalone",
            command=self._on_mode_change
        ).pack(side="left")
        
        ttk.Label(
            standalone_frame,
            text="Install as a standalone application",
            style="Body.TLabel"
        ).pack(side="left", padx=(10, 0))
    
    def _create_repository_section(self, parent: tk.Widget) -> None:
        """Create repository detection section."""
        self.repo_section = self.create_section(
            parent,
            "Detected Repositories",
            "CodeSentinel has detected the following Git repositories on your system."
        )
        
        # Repository list frame
        self.repo_list_frame = ttk.Frame(self.repo_section)
        self.repo_list_frame.pack(fill="x", pady=10)
        
        # Refresh button
        refresh_button = ttk.Button(
            self.repo_section,
            text="🔄 Refresh Repository List",
            command=self._detect_repositories
        )
        refresh_button.pack(anchor="w", pady=5)
    
    def _create_manual_selection(self, parent: tk.Widget) -> None:
        """Create manual location selection."""
        manual_section = self.create_section(
            parent,
            "Manual Selection",
            "Or choose a custom location manually."
        )
        
        location_frame = ttk.Frame(manual_section)
        location_frame.pack(fill="x", pady=10)
        
        # Location entry
        self.location_entry = ttk.Entry(
            location_frame,
            textvariable=self.location_var,
            font=("Consolas", 10)
        )
        self.location_entry.pack(side="left", fill="x", expand=True)
        
        # Browse button
        browse_button = ttk.Button(
            location_frame,
            text="Browse...",
            command=self._browse_location
        )
        browse_button.pack(side="right", padx=(10, 0))
    
    def _create_selection_display(self, parent: tk.Widget) -> None:
        """Create current selection display."""
        self.selection_section = self.create_section(
            parent,
            "Selected Location"
        )
        
        self.selection_info = ttk.Label(
            self.selection_section,
            text="No location selected",
            style="Body.TLabel",
            wraplength=500
        )
        self.selection_info.pack(anchor="w")
        
        self.status_label = self.create_status_label(self.selection_section)
    
    def _detect_repositories(self) -> None:
        """Detect Git repositories in common development directories."""
        self.detected_repos = []
        
        # Common development directories
        search_paths = [
            Path.home() / "Documents",
            Path.home() / "Projects",
            Path.home() / "Code",
            Path.home() / "Development",
            Path.home() / "repos",
            Path.cwd().parent
        ]
        
        # Clear existing repo list
        for widget in self.repo_list_frame.winfo_children():
            widget.destroy()
        
        repos_found = False
        
        for search_path in search_paths:
            if search_path.exists() and search_path.is_dir():
                try:
                    # Limit search depth to prevent performance issues
                    for repo_path in self._find_git_repos(search_path, max_depth=3):
                        repo_info = self._get_repo_info(repo_path)
                        if repo_info:
                            self.detected_repos.append(repo_info)
                            self._create_repo_button(repo_info)
                            repos_found = True
                            
                            # Limit to 10 repositories for performance
                            if len(self.detected_repos) >= 10:
                                break
                except PermissionError:
                    continue
            
            if len(self.detected_repos) >= 10:
                break
        
        if not repos_found:
            no_repos_label = ttk.Label(
                self.repo_list_frame,
                text="No Git repositories found in common locations.",
                style="Body.TLabel"
            )
            no_repos_label.pack(anchor="w", pady=10)
    
    def _find_git_repos(self, path: Path, max_depth: int = 3) -> List[Path]:
        """Find Git repositories in a directory."""
        repos = []
        
        if max_depth <= 0:
            return repos
        
        try:
            for item in path.iterdir():
                if item.is_dir():
                    if (item / ".git").exists():
                        repos.append(item)
                    else:
                        # Recurse into subdirectories
                        repos.extend(self._find_git_repos(item, max_depth - 1))
        except (PermissionError, OSError):
            pass
        
        return repos
    
    def _get_repo_info(self, repo_path: Path) -> Optional[Dict[str, str]]:
        """Get repository information."""
        try:
            # Get repository name
            name = repo_path.name
            
            # Get remote URL if available
            remote_url = ""
            try:
                result = subprocess.run(
                    ["git", "remote", "get-url", "origin"],
                    cwd=repo_path,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    remote_url = result.stdout.strip()
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass
            
            # Get current branch
            branch = "unknown"
            try:
                result = subprocess.run(
                    ["git", "branch", "--show-current"],
                    cwd=repo_path,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    branch = result.stdout.strip() or "main"
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass
            
            return {
                "name": name,
                "path": str(repo_path),
                "remote": remote_url,
                "branch": branch
            }
            
        except Exception:
            return None
    
    def _create_repo_button(self, repo_info: Dict[str, str]) -> None:
        """Create a button for a detected repository."""
        repo_frame = ttk.Frame(self.repo_list_frame)
        repo_frame.pack(fill="x", pady=2)
        
        # Repository button
        repo_button = ttk.Button(
            repo_frame,
            text=f"📁 {repo_info['name']}",
            command=lambda: self._select_repository(repo_info)
        )
        repo_button.pack(side="left")
        
        # Repository info
        info_text = f"{repo_info['path']}"
        if repo_info['remote']:
            info_text += f" • {repo_info['branch']} branch"
        
        info_label = ttk.Label(
            repo_frame,
            text=info_text,
            style="Body.TLabel",
            font=("Consolas", 9)
        )
        info_label.pack(side="left", padx=(10, 0))
    
    def _select_repository(self, repo_info: Dict[str, str]) -> None:
        """Select a detected repository."""
        self.location_var.set(repo_info['path'])
        self.mode_var.set("repository")
        self._update_selection_display()
    
    def _browse_location(self) -> None:
        """Browse for installation location."""
        directory = filedialog.askdirectory(
            title="Select Installation Location",
            initialdir=str(Path.home())
        )
        
        if directory:
            self.location_var.set(directory)
            
            # Check if it's a Git repository
            if (Path(directory) / ".git").exists():
                self.mode_var.set("repository")
            else:
                self.mode_var.set("standalone")
            
            self._update_selection_display()
    
    def _on_mode_change(self) -> None:
        """Handle installation mode change."""
        mode = self.mode_var.get()
        
        if mode == "repository":
            # Show repository section
            self.repo_section.pack(fill="x", pady=(0, 15))
        else:
            # Hide repository section for standalone mode
            # Note: We could hide it, but keeping it visible for user awareness
            pass
        
        self._update_selection_display()
    
    def _update_selection_display(self) -> None:
        """Update the selection display."""
        location = self.location_var.get()
        mode = self.mode_var.get()
        
        if not location:
            self.selection_info.config(text="No location selected")
            self.update_status(self.status_label, "Please select an installation location", "warning")
            self.next_button.config(state="disabled")
            return
        
        location_path = Path(location)
        
        # Check if location exists
        if not location_path.exists():
            self.selection_info.config(text=f"Location: {location}")
            self.update_status(self.status_label, "⚠️ Location does not exist (will be created)", "warning")
            self.next_button.config(state="normal")
            return
        
        # Check if it's a Git repository
        is_git_repo = (location_path / ".git").exists()
        
        if mode == "repository" and not is_git_repo:
            self.selection_info.config(text=f"Location: {location}")
            self.update_status(self.status_label, "⚠️ Selected location is not a Git repository", "warning")
            self.next_button.config(state="normal")
        elif mode == "standalone" and is_git_repo:
            self.selection_info.config(text=f"Location: {location}")
            self.update_status(self.status_label, "ℹ️ Location is a Git repository (will install as standalone)", "info")
            self.next_button.config(state="normal")
        else:
            self.selection_info.config(text=f"Location: {location}")
            mode_text = "Repository integration" if mode == "repository" else "Standalone installation"
            self.update_status(self.status_label, f"✅ Ready for {mode_text}", "success")
            self.next_button.config(state="normal")
    
    def validate_page(self) -> bool:
        """Validate the installation location."""
        location = self.location_var.get()
        
        if not location:
            self.show_error("Please select an installation location.")
            return False
        
        location_path = Path(location)
        
        # Try to create directory if it doesn't exist
        if not location_path.exists():
            try:
                location_path.mkdir(parents=True, exist_ok=True)
            except PermissionError:
                self.show_error(f"Permission denied: Cannot create directory {location}")
                return False
            except Exception as e:
                self.show_error(f"Error creating directory: {e}")
                return False
        
        # Check if directory is writable
        if not os.access(location_path, os.W_OK):
            self.show_error("The selected location is not writable.")
            return False
        
        return True
    
    def save_data(self) -> Dict[str, Any]:
        """Save page data."""
        return {
            "location": {
                "path": self.location_var.get(),
                "mode": self.mode_var.get()
            }
        }
    
    def on_page_shown(self) -> None:
        """Called when page is shown."""
        # Set current directory as default if no location selected
        if not self.location_var.get():
            current_dir = Path.cwd()
            if (current_dir / ".git").exists():
                self.location_var.set(str(current_dir))
                self.mode_var.set("repository")
            else:
                self.location_var.set(str(current_dir))
                self.mode_var.set("standalone")
            
            self._update_selection_display()