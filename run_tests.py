#!/usr/bin/env python3
"""Simple test runner for CodeSentinel."""

import subprocess
import sys
import os

def run_tests():
    """Run the test suite."""
    print("Running CodeSentinel tests...")

    # Change to the project root directory
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)

    # Run pytest
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pytest',
            'tests/',
            '--tb=short',
            '--verbose'
        ], capture_output=False)

        return result.returncode == 0

    except FileNotFoundError:
        print("pytest not found. Running with unittest...")
        # Fallback to unittest
        import unittest

        loader = unittest.TestLoader()
        suite = loader.discover('tests')

        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)

        return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)