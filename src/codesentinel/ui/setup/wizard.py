"""
CodeSentinel v2.0 - Setup Wizard Main Application

Created by: joediggidyyy
Architecture: SECURITY > EFFICIENCY > MINIMALISM

Main setup wizard that coordinates all setup pages with a clean,
modular architecture replacing the 3,150-line monolithic class.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from typing import List, Dict, Any, Optional

# Import setup pages
from .welcome_page import WelcomePage
from ..components.base_page import BasePage

class SetupWizard:
    """
    Main setup wizard coordinator. Replaces the monolithic 3,150-line
    GUI class with a clean, modular architecture.
    """
    
    def __init__(self):
        self.root = tk.Tk()
        self.current_page_index = 0
        self.pages: List[BasePage] = []
        self.config_data: Dict[str, Any] = {}
        
        # Setup window
        self._setup_window()
        self._configure_styles()
        self._create_pages()
        self._show_current_page()
    
    def _setup_window(self) -> None:
        """Configure the main window."""
        self.root.title("CodeSentinel v2.0 Setup Wizard")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Center window on screen
        self._center_window()
        
        # Set window icon (if available)
        try:
            icon_path = Path(__file__).parent.parent.parent / "assets" / "icon.ico"
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except:
            pass  # Icon not critical
        
        # Configure window behavior
        self.root.protocol("WM_DELETE_WINDOW", self._on_window_close)
    
    def _center_window(self) -> None:
        """Center window on screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def _configure_styles(self) -> None:
        """Configure TTK styles for consistent appearance."""
        style = ttk.Style()
        
        # Use modern theme
        try:
            style.theme_use("vista")  # Windows 10/11 style
        except:
            style.theme_use("clam")  # Fallback
        
        # Configure custom styles
        style.configure(
            "Header.TLabel",
            font=("Segoe UI", 16, "bold"),
            foreground="#2E3440"
        )
        
        style.configure(
            "Subheader.TLabel",
            font=("Segoe UI", 12, "bold"),
            foreground="#4C566A"
        )
        
        style.configure(
            "Body.TLabel",
            font=("Segoe UI", 10),
            foreground="#2E3440"
        )
        
        style.configure(
            "Success.TLabel",
            font=("Segoe UI", 10),
            foreground="#A3BE8C"
        )
        
        style.configure(
            "Error.TLabel",
            font=("Segoe UI", 10),
            foreground="#BF616A"
        )
        
        style.configure(
            "Warning.TLabel",
            font=("Segoe UI", 10),
            foreground="#D08770"
        )
    
    def _create_pages(self) -> None:
        """Create all setup wizard pages."""
        # Import page classes
        from .location_page import LocationPage
        from .security_page import SecurityPage
        from .alerts_page import AlertsPage
        from .github_page import GitHubPage
        from .features_page import FeaturesPage
        from .completion_page import CompletionPage
        
        # Create main container for pages
        self.page_container = ttk.Frame(self.root)
        self.page_container.pack(fill="both", expand=True)
        
        # Initialize pages
        page_classes = [
            ("Welcome", WelcomePage),
            ("Installation Location", LocationPage),
            ("Security Configuration", SecurityPage),
            ("Alert Preferences", AlertsPage),
            ("GitHub Integration", GitHubPage),
            ("Feature Selection", FeaturesPage),
            ("Setup Complete", CompletionPage)
        ]
        
        for title, page_class in page_classes:
            try:
                page = page_class(
                    parent=self.page_container,
                    on_next=self._next_page,
                    on_previous=self._previous_page,
                    config_data=self.config_data
                )
                page.title = title
                self.pages.append(page)
            except Exception as e:
                print(f"Error creating page {title}: {e}")
                # Create a placeholder page
                page = BasePage(
                    parent=self.page_container,
                    on_next=self._next_page,
                    on_previous=self._previous_page,
                    config_data=self.config_data
                )
                page.title = f"{title} (Error)"
                self.pages.append(page)
    
    def _show_current_page(self) -> None:
        """Show the current page and hide others."""
        # Hide all pages
        for page in self.pages:
            if hasattr(page, 'frame') and page.frame:
                page.frame.pack_forget()
        
        # Show current page
        if 0 <= self.current_page_index < len(self.pages):
            current_page = self.pages[self.current_page_index]
            
            # Create page frame if not exists
            if not hasattr(current_page, 'frame') or not current_page.frame:
                current_page.frame = current_page.create_page()
            
            # Show page
            current_page.frame.pack(fill="both", expand=True)
            
            # Update window title
            self.root.title(f"CodeSentinel v2.0 Setup - {current_page.title}")
            
            # Call page activation hook
            if hasattr(current_page, 'on_page_shown'):
                current_page.on_page_shown()
    
    def _next_page(self) -> None:
        """Navigate to next page."""
        current_page = self.pages[self.current_page_index]
        
        # Validate current page
        if hasattr(current_page, 'validate_page') and not current_page.validate_page():
            return
        
        # Save page data
        if hasattr(current_page, 'save_data'):
            page_data = current_page.save_data()
            self.config_data.update(page_data)
        
        # Move to next page
        if self.current_page_index < len(self.pages) - 1:
            self.current_page_index += 1
            self._show_current_page()
        else:
            # Finish setup
            self._finish_setup()
    
    def _previous_page(self) -> None:
        """Navigate to previous page."""
        if self.current_page_index > 0:
            self.current_page_index -= 1
            self._show_current_page()
    
    def _finish_setup(self) -> None:
        """Complete the setup process."""
        try:
            # Save final configuration
            from ...core.config.manager import config_manager
            
            # Update configuration with collected data
            self._apply_config_data()
            
            # Save configuration
            if config_manager.save_config():
                messagebox.showinfo(
                    "Setup Complete",
                    "CodeSentinel has been successfully configured!\n\n"
                    "You can now close this wizard and start using CodeSentinel."
                )
            else:
                messagebox.showerror(
                    "Setup Error",
                    "There was an error saving the configuration. "
                    "Please check the logs and try again."
                )
            
            # Close wizard
            self.root.destroy()
            
        except Exception as e:
            messagebox.showerror(
                "Setup Error",
                f"An error occurred during setup completion: {e}"
            )
    
    def _apply_config_data(self) -> None:
        """Apply collected configuration data to config manager."""
        from ...core.config.manager import config_manager
        
        # Apply location settings
        if 'location' in self.config_data:
            location_data = self.config_data['location']
            config_manager.config.install_location = location_data.get('path', '')
            config_manager.config.installation_mode = location_data.get('mode', 'repository')
        
        # Apply security settings
        if 'security' in self.config_data:
            security_data = self.config_data['security']
            config_manager.update_security(**security_data)
        
        # Apply alert settings
        if 'alerts' in self.config_data:
            alerts_data = self.config_data['alerts']
            config_manager.update_alerts(**alerts_data)
        
        # Apply email settings
        if 'email' in self.config_data:
            email_data = self.config_data['email']
            config_manager.update_email(**email_data)
        
        # Apply GitHub settings
        if 'github' in self.config_data:
            github_data = self.config_data['github']
            config_manager.update_github(**github_data)
        
        # Apply feature settings
        if 'features' in self.config_data:
            features_data = self.config_data['features']
            config_manager.update_maintenance(**features_data)
    
    def _on_window_close(self) -> None:
        """Handle window close event."""
        if messagebox.askyesno(
            "Exit Setup",
            "Are you sure you want to exit the setup wizard?\n\n"
            "Any unsaved configuration will be lost."
        ):
            self.root.destroy()
    
    def run(self) -> None:
        """Start the setup wizard."""
        self.root.mainloop()


def main():
    """Main entry point for the setup wizard."""
    try:
        # Check system requirements
        import sys
        if sys.version_info < (3, 8):
            messagebox.showerror(
                "System Requirements",
                "CodeSentinel requires Python 3.8 or higher.\n"
                f"Current version: {sys.version}"
            )
            return
        
        # Start setup wizard
        wizard = SetupWizard()
        wizard.run()
        
    except Exception as e:
        messagebox.showerror(
            "Startup Error",
            f"An error occurred starting the setup wizard: {e}"
        )


if __name__ == "__main__":
    main()