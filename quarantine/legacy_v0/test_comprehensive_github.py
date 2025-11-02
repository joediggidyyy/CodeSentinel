#!/usr/bin/env python3
"""
Comprehensive test for GitHub page rendering and navigation validation.
"""

import sys
import time
sys.path.append('.')

from tools.codesentinel.gui_setup_wizard import GUISetupWizard

def comprehensive_github_test():
    """Test both rendering and navigation validation comprehensively."""
    print("🧪 Comprehensive GitHub Integration Test")
    print("=" * 50)
    
    wizard = GUISetupWizard()
    
    # Test 1: Initial page rendering with unchecked API
    print("1. Testing initial rendering (API unchecked)...")
    wizard.api_var.set(False)
    wizard.current_step = 6
    wizard.show_step(6)
    
    content_widgets = len(wizard.content_frame.winfo_children())
    wizard.root.update()
    time.sleep(0.05)
    wizard.root.update()
    
    button_text = wizard.next_button['text']
    test1_pass = content_widgets > 0 and button_text == "Next"
    print(f"   - Content rendered: {'✅' if content_widgets > 0 else '❌'}")
    print(f"   - Navigation unlocked: {'✅' if button_text == 'Next' else '❌'} ('{button_text}')")
    
    # Test 2: API checkbox interaction
    print(f"\n2. Testing API checkbox interaction...")
    wizard.api_var.set(True)
    # Allow time for callbacks to execute
    wizard.root.update()
    time.sleep(0.1)
    wizard.root.update()
    
    button_text = wizard.next_button['text']
    test2_pass = "Validate GitHub API" in button_text
    print(f"   - Navigation locked: {'✅' if test2_pass else '❌'} ('{button_text}')")
    
    # Test 3: Back navigation and return
    print(f"\n3. Testing back navigation...")
    wizard.current_step = 5
    wizard.show_step(5)
    wizard.root.update()
    
    print(f"4. Testing return to GitHub page...")
    wizard.current_step = 6
    wizard.show_step(6)
    
    content_widgets_after = len(wizard.content_frame.winfo_children())
    wizard.root.update()
    time.sleep(0.1)
    wizard.root.update()
    
    button_text_after = wizard.next_button['text']
    test3_pass = content_widgets_after > 0 and "Validate GitHub API" in button_text_after
    print(f"   - Content rendered after back nav: {'✅' if content_widgets_after > 0 else '❌'}")
    print(f"   - Navigation state preserved: {'✅' if 'Validate GitHub API' in button_text_after else '❌'} ('{button_text_after}')")
    
    # Test 4: Validation simulation
    print(f"\n5. Testing validation simulation...")
    wizard.github_api_validated = True
    wizard.update_navigation_buttons(6)
    
    button_text_validated = wizard.next_button['text']
    test4_pass = button_text_validated == "Next"
    print(f"   - Navigation unlocked after validation: {'✅' if test4_pass else '❌'} ('{button_text_validated}')")
    
    # Overall result
    all_tests_pass = test1_pass and test2_pass and test3_pass and test4_pass
    
    print(f"\n{'='*50}")
    print(f"📊 TEST RESULTS:")
    print(f"   1. Initial rendering: {'✅ PASS' if test1_pass else '❌ FAIL'}")
    print(f"   2. Checkbox interaction: {'✅ PASS' if test2_pass else '❌ FAIL'}")
    print(f"   3. Back navigation: {'✅ PASS' if test3_pass else '❌ FAIL'}")
    print(f"   4. Validation unlock: {'✅ PASS' if test4_pass else '❌ FAIL'}")
    print(f"\n🎯 OVERALL: {'✅ ALL TESTS PASS' if all_tests_pass else '❌ SOME TESTS FAILED'}")
    
    wizard.root.destroy()
    return all_tests_pass

if __name__ == "__main__":
    success = comprehensive_github_test()
    exit(0 if success else 1)