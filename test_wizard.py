#!/usr/bin/env python3
"""Test script for wizard v2"""
import sys
import traceback

try:
    from codesentinel.gui_wizard_v2 import main
    print("Imported successfully")
    main()
    print("Wizard completed")
except Exception as e:
    print(f"Error: {e}")
    traceback.print_exc()
