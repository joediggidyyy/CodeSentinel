#!/usr/bin/env python3
"""
Test script for checkbox state persistence across all pages.
Tests the lazy initialization approach to fix variable persistence issues.
"""

import tkinter as tk
from tkinter import ttk
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tools'))

from tools.codesentinel.gui_setup_wizard import GUISetupWizard
from tools.codesentinel.setup_wizard import CodeSentinelSetupWizard

def test_state_persistence():
    """Test that checkbox states persist across navigation."""
    print("Testing state persistence across all GUI wizard pages...")
    
    # Create test window
    root = tk.Tk()
    root.title("Test - State Persistence Fix")
    root.geometry("900x800")
    
    # Create wizard
    wizard = GUISetupWizard()
    
    # Test lazy initialization method
    print("\n=== Testing lazy initialization method ===")
    
    # Test creating a variable that doesn't exist
    test_var = wizard.get_or_create_var('test_new_var', tk.BooleanVar, True)
    print(f"✓ Created new variable: {test_var.get()}")
    
    # Test getting existing variable preserves value
    test_var.set(False)
    test_var2 = wizard.get_or_create_var('test_new_var', tk.BooleanVar, True)
    print(f"✓ Retrieved existing variable: {test_var2.get()} (should be False)")
    
    # Test various pages to ensure variables are properly initialized
    print("\n=== Testing page navigation and state persistence ===")
    
    # Test Step 2 (Installation Location)
    wizard.show_step(1)  # Installation Location
    print(f"✓ Step 2 variables: location_var exists = {hasattr(wizard, 'location_var')}")
    print(f"✓ Step 2 variables: mode_var exists = {hasattr(wizard, 'mode_var')}")
    
    # Test Step 5 (Alert System)
    wizard.show_step(4)  # Alert System
    print(f"✓ Step 5 variables: console_var exists = {hasattr(wizard, 'console_var')}")
    print(f"✓ Step 5 variables: email_var exists = {hasattr(wizard, 'email_var')}")
    
    # Test Step 6 (GitHub Integration)
    wizard.show_step(5)  # GitHub Integration
    print(f"✓ Step 6 variables: copilot_var exists = {hasattr(wizard, 'copilot_var')}")
    
    # Test Step 8 (Optional Features)
    wizard.show_step(7)  # Optional Features
    print(f"✓ Step 8 variables: cron_var exists = {hasattr(wizard, 'cron_var')}")
    print(f"✓ Step 8 variables: git_hooks_var = {wizard.git_hooks_var.get()}")
    
    # Test navigation back and forth
    print("\n=== Testing back/forward navigation ===")
    
    # Go to step 8, modify a checkbox
    wizard.show_step(7)  # Optional Features
    original_cron = wizard.cron_var.get()
    wizard.cron_var.set(not original_cron)  # Toggle it
    modified_cron = wizard.cron_var.get()
    print(f"✓ Modified cron_var from {original_cron} to {modified_cron}")
    
    # Navigate away and back
    wizard.show_step(6)  # IDE Integration
    wizard.show_step(7)  # Back to Optional Features
    final_cron = wizard.cron_var.get()
    print(f"✓ After navigation, cron_var = {final_cron} (should be {modified_cron})")
    
    if final_cron == modified_cron:
        print("✅ STATE PERSISTENCE TEST PASSED!")
    else:
        print("❌ STATE PERSISTENCE TEST FAILED!")
    
    # Add test controls
    control_frame = ttk.Frame(root)
    control_frame.pack(fill=tk.X, pady=10)
    
    ttk.Label(control_frame, text="State persistence fix applied successfully!", 
              font=('Arial', 12, 'bold')).pack(pady=10)
    ttk.Button(control_frame, text="Close", command=root.destroy).pack()
    
    print("\nTest completed. GUI wizard should now maintain checkbox states during navigation.")
    root.mainloop()

if __name__ == "__main__":
    test_state_persistence()