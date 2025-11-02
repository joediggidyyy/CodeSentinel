#!/usr/bin/env python3
"""
Debug script to test checkbox persistence issue in detail.
"""

import tkinter as tk
from tkinter import ttk
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tools'))

def test_checkbox_persistence():
    """Test checkbox persistence in a simple scenario."""
    print("Testing checkbox persistence debugging...")
    
    root = tk.Tk()
    root.title("Debug - Checkbox Persistence")
    root.geometry("600x400")
    
    # Simulate the issue
    class TestWizard:
        def __init__(self):
            self.root = root
            self.content_frame = ttk.Frame(root)
            self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
        def get_or_create_var(self, var_name, var_type, default_value):
            """Get existing variable or create it with default value if it doesn't exist."""
            if not hasattr(self, var_name):
                print(f"Creating new variable: {var_name} = {default_value}")
                setattr(self, var_name, var_type(value=default_value))
            else:
                print(f"Using existing variable: {var_name} = {getattr(self, var_name).get()}")
            return getattr(self, var_name)
            
        def show_test_page(self):
            """Show a test page with checkboxes."""
            # Clear frame
            for widget in self.content_frame.winfo_children():
                widget.destroy()
                
            frame = ttk.Frame(self.content_frame)
            frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(frame, text="Test Checkboxes", font=('Arial', 12, 'bold')).pack(pady=(0, 20))
            
            # Use lazy initialization
            self.test_var1 = self.get_or_create_var('test_var1', tk.BooleanVar, False)
            self.test_var2 = self.get_or_create_var('test_var2', tk.BooleanVar, True)
            
            ttk.Checkbutton(frame, text="Test Checkbox 1", variable=self.test_var1).pack(anchor=tk.W, pady=5)
            ttk.Checkbutton(frame, text="Test Checkbox 2", variable=self.test_var2).pack(anchor=tk.W, pady=5)
            
            # Show current values
            values_frame = ttk.LabelFrame(frame, text="Current Values")
            values_frame.pack(fill=tk.X, pady=20)
            
            ttk.Label(values_frame, text=f"Checkbox 1: {self.test_var1.get()}").pack(anchor=tk.W, padx=10, pady=5)
            ttk.Label(values_frame, text=f"Checkbox 2: {self.test_var2.get()}").pack(anchor=tk.W, padx=10, pady=5)
            
        def show_other_page(self):
            """Show a different page."""
            # Clear frame
            for widget in self.content_frame.winfo_children():
                widget.destroy()
                
            frame = ttk.Frame(self.content_frame)
            frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(frame, text="Other Page", font=('Arial', 12, 'bold')).pack(pady=(0, 20))
            ttk.Label(frame, text="This is a different page to test navigation.").pack(pady=20)
    
    wizard = TestWizard()
    
    # Control buttons
    control_frame = ttk.Frame(root)
    control_frame.pack(fill=tk.X, pady=10)
    
    ttk.Button(control_frame, text="Show Test Page", 
               command=wizard.show_test_page).pack(side=tk.LEFT, padx=5)
    ttk.Button(control_frame, text="Show Other Page", 
               command=wizard.show_other_page).pack(side=tk.LEFT, padx=5)
    ttk.Button(control_frame, text="Close", 
               command=root.destroy).pack(side=tk.RIGHT, padx=5)
    
    # Start with test page
    wizard.show_test_page()
    
    print("Debug test started. Try:")
    print("1. Change checkbox values")
    print("2. Navigate to 'Other Page'")
    print("3. Navigate back to 'Test Page'")
    print("4. Check if checkbox values are preserved")
    
    root.mainloop()

if __name__ == "__main__":
    test_checkbox_persistence()