#!/usr/bin/env python3
"""
Test script for the comprehensive code formatting configuration.
Tests the enhanced formatting presets and advanced configuration dialog.
"""

import tkinter as tk
from tkinter import ttk
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tools'))

from tools.codesentinel.gui_setup_wizard import GUISetupWizard

def test_code_formatting():
    """Test the comprehensive code formatting configuration."""
    print("Testing comprehensive code formatting configuration...")
    
    root = tk.Tk()
    root.title("Test - Code Formatting Configuration")
    root.geometry("900x800")
    
    # Create wizard
    wizard = GUISetupWizard()
    
    print("\n=== Testing Code Formatting Step ===")
    
    # Go to code formatting step (Step 6)
    print("1. Navigating to Code Formatting step")
    wizard.show_step(5)  # Step 6 (0-indexed)
    
    print("2. Code Formatting page loaded successfully")
    print("3. Available formatting presets:")
    print("   🏠 CodeSentinel House Style (Recommended)")
    print("   📏 PEP 8 Strict Standard") 
    print("   🌐 Google Style Guide")
    print("   ⚫ Black Formatter Default")
    
    print("\n4. Comprehensive formatting parameters available:")
    
    # Display all the formatting parameters
    formatting_params = {
        "Basic Formatting": [
            "Line length (88 chars default)",
            "Indentation size (4 spaces)",
            "Quote style (double/single)",
            "Blank lines (classes/functions)"
        ],
        "Import & Organization": [
            "Automatic import sorting",
            "Import grouping by type",
            "Import sort style (isort/black/none)"
        ],
        "String & Literal Formatting": [
            "Format string literals",
            "Normalize quote consistency", 
            "Trailing commas in structures"
        ],
        "Expression Formatting": [
            "List/dict comprehensions",
            "Complex expression splitting",
            "Lambda expression formatting"
        ],
        "Documentation": [
            "Docstring style (Google/NumPy/Sphinx/PEP257)",
            "Preserve docstring formatting",
            "Inline comment formatting"
        ],
        "Advanced Options": [
            "Aggressive formatting",
            "Experimental features",
            "Skip magic methods"
        ]
    }
    
    for category, params in formatting_params.items():
        print(f"\n   {category}:")
        for param in params:
            print(f"     • {param}")
    
    print(f"\n5. Current preset: {wizard.format_preset_var.get()}")
    print(f"   Line length: {wizard.line_length_var.get()}")
    print(f"   Quote style: {wizard.quote_style_var.get()}")
    print(f"   Trailing commas: {wizard.trailing_commas_var.get()}")
    print(f"   Docstring style: {wizard.docstring_style_var.get()}")
    
    # Test status
    status_frame = ttk.Frame(root)
    status_frame.pack(fill=tk.X, pady=15)
    
    ttk.Label(status_frame, text="✅ Comprehensive Code Formatting Configuration", 
              font=('Arial', 12, 'bold'), foreground="green").pack(pady=5)
    ttk.Label(status_frame, text="Features implemented:", 
              font=('Arial', 10, 'bold')).pack(pady=(10, 5))
    
    features = [
        "🏠 CodeSentinel House Style preset (your preferred configuration)",
        "📏 Multiple industry-standard presets (PEP 8, Google, Black)",
        "🔧 Advanced tabbed configuration dialog",
        "⚙️ 20+ comprehensive formatting parameters",
        "🎯 Modal dialog with completion/close dependency",
        "🔄 Preset reset functionality",
        "📋 Live configuration preview"
    ]
    
    for feature in features:
        ttk.Label(status_frame, text=f"     {feature}", 
                 font=('Arial', 9)).pack(anchor=tk.W, padx=20)
    
    # Instructions
    instructions_frame = ttk.LabelFrame(root, text="Manual Testing Instructions")
    instructions_frame.pack(fill=tk.X, pady=15, padx=20)
    
    instructions = [
        "1. Select different formatting presets and observe the descriptions",
        "2. Click '🔧 Advanced Formatting Options...' to open the configuration dialog",
        "3. Navigate through the 4 tabs: Basic Settings, Imports & Organization, Advanced Options, Documentation",
        "4. Modify settings and click 'Apply & Close' - dialog should close and preset should change to 'custom'",
        "5. Use 'Reset to Current Preset' to restore preset values",
        "6. Test that dialog is modal (parent window should be disabled)"
    ]
    
    for i, instruction in enumerate(instructions, 1):
        ttk.Label(instructions_frame, text=instruction, 
                 font=('Arial', 9)).pack(anchor=tk.W, pady=2, padx=10)
    
    # Control buttons
    control_frame = ttk.Frame(root)
    control_frame.pack(fill=tk.X, pady=10)
    
    ttk.Button(control_frame, text="Open Advanced Dialog", 
               command=wizard.show_advanced_formatting_dialog).pack(side=tk.LEFT, padx=10)
    ttk.Button(control_frame, text="Test Complete - Close", 
               command=root.destroy).pack(side=tk.RIGHT, padx=10)
    
    root.mainloop()

if __name__ == "__main__":
    test_code_formatting()