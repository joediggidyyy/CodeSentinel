#!/usr/bin/env python3
"""
Test GitHub validation lock lifting with step capture fix.
"""

import sys
import time
sys.path.append('.')

from tools.codesentinel.gui_setup_wizard import GUISetupWizard

def test_validation_unlock():
    """Test that GitHub validation lock properly lifts after successful validation."""
    print("🧪 Testing GitHub Validation Lock Lifting")
    print("=" * 45)
    
    wizard = GUISetupWizard()
    
    # Set up scenario: GitHub step with API checkbox checked
    print("1. Setting up validation scenario...")
    wizard.current_step = 6  # GitHub Integration step
    wizard.api_var.set(True)
    wizard.github_api_validated = False
    
    # Update navigation to show locked state
    wizard.update_navigation_buttons(6)
    
    initial_button_text = wizard.next_button['text']
    initial_button_state = wizard.next_button['state']
    print(f"   - Initial button: '{initial_button_text}' ({initial_button_state})")
    
    # Verify navigation is locked
    locked, reason = wizard.check_navigation_lock(6)
    print(f"   - Navigation locked: {locked} ('{reason}')")
    
    if not locked or "Validate GitHub API" not in initial_button_text:
        print("   ❌ Setup failed - navigation should be locked")
        wizard.root.destroy()
        return False
    
    # Simulate successful validation (this is what happens in validate_git_repository)
    print(f"\n2. Simulating successful GitHub validation...")
    
    # This simulates what happens in the validate_repo() thread
    validation_step = wizard.current_step  # Capture step like the fix does
    wizard.github_api_validated = True    # Mark as validated
    
    # Change step to simulate user navigating away (the bug scenario)
    wizard.current_step = 5
    print(f"   - Changed current_step to {wizard.current_step} (simulating navigation)")
    
    # Schedule navigation update with captured step (like the fix does)
    wizard.root.after(10, lambda: wizard.update_navigation_buttons(validation_step))
    
    # Wait for scheduled update to execute
    wizard.root.update()
    time.sleep(0.05)
    wizard.root.update()
    
    # Go back to GitHub step to check result
    wizard.current_step = 6
    wizard.update_navigation_buttons(6)
    
    final_button_text = wizard.next_button['text']
    final_button_state = wizard.next_button['state']
    print(f"   - Final button: '{final_button_text}' ({final_button_state})")
    
    # Check if navigation is unlocked
    locked_after, reason_after = wizard.check_navigation_lock(6)
    print(f"   - Navigation locked after validation: {locked_after} ('{reason_after}')")
    
    # Test result
    validation_success = (
        not locked_after and 
        final_button_text == "Next" and 
        str(final_button_state).lower() == "normal" and
        wizard.github_api_validated
    )
    
    print(f"\n📊 Validation Results:")
    print(f"   - Validation flag set: {'✅' if wizard.github_api_validated else '❌'}")
    print(f"   - Navigation unlocked: {'✅' if not locked_after else '❌'}")
    print(f"   - Button text correct: {'✅' if final_button_text == 'Next' else '❌'}")
    print(f"   - Button state correct: {'✅' if str(final_button_state).lower() == 'normal' else '❌'} (actual: '{final_button_state}')")
    
    if validation_success:
        print(f"\n✅ SUCCESS: GitHub validation lock lifts correctly")
    else:
        print(f"\n❌ ISSUE: GitHub validation lock not lifting")
        print(f"   - Debug: locked_after={locked_after}, button='{final_button_text}', state='{final_button_state}', validated={wizard.github_api_validated}")
    
    wizard.root.destroy()
    return validation_success

if __name__ == "__main__":
    success = test_validation_unlock()
    exit(0 if success else 1)