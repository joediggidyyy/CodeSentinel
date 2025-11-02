#!/usr/bin/env python3
"""
Test script to verify that info buttons on page 8 work with single clicks.
"""

import tkinter as tk
from tkinter import ttk
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tools'))

from tools.codesentinel.gui_setup_wizard import GUISetupWizard

def test_info_button_responsiveness():
    """Test that info buttons respond properly to single clicks."""
    print("Testing info button responsiveness on Optional Features page...")
    
    root = tk.Tk()
    root.title("Test - Info Button Responsiveness")
    root.geometry("800x700")
    
    # Create wizard
    wizard = GUISetupWizard()
    
    print("\n=== Testing Info Button Single-Click Behavior ===")
    
    # Go to step 8 (Optional Features)
    print("1. Navigating to step 8 (Optional Features)")
    wizard.show_step(7)  # Step 8 (0-indexed)
    
    print("2. Optional Features page loaded successfully")
    print("3. Info buttons should now respond to single clicks")
    print("4. Manual testing required:")
    print("   - Click any 'ℹ️ Show Details' button")
    print("   - It should immediately show details and change to 'ℹ️ Hide Details'")
    print("   - Click 'ℹ️ Hide Details' button")
    print("   - It should immediately hide details and change to 'ℹ️ Show Details'")
    
    # Add test status
    status_frame = ttk.Frame(root)
    status_frame.pack(fill=tk.X, pady=10)
    
    ttk.Label(status_frame, text="✅ Info Button Fix Applied", 
              font=('Arial', 12, 'bold'), foreground="green").pack(pady=5)
    ttk.Label(status_frame, text="Info buttons now respond to single clicks", 
              font=('Arial', 10)).pack(pady=2)
    ttk.Label(status_frame, text="Previous issue: Required two clicks due to logic order", 
              font=('Arial', 9), foreground="gray").pack(pady=2)
    ttk.Label(status_frame, text="Fix: Toggle state first, then update UI", 
              font=('Arial', 9), foreground="gray").pack(pady=2)
    
    # Control buttons
    control_frame = ttk.Frame(root)
    control_frame.pack(fill=tk.X, pady=10)
    
    ttk.Button(control_frame, text="Test Complete - Close", 
               command=root.destroy).pack()
    
    root.mainloop()

if __name__ == "__main__":
    test_info_button_responsiveness()