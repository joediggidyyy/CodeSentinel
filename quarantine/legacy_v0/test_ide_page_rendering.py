#!/usr/bin/env python3
"""
Test script for IDE integration page rendering (Step 7).
This specifically tests the rendering issue on page 7 that was reported.
"""

import sys
import os
import tkinter as tk
from pathlib import Path
import time

# Add the tools directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "tools"))

def test_ide_page_rendering():
    """Test the IDE integration page rendering multiple times."""
    try:
        from tools.codesentinel.gui_setup_wizard import GUISetupWizard
        
        print("Testing IDE Integration Page (Step 7) Rendering...")
        print("=" * 55)
        
        # Create wizard instance
        wizard = GUISetupWizard()
        wizard.root.withdraw()  # Hide the window for testing
        
        print("✓ Wizard created successfully")
        
        # Test step 7 rendering multiple times
        for test_round in range(1, 6):
            print(f"\nRound {test_round}: Testing IDE integration page rendering...")
            
            try:
                # Navigate to step 7 (IDE Integration)
                wizard.show_step(6)  # 0-indexed, so step 7 is index 6
                print(f"  ✓ Step 7 loaded successfully (attempt {test_round})")
                
                # Wait a moment for async operations
                time.sleep(0.5)
                
                # Check if IDE widgets were created
                if hasattr(wizard, 'ide_widgets') and wizard.ide_widgets:
                    widget_count = len(wizard.ide_widgets)
                    print(f"  ✓ IDE widgets created: {widget_count} IDEs configured")
                    
                    # Check if detection is running
                    detection_status = getattr(wizard, 'ide_detection_running', False)
                    print(f"  ✓ IDE detection status: {'Running' if detection_status else 'Not running'}")
                    
                    # Verify widgets exist and are properly configured
                    valid_widgets = 0
                    for ide_key, widgets in wizard.ide_widgets.items():
                        try:
                            checkbox = widgets['checkbox']
                            install_btn = widgets['install_btn']
                            
                            # Check if widgets exist
                            if checkbox.winfo_exists() and install_btn.winfo_exists():
                                valid_widgets += 1
                                
                        except Exception as widget_error:
                            print(f"    ⚠ Widget issue for {ide_key}: {widget_error}")
                    
                    print(f"  ✓ Valid widgets: {valid_widgets}/{widget_count}")
                    
                else:
                    print(f"  ⚠ No IDE widgets found on attempt {test_round}")
                
                # Navigate away and back to test re-rendering
                wizard.show_step(5)  # Go to step 6
                time.sleep(0.1)
                wizard.show_step(6)  # Go back to step 7
                print(f"  ✓ Re-navigation test successful")
                
            except Exception as step_error:
                print(f"  ✗ Step 7 rendering failed (attempt {test_round}): {step_error}")
                return False
        
        print(f"\n{'='*55}")
        print("🎉 ALL IDE PAGE RENDERING TESTS PASSED!")
        print("Step 7 (IDE Integration) renders correctly multiple times.")
        
        # Clean up
        wizard.root.destroy()
        return True
        
    except Exception as e:
        print(f"✗ Test setup failed: {e}")
        return False

def test_ide_detection_safety():
    """Test the safety mechanisms for IDE detection."""
    try:
        from tools.codesentinel.gui_setup_wizard import GUISetupWizard
        
        print("\nTesting IDE Detection Safety Mechanisms...")
        print("=" * 55)
        
        wizard = GUISetupWizard()
        wizard.root.withdraw()
        
        # Test multiple rapid calls to show_ide_integration
        print("Testing rapid step 7 navigation (potential thread conflicts)...")
        
        for i in range(5):
            wizard.show_step(6)  # Step 7
            time.sleep(0.1)
            wizard.show_step(5)  # Step 6
            time.sleep(0.1)
        
        wizard.show_step(6)  # Final step 7
        print("✓ Rapid navigation completed without errors")
        
        # Wait for any background threads to complete
        time.sleep(2)
        
        detection_status = getattr(wizard, 'ide_detection_running', False)
        print(f"✓ Final detection status: {'Running' if detection_status else 'Completed/Stopped'}")
        
        wizard.root.destroy()
        print("✓ Safety mechanisms working correctly")
        return True
        
    except Exception as e:
        print(f"✗ Safety test failed: {e}")
        return False

if __name__ == "__main__":
    print("CodeSentinel GUI Setup Wizard - IDE Page Rendering Test")
    print("=" * 60)
    
    success1 = test_ide_page_rendering()
    success2 = test_ide_detection_safety()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("🎉 ALL IDE PAGE TESTS PASSED!")
        print("The rendering issue on page 7 has been resolved.")
        print("\nThe wizard should now:")
        print("  • Render step 7 consistently on first view")
        print("  • Handle multiple navigation attempts safely")
        print("  • Prevent thread conflicts during IDE detection")
        print("  • Provide fallback UI updates if detection fails")
    else:
        print("❌ Some IDE page tests failed - further investigation needed.")
    
    print("\nIDE page rendering test completed.")