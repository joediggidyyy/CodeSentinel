#!/usr/bin/env python3
"""
Test GitHub checkbox navigation with command callback.
"""

import sys
sys.path.append('.')

from tools.codesentinel.gui_setup_wizard import GUISetupWizard

def test_github_checkbox_with_command():
    """Test GitHub checkbox navigation with the command callback."""
    print("🧪 Testing GitHub Checkbox with Command Callback")
    print("=" * 50)
    
    wizard = GUISetupWizard()
    wizard.current_step = 6
    
    print(f"📍 Current step: {wizard.current_step} ({wizard.steps[wizard.current_step]})")
    
    # Test initial state
    print(f"\n1. Initial state (checkbox unchecked):")
    wizard.api_var.set(False)
    wizard.github_api_validated = False
    
    # Call toggle_api_config to simulate clicking the checkbox OFF
    wizard.toggle_api_config()
    
    button_text = wizard.next_button['text']
    button_state = wizard.next_button['state']
    print(f"   - Button: '{button_text}' ({button_state})")
    
    # Check the checkbox
    print(f"\n2. Checking API checkbox:")
    wizard.api_var.set(True)
    wizard.github_api_validated = False
    
    # Call toggle_api_config to simulate clicking the checkbox ON
    wizard.toggle_api_config()
    
    button_text = wizard.next_button['text']
    button_state = wizard.next_button['state']
    print(f"   - Button: '{button_text}' ({button_state})")
    
    # Verify the button shows validation requirement
    if "Validate GitHub API" in button_text and button_state == "disabled":
        print(f"\n✅ SUCCESS: Navigation properly locked when API checkbox is checked")
        print(f"   Button correctly shows: '{button_text}' ({button_state})")
        result = True
    else:
        print(f"\n❌ ISSUE: Navigation not properly locked")
        print(f"   Expected: Button with 'Validate GitHub API' and disabled state")
        print(f"   Actual: '{button_text}' ({button_state})")
        result = False
    
    wizard.root.destroy()
    return result

if __name__ == "__main__":
    success = test_github_checkbox_with_command()
    exit(0 if success else 1)