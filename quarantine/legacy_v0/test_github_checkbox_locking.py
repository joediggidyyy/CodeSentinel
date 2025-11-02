#!/usr/bin/env python3
"""
Test GitHub checkbox navigation locking in real GUI scenario.
"""

import sys
sys.path.append('.')

from tools.codesentinel.gui_setup_wizard import GUISetupWizard

def test_github_checkbox_locking():
    """Test that GitHub checkbox properly locks navigation."""
    print("🧪 Testing GitHub Checkbox Navigation Locking")
    print("=" * 50)
    
    wizard = GUISetupWizard()
    
    # Navigate to GitHub Integration step (index 6)
    wizard.current_step = 6
    wizard.show_step(6)
    
    print(f"📍 Current step: {wizard.current_step} ({wizard.steps[wizard.current_step]})")
    
    # Test initial state (checkbox should be unchecked by default)
    print(f"\n1. Initial state:")
    print(f"   - API checkbox: {wizard.api_var.get()}")
    print(f"   - Validated flag: {wizard.github_api_validated}")
    locked, reason = wizard.check_navigation_lock(6)
    print(f"   - Navigation locked: {locked}")
    print(f"   - Lock reason: '{reason}'")
    
    button_text = wizard.next_button['text']
    button_state = wizard.next_button['state']
    print(f"   - Button: '{button_text}' ({button_state})")
    
    # Check the API checkbox
    print(f"\n2. Checking API checkbox...")
    wizard.api_var.set(True)
    
    # Force update navigation (this should happen automatically via trace)
    wizard.update_navigation_buttons(6)
    
    print(f"   - API checkbox: {wizard.api_var.get()}")
    print(f"   - Validated flag: {wizard.github_api_validated}")
    locked, reason = wizard.check_navigation_lock(6)
    print(f"   - Navigation locked: {locked}")
    print(f"   - Lock reason: '{reason}'")
    
    button_text = wizard.next_button['text']
    button_state = wizard.next_button['state']
    print(f"   - Button: '{button_text}' ({button_state})")
    
    # Test result
    expected_locked = True
    expected_reason = "Validate GitHub API"
    
    if locked == expected_locked and reason == expected_reason and "Validate GitHub API" in button_text:
        print(f"\n✅ SUCCESS: Navigation correctly locked when API checkbox is checked")
        result = True
    else:
        print(f"\n❌ ISSUE: Navigation not properly locked")
        print(f"   Expected: locked={expected_locked}, reason='{expected_reason}'")
        print(f"   Actual: locked={locked}, reason='{reason}'")
        result = False
    
    wizard.root.destroy()
    return result

if __name__ == "__main__":
    success = test_github_checkbox_locking()
    exit(0 if success else 1)