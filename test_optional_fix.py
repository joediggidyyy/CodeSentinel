#!/usr/bin/env python3
"""
Test checkbox persistence specifically on page 8 (Optional Features).
"""

import tkinter as tk
from tkinter import ttk
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tools'))

from tools.codesentinel.gui_setup_wizard import GUISetupWizard

def test_optional_features_persistence():
    """Test the optional features page persistence specifically."""
    print("Testing Optional Features page (Step 8) checkbox persistence...")
    
    root = tk.Tk()
    root.title("Test - Optional Features Persistence")
    root.geometry("800x700")
    
    # Create wizard
    wizard = GUISetupWizard()
    
    print("\n=== Testing Optional Features Navigation ===")
    
    # Go directly to step 8 (Optional Features)
    print("1. Going to step 8 (Optional Features)")
    wizard.show_step(7)  # Step 8 (0-indexed)
    
    # Check initial values
    print(f"Initial values:")
    print(f"  cron_var: {wizard.cron_var.get()}")
    print(f"  git_hooks_var: {wizard.git_hooks_var.get()}")
    print(f"  ci_cd_var: {wizard.ci_cd_var.get()}")
    
    # Modify values
    print("\n2. Modifying checkbox values")
    wizard.cron_var.set(True)
    wizard.git_hooks_var.set(False)
    wizard.ci_cd_var.set(True)
    
    print(f"Modified values:")
    print(f"  cron_var: {wizard.cron_var.get()}")
    print(f"  git_hooks_var: {wizard.git_hooks_var.get()}")
    print(f"  ci_cd_var: {wizard.ci_cd_var.get()}")
    
    # Navigate to step 9 (Summary)
    print("\n3. Going to step 9 (Summary)")
    wizard.show_step(8)  # Step 9 (0-indexed)
    
    # Navigate back to step 8
    print("\n4. Going back to step 8 (Optional Features)")
    wizard.show_step(7)  # Step 8 (0-indexed)
    
    # Check if values persisted
    print(f"Values after navigation:")
    print(f"  cron_var: {wizard.cron_var.get()}")
    print(f"  git_hooks_var: {wizard.git_hooks_var.get()}")
    print(f"  ci_cd_var: {wizard.ci_cd_var.get()}")
    
    # Check if they match expected values
    expected = {'cron_var': True, 'git_hooks_var': False, 'ci_cd_var': True}
    actual = {
        'cron_var': wizard.cron_var.get(),
        'git_hooks_var': wizard.git_hooks_var.get(),
        'ci_cd_var': wizard.ci_cd_var.get()
    }
    
    if actual == expected:
        print("\n✅ CHECKBOX PERSISTENCE TEST PASSED!")
        print("All checkbox values were preserved during navigation.")
    else:
        print("\n❌ CHECKBOX PERSISTENCE TEST FAILED!")
        print(f"Expected: {expected}")
        print(f"Actual: {actual}")
    
    # Add test controls
    control_frame = ttk.Frame(root)
    control_frame.pack(fill=tk.X, pady=10)
    
    ttk.Label(control_frame, text="Manual Test: Use Next/Back buttons to test persistence", 
              font=('Arial', 10)).pack(pady=5)
    ttk.Button(control_frame, text="Close", command=root.destroy).pack()
    
    root.mainloop()

if __name__ == "__main__":
    test_optional_features_persistence()