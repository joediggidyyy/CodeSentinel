#!/usr/bin/env python3
"""
Test GitHub validation issue specifically.
"""

import sys
import time
sys.path.append('.')

from tools.codesentinel.gui_setup_wizard import GUISetupWizard
import tkinter as tk

def test_github_validation():
    """Test the specific GitHub validation issue."""
    print("🧪 Testing GitHub Validation Issue")
    print("=" * 40)
    
    # Create wizard
    wizard = GUISetupWizard()
    
    # Navigate to GitHub Integration step (index 6)
    wizard.current_step = 6
    wizard.show_step(6)
    
    print(f"📍 On step {wizard.current_step}: {wizard.steps[wizard.current_step]}")
    
    # Check initial state
    print(f"🔍 Initial state:")
    print(f"   - API checkbox: {wizard.api_var.get()}")
    print(f"   - Validated flag: {wizard.github_api_validated}")
    
    # Enable API checkbox
    print(f"\n✅ Checking API checkbox...")
    wizard.api_var.set(True)
    time.sleep(0.1)  # Let the trace callback execute
    
    print(f"   - API checkbox: {wizard.api_var.get()}")
    print(f"   - Validated flag: {wizard.github_api_validated}")
    
    # Check navigation state
    locked, reason = wizard.check_navigation_lock(6)
    print(f"   - Navigation locked: {locked}")
    print(f"   - Lock reason: '{reason}'")
    
    # Simulate successful validation
    print(f"\n🔑 Simulating successful GitHub validation...")
    wizard.github_api_validated = True
    
    # Force navigation button update
    wizard.update_navigation_buttons(6)
    
    # Check navigation state again
    locked, reason = wizard.check_navigation_lock(6)
    print(f"   - API checkbox: {wizard.api_var.get()}")
    print(f"   - Validated flag: {wizard.github_api_validated}")
    print(f"   - Navigation locked: {locked}")
    print(f"   - Lock reason: '{reason}'")
    
    # Check button state
    button_text = wizard.next_button['text']
    button_state = wizard.next_button['state']
    print(f"   - Button text: '{button_text}'")
    print(f"   - Button state: {button_state}")
    
    print(f"\n🎯 Expected: Button should show 'Next' and be enabled")
    print(f"🎯 Actual: Button shows '{button_text}' and is {button_state}")
    
    if button_text == "Next" and button_state == "normal":
        print("✅ SUCCESS: Navigation validation working correctly!")
    else:
        print("❌ ISSUE: Navigation remains locked after validation")
        
        # Additional debugging
        print(f"\n🔧 Debug info:")
        print(f"   - hasattr(wizard, 'api_var'): {hasattr(wizard, 'api_var')}")
        print(f"   - hasattr(wizard, 'github_api_validated'): {hasattr(wizard, 'github_api_validated')}")
        if hasattr(wizard, 'api_var'):
            print(f"   - wizard.api_var.get(): {wizard.api_var.get()}")
        print(f"   - wizard.github_api_validated: {wizard.github_api_validated}")
    
    # Cleanup
    wizard.root.destroy()
    
    return button_text == "Next" and button_state == "normal"

if __name__ == "__main__":
    success = test_github_validation()
    exit(0 if success else 1)