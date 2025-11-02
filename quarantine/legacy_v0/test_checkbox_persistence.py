#!/usr/bin/env python3
"""
Test script for checkbox state persistence in the optional features page.
Tests that checkbox selections persist when navigating back and forth.
"""

import tkinter as tk
from tkinter import ttk
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tools'))

from tools.codesentinel.gui_setup_wizard import GUISetupWizard
from tools.codesentinel.setup_wizard import CodeSentinelSetupWizard

def test_checkbox_persistence():
    """Test checkbox state persistence across navigation."""
    print("Testing checkbox state persistence...")
    
    # Create test window
    root = tk.Tk()
    root.title("Test - Checkbox State Persistence")
    root.geometry("800x700")
    
    # Create wizard
    wizard = GUISetupWizard()
    
    # Navigate to step 8 (Optional Features)
    wizard.current_step = 7  # 0-based, so step 8 is index 7
    wizard.show_step(7)
    
    print("✓ Navigated to Optional Features page")
    print(f"Initial checkbox states:")
    print(f"  - Cron: {wizard.cron_var.get()}")
    print(f"  - Git Hooks: {wizard.git_hooks_var.get()}")
    print(f"  - CI/CD: {wizard.ci_cd_var.get()}")
    
    # Add test controls
    control_frame = ttk.Frame(root)
    control_frame.pack(fill=tk.X, pady=10)
    
    # Control buttons
    def modify_and_test():
        # Modify checkbox states
        wizard.cron_var.set(True)
        wizard.git_hooks_var.set(False)
        wizard.ci_cd_var.set(True)
        print("Modified checkbox states:")
        print(f"  - Cron: {wizard.cron_var.get()}")
        print(f"  - Git Hooks: {wizard.git_hooks_var.get()}")
        print(f"  - CI/CD: {wizard.ci_cd_var.get()}")
    
    def navigate_away_and_back():
        # Navigate to step 9 (Summary)
        wizard.show_step(8)
        print("Navigated to Summary page")
        
        # Navigate back to step 8 (Optional Features)
        wizard.show_step(7)
        print("Navigated back to Optional Features page")
        print("Checkbox states after navigation:")
        print(f"  - Cron: {wizard.cron_var.get()}")
        print(f"  - Git Hooks: {wizard.git_hooks_var.get()}")
        print(f"  - CI/CD: {wizard.ci_cd_var.get()}")
    
    def test_back_button():
        # Simulate back button navigation
        wizard.current_step = 8  # Set to step 9
        wizard.go_back()  # Should go to step 8
        print("Used back button navigation")
        print("Final checkbox states:")
        print(f"  - Cron: {wizard.cron_var.get()}")
        print(f"  - Git Hooks: {wizard.git_hooks_var.get()}")
        print(f"  - CI/CD: {wizard.ci_cd_var.get()}")
    
    ttk.Button(control_frame, text="1. Modify Checkboxes", 
               command=modify_and_test).pack(side=tk.LEFT, padx=5)
    ttk.Button(control_frame, text="2. Navigate Away & Back", 
               command=navigate_away_and_back).pack(side=tk.LEFT, padx=5)
    ttk.Button(control_frame, text="3. Test Back Button", 
               command=test_back_button).pack(side=tk.LEFT, padx=5)
    ttk.Button(control_frame, text="Close", 
               command=root.destroy).pack(side=tk.RIGHT, padx=5)
    
    print("\nTest Instructions:")
    print("1. Click 'Modify Checkboxes' to change the selections")
    print("2. Click 'Navigate Away & Back' to test persistence")
    print("3. Click 'Test Back Button' to simulate back button usage")
    print("4. Verify that checkbox states are preserved throughout")
    
    root.mainloop()

if __name__ == "__main__":
    test_checkbox_persistence()