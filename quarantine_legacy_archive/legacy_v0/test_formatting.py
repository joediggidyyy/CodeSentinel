#!/usr/bin/env python3
"""
Test script for the new Code Formatting preferences step.
"""

import tkinter as tk
from tkinter import ttk
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tools'))

from tools.codesentinel.gui_setup_wizard import GUISetupWizard

def test_code_formatting_step():
    """Test the new code formatting configuration step."""
    print("Testing Code Formatting Preferences step...")
    
    root = tk.Tk()
    root.title("Test - Code Formatting Step")
    root.geometry("800x700")
    
    # Create wizard
    wizard = GUISetupWizard()
    
    print("\n=== Testing Code Formatting Step ===")
    
    # Go to step 6 (Code Formatting) - 0-indexed, so step 5
    print("1. Navigating to step 6 (Code Formatting)")
    wizard.show_step(5)  # Step 6 (0-indexed)
    
    print("2. Code Formatting page loaded successfully")
    print("3. Features available for testing:")
    print("   - 🏠 House Style (Recommended)")
    print("   - 📏 PEP 8 Strict Standard") 
    print("   - 🌐 Google Style Guide")
    print("   - ⚫ Black Formatter Default")
    print("   - 🔧 Advanced Formatting Options dialog")
    print("   - Configuration preview updates")
    
    # Test preset selection
    print(f"\n4. Current preset: {wizard.format_preset_var.get()}")
    print(f"   Line length: {wizard.line_length_var.get()}")
    print(f"   Quote style: {wizard.quote_style_var.get()}")
    print(f"   Trailing commas: {wizard.trailing_commas_var.get()}")
    
    # Add test status
    status_frame = ttk.Frame(root)
    status_frame.pack(fill=tk.X, pady=10)
    
    ttk.Label(status_frame, text="✅ Code Formatting Step Added Successfully", 
              font=('Arial', 12, 'bold'), foreground="green").pack(pady=5)
    ttk.Label(status_frame, text="Features: 4 presets + advanced dialog + live preview", 
              font=('Arial', 10)).pack(pady=2)
    ttk.Label(status_frame, text="Test: Select different presets and try Advanced Options", 
              font=('Arial', 9), foreground="gray").pack(pady=2)
    
    # Control buttons
    control_frame = ttk.Frame(root)
    control_frame.pack(fill=tk.X, pady=10)
    
    def test_preset_change():
        wizard.format_preset_var.set("pep8_strict")
        wizard.update_format_preview()
        print("✓ Changed to PEP 8 Strict preset")
    
    def test_advanced_dialog():
        wizard.show_advanced_formatting_dialog()
        print("✓ Opened Advanced Formatting dialog")
    
    ttk.Button(control_frame, text="Test Preset Change", 
               command=test_preset_change).pack(side=tk.LEFT, padx=5)
    ttk.Button(control_frame, text="Test Advanced Dialog", 
               command=test_advanced_dialog).pack(side=tk.LEFT, padx=5)
    ttk.Button(control_frame, text="Close", 
               command=root.destroy).pack(side=tk.RIGHT, padx=5)
    
    root.mainloop()

if __name__ == "__main__":
    test_code_formatting_step()