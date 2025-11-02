#!/usr/bin/env python3
"""
Integration test for CodeSentinel GUI Setup Wizard.
Tests the specific operations that previously caused Tkinter naming conflicts.
"""

import sys
import os
import tkinter as tk
import threading
import time
from pathlib import Path

# Add the tools directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "tools"))

def test_reset_wizard_functionality():
    """Test the reset wizard functionality that was causing naming conflicts."""
    try:
        from tools.codesentinel.gui_setup_wizard import GUISetupWizard
        
        print("Testing reset wizard functionality...")
        
        wizard = GUISetupWizard()
        wizard.root.withdraw()  # Hide window for testing
        
        # Navigate to different steps to populate state
        wizard.show_step(2)  # System requirements
        wizard.show_step(4)  # Alert system  
        wizard.show_step(6)  # GitHub integration
        
        # Simulate some configuration changes
        wizard.config['install_location'] = str(Path.cwd())
        wizard.config['email_alerts'] = True
        wizard.config['github_integration'] = True
        
        print("✓ Wizard state populated with test configuration")
        
        # Test reset functionality
        wizard.reset_wizard_state()
        print("✓ Reset wizard state completed without errors")
        
        # Verify reset worked
        if wizard.current_step == 0:
            print("✓ Current step correctly reset to 0")
        else:
            print(f"⚠ Current step is {wizard.current_step}, expected 0")
        
        # Test navigation after reset
        wizard.show_step(1)
        wizard.show_step(2)
        wizard.show_step(0)
        print("✓ Navigation after reset works correctly")
        
        wizard.root.destroy()
        return True
        
    except Exception as e:
        print(f"✗ Reset wizard test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_error_step_handling():
    """Test error step display that was causing widget conflicts."""
    try:
        from tools.codesentinel.gui_setup_wizard import GUISetupWizard
        
        print("\nTesting error step handling...")
        
        wizard = GUISetupWizard()
        wizard.root.withdraw()
        
        # Test various error scenarios
        error_messages = [
            "Test error message",
            "Git repository initialization failed",
            "Email connection timeout",
            "Invalid installation directory",
            "Setup failed with error: invalid command name"  # The actual error we fixed
        ]
        
        for i, error_msg in enumerate(error_messages):
            try:
                wizard.show_error_step(error_msg)
                print(f"✓ Error step test {i + 1} passed: {error_msg[:30]}...")
            except Exception as e:
                print(f"✗ Error step test {i + 1} failed: {e}")
                return False
        
        # Test recovery from error step
        wizard.show_step(0)  # Should work after error
        print("✓ Recovery from error step works correctly")
        
        wizard.root.destroy()
        return True
        
    except Exception as e:
        print(f"✗ Error step handling test failed: {e}")
        return False

def test_step_transition_stress():
    """Stress test step transitions to catch naming conflicts."""
    try:
        from tools.codesentinel.gui_setup_wizard import GUISetupWizard
        
        print("\nTesting step transition stress scenarios...")
        
        wizard = GUISetupWizard()
        wizard.root.withdraw()
        
        # Rapid step transitions (this was causing the naming conflicts)
        transition_sequence = [
            0, 1, 2, 1, 0, 3, 4, 3, 2, 1, 0,
            5, 6, 5, 4, 3, 2, 1, 0,
            7, 8, 7, 6, 5, 4, 3, 2, 1, 0,
            9, 8, 7, 6, 5, 4, 3, 2, 1, 0
        ]
        
        for i, step in enumerate(transition_sequence):
            try:
                wizard.show_step(step)
                if i % 10 == 0:
                    print(f"✓ Completed {i + 1}/40 rapid transitions")
            except Exception as e:
                print(f"✗ Transition {i + 1} failed at step {step}: {e}")
                return False
        
        print("✓ All 40 rapid step transitions completed successfully")
        
        wizard.root.destroy()
        return True
        
    except Exception as e:
        print(f"✗ Step transition stress test failed: {e}")
        return False

def test_wizard_complete_workflow():
    """Test a complete wizard workflow simulation."""
    try:
        from tools.codesentinel.gui_setup_wizard import GUISetupWizard
        
        print("\nTesting complete wizard workflow...")
        
        wizard = GUISetupWizard()
        wizard.root.withdraw()
        
        # Simulate going through all steps
        for step in range(10):  # 0-9 for all steps
            try:
                wizard.show_step(step)
                print(f"✓ Step {step + 1} loaded successfully")
                
                # Simulate some user interaction time
                wizard.root.update_idletasks()
                
            except Exception as e:
                print(f"✗ Step {step + 1} failed: {e}")
                return False
        
        # Test reset in the middle of workflow
        wizard.reset_wizard_state()
        print("✓ Mid-workflow reset successful")
        
        # Test continuing after reset
        wizard.show_step(0)
        wizard.show_step(5)
        wizard.show_step(9)
        print("✓ Post-reset navigation successful")
        
        wizard.root.destroy()
        return True
        
    except Exception as e:
        print(f"✗ Complete workflow test failed: {e}")
        return False

if __name__ == "__main__":
    print("CodeSentinel GUI Setup Wizard - Integration Test")
    print("=" * 52)
    
    tests = [
        test_reset_wizard_functionality,
        test_error_step_handling, 
        test_step_transition_stress,
        test_wizard_complete_workflow
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"Test {test_func.__name__} failed")
        except Exception as e:
            print(f"Test {test_func.__name__} crashed: {e}")
    
    print("\n" + "=" * 52)
    print(f"INTEGRATION TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL INTEGRATION TESTS PASSED!")
        print("The GUI wizard is now stable and free from naming conflicts.")
        print("\nYou can safely use:")
        print("  python -m tools.codesentinel.gui_setup_wizard")
        print("  codesentinel-setup-gui")
    else:
        print("❌ Some integration tests failed.")
        print("Further investigation may be needed.")
    
    print("\nIntegration test completed.")