#!/usr/bin/env python3
import sys
sys.path.append('.')

from tools.codesentinel.gui_setup_wizard import GUISetupWizard

wizard = GUISetupWizard()

print('=== Testing GitHub Navigation Lock ===')
print(f'Steps: {wizard.steps}')
print(f'GitHub Integration is at index: {wizard.steps.index("GitHub Integration")}')

# Test step 6 (GitHub Integration)
wizard.current_step = 6
print(f'Current step: {wizard.current_step} - {wizard.steps[6]}')

# Test with API checkbox unchecked
wizard.api_var.set(False)
wizard.github_api_validated = False
locked, reason = wizard.check_navigation_lock(6)
print(f'API unchecked: locked={locked}, reason="{reason}"')

# Test with API checkbox checked
wizard.api_var.set(True) 
wizard.github_api_validated = False
locked, reason = wizard.check_navigation_lock(6)
print(f'API checked: locked={locked}, reason="{reason}"')

wizard.root.destroy()