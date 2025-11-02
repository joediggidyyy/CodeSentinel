"""
CodeSentinel v2.0 - Welcome Page Component

Created by: joediggidyyy
Architecture: SECURITY > EFFICIENCY > MINIMALISM

Professional welcome page with relevant information and GitHub repository link.
"""

import tkinter as tk
from tkinter import ttk
import webbrowser
from pathlib import Path
from typing import Callable

class WelcomePage:
    """
    Professional welcome page for CodeSentinel setup wizard.
    Displays relevant information for first-time installation.
    """
    
    def __init__(self, parent: tk.Widget, on_next: Callable[[], None]):
        self.parent = parent
        self.on_next = on_next
        self.frame = None
        
    def create_page(self) -> tk.Frame:
        """Create and return the welcome page frame."""
        self.frame = ttk.Frame(self.parent)
        
        # Main content area with padding
        content_frame = ttk.Frame(self.frame)
        content_frame.pack(fill="both", expand=True, padx=40, pady=30)
        
        # Header section
        self._create_header(content_frame)
        
        # Welcome message
        self._create_welcome_message(content_frame)
        
        # Feature highlights
        self._create_feature_highlights(content_frame)
        
        # System information
        self._create_system_info(content_frame)
        
        # Footer with links
        self._create_footer(content_frame)
        
        # Navigation buttons
        self._create_navigation(content_frame)
        
        return self.frame
    
    def _create_header(self, parent: tk.Widget) -> None:
        """Create the header section with branding."""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Main title
        title_label = ttk.Label(
            header_frame,
            text="CodeSentinel v2.0",
            font=("Segoe UI", 24, "bold"),
            foreground="#2E3440"
        )
        title_label.pack(anchor="center")
        
        # Subtitle with principle
        subtitle_label = ttk.Label(
            header_frame,
            text="SECURITY > EFFICIENCY > MINIMALISM",
            font=("Segoe UI", 12, "italic"),
            foreground="#5E81AC"
        )
        subtitle_label.pack(anchor="center", pady=(5, 0))
        
        # Creator attribution
        creator_label = ttk.Label(
            header_frame,
            text="Created by joediggidyyy",
            font=("Segoe UI", 10),
            foreground="#81A1C1"
        )
        creator_label.pack(anchor="center", pady=(5, 0))
    
    def _create_welcome_message(self, parent: tk.Widget) -> None:
        """Create the welcome message section."""
        welcome_frame = ttk.LabelFrame(parent, text="Welcome to CodeSentinel", padding=20)
        welcome_frame.pack(fill="x", pady=(0, 20))
        
        welcome_text = (
            "Welcome to CodeSentinel v2.0, a security-first automated maintenance and monitoring "
            "system for development projects. This setup wizard will guide you through configuring "
            "CodeSentinel for your development environment.\n\n"
            "CodeSentinel provides comprehensive monitoring capabilities with multi-channel alerting, "
            "scheduled maintenance tasks, and seamless integration with your development workflows."
        )
        
        welcome_label = ttk.Label(
            welcome_frame,
            text=welcome_text,
            font=("Segoe UI", 11),
            wraplength=600,
            justify="left"
        )
        welcome_label.pack(anchor="w")
    
    def _create_feature_highlights(self, parent: tk.Widget) -> None:
        """Create the feature highlights section."""
        features_frame = ttk.LabelFrame(parent, text="Key Features", padding=20)
        features_frame.pack(fill="x", pady=(0, 20))
        
        # Create two columns for features
        left_column = ttk.Frame(features_frame)
        left_column.pack(side="left", fill="both", expand=True)
        
        right_column = ttk.Frame(features_frame)
        right_column.pack(side="right", fill="both", expand=True)
        
        # Security features (left column)
        security_label = ttk.Label(
            left_column,
            text="🔒 Security & Monitoring",
            font=("Segoe UI", 12, "bold"),
            foreground="#D08770"
        )
        security_label.pack(anchor="w", pady=(0, 5))
        
        security_features = [
            "• Automated vulnerability scanning",
            "• Secure credential management",
            "• Real-time security alerts",
            "• Dependency security audits"
        ]
        
        for feature in security_features:
            ttk.Label(left_column, text=feature, font=("Segoe UI", 10)).pack(anchor="w")
        
        # Automation features (right column)
        automation_label = ttk.Label(
            right_column,
            text="🔧 Automation & Integration",
            font=("Segoe UI", 12, "bold"),
            foreground="#A3BE8C"
        )
        automation_label.pack(anchor="w", pady=(0, 5))
        
        automation_features = [
            "• Scheduled maintenance tasks",
            "• Multi-channel alerts (Email/Slack)",
            "• GitHub integration & Copilot",
            "• IDE configuration automation"
        ]
        
        for feature in automation_features:
            ttk.Label(right_column, text=feature, font=("Segoe UI", 10)).pack(anchor="w")
    
    def _create_system_info(self, parent: tk.Widget) -> None:
        """Create system information section."""
        system_frame = ttk.LabelFrame(parent, text="System Information", padding=20)
        system_frame.pack(fill="x", pady=(0, 20))
        
        # Get system information
        import platform
        import sys
        
        system_info = [
            f"Operating System: {platform.system()} {platform.release()}",
            f"Python Version: {sys.version.split()[0]}",
            f"Current Directory: {Path.cwd()}",
            f"Setup Mode: First-time installation"
        ]
        
        for info in system_info:
            info_label = ttk.Label(
                system_frame,
                text=info,
                font=("Segoe UI", 10),
                foreground="#4C566A"
            )
            info_label.pack(anchor="w", pady=1)
    
    def _create_footer(self, parent: tk.Widget) -> None:
        """Create footer with links and additional information."""
        footer_frame = ttk.Frame(parent)
        footer_frame.pack(fill="x", pady=(20, 0))
        
        # Links frame
        links_frame = ttk.Frame(footer_frame)
        links_frame.pack(anchor="center")
        
        # GitHub repository link
        github_button = ttk.Button(
            links_frame,
            text="🔗 View on GitHub",
            command=self._open_github_repo,
            style="Link.TButton"
        )
        github_button.pack(side="left", padx=(0, 20))
        
        # Documentation link
        docs_button = ttk.Button(
            links_frame,
            text="📖 Documentation",
            command=self._open_documentation,
            style="Link.TButton"
        )
        docs_button.pack(side="left", padx=(0, 20))
        
        # Support link
        support_button = ttk.Button(
            links_frame,
            text="💬 Get Support",
            command=self._open_support,
            style="Link.TButton"
        )
        support_button.pack(side="left")
        
        # Version and license info
        version_frame = ttk.Frame(footer_frame)
        version_frame.pack(anchor="center", pady=(10, 0))
        
        version_label = ttk.Label(
            version_frame,
            text="CodeSentinel v2.0 | MIT License | © 2025 joediggidyyy",
            font=("Segoe UI", 9),
            foreground="#81A1C1"
        )
        version_label.pack()
    
    def _create_navigation(self, parent: tk.Widget) -> None:
        """Create navigation buttons."""
        nav_frame = ttk.Frame(parent)
        nav_frame.pack(fill="x", pady=(30, 0))
        
        # Next button (right-aligned)
        next_button = ttk.Button(
            nav_frame,
            text="Get Started →",
            command=self.on_next,
            style="Accent.TButton"
        )
        next_button.pack(side="right")
        
        # Exit button (left-aligned)
        exit_button = ttk.Button(
            nav_frame,
            text="Exit Setup",
            command=self._exit_setup
        )
        exit_button.pack(side="left")
    
    def _open_github_repo(self) -> None:
        """Open GitHub repository in browser."""
        webbrowser.open("https://github.com/joediggidyyy/CodeSentinel")
    
    def _open_documentation(self) -> None:
        """Open documentation in browser."""
        webbrowser.open("https://github.com/joediggidyyy/CodeSentinel/wiki")
    
    def _open_support(self) -> None:
        """Open support/issues page in browser."""
        webbrowser.open("https://github.com/joediggidyyy/CodeSentinel/issues")
    
    def _exit_setup(self) -> None:
        """Exit the setup wizard."""
        import sys
        if tk.messagebox.askyesno("Exit Setup", "Are you sure you want to exit the setup wizard?"):
            sys.exit(0)
    
    def configure_styles(self, root: tk.Tk) -> None:
        """Configure custom styles for the welcome page."""
        style = ttk.Style()
        
        # Configure link button style
        style.configure(
            "Link.TButton",
            foreground="#5E81AC",
            background="white",
            borderwidth=0,
            focuscolor="none"
        )
        
        style.map(
            "Link.TButton",
            foreground=[("active", "#81A1C1")]
        )
        
        # Configure accent button style
        style.configure(
            "Accent.TButton",
            foreground="white",
            background="#5E81AC",
            borderwidth=1,
            focuscolor="none"
        )
        
        style.map(
            "Accent.TButton",
            background=[("active", "#81A1C1")]
        )