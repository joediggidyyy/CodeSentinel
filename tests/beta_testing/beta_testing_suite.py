"""
CodeSentinel Beta Testing Suite
===============================

Provides a command-line interface for managing isolated beta testing environments.

Features:
- Isolated virtual environment creation
- Beta version installation with validation
- Test iteration management with templated reports
- Session state persistence and resume capability
- Consolidated reporting across iterations
- Comprehensive error handling and logging

Platform Independent: Uses ASCII-only console output for cross-platform compatibility.
"""

import json
import os
import sys
import subprocess
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
import argparse
import uuid


class BetaTestingManager:
    """Manages isolated beta testing environments for CodeSentinel."""

    def __init__(self, version: str, session_id: Optional[str] = None):
        """
        Initialize the beta testing manager.

        Args:
            version: The version being tested (e.g., "v1.1.0-beta.1").
            session_id: Optional existing session ID to resume a previous session.
        """
        self.version = version
        self.workspace_root = Path(__file__).parent.parent.parent
        self.test_root = self.workspace_root / 'tests' / 'beta_testing' / self.version
        self.session_id = session_id or str(uuid.uuid4())
        self.iteration_count = 0
        self.tester_name = None
        self.python_executable = None
        self.wheel_file = None
        self.venv_path = None

        # Ensure directories exist
        self.env_dir = self.test_root / 'environment'
        self.logs_dir = self.test_root / 'logs'
        self.iterations_dir = self.test_root / 'iterations'
        self.consolidated_dir = self.test_root / 'consolidated'
        self.templates_dir = self.test_root / 'templates'
        self.sessions_dir = self.test_root / 'sessions'

        for d in [self.env_dir, self.logs_dir, self.iterations_dir, self.consolidated_dir, self.templates_dir, self.sessions_dir]:
            d.mkdir(parents=True, exist_ok=True)

    def create_isolated_env(self, python_executable: str = 'python'):
        """
        Create an isolated virtual environment for testing.

        Args:
            python_executable: Path to the Python executable to use.
            
        Returns:
            Path to created virtual environment, or None on failure.
        """
        venv_path = self.env_dir / f"venv_{self.session_id}"
        print(f"Creating isolated environment at: {venv_path}")

        try:
            # Validate Python executable first
            result = subprocess.run(
                [python_executable, '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                print(f"[FAIL] Invalid Python executable: {python_executable}")
                return None
            
            print(f"Using Python: {result.stdout.strip()}")
            
            # Create venv
            subprocess.run([python_executable, '-m', 'venv', str(venv_path)], check=True)
            print("[OK] Virtual environment created successfully.")
            return str(venv_path)
            
        except subprocess.TimeoutExpired:
            print(f"[FAIL] Timeout validating Python executable")
            return None
        except subprocess.CalledProcessError as e:
            print(f"[FAIL] Error creating virtual environment: {e}")
            return None
        except FileNotFoundError:
            print(f"[FAIL] Python executable not found: {python_executable}")
            return None

    def install_beta_version(self, venv_path: str, wheel_path: str):
        """
        Install the beta version of CodeSentinel into the isolated environment.

        Args:
            venv_path: Path to the virtual environment.
            wheel_path: Path to the CodeSentinel wheel file.
            
        Returns:
            True on success, False on failure.
        """
        # Validate wheel file exists
        if not Path(wheel_path).exists():
            print(f"[FAIL] Wheel file not found: {wheel_path}")
            return False
        
        if sys.platform == "win32":
            pip_executable = Path(venv_path) / 'Scripts' / 'pip.exe'
        else:
            pip_executable = Path(venv_path) / 'bin' / 'pip'
        
        if not pip_executable.exists():
            print(f"[FAIL] pip not found in virtual environment: {pip_executable}")
            return False

        print(f"Installing CodeSentinel from {wheel_path}...")
        try:
            # Upgrade pip first
            subprocess.run(
                [str(pip_executable), 'install', '--upgrade', 'pip'],
                check=True,
                capture_output=True,
                timeout=60
            )
            
            # Install the wheel
            result = subprocess.run(
                [str(pip_executable), 'install', wheel_path],
                check=True,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            print("[OK] CodeSentinel installed successfully.")
            
            # Verify installation
            verify_result = subprocess.run(
                [str(pip_executable), 'show', 'codesentinel'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if verify_result.returncode == 0 and 'Version:' in verify_result.stdout:
                version_line = [line for line in verify_result.stdout.split('\n') if 'Version:' in line][0]
                print(f"[OK] Verified installation: {version_line.strip()}")
            
            return True
            
        except subprocess.TimeoutExpired:
            print("[FAIL] Installation timeout")
            return False
        except subprocess.CalledProcessError as e:
            print(f"[FAIL] Error installing CodeSentinel: {e}")
            if e.stderr:
                print(f"Error details: {e.stderr}")
            return False

    def start_test_iteration(self, tester_name: str):
        """
        Start a new test iteration.
        
        Args:
            tester_name: Name of the tester conducting this iteration.

        Returns:
            Path to the new iteration report, or None on failure.
        """
        if not tester_name or not tester_name.strip():
            print("[WARN] No tester name provided, using 'Anonymous'")
            tester_name = "Anonymous"
        
        self.iteration_count += 1
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_filename = f"iteration_{self.iteration_count}_{timestamp}.md"
        report_path = self.iterations_dir / report_filename

        template_path = self.templates_dir / 'iteration_report_template.md'
        if not template_path.exists():
            print(f"[FAIL] Iteration report template not found at {template_path}")
            print("[INFO] Creating default template...")
            
            # Create a basic template if missing
            default_template = """# Beta Test Iteration Report

## Session Information
- **Session ID**: {{ session_id }}
- **Iteration Number**: {{ iteration_number }}
- **Tester**: {{ tester_name }}
- **Timestamp**: {{ timestamp }}

## Test Results
[Document test results here]

## Issues Found
[Document any issues discovered]

## Notes
[Additional observations]
"""
            template_path.parent.mkdir(parents=True, exist_ok=True)
            with open(template_path, 'w') as f:
                f.write(default_template)
            print(f"[OK] Created default template at {template_path}")

        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template = f.read()

            # Pre-fill template fields
            content = template.replace('{{ session_id }}', self.session_id)
            content = content.replace('{{ iteration_number }}', str(self.iteration_count))
            content = content.replace('{{ tester_name }}', tester_name.strip())
            content = content.replace('{{ timestamp }}', datetime.now().isoformat())

            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"[OK] Started new test iteration. Report at: {report_path}")
            return str(report_path)
            
        except Exception as e:
            print(f"[FAIL] Error creating iteration report: {e}")
            return None

    def consolidate_reports(self, lead_tester: str):
        """
        Consolidate all iteration reports into a single report.
        
        Args:
            lead_tester: Name of the lead tester for the consolidated report.
            
        Returns:
            Path to consolidated report, or None on failure.
        """
        if not lead_tester or not lead_tester.strip():
            print("[WARN] No lead tester name provided, using 'Anonymous'")
            lead_tester = "Anonymous"
        
        consolidated_report_path = self.consolidated_dir / f"consolidated_report_{self.session_id}.md"
        template_path = self.templates_dir / 'consolidated_report_template.md'

        if not template_path.exists():
            print(f"[FAIL] Consolidated report template not found at {template_path}")
            print("[INFO] Creating default consolidated template...")
            
            # Create basic template if missing
            default_template = """# Beta Testing Consolidated Report

## Session Information
- **Session ID**: {{ session_id }}
- **Lead Tester**: {{ lead_tester }}
- **Total Iterations**: {{ total_iterations }}
- **Report Generated**: {{ report_timestamp }}

## Iteration Summary
{{ iteration_summary_table }}

## Overall Assessment
[Summary of findings across all iterations]
"""
            template_path.parent.mkdir(parents=True, exist_ok=True)
            with open(template_path, 'w') as f:
                f.write(default_template)
            print(f"[OK] Created default template at {template_path}")

        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template = f.read()

            # Collect data from iteration reports
            iteration_reports = sorted(self.iterations_dir.glob('*.md'))
            
            if not iteration_reports:
                print("[WARN] No iteration reports found to consolidate")
            
            iteration_summary = []
            for idx, report in enumerate(iteration_reports, 1):
                iteration_summary.append(f"{idx}. {report.name}")

            # Fill template
            content = template.replace('{{ session_id }}', self.session_id)
            content = content.replace('{{ lead_tester }}', lead_tester.strip())
            content = content.replace('{{ total_iterations }}', str(len(iteration_reports)))
            content = content.replace('{{ iteration_summary_table }}', "\n".join(iteration_summary) if iteration_summary else "[No iterations]")
            content = content.replace('{{ report_timestamp }}', datetime.now().isoformat())

            with open(consolidated_report_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"[OK] Consolidated report created at: {consolidated_report_path}")
            return str(consolidated_report_path)
            
        except Exception as e:
            print(f"[FAIL] Error creating consolidated report: {e}")
            return None

    def save_session_state(self, test_results: Optional[Dict[str, Any]] = None):
        """
        Save the current session state to enable resume capability.
        
        Args:
            test_results: Dictionary of test results (test_id -> {completed, failed, etc.})
        """
        session_file = self.sessions_dir / f"session_{self.session_id}.json"
        
        state = {
            'session_id': self.session_id,
            'version': self.version,
            'tester_name': self.tester_name,
            'python_executable': str(self.python_executable) if self.python_executable else None,
            'wheel_file': str(self.wheel_file) if self.wheel_file else None,
            'venv_path': str(self.venv_path) if self.venv_path else None,
            'iteration_count': self.iteration_count,
            'test_results': test_results or {},
            'last_updated': datetime.now().isoformat()
        }
        
        with open(session_file, 'w') as f:
            json.dump(state, f, indent=2)
        
        print(f"[OK] Session state saved: {session_file}")
        return session_file
    
    def load_session_state(self):
        """
        Load a previously saved session state.
        
        Returns:
            Dictionary containing session state, or None if not found.
        """
        session_file = self.sessions_dir / f"session_{self.session_id}.json"
        
        if not session_file.exists():
            return None
        
        try:
            with open(session_file, 'r') as f:
                state = json.load(f)
            
            # Restore manager state
            self.tester_name = state.get('tester_name')
            self.python_executable = state.get('python_executable')
            self.wheel_file = state.get('wheel_file')
            self.venv_path = state.get('venv_path')
            self.iteration_count = state.get('iteration_count', 0)
            
            print(f"[OK] Session state loaded from: {session_file}")
            return state
        except Exception as e:
            print(f"[WARN] Error loading session state: {e}")
            return None
    
    @staticmethod
    def find_active_sessions(version: str):
        """
        Find all active (saved) sessions for a given version.
        
        Args:
            version: Version to search for sessions.
            
        Returns:
            List of tuples: (session_id, session_file_path, last_updated)
        """
        workspace_root = Path(__file__).parent.parent.parent
        sessions_dir = workspace_root / 'tests' / 'beta_testing' / version / 'sessions'
        
        if not sessions_dir.exists():
            return []
        
        sessions = []
        for session_file in sessions_dir.glob('session_*.json'):
            try:
                with open(session_file, 'r') as f:
                    state = json.load(f)
                sessions.append((
                    state['session_id'],
                    session_file,
                    state.get('last_updated', 'Unknown')
                ))
            except Exception:
                continue
        
        return sessions

    def cleanup_session(self):
        """
        Clean up the testing environment for the current session.
        
        Removes virtual environment and provides summary of session artifacts.
        """
        cleanup_success = True
        
        venv_path = self.env_dir / f"venv_{self.session_id}"
        if venv_path.exists():
            print(f"[INFO] Removing virtual environment: {venv_path}")
            try:
                shutil.rmtree(venv_path)
                print("[OK] Virtual environment removed")
            except Exception as e:
                print(f"[FAIL] Error removing virtual environment: {e}")
                cleanup_success = False
        else:
            print("[INFO] No virtual environment to remove")

        # Report on session artifacts
        iteration_reports = list(self.iterations_dir.glob('*.md'))
        if iteration_reports:
            print(f"\n[INFO] Session artifacts preserved:")
            print(f"  Iteration reports: {len(iteration_reports)}")
            for report in iteration_reports:
                print(f"    - {report.name}")
        
        # Check for session state file
        session_file = self.sessions_dir / f"session_{self.session_id}.json"
        if session_file.exists():
            print(f"  Session state: {session_file.name}")
        
        # Check for consolidated report
        consolidated_report = self.consolidated_dir / f"consolidated_report_{self.session_id}.md"
        if consolidated_report.exists():
            print(f"  Consolidated report: {consolidated_report.name}")

        if cleanup_success:
            print("\n[OK] Test session cleanup complete.")
        else:
            print("\n[WARN] Test session cleanup completed with errors.")
        
        return cleanup_success


def main():
    """Main entry point for the beta testing suite CLI."""
    parser = argparse.ArgumentParser(
        description='CodeSentinel Beta Testing Suite',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s create-env --version v1.1.2-beta.1
  %(prog)s install --version v1.1.2-beta.1 --wheel dist/codesentinel-1.1.2-py3-none-any.whl
  %(prog)s start-iteration --version v1.1.2-beta.1 --tester "John Doe"
  %(prog)s consolidate --version v1.1.2-beta.1 --lead-tester "Jane Smith"
  %(prog)s cleanup --version v1.1.2-beta.1
        """
    )
    
    parser.add_argument(
        'action',
        choices=['create-env', 'install', 'start-iteration', 'consolidate', 'cleanup'],
        help='Action to perform'
    )
    parser.add_argument(
        '--version',
        required=True,
        help='Version being tested (e.g., "v1.1.2-beta.1")'
    )
    parser.add_argument(
        '--python',
        default='python',
        help='Python executable for venv creation (default: python)'
    )
    parser.add_argument(
        '--wheel',
        help='Path to the CodeSentinel wheel file for installation'
    )
    parser.add_argument(
        '--tester',
        default='Anonymous',
        help='Name of the tester for iteration reports'
    )
    parser.add_argument(
        '--lead-tester',
        default='Anonymous',
        help='Name of the lead tester for consolidated report'
    )

    args = parser.parse_args()

    # Validate version format
    if not args.version.startswith('v'):
        print("[WARN] Version should start with 'v' (e.g., 'v1.1.2-beta.1')")
        print(f"[INFO] Proceeding with version: {args.version}")

    manager = BetaTestingManager(args.version)

    # Execute requested action
    try:
        if args.action == 'create-env':
            result = manager.create_isolated_env(args.python)
            sys.exit(0 if result else 1)
            
        elif args.action == 'install':
            if not args.wheel:
                print("[FAIL] --wheel parameter is required for install action")
                print("Usage: %(prog)s install --version VERSION --wheel PATH")
                sys.exit(1)
            
            venv_path = manager.env_dir / f"venv_{manager.session_id}"
            if not venv_path.exists():
                print(f"[FAIL] Virtual environment not found: {venv_path}")
                print("[INFO] Run 'create-env' action first")
                sys.exit(1)
            
            result = manager.install_beta_version(str(venv_path), args.wheel)
            sys.exit(0 if result else 1)
            
        elif args.action == 'start-iteration':
            result = manager.start_test_iteration(args.tester)
            sys.exit(0 if result else 1)
            
        elif args.action == 'consolidate':
            result = manager.consolidate_reports(args.lead_tester)
            sys.exit(0 if result else 1)
            
        elif args.action == 'cleanup':
            result = manager.cleanup_session()
            sys.exit(0 if result else 1)
            
    except KeyboardInterrupt:
        print("\n[INFO] Operation cancelled by user")
        sys.exit(130)  # Standard exit code for SIGINT
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
