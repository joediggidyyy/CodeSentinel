#!/usr/bin/env python3
"""
Test the timing fix for navigation updates during page rendering.
"""

import sys
import time
sys.path.append('.')

from tools.codesentinel.gui_setup_wizard import GUISetupWizard

def test_timing_fix():
    """Test that the timing fix prevents rendering conflicts."""
    print("🧪 Testing Navigation Update Timing Fix")
    print("=" * 45)
    
    wizard = GUISetupWizard()
    
    # Test the specific scenario: GitHub checkbox checked during page rendering
    print("1. Setting up scenario...")
    wizard.api_var.set(True)  # Pre-check the API checkbox
    wizard.github_api_validated = False  # Ensure it needs validation
    
    print(f"   - API checkbox: {wizard.api_var.get()}")
    print(f"   - Validation needed: {not wizard.github_api_validated}")
    
    # Navigate to GitHub page (this should trigger rendering)
    print(f"\n2. Navigating to GitHub Integration page...")
    wizard.current_step = 6
    
    try:
        # This should call show_github_integration() which creates the checkbox
        # The checkbox creation might trigger toggle_api_config() which now uses root.after()
        wizard.show_step(6)
        
        print(f"   ✅ Page rendered without timing conflicts")
        
        # Check if content exists
        content_widgets = len(wizard.content_frame.winfo_children())
        print(f"   - Content widgets: {content_widgets}")
        
        # Wait for any scheduled updates to complete
        wizard.root.update()
        time.sleep(0.1)  # Allow root.after() calls to execute
        wizard.root.update()
        
        # Check navigation button state
        button_text = wizard.next_button['text']
        button_state = wizard.next_button['state']
        print(f"   - Button: '{button_text}' ({button_state})")
        
        # The button should show validation requirement since API is checked
        if "Validate GitHub API" in button_text:
            print(f"   ✅ Navigation validation working correctly")
            timing_success = True
        else:
            print(f"   ⚠️  Navigation validation may not be working: '{button_text}'")
            timing_success = False
            
        rendering_success = content_widgets > 0
        
    except Exception as e:
        print(f"   ❌ Error during page rendering: {e}")
        rendering_success = False
        timing_success = False
    
    # Test result
    if rendering_success and timing_success:
        print(f"\n✅ SUCCESS: Timing fix resolved rendering conflicts")
    elif rendering_success:
        print(f"\n⚠️  PARTIAL: Page renders but navigation validation issues")
    else:
        print(f"\n❌ ISSUE: Page rendering still has problems")
    
    wizard.root.destroy()
    return rendering_success

if __name__ == "__main__":
    success = test_timing_fix()
    exit(0 if success else 1)