#!/usr/bin/env python3
"""
Test script for the enhanced requirements page (Step 3) of the GUI setup wizard.
Tests the new system information display and capabilities preview.
"""

import tkinter as tk
from tkinter import ttk
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tools'))

from tools.codesentinel.gui_setup_wizard import GUISetupWizard
from tools.codesentinel.setup_wizard import CodeSentinelSetupWizard

def test_requirements_page():
    """Test the enhanced requirements check page."""
    print("Testing enhanced Requirements Check page (Step 3)...")
    
    # Create test window
    root = tk.Tk()
    root.title("Test - Requirements Check Enhancement")
    root.geometry("800x700")
    
    # Create backend wizard
    backend = CodeSentinelSetupWizard()
    backend.check_system_requirements()  # Ensure requirements are checked
    
    # Create GUI wizard
    wizard = GUISetupWizard()
    wizard.backend_wizard = backend
    
    # Force requirements result to True to test the enhanced display
    wizard.requirements_result = True
    
    # Test the enhanced requirements result display
    wizard.show_requirements_result()
    
    print("✓ Enhanced requirements page loaded")
    print("Features tested:")
    print("  - System specifications display")
    print("  - Python version detection")
    print("  - Operating system information")
    print("  - Git availability check")
    print("  - Architecture information")
    print("  - CodeSentinel capabilities preview")
    print("  - Installation readiness indicator")
    
    # Add test controls
    control_frame = ttk.Frame(root)
    control_frame.pack(fill=tk.X, pady=10)
    
    ttk.Button(control_frame, text="Test Failed Requirements", 
               command=lambda: test_failed_requirements(wizard)).pack(side=tk.LEFT, padx=5)
    ttk.Button(control_frame, text="Test Passed Requirements", 
               command=lambda: test_passed_requirements(wizard)).pack(side=tk.LEFT, padx=5)
    ttk.Button(control_frame, text="Close", 
               command=root.destroy).pack(side=tk.RIGHT, padx=5)
    
    print("Test window opened. Use buttons to test different scenarios.")
    root.mainloop()

def test_failed_requirements(wizard):
    """Test the failed requirements display."""
    wizard.requirements_result = False
    wizard.show_requirements_result()
    print("Switched to failed requirements view")

def test_passed_requirements(wizard):
    """Test the passed requirements display with enhanced info."""
    wizard.requirements_result = True
    wizard.show_requirements_result()
    print("Switched to enhanced passed requirements view")

if __name__ == "__main__":
    test_requirements_page()