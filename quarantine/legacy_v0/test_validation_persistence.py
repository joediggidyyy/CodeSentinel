#!/usr/bin/env python3
"""
Test the specific GitHub validation persistence issue.
"""

import sys
sys.path.append('.')

from tools.codesentinel.gui_setup_wizard import GUISetupWizard

def test_validation_persistence():
    """Test that GitHub validation state persists after successful validation."""
    print("🧪 Testing GitHub Validation Persistence")
    print("=" * 45)
    
    wizard = GUISetupWizard()
    wizard.current_step = 6  # GitHub Integration step
    
    # Start with API checkbox checked and not validated (realistic scenario)
    wizard.api_var.set(True)
    wizard.github_api_validated = False  # Force initial state
    print(f"1. Initial state: checkbox={wizard.api_var.get()}, validated={wizard.github_api_validated}")
    
    # Check navigation (should be locked)
    locked, reason = wizard.check_navigation_lock(6)
    print(f"2. Before validation: locked={locked}, reason='{reason}'")
    
    # Simulate successful validation
    wizard.github_api_validated = True
    print(f"3. After validation: checkbox={wizard.api_var.get()}, validated={wizard.github_api_validated}")
    
    # Check navigation (should be unlocked)
    locked, reason = wizard.check_navigation_lock(6)
    print(f"4. After validation: locked={locked}, reason='{reason}'")
    
    # Trigger checkbox change callback (simulating UI events that might happen)
    # This should NOT reset the validation state since checkbox is still checked
    wizard.on_api_checkbox_change()
    print(f"5. After callback: checkbox={wizard.api_var.get()}, validated={wizard.github_api_validated}")
    
    # Check navigation again (should still be unlocked)
    locked, reason = wizard.check_navigation_lock(6)
    print(f"6. After callback: locked={locked}, reason='{reason}'")
    
    # Update navigation buttons to see final state
    wizard.update_navigation_buttons(6)
    button_text = wizard.next_button['text']
    button_state = wizard.next_button['state']
    print(f"7. Button state: text='{button_text}', state={button_state}")
    
    # Test result - navigation should remain unlocked
    success = (not locked and button_text == "Next" and str(button_state) == "normal" and wizard.github_api_validated)
    
    if success:
        print("✅ SUCCESS: Validation state preserved correctly!")
    else:
        print("❌ ISSUE: Validation state was reset or navigation not working")
        print(f"   Debug: locked={locked}, button_text='{button_text}', button_state='{button_state}', validated={wizard.github_api_validated}")
        print(f"   Types: locked={type(locked)}, button_text={type(button_text)}, button_state={type(button_state)}, validated={type(wizard.github_api_validated)}")
        
    wizard.root.destroy()
    return success

if __name__ == "__main__":
    success = test_validation_persistence()
    print(f"\nTest {'PASSED' if success else 'FAILED'}")
    exit(0 if success else 1)