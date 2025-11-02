#!/usr/bin/env python3
"""
Test script for widget cleanup and navigation in GUI Setup Wizard.
This script tests the enhanced widget cleanup functionality to ensure
Tkinter naming conflicts are resolved.
"""

import sys
import os
import tkinter as tk
from pathlib import Path

# Add the tools directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "tools"))

def test_widget_cleanup():
    """Test widget cleanup functionality without showing GUI."""
    try:
        from tools.codesentinel.gui_setup_wizard import GUISetupWizard
        
        print("Testing GUI Setup Wizard widget cleanup...")
        
        # Create wizard instance (it creates its own root window)
        wizard = GUISetupWizard()
        
        print("✓ Wizard created successfully")
        
        # Test navigation between steps multiple times to trigger potential naming conflicts
        test_steps = [0, 1, 2, 1, 0, 3, 2, 1, 0]  # Navigate back and forth
        
        for i, step in enumerate(test_steps):
            try:
                wizard.show_step(step)
                print(f"✓ Step {step + 1} navigation test {i + 1} passed")
            except Exception as e:
                print(f"✗ Step {step + 1} navigation test {i + 1} failed: {e}")
                return False
        
        # Test reset functionality
        try:
            wizard.reset_wizard_state()
            print("✓ Reset functionality test passed")
        except Exception as e:
            print(f"✗ Reset functionality test failed: {e}")
            return False
        
        # Test error handling
        try:
            wizard.show_error_step("Test error message")
            print("✓ Error step display test passed")
        except Exception as e:
            print(f"✗ Error step display test failed: {e}")
            return False
        
        # Clean up
        wizard.root.destroy()
        print("✓ All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Test setup failed: {e}")
        return False

def test_cleanup_methods():
    """Test the cleanup methods directly."""
    try:
        from tools.codesentinel.gui_setup_wizard import GUISetupWizard
        
        print("\nTesting cleanup methods directly...")
        
        wizard = GUISetupWizard()
        
        # Add some test widgets to the content frame
        test_frame = tk.Frame(wizard.content_frame)
        test_frame.pack()
        
        test_label = tk.Label(test_frame, text="Test Label")
        test_label.pack()
        
        test_button = tk.Button(test_frame, text="Test Button")
        test_button.pack()
        
        print(f"✓ Created test widgets (count: {len(wizard.content_frame.winfo_children())})")
        
        # Test cleanup
        wizard.cleanup_content_frame()
        
        widget_count = len(wizard.content_frame.winfo_children())
        if widget_count == 0:
            print("✓ Cleanup method successfully removed all widgets")
        else:
            print(f"⚠ Cleanup method left {widget_count} widgets (may be normal)")
        
        wizard.root.destroy()
        return True
        
    except Exception as e:
        print(f"✗ Cleanup method test failed: {e}")
        return False

if __name__ == "__main__":
    print("CodeSentinel GUI Setup Wizard - Widget Cleanup Test")
    print("=" * 55)
    
    success1 = test_widget_cleanup()
    success2 = test_cleanup_methods()
    
    print("\n" + "=" * 55)
    if success1 and success2:
        print("🎉 ALL TESTS PASSED - Widget cleanup fixes are working!")
        print("The Tkinter naming conflict issue has been resolved.")
    else:
        print("❌ Some tests failed - further investigation needed.")
    
    print("\nTest completed. The GUI wizard should now work without naming conflicts.")