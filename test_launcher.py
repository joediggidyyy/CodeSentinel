#!/usr/bin/env python3
"""Test GUI launcher entry points"""
import sys
import traceback

print("Testing gui_launcher.main()...")
try:
    from codesentinel.gui_launcher import main
    print("Imported successfully")
    result = main()
    print(f"Result: {result}")
except Exception as e:
    print(f"Error: {e}")
    traceback.print_exc()
