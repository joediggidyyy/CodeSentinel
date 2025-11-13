"""
Utility functions for the 'test' command in the CodeSentinel CLI.

This module provides integration between the main CLI and the beta testing suite,
enabling streamlined beta testing workflows directly from the command line.
"""

import sys
import re
import subprocess
from pathlib import Path


def _get_relative_path(absolute_path):
    """
    Convert an absolute path to a repository-relative path.
    
    Args:
        absolute_path: Absolute path to convert (Path or str)
        
    Returns:
        String representation of path relative to repository root, prefixed with 'CodeSentinel/'
    """
    try:
        abs_path = Path(absolute_path)
        repo_root = Path.cwd()
        
        # Try to get relative path
        try:
            rel_path = abs_path.relative_to(repo_root)
            return f"CodeSentinel/{rel_path}".replace("\\", "/")
        except ValueError:
            # If path is not under repo root, just return the name with parent
            return f"CodeSentinel/.../{abs_path.parent.name}/{abs_path.name}".replace("\\", "/")
    except Exception:
        return str(absolute_path)


def _get_installed_version(venv_path):
    """
    Get the version of CodeSentinel installed in a virtual environment.
    
    Args:
        venv_path: Path to the virtual environment.
        
    Returns:
        Version string (e.g., "1.1.2") or None if not found.
    """
    if sys.platform == "win32":
        python_exec = Path(venv_path) / 'Scripts' / 'python.exe'
    else:
        python_exec = Path(venv_path) / 'bin' / 'python'
    
    try:
        result = subprocess.run(
            [str(python_exec), '-c', 'import codesentinel; print(codesentinel.__version__)'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    
    return None


def _view_session_reports(manager):
    """
    Display reports from the current session.
    
    Args:
        manager: BetaTestingManager instance.
    """
    print("\n" + "=" * 70)
    print("SESSION REPORTS")
    print("=" * 70)
    print()
    
    # Check for iteration reports
    iteration_reports = sorted(manager.iterations_dir.glob('*.md'))
    
    # Check for consolidated report
    consolidated_report = manager.consolidated_dir / f"consolidated_report_{manager.session_id}.md"
    
    # Check for session state
    session_file = manager.sessions_dir / f"session_{manager.session_id}.json"
    
    if not iteration_reports and not consolidated_report.exists():
        print("[INFO] No reports found for current session.")
        print(f"  Session ID: {manager.session_id[-8:]}")
        print(f"  Version: {manager.version}")
        print()
        print("Reports will be created as you run tests.")
        print("=" * 70)
        return
    
    print(f"Session ID: {manager.session_id}")
    print(f"Version: {manager.version}")
    print()
    
    # Display session state info
    if session_file.exists():
        try:
            import json
            with open(session_file, 'r') as f:
                state = json.load(f)
            print("Session State:")
            print("-" * 70)
            print(f"  File: {_get_relative_path(session_file)}")
            print(f"  Tester: {state.get('tester_name', 'Unknown')}")
            print(f"  Last Updated: {state.get('last_updated', 'Unknown')}")
            print(f"  Iterations: {state.get('iteration_count', 0)}")
            print("-" * 70)
            print()
        except Exception as e:
            print(f"[WARN] Could not read session state: {e}")
    
    # Display iteration reports
    if iteration_reports:
        print(f"Iteration Reports: ({len(iteration_reports)})")
        print("-" * 70)
        for idx, report in enumerate(iteration_reports, 1):
            print(f"  {idx}. {report.name}")
            print(f"     {_get_relative_path(report)}")
            print(f"     Full Path: {report}")
        print("-" * 70)
        print()
    
    # Display consolidated report
    if consolidated_report.exists():
        print("Consolidated Report:")
        print("-" * 70)
        print(f"  File: {consolidated_report.name}")
        print(f"  {_get_relative_path(consolidated_report)}")
        print(f"  Full Path: {consolidated_report}")
        print("-" * 70)
        print()
        
        # Ask if user wants to preview
        preview = input("Preview consolidated report? (y/n): ").strip().lower()
        if preview == 'y':
            try:
                with open(consolidated_report, 'r', encoding='utf-8') as f:
                    content = f.read()
                print()
                print("=" * 70)
                print("REPORT PREVIEW")
                print("=" * 70)
                lines = content.split('\n')
                for idx, line in enumerate(lines[:30], 1):  # Show first 30 lines
                    print(f"{idx:3}| {line}")
                if len(lines) > 30:
                    print(f"     ... ({len(lines) - 30} more lines)")
                print("=" * 70)
            except Exception as e:
                print(f"[FAIL] Could not read report: {e}")
    
    print()
    input("Press Enter to continue...")


def _view_all_session_reports(manager, active_sessions):
    """
    Display reports from all saved sessions for the current version.
    
    Args:
        manager: BetaTestingManager instance.
        active_sessions: List of tuples (session_id, session_file, last_updated).
    """
    import json
    
    print("\n" + "=" * 70)
    print(f"ALL SESSION REPORTS - {manager.version}")
    print("=" * 70)
    print()
    
    if not active_sessions:
        print("[INFO] No saved sessions found.")
        print("=" * 70)
        input("Press Enter to continue...")
        return
    
    for idx, (session_id, session_file, last_updated) in enumerate(active_sessions, 1):
        print(f"\nSession {idx}: {session_id[-8:]}")
        print("-" * 70)
        
        # Load session state
        try:
            with open(session_file, 'r') as f:
                state = json.load(f)
            
            print(f"  Tester: {state.get('tester_name', 'Unknown')}")
            print(f"  Last Updated: {last_updated}")
            print(f"  Iterations: {state.get('iteration_count', 0)}")
            
            # Check for reports
            session_test_root = manager.workspace_root / 'tests' / 'beta_testing' / manager.version
            session_iterations_dir = session_test_root / 'iterations'
            session_consolidated_dir = session_test_root / 'consolidated'
            
            # Find iteration reports for this session (files contain session ID)
            iteration_reports = []
            if session_iterations_dir.exists():
                # Since we don't have session-specific filtering, show all for now
                all_reports = list(session_iterations_dir.glob('*.md'))
                if all_reports:
                    print(f"  Iteration Reports: {len(all_reports)} total in version directory")
            
            # Check for consolidated report
            consolidated_report = session_consolidated_dir / f"consolidated_report_{session_id}.md"
            if consolidated_report.exists():
                print(f"  Consolidated Report: {_get_relative_path(consolidated_report)}")
            else:
                print(f"  Consolidated Report: Not yet generated")
                
        except Exception as e:
            print(f"  [WARN] Could not load session details: {e}")
        
        print("-" * 70)
    
    print()
    print("To view detailed reports, resume a session and use option 'W'")
    print("=" * 70)
    input("Press Enter to continue...")


def _delete_sessions_menu(manager, active_sessions):
    """
    Interactive menu for removing sessions from the active list.
    
    NOTE: This only removes the session state file to hide the session from the list.
    All iteration reports and consolidated reports are preserved for reference.
    
    Args:
        manager: BetaTestingManager instance.
        active_sessions: List of tuples (session_id, session_file, last_updated).
    """
    import shutil
    
    print("\n" + "=" * 70)
    print("REMOVE SESSIONS FROM LIST")
    print("=" * 70)
    print("\nThis removes sessions from the active sessions list.")
    print("All reports and test artifacts will be preserved.")
    print()
    
    for idx, (session_id, session_file, last_updated) in enumerate(active_sessions, 1):
        print(f"  {idx}. {session_id[-8:]} (Last: {last_updated})")
    
    print()
    print("Options:")
    print("  - Enter number(s) separated by commas to remove specific sessions")
    print("  - ALL to remove all sessions from list")
    print("  - C to cancel")
    print()
    
    choice = input("Your choice: ").strip().upper()
    
    if choice == 'C':
        print("Cancelled.")
        return
    
    if choice == 'ALL':
        confirm = input(f"Remove all {len(active_sessions)} session(s) from list? (yes/no): ").strip().lower()
        if confirm == 'yes':
            for session_id, session_file, _ in active_sessions:
                try:
                    # Delete ONLY the session state file
                    Path(session_file).unlink()
                    print(f"[OK] Removed session from list: {session_id[-8:]}")
                    print(f"     Reports preserved in tests/beta_testing/{manager.version}/")
                except Exception as e:
                    print(f"[FAIL] Error removing {session_id[-8:]}: {e}")
            print(f"\n[OK] Removed all sessions from active list")
            print("[INFO] All reports have been preserved")
        else:
            print("Cancelled.")
        return
    
    # Parse comma-separated numbers
    try:
        selections = [int(x.strip()) for x in choice.split(',')]
        sessions_to_remove = []
        
        for sel in selections:
            if 1 <= sel <= len(active_sessions):
                sessions_to_remove.append(active_sessions[sel - 1])
            else:
                print(f"[WARN]  Invalid number: {sel} (skipping)")
        
        if not sessions_to_remove:
            print("No valid selections. Cancelled.")
            return
        
        # Show what will be removed
        print(f"\nWill remove {len(sessions_to_remove)} session(s) from active list:")
        for session_id, session_file, last_updated in sessions_to_remove:
            print(f"  - {session_id[-8:]} (Last: {last_updated})")
        print("\nReports will be preserved in the beta_testing directory.")
        
        confirm = input("\nConfirm removal? (yes/no): ").strip().lower()
        if confirm == 'yes':
            for session_id, session_file, _ in sessions_to_remove:
                try:
                    # Delete ONLY the session state file
                    Path(session_file).unlink()
                    print(f"[OK] Removed session from list: {session_id[-8:]}")
                except Exception as e:
                    print(f"[FAIL] Error removing {session_id[-8:]}: {e}")
            print(f"\n[OK] Removed {len(sessions_to_remove)} session(s) from list")
            print("[INFO] All reports have been preserved")
        else:
            print("Cancelled.")
    
    except ValueError:
        print("[FAIL] Invalid input. Please enter comma-separated numbers or 'ALL'.")


def _select_python_executable():
    """
    Smart Python executable selection.
    
    Auto-detects the current Python interpreter and suggests it as default.
    Allows user to confirm or specify a different Python executable.
    
    Returns:
        Path to selected Python executable, or None if cancelled.
    """
    # Detect current Python interpreter
    current_python = sys.executable
    
    # Get Python version
    try:
        version_output = subprocess.check_output(
            [current_python, '--version'],
            stderr=subprocess.STDOUT,
            text=True
        ).strip()
    except Exception:
        version_output = "Unknown version"
    
    print(f"\nDetected Python interpreter:")
    print(f"  Python: {version_output}")
    print(f"  Path: {current_python}")
    
    choice = input("\nUse this Python interpreter? (y/n): ").strip().lower()
    
    if choice == 'y':
        return current_python
    
    # User wants to specify a different Python
    print("\nEnter path to Python executable (or press Enter to cancel):")
    print("Examples:")
    print("  - python")
    print("  - python3.13")
    print("  - C:\\Python313\\python.exe")
    
    custom_path = input("\nPython executable: ").strip()
    
    if not custom_path:
        print("Cancelled.")
        return None
    
    # Validate the custom Python executable
    try:
        test_output = subprocess.check_output(
            [custom_path, '--version'],
            stderr=subprocess.STDOUT,
            text=True
        ).strip()
        print(f"[OK] Found: {test_output}")
        return custom_path
    except FileNotFoundError:
        print(f"[FAIL] Python executable not found: {custom_path}")
        return None
    except Exception as e:
        print(f"[FAIL] Error validating Python executable: {e}")
        return None


def _select_wheel_file():
    """
    Smart wheel file selection from dist directory.
    
    Scans the dist directory for .whl files, identifies the most recent version,
    and prompts the user to confirm or select a different file.
    
    Returns:
        Path to selected wheel file, or None if cancelled.
    """
    dist_dir = Path.cwd() / 'dist'
    
    if not dist_dir.exists():
        print(f"[FAIL] Distribution directory not found: {dist_dir}")
        print("Please build the package first (e.g., python -m build)")
        return None
    
    # Find all wheel files
    wheel_files = list(dist_dir.glob('*.whl'))
    
    if not wheel_files:
        print(f"[FAIL] No wheel files found in: {dist_dir}")
        print("Please build the package first (e.g., python -m build)")
        return None
    
    # Extract version numbers and sort by version
    def extract_version(wheel_path):
        """Extract version from wheel filename (e.g., codesentinel-1.1.0b1-py3-none-any.whl)"""
        match = re.search(r'-(\d+\.\d+\.\d+(?:b\d+)?)-', wheel_path.name)
        if match:
            version_str = match.group(1)
            # Convert to tuple for proper version comparison (e.g., '1.1.0b1' -> (1, 1, 0, 'b', 1))
            parts = re.split(r'(\d+|[a-z]+)', version_str)
            parts = [int(p) if p.isdigit() else p for p in parts if p]
            return parts
        return (0,)  # Fallback for malformed filenames
    
    wheel_files.sort(key=extract_version, reverse=True)
    latest_wheel = wheel_files[0]
    
    # Suggest the latest version
    print(f"\nMost recent wheel file found:")
    print(f"  File: {latest_wheel.name}")
    print(f"  Path: {latest_wheel}")
    
    choice = input("\nUse this file? (y/n): ").strip().lower()
    
    if choice == 'y':
        return str(latest_wheel)
    
    # Show list of all available wheel files
    print("\nAvailable wheel files in dist/:")
    print("-" * 70)
    for idx, wheel in enumerate(wheel_files, 1):
        print(f"  {idx}. {wheel.name}")
    print(f"  0. Cancel")
    print("-" * 70)
    
    while True:
        try:
            selection = input("Select file number (or 0 to cancel): ").strip()
            if not selection:
                continue
            
            selection = int(selection)
            
            if selection == 0:
                print("Installation cancelled.")
                return None
            
            if 1 <= selection <= len(wheel_files):
                selected_wheel = wheel_files[selection - 1]
                print(f"[OK] Selected: {selected_wheel.name}")
                return str(selected_wheel)
            else:
                print(f"[FAIL] Invalid selection. Please enter a number between 0 and {len(wheel_files)}.")
        except ValueError:
            print("[FAIL] Invalid input. Please enter a number.")
        except KeyboardInterrupt:
            print("\nCancelled.")
            return None


def _get_package_version():
    """
    Get the current CodeSentinel package version from source.
    
    Returns:
        Version string (e.g., "1.1.2")
    """
    try:
        # First try to read from __init__.py in source tree
        init_file = Path(__file__).parent.parent / "__init__.py"
        if init_file.exists():
            with open(init_file, 'r') as f:
                for line in f:
                    if line.startswith('__version__'):
                        # Extract version: __version__ = "1.1.2"
                        version = line.split('=')[1].strip().strip('"').strip("'")
                        return version
        
        # Fallback to import (for installed package)
        from codesentinel import __version__
        return __version__
    except Exception:
        return "unknown"


def add_test_parser(subparsers):
    """
    Add the 'test' command parser to the main CLI.
    
    Args:
        subparsers: The subparsers object from argparse.
        
    Returns:
        The test parser object.
    """
    current_version = _get_package_version()
    default_test_version = f'v{current_version}-beta.1' if current_version != "unknown" else 'v1.1.2-beta.1'
    
    test_parser = subparsers.add_parser(
        'test',
        help='Run beta testing workflow'
    )
    test_parser.add_argument(
        '--version',
        type=str,
        default=default_test_version,
        help=f'Version to test (default: {default_test_version})'
    )
    test_parser.add_argument(
        '--interactive',
        action='store_true',
        default=True,
        help='Run in interactive mode (default)'
    )
    test_parser.add_argument(
        '--automated',
        action='store_true',
        help='Run in automated mode without user prompts'
    )
    test_parser.set_defaults(func=handle_test_command)
    
    return test_parser


def handle_test_command(args, codesentinel=None):
    """
    Handle the 'test' command execution.
    
    Args:
        args: Parsed command-line arguments.
        codesentinel: CodeSentinel instance (not used for testing).
    """
    # Add the tests directory to the path to import beta_testing_suite
    workspace_root = Path.cwd()
    tests_path = workspace_root / 'tests' / 'beta_testing'
    
    if not tests_path.exists():
        print(f"[FAIL] Beta testing directory not found: {tests_path}")
        print("Please ensure you're running from the CodeSentinel workspace root.")
        sys.exit(1)
    
    sys.path.insert(0, str(tests_path.parent))
    sys.path.insert(0, str(tests_path))  # Also add tests directory directly
    
    try:
        from beta_testing.beta_testing_suite import BetaTestingManager
    except ImportError as e:
        print(f"[FAIL] Could not import BetaTestingManager: {e}")
        print(f"Tried to import from: {tests_path.parent} and {tests_path}")
        sys.exit(1)
    
    # Get current version for display
    current_version = _get_package_version()
    
    print("=" * 70)
    print(f"CodeSentinel Beta Testing Workflow - v{current_version}")
    print("=" * 70)
    print(f"Test Version: {args.version}")
    print(f"Mode: {'Automated' if args.automated else 'Interactive'}")
    print()
    
    # Initialize the beta testing manager
    manager = BetaTestingManager(version=args.version)
    
    try:
        if args.automated:
            print("Running automated beta testing pipeline...")
            run_automated_workflow(manager)
        else:
            print("Running interactive beta testing pipeline...")
            run_interactive_workflow(manager)
    except KeyboardInterrupt:
        print("\n\n[INFO] Operation cancelled by user (Ctrl+C)")
        print("Exiting gracefully...")
        sys.exit(0)


def run_interactive_workflow(manager):
    """
    Run the interactive beta testing workflow with menu-driven test suite.
    
    Args:
        manager: BetaTestingManager instance.
    """
    try:
        _run_interactive_workflow_impl(manager)
    except KeyboardInterrupt:
        print("\n\n[INFO] Operation cancelled by user (Ctrl+C)")
        print("Exiting gracefully...")
        return


def _run_interactive_workflow_impl(manager):
    """
    Implementation of interactive workflow with session management.
    
    Args:
        manager: BetaTestingManager instance.
    """
    print("\n" + "=" * 70)
    print(f"CodeSentinel Beta Testing Workflow - {manager.version}")
    print("=" * 70)
    print()
    
    # Check for existing sessions
    active_sessions = manager.__class__.find_active_sessions(manager.version)
    
    resume_session = False
    if active_sessions:
        print(f"Found {len(active_sessions)} active session(s):")
        for idx, (session_id, session_file, last_updated) in enumerate(active_sessions, 1):
            print(f"  {idx}. {session_id[-8:]} (Last: {last_updated})")
        print()
        print("Options:")
        print("  - Enter number or last 8 chars to resume")
        print("  - N for new session")
        print("  - V to view reports from saved sessions")
        print("  - D to remove sessions from list (reports preserved)")
        print("  - X to exit")
        print()
        choice = input("Your choice: ").strip()
        
        # Handle exit
        if choice.upper() == 'X':
            print("Exiting.")
            return
        
        # Handle view reports
        if choice.upper() == 'V':
            _view_all_session_reports(manager, active_sessions)
            # Re-prompt after viewing
            print("\nReturning to session selection...")
            print()
            choice = input("Resume a session? (Enter number, last 8 chars, N for new, or X to exit): ").strip()
            if choice.upper() == 'X':
                print("Exiting.")
                return
            elif choice.upper() == 'N':
                print("[OK] Starting new session...")
            else:
                # Fall through to selection logic below
                pass
        
        # Handle delete sessions
        if choice.upper() == 'D':
            _delete_sessions_menu(manager, active_sessions)
            # Refresh active sessions list after deletion
            active_sessions = manager.__class__.find_active_sessions(manager.version)
            if not active_sessions:
                print("No sessions remaining. Starting new session...")
            else:
                # Re-prompt
                print("\nRemaining sessions:")
                for idx, (session_id, session_file, last_updated) in enumerate(active_sessions, 1):
                    print(f"  {idx}. {session_id[-8:]} (Last: {last_updated})")
                print()
                choice = input("Resume a session? (Enter number, last 8 chars, N for new, or X to exit): ").strip()
                if choice.upper() == 'X':
                    print("Exiting.")
                    return
                elif choice.upper() == 'N':
                    print("[OK] Starting new session...")
                else:
                    # Try to match by number or ID
                    if choice.isdigit() and 1 <= int(choice) <= len(active_sessions):
                        selected_session = active_sessions[int(choice) - 1]
                        manager.session_id = selected_session[0]
                        resume_session = True
                        print(f"[OK] Resuming session: {manager.session_id[-8:]}...")
                    else:
                        matched_sessions = [s for s in active_sessions if s[0].endswith(choice)]
                        if len(matched_sessions) == 1:
                            manager.session_id = matched_sessions[0][0]
                            resume_session = True
                            print(f"[OK] Resuming session: {manager.session_id[-8:]}...")
                        else:
                            print("[FAIL] Invalid selection. Starting new session...")
        
        # Try to match by number first
        elif choice.upper() == 'N':
            print("[OK] Starting new session...")
        elif choice.isdigit() and 1 <= int(choice) <= len(active_sessions):
            selected_session = active_sessions[int(choice) - 1]
            manager.session_id = selected_session[0]
            resume_session = True
            print(f"[OK] Resuming session: {manager.session_id[-8:]}...")
        else:
            # Try to match by partial session ID (last 8 chars)
            matched_sessions = [s for s in active_sessions if s[0].endswith(choice)]
            if len(matched_sessions) == 1:
                manager.session_id = matched_sessions[0][0]
                resume_session = True
                print(f"[OK] Resuming session: {manager.session_id[-8:]}...")
            elif len(matched_sessions) > 1:
                print(f"[FAIL] Ambiguous session ID. Multiple matches found.")
                print("[OK] Starting new session...")
            else:
                print(f"[FAIL] No session found matching '{choice}'")
                print("[OK] Starting new session...")
    
    if resume_session:
        # Load session state
        tests, tester_name, venv_path = _load_session_state(manager)
        
        if tests and tester_name and venv_path:
            print(f"[OK] Session restored!")
            print(f"  Tester: {tester_name}")
            print(f"  Environment: {_get_relative_path(venv_path)}")
            print(f"  Tests completed: {sum(1 for t in tests if t.get('completed', False))}/{len(tests)}")
            print()
            
            # Verify venv still exists
            if not Path(venv_path).exists():
                print("[WARN]  Virtual environment not found. Recreating...")
                venv_path = manager.create_isolated_env(manager.python_executable or sys.executable)
                manager.install_beta_version(venv_path, manager.wheel_file)
                manager.venv_path = venv_path
            
            # Jump directly to test menu
            _run_test_menu(manager, venv_path, tester_name, installation_complete=tests[0].get('completed', False))
            return
        else:
            print("[WARN]  Could not restore session. Starting fresh...")
            resume_session = False
    
    # Early exit option before starting new session
    if not resume_session:
        print("\nStarting new testing session...")
        choice = input("Continue? (y/n): ").strip().lower()
        if choice != 'y':
            print("Exiting.")
            return
    
    # New session - continue with normal workflow
    # Auto-detect Python and wheel
    python_exec = sys.executable
    try:
        python_version = subprocess.check_output(
            [python_exec, '--version'],
            stderr=subprocess.STDOUT,
            text=True
        ).strip()
        print(f"Detected Python: {python_version} [OK]")
    except Exception:
        print(f"Detected Python: {python_exec}")
    
    # Find latest wheel
    dist_dir = Path.cwd() / 'dist'
    wheel_files = list(dist_dir.glob('*.whl')) if dist_dir.exists() else []
    
    if wheel_files:
        def extract_version(wheel_path):
            match = re.search(r'-(\d+\.\d+\.\d+(?:b\d+)?)-', wheel_path.name)
            if match:
                version_str = match.group(1)
                parts = re.split(r'(\d+|[a-z]+)', version_str)
                parts = [int(p) if p.isdigit() else p for p in parts if p]
                return parts
            return (0,)
        
        wheel_files.sort(key=extract_version, reverse=True)
        latest_wheel = wheel_files[0]
        print(f"Latest wheel: {latest_wheel.name} [OK]")
    else:
        print("[WARN]  No wheel files found in dist/")
        print("Please build the package first (e.g., python -m build)")
        return
    
    print()
    
    # Get tester name (only question asked upfront)
    tester_name = input("Your name: ").strip() or "Anonymous"
    
    # Clear input buffer to prevent bleed-through to menu
    sys.stdout.flush()
    print()
    
    # Store configuration in manager
    manager.python_executable = python_exec
    manager.wheel_file = str(latest_wheel)
    manager.tester_name = tester_name
    
    # Auto-setup: Create environment and install
    print("Setting up isolated environment...")
    venv_path = manager.create_isolated_env(python_exec)
    if not venv_path:
        print("[FAIL] Failed to create environment.")
        return
    
    print("Installing CodeSentinel beta...")
    manager.install_beta_version(venv_path, str(latest_wheel))
    
    # Install pytest in the venv for testing
    print("Installing test dependencies...")
    if sys.platform == "win32":
        pip_exec = Path(venv_path) / 'Scripts' / 'pip.exe'
    else:
        pip_exec = Path(venv_path) / 'bin' / 'pip'
    
    try:
        subprocess.run([str(pip_exec), 'install', 'pytest'], check=True, capture_output=True)
        print("[OK] Test dependencies installed")
    except Exception as e:
        print(f"[WARN]  Could not install pytest: {e}")
    
    print()
    
    # Store venv path in manager
    manager.venv_path = venv_path
    
    # Start test iteration
    iteration_path = manager.start_test_iteration(tester_name)
    if not iteration_path:
        print("[FAIL] Failed to start test iteration.")
        return
    
    print(f"[OK] Test iteration ready!")
    print(f"  Report: {_get_relative_path(iteration_path)}")
    print()
    
    # Run interactive test menu (mark installation as complete since we just did it)
    _run_test_menu(manager, venv_path, tester_name, installation_complete=True)
    
    # Workflow complete - final report shown in menu if 'C' option was chosen


def _run_test_menu(manager, venv_path, tester_name, installation_complete=False):
    """
    Display and handle the interactive test menu.
    
    Args:
        manager: BetaTestingManager instance.
        venv_path: Path to the virtual environment.
        tester_name: Name of the tester.
        installation_complete: Whether installation was already completed.
    """
    # Define available tests
    tests = [
        {"id": 1, "name": "Installation Test", "script": "test_installation.py", "completed": installation_complete, "skip_in_run_all": True},
        {"id": 2, "name": "CLI Commands Test", "script": "test_cli.py", "completed": False, "skip_in_run_all": False},
        {"id": 3, "name": "Core Functionality Test", "script": "test_core.py", "completed": False, "skip_in_run_all": False},
        {"id": 4, "name": "Configuration Test", "script": "test_config.py", "completed": False, "skip_in_run_all": False},
        {"id": 5, "name": "Documentation Test", "script": "test_docs_formatting.py", "completed": False, "skip_in_run_all": False},
        {"id": 6, "name": "Integrity Test", "script": "test_integrity.py", "completed": False, "skip_in_run_all": False},
        {"id": 7, "name": "Process Monitor Test", "script": "test_process_monitor.py", "completed": False, "skip_in_run_all": False},
        {"id": 8, "name": "Dev Audit Test", "script": "test_dev_audit.py", "completed": False, "skip_in_run_all": False},
    ]
    
    # Track if any test has been run
    any_test_run = False
    
    while True:
        # Display menu
        print("\n" + "=" * 70)
        print("TEST SUITE MENU")
        print("=" * 70)
        print()
        
        for test in tests:
            if test["completed"]:
                status = "[OK]"
            elif test.get("failed", False):
                status = "✗"
            else:
                status = " "
            print(f"  [{status}] {test['id']}. {test['name']}")
        
        print()
        print("  A. Run All Tests")
        
        # Show reload option only after tests have been run
        if any_test_run:
            print("  R. Reload Version (reinstall from updated wheel)")
        
        print("  S. Save & Exit (resume later)")
        
        # Show complete session option only after tests have been run
        if any_test_run:
            print("  C. Complete Session (Save & Generate Final Report)")
        
        # Show view reports option
        print("  W. View Session Reports")
        
        # Show remove sessions option
        print("  D. Remove Sessions from List (reports preserved)")
        
        print("  X. Exit Without Saving")
        
        # Show change options only if no tests have been run yet
        if not any_test_run:
            print()
            print("  P. Change Python Interpreter")
            print("  V. Change Version/Wheel")
        
        print()
        print("=" * 70)
        
        try:
            choice = input("Select option: ").strip().upper()
        except KeyboardInterrupt:
            # Ctrl+C should act like 'X' (Exit Without Saving)
            print("\n\nInterrupted. Exiting without saving...")
            confirm = input("Are you sure? Test results will be lost. (y/n): ").strip().lower()
            if confirm == 'y':
                _cleanup_session(manager, venv_path)
                print("Session discarded.")
                break
            else:
                continue  # Return to menu
        
        if choice == 'A':
            # Run all tests (skip installation test)
            print("\nRunning all tests...")
            for test in tests:
                if not test.get("skip_in_run_all", False):
                    _run_single_test(manager, venv_path, test)
            any_test_run = True
            
            # Auto-save after running tests
            _save_session_state(manager, tests, tester_name)
        
        elif choice == 'R':
            # Reload version - reinstall from updated wheel
            if not any_test_run:
                print("\n[FAIL] Reload Version option not available yet.")
                print("   Run at least one test before reloading to a new version.")
                continue
            
            print("\n" + "=" * 70)
            print("RELOAD VERSION")
            print("=" * 70)
            print("\nThis will reinstall CodeSentinel from an updated wheel file.")
            print("Your test progress will be preserved.")
            print()
            
            # Save current state
            _save_session_state(manager, tests, tester_name)
            
            # Select new wheel
            new_wheel = _select_wheel_file()
            if new_wheel:
                wheel_path = Path(new_wheel) if isinstance(new_wheel, str) else new_wheel
                print(f"\nReinstalling from: {wheel_path.name}")
                try:
                    # Uninstall current version
                    if sys.platform == "win32":
                        pip_exec = Path(venv_path) / 'Scripts' / 'pip.exe'
                    else:
                        pip_exec = Path(venv_path) / 'bin' / 'pip'
                    
                    subprocess.run([str(pip_exec), 'uninstall', 'codesentinel', '-y'], 
                                   check=True, capture_output=True)
                    print("[OK] Uninstalled previous version")
                    
                    # Install new version
                    manager.install_beta_version(venv_path, str(new_wheel))
                    
                    # Get the newly installed version
                    new_version = _get_installed_version(venv_path)
                    if new_version:
                        print(f"[OK] Installed updated version: {new_version}")
                    else:
                        print("[OK] Installed updated version")
                    
                    # Update manager state
                    manager.wheel_file = str(new_wheel)
                    manager.iteration_count += 1
                    
                    # Save updated state
                    _save_session_state(manager, tests, tester_name)
                    
                except Exception as e:
                    print(f"[FAIL] Error reloading version: {e}")
            else:
                print("[FAIL] No wheel file selected")
        
        elif choice == 'S':
            # Save and exit (resume later)
            print("\n" + "=" * 70)
            print("SAVING SESSION")
            print("=" * 70)
            session_file = _save_session_state(manager, tests, tester_name)
            
            # Get iteration reports
            iteration_reports = list(manager.iterations_dir.glob('*.md'))
            
            print(f"\n[OK] Session saved successfully!")
            print()
            print("Session Information:")
            print("-" * 70)
            print(f"  Session ID:       {manager.session_id}")
            print(f"  Short ID:         {manager.session_id[-8:]}")
            print(f"  Version:          {manager.version}")
            print(f"  Tester:           {tester_name}")
            print(f"  Tests Completed:  {sum(1 for t in tests if t.get('completed', False))}/{len(tests)}")
            print("-" * 70)
            print()
            print("Saved Files:")
            print("-" * 70)
            print(f"  Session State:")
            print(f"    {_get_relative_path(session_file)}")
            if iteration_reports:
                print(f"  Iteration Reports: ({len(iteration_reports)})")
                for report in sorted(iteration_reports)[-3:]:  # Show last 3
                    print(f"    {_get_relative_path(report)}")
                if len(iteration_reports) > 3:
                    print(f"    ... and {len(iteration_reports) - 3} more")
            print("-" * 70)
            print()
            print("To Resume:")
            print(f"  codesentinel test --version {manager.version}")
            print(f"  Then select session: {manager.session_id[-8:]}")
            print()
            print("Session preserved. Use option 'C' when ready to complete.")
            print("=" * 70)
            break
        
        elif choice == 'C':
            # Complete session - save and generate final report
            if not any_test_run:
                print("\n[FAIL] Complete Session option not available yet.")
                print("   Run at least one test before completing the session.")
                continue
            
            print("\n" + "=" * 70)
            print("COMPLETING SESSION")
            print("=" * 70)
            print("Saving session state...")
            _save_session_state(manager, tests, tester_name)
            
            print("Generating consolidated report...")
            final_report = _generate_final_report(manager, tester_name)
            
            # Get iteration reports
            iteration_reports = list(manager.iterations_dir.glob('*.md'))
            
            # Display session summary
            print()
            print("=" * 70)
            print("BETA TESTING SESSION COMPLETE")
            print("=" * 70)
            print()
            print("Session Summary:")
            print("-" * 70)
            print(f"  Session ID:       {manager.session_id}")
            print(f"  Version:          {manager.version}")
            print(f"  Tester:           {tester_name}")
            print(f"  Tests Completed:  {sum(1 for t in tests if t.get('completed', False))}/{len(tests)}")
            print(f"  Tests Failed:     {sum(1 for t in tests if t.get('failed', False))}")
            print(f"  Iterations:       {len(iteration_reports)}")
            print("-" * 70)
            print()
            
            if final_report and final_report.exists():
                print("Generated Reports:")
                print("-" * 70)
                print(f"  Consolidated Report:")
                print(f"    {_get_relative_path(final_report)}")
                print(f"    Full Path: {final_report}")
                print()
                
                if iteration_reports:
                    print(f"  Iteration Reports: ({len(iteration_reports)})")
                    for report in sorted(iteration_reports):
                        print(f"    {_get_relative_path(report)}")
                print("-" * 70)
                print()
                
                # Display report content preview
                try:
                    with open(final_report, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    print("Report Preview:")
                    print("-" * 70)
                    
                    # Show first 15 lines of report
                    lines = content.split('\n')[:15]
                    for line in lines:
                        print(f"  {line}")
                    if len(content.split('\n')) > 15:
                        newline_char = '\n'
                        total_lines = len(content.split(newline_char))
                        remaining = total_lines - 15
                        print(f"  ... ({remaining} more lines)")
                        
                    print("-" * 70)
                except Exception as e:
                    print(f"[WARN] Could not preview report: {e}")
            
            print()
            print("=" * 70)
            
            _cleanup_session(manager, venv_path)
            break
        
        elif choice.upper() == 'W':
            # View session reports
            _view_session_reports(manager)
        
        elif choice.upper() == 'D':
            # Delete saved sessions
            active_sessions = manager.__class__.find_active_sessions(manager.version)
            if active_sessions:
                _delete_sessions_menu(manager, active_sessions)
            else:
                print(f"\n[INFO] No saved sessions found for version {manager.version}")
        
        elif choice == 'X':
            # Exit without saving
            print("\nExiting without saving...")
            confirm = input("Are you sure? Test results will be lost. (y/n): ").strip().lower()
            if confirm == 'y':
                _cleanup_session(manager, venv_path)
                print("Session discarded.")
                break
        
        elif choice.isdigit():
            # Run specific test
            test_id = int(choice)
            test = next((t for t in tests if t["id"] == test_id), None)
            if test:
                _run_single_test(manager, venv_path, test)
                any_test_run = True
                
                # Auto-save after each test
                _save_session_state(manager, tests, tester_name)
            else:
                print(f"[FAIL] Invalid test number: {test_id}")
        
        elif choice == 'P' and not any_test_run:
            # Change Python interpreter (only before tests run)
            print("\n[WARN]  Changing Python will require reinstalling the environment.")
            confirm = input("Continue? (y/n): ").strip().lower()
            if confirm == 'y':
                new_python = _select_python_executable()
                if new_python:
                    print("\nRecreating environment with new Python...")
                    _cleanup_session(manager, venv_path)
                    # This would need to return and restart the workflow
                    print("[WARN]  Please restart the test workflow to use the new Python interpreter.")
                    break
        
        elif choice == 'V' and not any_test_run:
            # Change version/wheel (only before tests run)
            print("\n[WARN]  Changing version will require reinstalling the environment.")
            confirm = input("Continue? (y/n): ").strip().lower()
            if confirm == 'y':
                new_wheel = _select_wheel_file()
                if new_wheel:
                    print("\nReinstalling with new wheel...")
                    # Reinstall in existing venv
                    if sys.platform == "win32":
                        pip_exec = Path(venv_path) / 'Scripts' / 'pip.exe'
                    else:
                        pip_exec = Path(venv_path) / 'bin' / 'pip'
                    
                    try:
                        # Uninstall old version
                        subprocess.run([str(pip_exec), 'uninstall', 'codesentinel', '-y'], 
                                     check=False, capture_output=True)
                        # Install new version
                        subprocess.run([str(pip_exec), 'install', new_wheel], 
                                     check=True, capture_output=True)
                        print("[OK] New version installed successfully")
                    except Exception as e:
                        print(f"[FAIL] Error reinstalling: {e}")
        
        else:
            if choice in ['P', 'V'] and any_test_run:
                print(f"[FAIL] Cannot change configuration after tests have been run")
            else:
                print(f"[FAIL] Invalid option: {choice}")


def _run_single_test(manager, venv_path, test):
    """
    Run a single test and update its status.
    
    Args:
        manager: BetaTestingManager instance.
        venv_path: Path to the virtual environment.
        test: Test dictionary.
    """
    print(f"\n{'─' * 70}")
    print(f"Running: {test['name']}")
    print('─' * 70)
    
    # Determine Python executable in venv
    if sys.platform == "win32":
        python_exec = Path(venv_path) / 'Scripts' / 'python.exe'
    else:
        python_exec = Path(venv_path) / 'bin' / 'python'
    
    # Path to test file
    test_file = Path.cwd() / 'tests' / test['script']
    
    if not test_file.exists():
        print(f"[WARN]  Test file not found: {test_file}")
        print(f"   Skipping {test['name']}")
        test['completed'] = False
        print('─' * 70)
        return
    
    try:
        # Run the test using pytest in the venv
        result = subprocess.run(
            [str(python_exec), '-m', 'pytest', str(test_file), '-v'],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Display the test output first
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        # Then show pass/fail status with enhanced verbosity
        print()  # Blank line for separation
        print("=" * 70)
        if result.returncode == 0:
            print(f"[PASS][PASS][PASS] {test['name']} PASSED [PASS][PASS][PASS]")
            print(f"Status: ALL TESTS SUCCESSFUL")
            print(f"Return Code: {result.returncode}")
            test['completed'] = True
            test['failed'] = False
        else:
            print(f"[FAIL][FAIL][FAIL] {test['name']} FAILED [FAIL][FAIL][FAIL]")
            print(f"Status: TEST FAILURES DETECTED")
            print(f"Return Code: {result.returncode}")
            
            # Extract and display consolidated failure summary
            print()
            print("Failure Summary:")
            print("-" * 70)
            
            # Combine stdout and stderr for analysis
            combined_output = (result.stdout or "") + (result.stderr or "")
            
            # Parse pytest output for failure information
            if "FAILED" in combined_output:
                # Extract failed test names
                import re
                failed_tests = re.findall(r'FAILED (.*?)(?:\s-|\s\[|$)', combined_output)
                if failed_tests:
                    for failed_test in failed_tests:
                        print(f"  * {failed_test.strip()}")
                else:
                    print("  * See output above for details")
            else:
                print("  * See output above for details")
            
            # Check for common error patterns
            if "ModuleNotFoundError" in combined_output or "ImportError" in combined_output:
                print("  * Missing dependencies detected")
            if "AssertionError" in combined_output:
                print("  * Assertion failures detected")
            if "AttributeError" in combined_output:
                print("  * Attribute/method errors detected")
            
            print("-" * 70)
            
            test['completed'] = False
            test['failed'] = True
        print("=" * 70)
    
    except subprocess.TimeoutExpired:
        print(f"[FAIL] {test['name']} TIMEOUT (exceeded 60s)")
        test['completed'] = False
        test['failed'] = True
    except Exception as e:
        print(f"[FAIL] {test['name']} ERROR: {e}")
        test['completed'] = False
        test['failed'] = True
    
    print('─' * 70)


def _save_session_state(manager, tests, tester_name):
    """
    Save the current session state including test results.
    
    Args:
        manager: BetaTestingManager instance.
        tests: List of test dictionaries with status.
        tester_name: Name of the tester.
        
    Returns:
        Path to the saved session file.
    """
    # Convert tests to serializable format
    test_results = {
        str(test['id']): {
            'name': test['name'],
            'script': test['script'],
            'completed': test.get('completed', False),
            'failed': test.get('failed', False),
            'skip_in_run_all': test.get('skip_in_run_all', False)
        }
        for test in tests
    }
    
    # Update manager state
    manager.tester_name = tester_name
    
    # Save to file
    return manager.save_session_state(test_results)


def _load_session_state(manager):
    """
    Load a previously saved session state and reconstruct test list.
    
    Args:
        manager: BetaTestingManager instance.
        
    Returns:
        Tuple of (tests_list, tester_name, venv_path) or (None, None, None) if load failed.
    """
    state = manager.load_session_state()
    
    if not state:
        return None, None, None
    
    # Reconstruct tests list from saved state
    test_results = state.get('test_results', {})
    tests = []
    for test_id, test_data in sorted(test_results.items(), key=lambda x: int(x[0])):
        tests.append({
            'id': int(test_id),
            'name': test_data['name'],
            'script': test_data['script'],
            'completed': test_data.get('completed', False),
            'failed': test_data.get('failed', False),
            'skip_in_run_all': test_data.get('skip_in_run_all', False)
        })
    
    tester_name = state.get('tester_name')
    venv_path = state.get('venv_path')
    
    return tests, tester_name, venv_path


def _generate_final_report(manager, tester_name):
    """
    Generate the final consolidated report and return its path.
    
    Args:
        manager: BetaTestingManager instance.
        tester_name: Name of the tester.
        
    Returns:
        Path to the consolidated report, or None if generation failed.
    """
    print("\nGenerating final report...")
    try:
        manager.consolidate_reports(tester_name)
        consolidated_path = manager.consolidated_dir / f"consolidated_report_{manager.session_id}.md"
        
        if consolidated_path.exists():
            print(f"[OK] Consolidated report: {_get_relative_path(consolidated_path)}")
            return consolidated_path
        else:
            print("[WARN]  Report file not found after generation")
            return None
    except Exception as e:
        print(f"[FAIL] Error generating report: {e}")
        return None


def _cleanup_session(manager, venv_path):
    """
    Clean up the testing session.
    
    Args:
        manager: BetaTestingManager instance.
        venv_path: Path to the virtual environment.
    """
    print("\nCleaning up session...")
    try:
        # Remove virtual environment
        if Path(venv_path).exists():
            import shutil
            shutil.rmtree(venv_path)
            print(f"[OK] Removed virtual environment: {_get_relative_path(venv_path)}")
    except Exception as e:
        print(f"[WARN]  Could not remove venv: {e}")
    
    print("[OK] Cleanup complete")


def run_automated_workflow(manager):
    """
    Run the automated beta testing workflow.
    
    Args:
        manager: BetaTestingManager instance.
    """
    print("[WARN]  Automated workflow not yet fully implemented.")
    print("This will be enhanced in future releases.")
    print("\nPlease use interactive mode (default) for now.")
