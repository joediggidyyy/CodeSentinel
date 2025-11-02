#!/usr/bin/env python3
"""
CodeSentinel Setup Launcher
===========================

Unified launcher for CodeSentinel setup wizards.
Provides both terminal and GUI setup options.
"""

import argparse
import sys
from pathlib import Path

def main():
    """Main launcher entry point."""
    parser = argparse.ArgumentParser(
        description="CodeSentinel Setup Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
CodeSentinel Setup Options:

Terminal Mode (default):
  Interactive command-line setup wizard
  Best for headless environments and automation

GUI Mode:
  Graphical setup wizard with pop-up dialogs
  Best for desktop environments and first-time users

Examples:
  codesentinel-setup                    # Terminal mode (interactive)
  codesentinel-setup --gui             # GUI mode
  codesentinel-setup --non-interactive # Terminal mode (automated)
  codesentinel-setup --help            # Show this help
        """
    )

    parser.add_argument(
        '--gui',
        action='store_true',
        help='Launch GUI setup wizard instead of terminal wizard'
    )

    parser.add_argument(
        '--non-interactive',
        action='store_true',
        help='Run setup with default values (terminal mode only)'
    )

    parser.add_argument(
        '--install-location',
        type=str,
        help='Specify installation location (default: auto-detect)'
    )

    args = parser.parse_args()

    # Validate arguments
    if args.gui and args.non_interactive:
        print("Error: --gui and --non-interactive cannot be used together.")
        print("GUI mode is always interactive.")
        sys.exit(1)

    try:
        install_location = Path(args.install_location) if args.install_location else None

        if args.gui:
            # Launch GUI wizard
            print("Launching CodeSentinel GUI Setup Wizard...")
            from gui_setup_wizard import main as gui_main

            # Pass the install location to GUI wizard
            if install_location:
                sys.argv = ['gui_setup_wizard.py', '--install-location', str(install_location)]
            else:
                sys.argv = ['gui_setup_wizard.py']

            gui_main()
        else:
            # Launch terminal wizard
            from setup_wizard import main as terminal_main
            terminal_main()

    except ImportError as e:
        if args.gui:
            print(f"Error: GUI wizard requires tkinter. {e}")
            print("Install tkinter or use terminal mode: codesentinel-setup")
        else:
            print(f"Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nSetup failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()