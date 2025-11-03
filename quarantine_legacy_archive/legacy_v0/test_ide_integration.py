#!/usr/bin/env python3
"""
Test script to verify the enhanced IDE integration step functionality.
"""

import tkinter as tk
from tools.codesentinel.gui_setup_wizard import GUISetupWizard

def test_ide_integration():
    """Test the enhanced IDE integration step."""
    try:
        # Create wizard instance
        wizard = GUISetupWizard()
        
        print("Testing IDE Integration step (page 7)...")
        
        # Go to step 7 (IDE Integration)
        wizard.show_step(6)  # Index 6 = step 7
        print("✓ Navigated to IDE Integration step")
        
        # Test IDE detection
        detected_ides = wizard.detect_installed_ides()
        print(f"✓ IDE detection completed. Found: {detected_ides}")
        
        # Check if IDE variables exist
        if hasattr(wizard, 'ide_vars'):
            print(f"✓ IDE variables created: {list(wizard.ide_vars.keys())}")
            for ide_key, var in wizard.ide_vars.items():
                print(f"  - {ide_key}: {var.get()}")
        else:
            print("❌ IDE variables missing")
        
        wizard.root.destroy()
        print("✓ IDE integration test completed successfully")
        
    except Exception as e:
        print(f"❌ Error during IDE integration test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ide_integration()