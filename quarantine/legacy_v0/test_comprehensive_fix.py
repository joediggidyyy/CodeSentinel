#!/usr/bin/env python3
"""
Test the comprehensive fix for checkbox persistence across all pages.
"""

import tkinter as tk
from tkinter import ttk
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tools'))

from tools.codesentinel.gui_setup_wizard import GUISetupWizard

def test_comprehensive_persistence():
    """Test that ALL checkbox states persist across ALL pages."""
    print("Testing comprehensive checkbox persistence fix...")
    
    root = tk.Tk()
    root.title("Test - Comprehensive State Persistence")
    root.geometry("800x600")
    
    # Create wizard
    wizard = GUISetupWizard()
    
    print("\n=== Testing All Page Navigation and State Persistence ===")
    
    # Test Step 2 (Installation Location)
    print("Testing Step 2 (Installation Location)")
    wizard.show_step(1)
    original_location = wizard.location_var.get()
    wizard.location_var.set("C:\\TestLocation")
    wizard.mode_var.set("standalone")
    print(f"Modified location: {wizard.location_var.get()}")
    print(f"Modified mode: {wizard.mode_var.get()}")
    
    # Test Step 5 (Alert System)  
    print("\nTesting Step 5 (Alert System)")
    wizard.show_step(4)
    wizard.console_var.set(False)
    wizard.email_var.set(True)
    wizard.security_var.set(False)
    print(f"Modified console: {wizard.console_var.get()}")
    print(f"Modified email: {wizard.email_var.get()}")
    print(f"Modified security: {wizard.security_var.get()}")
    
    # Test Step 8 (Optional Features)
    print("\nTesting Step 8 (Optional Features)")
    wizard.show_step(7)
    wizard.cron_var.set(True)
    wizard.git_hooks_var.set(False)
    wizard.ci_cd_var.set(True)
    print(f"Modified cron: {wizard.cron_var.get()}")
    print(f"Modified git_hooks: {wizard.git_hooks_var.get()}")
    print(f"Modified ci_cd: {wizard.ci_cd_var.get()}")
    
    # Navigate to different pages and back
    print("\n=== Testing Navigation Back and Forth ===")
    
    # Go to step 1 and back to step 2
    wizard.show_step(0)
    wizard.show_step(1)
    print(f"Step 2 after navigation - location: {wizard.location_var.get()}, mode: {wizard.mode_var.get()}")
    
    # Go to step 3 and back to step 5
    wizard.show_step(2)
    wizard.show_step(4)
    print(f"Step 5 after navigation - console: {wizard.console_var.get()}, email: {wizard.email_var.get()}, security: {wizard.security_var.get()}")
    
    # Go to step 6 and back to step 8
    wizard.show_step(5)
    wizard.show_step(7)
    print(f"Step 8 after navigation - cron: {wizard.cron_var.get()}, git_hooks: {wizard.git_hooks_var.get()}, ci_cd: {wizard.ci_cd_var.get()}")
    
    # Verify all values are still correct
    expected = {
        'location': "C:\\TestLocation",
        'mode': "standalone",
        'console': False,
        'email': True,
        'security': False,
        'cron': True,
        'git_hooks': False,
        'ci_cd': True
    }
    
    actual = {
        'location': wizard.location_var.get(),
        'mode': wizard.mode_var.get(),
        'console': wizard.console_var.get(),
        'email': wizard.email_var.get(),
        'security': wizard.security_var.get(),
        'cron': wizard.cron_var.get(),
        'git_hooks': wizard.git_hooks_var.get(),
        'ci_cd': wizard.ci_cd_var.get()
    }
    
    if actual == expected:
        print("\n✅ COMPREHENSIVE PERSISTENCE TEST PASSED!")
        print("All checkbox and input values were preserved across ALL pages!")
    else:
        print("\n❌ COMPREHENSIVE PERSISTENCE TEST FAILED!")
        print(f"Expected: {expected}")
        print(f"Actual: {actual}")
        
        # Show differences
        for key in expected:
            if expected[key] != actual[key]:
                print(f"  MISMATCH: {key} expected {expected[key]}, got {actual[key]}")
    
    # Add test controls
    control_frame = ttk.Frame(root)
    control_frame.pack(fill=tk.X, pady=10)
    
    ttk.Label(control_frame, text="Comprehensive persistence fix applied!", 
              font=('Arial', 12, 'bold')).pack(pady=5)
    ttk.Button(control_frame, text="Close", command=root.destroy).pack()
    
    root.mainloop()

if __name__ == "__main__":
    test_comprehensive_persistence()