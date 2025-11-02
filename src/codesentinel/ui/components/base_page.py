"""
CodeSentinel - Base Page Component

Created by: joediggidyyy
Architecture: SECURITY > EFFICIENCY > MINIMALISM

Base class for all setup wizard pages providing common functionality.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Callable, Optional

class BasePage:
    """
    Base class for setup wizard pages.
    Provides common functionality and interface for all pages.
    """
    
    def __init__(
        self,
        parent: tk.Widget,
        on_next: Callable[[], None],
        on_previous: Callable[[], None],
        config_data: Dict[str, Any]
    ):
        self.parent = parent
        self.on_next = on_next
        self.on_previous = on_previous
        self.config_data = config_data
        self.frame: Optional[tk.Frame] = None
        self.title = "Setup Page"
        
    def create_page(self) -> tk.Frame:
        """
        Create and return the page frame.
        Must be implemented by subclasses.
        """
        self.frame = ttk.Frame(self.parent)
        
        # Default content for base page
        content_frame = ttk.Frame(self.frame)
        content_frame.pack(fill="both", expand=True, padx=40, pady=30)
        
        title_label = ttk.Label(
            content_frame,
            text=self.title,
            style="Header.TLabel"
        )
        title_label.pack(pady=(0, 20))
        
        info_label = ttk.Label(
            content_frame,
            text="This is a placeholder page. Implementation needed.",
            style="Body.TLabel"
        )
        info_label.pack()
        
        # Navigation buttons
        self._create_navigation(content_frame)
        
        return self.frame
    
    def _create_navigation(self, parent: tk.Widget) -> None:
        """Create standard navigation buttons."""
        nav_frame = ttk.Frame(parent)
        nav_frame.pack(fill="x", pady=(30, 0), side="bottom")
        
        # Previous button (left-aligned)
        self.previous_button = ttk.Button(
            nav_frame,
            text="← Previous",
            command=self.on_previous
        )
        self.previous_button.pack(side="left")
        
        # Next button (right-aligned)
        self.next_button = ttk.Button(
            nav_frame,
            text="Next →",
            command=self.on_next
        )
        self.next_button.pack(side="right")
    
    def validate_page(self) -> bool:
        """
        Validate page input before proceeding.
        Override in subclasses for specific validation.
        """
        return True
    
    def save_data(self) -> Dict[str, Any]:
        """
        Save page data to configuration.
        Override in subclasses to return page-specific data.
        """
        return {}
    
    def on_page_shown(self) -> None:
        """
        Called when page is shown.
        Override in subclasses for page-specific initialization.
        """
        pass
    
    def show_error(self, message: str) -> None:
        """Display error message to user."""
        from tkinter import messagebox
        messagebox.showerror("Error", message)
    
    def show_warning(self, message: str) -> None:
        """Display warning message to user."""
        from tkinter import messagebox
        messagebox.showwarning("Warning", message)
    
    def show_info(self, message: str) -> None:
        """Display information message to user."""
        from tkinter import messagebox
        messagebox.showinfo("Information", message)
    
    def create_section(self, parent: tk.Widget, title: str, description: str = "") -> ttk.Frame:
        """Create a standard section with title and optional description."""
        section_frame = ttk.LabelFrame(parent, text=title, padding=20)
        section_frame.pack(fill="x", pady=(0, 15))
        
        if description:
            desc_label = ttk.Label(
                section_frame,
                text=description,
                style="Body.TLabel",
                wraplength=500
            )
            desc_label.pack(anchor="w", pady=(0, 10))
        
        return section_frame
    
    def create_field(
        self,
        parent: tk.Widget,
        label: str,
        widget_type: str = "entry",
        **kwargs
    ) -> tuple:
        """Create a labeled input field."""
        field_frame = ttk.Frame(parent)
        field_frame.pack(fill="x", pady=5)
        
        # Label
        label_widget = ttk.Label(field_frame, text=label)
        label_widget.pack(side="left", padx=(0, 10))
        
        # Input widget
        if widget_type == "entry":
            widget = ttk.Entry(field_frame, **kwargs)
        elif widget_type == "combobox":
            widget = ttk.Combobox(field_frame, **kwargs)
        elif widget_type == "checkbutton":
            widget = ttk.Checkbutton(field_frame, **kwargs)
        else:
            widget = ttk.Entry(field_frame, **kwargs)
        
        widget.pack(side="right", fill="x", expand=True)
        
        return label_widget, widget
    
    def create_status_label(self, parent: tk.Widget) -> ttk.Label:
        """Create a status label for displaying validation results."""
        status_label = ttk.Label(
            parent,
            text="",
            style="Body.TLabel"
        )
        status_label.pack(pady=5)
        return status_label
    
    def update_status(self, status_label: ttk.Label, message: str, status_type: str = "info") -> None:
        """Update status label with message and appropriate style."""
        status_label.config(text=message)
        
        style_map = {
            "success": "Success.TLabel",
            "error": "Error.TLabel",
            "warning": "Warning.TLabel",
            "info": "Body.TLabel"
        }
        
        style = style_map.get(status_type, "Body.TLabel")
        status_label.config(style=style)