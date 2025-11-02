#!/usr/bin/env python3
"""
Check step index and content for GitHub Integration.
"""

import sys
sys.path.append('.')

from tools.codesentinel.gui_setup_wizard import GUISetupWizard

def check_step_info():
    """Check step information."""
    wizard = GUISetupWizard()
    
    print("📊 Step Information:")
    print("=" * 30)
    
    for i, step in enumerate(wizard.steps):
        print(f"Index {i}: {step}")
    
    print(f"\nGitHub Integration is at index: {wizard.steps.index('GitHub Integration')}")
    print(f"That corresponds to 'Step {wizard.steps.index('GitHub Integration') + 1} of {len(wizard.steps)}'")
    
    # Test what the screenshot shows - step 7 would be index 6
    if len(wizard.steps) > 6:
        print(f"Step 7 (index 6) is: {wizard.steps[6]}")
    
    wizard.root.destroy()

if __name__ == "__main__":
    check_step_info()